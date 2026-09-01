# -*- coding: utf-8 -*-
"""Measure what the local model can and cannot do, on real mod data.

Four archetypes, each with ground truth that is computed or hand-checked, so the
routing rule in SKILL.md rests on numbers rather than on impressions about LLMs.
Re-run this after changing the model or the quantisation.

    python .claude/skills/local-llm/scripts/benchmark.py

Needs the llama.cpp server on localhost:8080 and an EU4 install (EU4_DIR).
Runs in about four minutes.
"""
import io
import os
import re
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tests", "dev_tools"))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from local_llm import Task, run_batch, health          # noqa: E402

EU4 = os.environ.get("EU4_DIR") or r"D:\Programs Files(x86)\Steam\steamapps\common\Europa Universalis IV"
PN = os.path.join(ROOT, "common", "province_names")
CORE = {"ruthenia_region", "crimea_region", "carpathia_region", "poland_region"}


def top_blocks(text):
    """Brace-aware iteration. area.txt nests `color = { r g b }`, which a plain
    `\\{[^{}]*\\}` regex swallows instead of the area - that mis-parse costs 182
    provinces and mislabels 90 more."""
    i = 0
    pattern = re.compile(r'([a-z_0-9]+)\s*=\s*\{')
    while True:
        m = pattern.search(text, i)
        if not m:
            return
        depth, j = 1, m.end()
        while depth and j < len(text):
            depth += (text[j] == "{") - (text[j] == "}")
            j += 1
        yield m.group(1), text[m.end():j - 1]
        i = j


def load_map():
    defn = {}
    for line in io.open(os.path.join(EU4, "map", "definition.csv"),
                        encoding="cp1252", errors="replace"):
        p = line.split(";")
        if len(p) > 4 and p[0].isdigit():
            defn[int(p[0])] = p[4].strip()
    atext = re.sub(r"#.*", "", io.open(os.path.join(EU4, "map", "area.txt"),
                                       encoding="cp1252", errors="replace").read())
    area_of = {}
    for name, body in top_blocks(atext):
        inner = re.sub(r'[a-z_0-9]+\s*=\s*\{[^{}]*\}', '', body)
        for tok in inner.split():
            if tok.isdigit():
                area_of[int(tok)] = name
    rtext = re.sub(r"#.*", "", io.open(os.path.join(EU4, "map", "region.txt"),
                                       encoding="cp1252", errors="replace").read())
    region_of = {}
    for m in re.finditer(r"([a-z_0-9]+)\s*=\s*\{(.*?)\n\}", rtext, re.S):
        for a in re.findall(r"([a-z_0-9]+_area)", m.group(2)):
            region_of[a] = m.group(1)
    return defn, area_of, region_of


ENTRY = re.compile(r'^\s*(\d+)\s*=\s*"([^"]*)"')


def read_names(path):
    text = io.open(path, encoding="utf-8-sig", errors="replace").read().replace("\r\n", "\n")
    return [(int(m.group(1)), m.group(2))
            for m in (ENTRY.match(l) for l in text.split("\n")) if m]


REPORT = []


def score(title, tasks, truth, note=""):
    hit = sum(1 for t in tasks
              if t.answer and t.answer.strip().upper().rstrip(".") == truth[t.key])
    n = len(tasks)
    answers = [(t.answer or "").strip().upper().rstrip(".") for t in tasks]
    collapsed = len(set(a for a in answers if a)) == 1 and n > 1
    REPORT.append((title, hit, n, collapsed))
    print("\n  %-38s %2d/%-3d %3.0f%%%s" % (title, hit, n, 100.0 * hit / n if n else 0,
                                            "   COLLAPSED TO ONE ANSWER" if collapsed else ""))
    if note:
        print("     " + note)
    for t in tasks:
        got = (t.answer or "<rejected>").strip().upper().rstrip(".")
        if got != truth[t.key]:
            print("     miss %-22s want=%-20s got=%s" % (t.key, truth[t.key], got[:34]))


def main():
    if not health():
        sys.exit("no llama.cpp server on localhost:8080")
    if not os.path.isdir(EU4):
        sys.exit("EU4_DIR does not point at an install: %s" % EU4)
    defn, area_of, region_of = load_map()
    rows = read_names(os.path.join(PN, "ruthenian.txt"))
    t0 = time.time()

    # A. classify against a closed set, every fact inlined
    sample = rows[::3][:40]
    truth = {}
    tasks = []
    for pid, name in sample:
        truth[str(pid)] = "INSIDE" if region_of.get(area_of.get(pid, "")) in CORE else "BEYOND"
        tasks.append(Task(
            key=str(pid), max_tokens=12,
            prompt=("A Europa Universalis IV mod is set in the Ruthenian lands: Ukraine, "
                    "Belarus, Crimea, the Pontic steppe, Poland and Transcarpathia.\n"
                    "Province: \"%s\" (the map calls it %s).\n"
                    "Is this place inside that area or beyond it?\n"
                    "Answer with exactly one word: INSIDE or BEYOND." % (name, defn.get(pid, "?"))),
            check=lambda s: s.strip().upper().rstrip(".") in ("INSIDE", "BEYOND")))
    run_batch(tasks)
    majority = max(sum(1 for v in truth.values() if v == "INSIDE"),
                   sum(1 for v in truth.values() if v == "BEYOND"))
    score("A. classify (in / out of scope)", tasks, truth,
          "always-majority baseline would score %d/%d" % (majority, len(tasks)))

    # B. deterministic string transform
    apo = [(p, n) for p, n in rows if "'" in n][:30]
    truth = {str(p): n.replace("'", "").upper() for p, n in apo}
    tasks = [Task(key=str(p), max_tokens=24,
                  prompt=("Delete every apostrophe from this word and print the result. "
                          "Change nothing else. Print only the word.\n%s" % n),
                  check=lambda s: bool(s) and "'" not in s)
             for p, n in apo]
    run_batch(tasks)
    score("B. transform (strip apostrophe)", tasks, truth)

    # C. binary factual judgement - the call that catches anachronisms
    founded = [("Katerynoslav", "YES"), ("Sevastopol", "YES"), ("Mykolayiv", "YES"),
               ("Kherson", "YES"), ("Novocherkassk", "YES"), ("Stavropol", "YES"),
               ("Odessa", "YES"), ("Vladivostok", "YES"), ("Petropavlovsk", "YES"),
               ("Yekaterinburg", "NO"), ("Omsk", "NO"), ("Tobolsk", "NO"),
               ("Kyiv", "NO"), ("Chernihiv", "NO"), ("Poltava", "NO"), ("Kaffa", "NO"),
               ("Azov", "NO"), ("Smolensk", "NO"), ("Vilnius", "NO"), ("Astrakhan", "NO")]
    truth = dict(founded)
    tasks = [Task(key=n, max_tokens=12,
                  prompt=("Europa Universalis IV runs from 1444 to 1821.\n"
                          "Was the city of %s founded after 1750?\n"
                          "Answer with exactly one word: YES or NO." % n),
                  check=lambda s: s.strip().upper().rstrip(".") in ("YES", "NO"))
             for n, _ in founded]
    run_batch(tasks)
    score("C. judgement (founded after 1750)", tasks, truth)

    # D. audit control - the corpus is clean, so NONE is the only right answer
    src = "\n".join(io.open(os.path.join(PN, f), encoding="utf-8-sig").read()
                    for f in ("CHR.txt", "UZH.txt"))
    d = Task(key="audit", max_tokens=250, stop=("<|im_end|>",),
             prompt=("These are Europa Universalis IV province_names files.\n"
                     "Every entry must be `<number> = \"<Name>\"`, and each entry may carry a "
                     "trailing # comment.\n"
                     "List every entry that breaks those rules. If none break them, reply "
                     "exactly NONE.\n\n" + src),
             check=lambda s: bool(s.strip()))
    run_batch([d], workers=1)
    verdict = (d.answer or "").strip()
    ok = verdict.upper().startswith("NONE")
    REPORT.append(("D. audit (control, answer is NONE)", 1 if ok else 0, 1, False))
    print("\n  %-38s %2d/%-3d %3.0f%%" % ("D. audit (control, answer is NONE)",
                                          1 if ok else 0, 1, 100.0 if ok else 0.0))
    for line in verdict.split("\n")[:8]:
        print("     | " + line)

    print("\n  wall %.0fs\n\n  SUMMARY" % (time.time() - t0))
    for title, hit, n, collapsed in REPORT:
        print("    %-38s %2d/%-3d %3.0f%%%s" % (title, hit, n, 100.0 * hit / n,
                                                "  (collapsed)" if collapsed else ""))


if __name__ == "__main__":
    main()
