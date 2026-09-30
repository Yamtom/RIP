"""Compares two EU4 logs/error.log files by line multiset and lists the RIP-related keyword lines.

    python errlog_diff.py <new error.log> <baseline error.log> [<baseline2> ...]

Prints the lines that appear in <new> and in none of the baselines, the lines that disappeared, and, for the keywords of
the eparchy work (rip_eparchy, rip_uzh, rip_diocesan, khmelnytsky, uzh_eparchy, HLCMetropolitan, synod, ...), every line of
the new log that mentions one of them (marked NEW when no baseline has it).
"""
import collections
import re
import sys

KEYWORDS = ["rip_eparchy", "rip_uzh", "rip_diocesan", "rip_du_", "khmelnytsky", "uzh_eparchy", "uzh_can_", "HLCMetropolitan",
            "hlc_confirm", "hlc_complete", "synod", "hierarchy_standing", "rip_ee", "union_of_brest", "Eparchy", "RIP_Uzh",
            "rip_church_sponsor", "sponsor", "KyivTriggers", "RIP_ChurchCouncils", "Galicia_AltHistory", "Volhynia_Alt_History",
            "greek_catholic_diocese", "uniate_metropolitan_see", "resistance_to_greek_catholic_spread"]


def load(p):
    with open(p, encoding="utf-8", errors="replace") as f:
        return [l.rstrip("\r\n") for l in f if l.strip()]


new = load(sys.argv[1])
bases = [load(p) for p in sys.argv[2:]]
base_set = set()
for b in bases:
    base_set.update(b)
cn, cb = collections.Counter(new), collections.Counter()
for b in bases:
    for k, v in collections.Counter(b).items():
        cb[k] = max(cb[k], v)

only_new = sorted(k for k in cn if k not in base_set)
gone = sorted(k for k in cb if k not in cn)
print("new log: %d lines (%d distinct); baselines: %s" % (len(new), len(cn), ", ".join("%d" % len(b) for b in bases)))
print("\n== lines in the new log that no baseline has: %d" % len(only_new))
for l in only_new:
    print("  NEW  x%d  %s" % (cn[l], l))
print("\n== lines the baselines have that the new log lacks: %d" % len(gone))
for l in gone:
    print("  GONE x%d  %s" % (cb[l], l))
print("\n== keyword lines in the new log")
hits = 0
for l, n in sorted(cn.items()):
    if any(re.search(re.escape(k), l, re.I) for k in KEYWORDS):
        hits += 1
        print("  %s x%d (baseline x%d)  %s" % ("NEW " if l not in base_set else "old ", n, cb.get(l, 0), l))
print("  keyword lines: %d" % hits)
