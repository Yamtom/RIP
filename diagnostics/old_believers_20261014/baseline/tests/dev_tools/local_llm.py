"""Local llama.cpp worker pool, sized for what a Q3 22B can actually do well.

Measured on this machine (Codestral-22B-v0.1 Q3_K_M, http://localhost:8080):
3.0 tok/s per stream, 4 slots, n_ctx 8192. Two consequences drive the design:

  * Output length is the whole cost. A 900-token answer is five minutes; a
    15-token answer is five seconds. Every task must have a tiny output.
  * The model is unreliable at judgement over a corpus it cannot hold. Asked to
    audit eight small script files against five rules it invented eight
    violations that were not there and missed all the real ones. So it never
    gets asked what is wrong with something - only to produce one short string
    from facts that are already in its prompt.

The pattern that works: one task per item, every fact inlined, a strict output
contract, a stop sequence, and a `check` callable that either accepts the answer
or rejects it. Rejections are retried once at temperature 0 and then handed back
so a human (or a bigger model) decides. Nothing unvalidated leaves this module.

Usage:

    from local_llm import Task, run_batch

    tasks = [Task(key="het_grain_trade",
                  prompt="...",
                  check=lambda s: s.istitle() and len(s) < 40)
             for ...]
    done, failed = run_batch(tasks)

Run this file directly for a self-test against the live server.
"""
import collections
import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

ENDPOINT = "http://localhost:8080/v1/chat/completions"
SLOTS = 4          # llama.cpp total_slots; more requests than this just queue
TIMEOUT = 180
CONTEXT_LIMIT = 8192


def one_line(answer):
    return "answer must be one line" if "\n" in answer else True


def word_count(minimum, maximum):
    def check(answer):
        count = len(answer.split())
        return True if minimum <= count <= maximum else (
            "expected %d-%d words, got %d" % (minimum, maximum, count))
    return check


def title_case(answer):
    return "answer must start with an uppercase letter" if not answer[:1].isupper() else True


def forbid(*terms):
    def check(answer):
        found = next((term for term in terms if term.casefold() in answer.casefold()), None)
        return True if found is None else "forbidden term: %s" % found
    return check


def matches(pattern):
    compiled = re.compile(pattern)
    return lambda answer: True if compiled.fullmatch(answer) else "answer does not match %s" % pattern


def choice_from(*choices):
    allowed = set(choices)
    return lambda answer: True if answer in allowed else "answer is not an allowed choice"


def all_of(*checks):
    def check(answer):
        for candidate in checks:
            result = candidate(answer)
            if result is not True:
                return result if isinstance(result, str) else "validator rejected answer"
        return True
    return check


def constrained_prompt(task, facts, contract):
    """Build the only prompt shape appropriate for the local Q3 model."""
    return (
        "You generate one short draft only from the facts below.\n"
        "Do not verify facts, find errors, or invent missing information.\n"
        "Return only the requested format, with no explanation.\n"
        "If the format cannot be met, return REJECT.\n\n"
        "Task: %s\nFacts: %s\nAnswer contract: %s"
    ) % (task, facts, contract)


@dataclass
class Task:
    key: str
    prompt: str
    check: Callable[[str], bool] = lambda s: bool(s.strip())
    max_tokens: int = 48
    stop: tuple = ("\n", "<|im_end|>")
    source: Optional[str] = None
    normalizer: Callable[[str], str] = str.casefold
    metadata: dict = field(default_factory=dict)
    answer: Optional[str] = None
    error: Optional[str] = None
    tokens: int = 0
    seconds: float = 0.0
    attempts: int = 0


def _post(prompt, max_tokens, stop, temperature):
    body = json.dumps({
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stop": list(stop),
        "stream": False,
    }).encode("utf-8")
    req = urllib.request.Request(ENDPOINT, data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return json.loads(r.read().decode("utf-8"))


MARKERS = ("<|im_end|>", "<|im_start|>", "</s>")


def _clean(text):
    """Strip the chat-template residue and framing the model likes to add.

    A short max_tokens can cut the end marker in half, so "INSIDE<|im_" comes
    back and a plain split on the whole marker leaves it in place. That cost a
    whole benchmark run reading as 0%. Trim any prefix of a marker too.
    """
    for mark in MARKERS:
        text = text.split(mark)[0]
        for n in range(len(mark) - 1, 1, -1):       # "<|im_", "<|i", "<|"
            if text.endswith(mark[:n]):
                text = text[:-n]
                break
    text = text.strip()
    text = re.sub(r'^(sure|here(\s+is|\'s)[^:]*|answer)\s*:\s*', '', text, flags=re.I)
    return text.strip().strip('"').strip()


def _run_one(task):
    for temperature in (0.2, 0.0):
        task.attempts += 1
        t0 = time.time()
        try:
            data = _post(task.prompt, task.max_tokens, task.stop, temperature)
        except (urllib.error.URLError, OSError, ValueError) as exc:
            task.error = "transport: %s" % exc
            return task
        task.seconds += time.time() - t0
        task.tokens += data.get("usage", {}).get("completion_tokens", 0)
        answer = _clean(data["choices"][0]["message"]["content"])
        checked = task.check(answer)
        if checked is True:
            task.answer, task.error = answer, None
            return task
        reason = checked if isinstance(checked, str) else "validator rejected answer"
        task.error = "rejected (%s): %r" % (reason, answer[:80])
    return task


def _fingerprint(task):
    payload = json.dumps({"prompt": task.prompt, "max_tokens": task.max_tokens,
                          "stop": task.stop}, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _read_cache(path):
    if not path or not Path(path).is_file():
        return {}
    return {item["fingerprint"]: item["answer"]
            for line in Path(path).read_text(encoding="utf-8").splitlines()
            if (item := json.loads(line)).get("answer")}


def _write_cache(path, tasks):
    if not path:
        return
    with Path(path).open("w", encoding="utf-8", newline="\n") as handle:
        for task in tasks:
            if task.answer is not None:
                handle.write(json.dumps({"fingerprint": _fingerprint(task),
                                         "answer": task.answer}, ensure_ascii=False) + "\n")


def _write_report(path, tasks):
    if not path:
        return
    with Path(path).open("w", encoding="utf-8", newline="\n") as handle:
        for task in tasks:
            handle.write(json.dumps({
                "key": task.key, "source": task.source, "fingerprint": _fingerprint(task),
                "answer": task.answer, "error": task.error, "attempts": task.attempts,
                "tokens": task.tokens, "seconds": round(task.seconds, 3),
                "metadata": task.metadata,
            }, ensure_ascii=False) + "\n")


def preflight(tasks, context_limit=CONTEXT_LIMIT):
    """Reject task batches that cannot fit the live server's 8192-token context."""
    if not health():
        raise RuntimeError("no llama.cpp server on localhost:8080")
    for task in tasks:
        estimated_tokens = len(task.prompt) // 3 + task.max_tokens
        if estimated_tokens >= context_limit - 256:
            raise ValueError("%s may exceed context: ~%d tokens" %
                             (task.key, estimated_tokens))


def run_batch(tasks, workers=SLOTS, progress=True, unique=False, cache_path=None,
              report_path=None):
    """Run tasks across the server's slots. Returns (accepted, rejected).

    `unique=True` rejects an answer that repeats one another task already gave.
    A per-task `check` only sees its own answer, so it cannot notice that the
    model handed back the same phrase for two different keys - which is exactly
    what it does when two prompts differ only in a proper noun.

    It is OFF by default because it is right for generation and ruinous for
    classification: on a closed set every answer is legitimately a duplicate,
    and turning it on there rejected 58 of 58 correct-format answers. Switch it
    on when each task is supposed to produce a distinct string.
    """
    cached = _read_cache(cache_path)
    pending = []
    for task in tasks:
        answer = cached.get(_fingerprint(task))
        if answer is not None and task.check(answer) is True:
            task.answer = answer
        else:
            pending.append(task)

    t0 = time.time()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        done = list(pool.map(_run_one, pending))
    if unique:
        seen = collections.Counter(t.normalizer(t.answer) for t in tasks if t.answer is not None)
        for t in tasks:
            if t.answer is not None and seen[t.normalizer(t.answer)] > 1:
                t.error = "duplicate answer: %r" % t.answer
                t.answer = None
    ok = [t for t in tasks if t.answer is not None]
    bad = [t for t in tasks if t.answer is None]
    _write_cache(cache_path, ok)
    _write_report(report_path, tasks)
    if progress:
        wall = time.time() - t0
        toks = sum(t.tokens for t in tasks)
        print("local_llm: %d/%d accepted, %d tok in %.0fs (%.1f tok/s aggregate)"
              % (len(ok), len(done), toks, wall, toks / wall if wall else 0),
              file=sys.stderr)
        for t in bad:
            print("  REJECTED %-45s %s" % (t.key, t.error), file=sys.stderr)
    return ok, bad


def health():
    try:
        with urllib.request.urlopen("http://localhost:8080/health", timeout=5) as r:
            return json.loads(r.read().decode())["status"] == "ok"
    except Exception:
        return False


if __name__ == "__main__":
    if not health():
        sys.exit("no llama.cpp server on localhost:8080")
    # Self-test: the exact shape this is meant for - short, factual, checkable.
    sample = [("het_grain_trade", "the Hetmanate sells grain down the Dnieper"),
              ("zaz_betrayed_sich", "someone broke a sworn promise to the Sich"),
              ("plc_cossack_allies", "Cossack regiments fight for the Commonwealth"),
              ("rus_abolished_sich", "Russia abolished the Sich outright")]
    tasks = [Task(key=k,
                  prompt=("Name an Europa Universalis IV opinion modifier.\n"
                          "Meaning: %s.\n"
                          "Reply with a Title Case English noun phrase of two to five words. "
                          "No quotes, no explanation, one line." % gloss),
                  check=lambda s: 2 <= len(s.split()) <= 5 and s[:1].isupper() and '"' not in s)
             for k, gloss in sample]
    ok, bad = run_batch(tasks)
    for t in ok:
        print("%-28s %s" % (t.key, t.answer))
