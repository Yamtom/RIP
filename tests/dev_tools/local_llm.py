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
import json
import re
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Callable, Optional

ENDPOINT = "http://localhost:8080/v1/chat/completions"
SLOTS = 4          # llama.cpp total_slots; more requests than this just queue
TIMEOUT = 180


@dataclass
class Task:
    key: str
    prompt: str
    check: Callable[[str], bool] = lambda s: bool(s.strip())
    max_tokens: int = 48
    stop: tuple = ("\n", "<|im_end|>")
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


def _clean(text):
    """Strip the chat-template residue and framing the model likes to add."""
    text = text.split("<|im_end|>")[0].strip()
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
        if task.check(answer):
            task.answer, task.error = answer, None
            return task
        task.error = "rejected: %r" % answer[:80]
    return task


def run_batch(tasks, workers=SLOTS, progress=True, unique=True):
    """Run tasks across the server's slots. Returns (accepted, rejected).

    `unique` rejects an answer that repeats one another task already gave. A
    per-task `check` only sees its own answer, so it cannot notice that the
    model handed back the same phrase for two different keys - which is exactly
    what it does when two prompts differ only in a proper noun.
    """
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        done = list(pool.map(_run_one, tasks))
    if unique:
        seen = collections.Counter(t.answer for t in done if t.answer is not None)
        for t in done:
            if t.answer is not None and seen[t.answer] > 1:
                t.error = "duplicate answer: %r" % t.answer
                t.answer = None
    ok = [t for t in done if t.answer is not None]
    bad = [t for t in done if t.answer is None]
    if progress:
        wall = time.time() - t0
        toks = sum(t.tokens for t in done)
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
