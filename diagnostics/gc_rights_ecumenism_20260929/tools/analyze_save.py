"""Harness analysis (scratchpad tool, not part of the mod).

Reads an uncompressed EU4txt save and prints, for every country that carries a
rip_church_opinion_* / rip_gcr_probe_* opinion modifier in its active_relations,
the partner, the modifier, the value and the date; then a per-country verdict on
rip_church_opinion_gc_ecumenical toward the player; then the province modifiers
of the two harness test provinces.
"""
import re, sys, collections

path = sys.argv[1]
PLAYER = "MOS"
with open(path, encoding="latin-1") as f:
    lines = f.read().split("\n")

hdr = [l for l in lines[:5]]
print("save file:", path.replace("\\", "/").split("/")[-1], "| header:", " ".join(hdr[:2]))

# countries section
start = next(i for i, l in enumerate(lines) if l == "countries={")
i = start + 1
countries = {}
cur = None
cstart = None
while i < len(lines):
    l = lines[i]
    if l == "}":
        break
    m = re.match(r"^\t([A-Z0-9]{3})=\{$", l)
    if m:
        cur = m.group(1)
        cstart = i
    elif l == "\t}" and cur:
        countries[cur] = (cstart, i)
        cur = None
    i += 1

info = {}
entries = []   # (owner, partner, modifier, value, date)
for tag, (a, b) in countries.items():
    rel = None
    flags = []
    inflags = False
    for j in range(a, b):
        l = lines[j]
        if l.startswith("\t\treligion=") and rel is None:
            rel = l.split("=")[1]
        if l == "\t\tflags={":
            inflags = True
            continue
        if inflags:
            if l == "\t\t}":
                inflags = False
            else:
                flags.append(l.strip().split("=")[0])
    info[tag] = {"religion": rel, "flags": flags}
    # active relations
    j = a
    while j < b and lines[j] != "\t\tactive_relations={":
        j += 1
    if j >= b:
        continue
    partner = None
    k = j + 1
    while k < b and lines[k] != "\t\t}":
        l = lines[k]
        m = re.match(r"^\t\t\t([A-Z0-9]{3})=\{$", l)
        if m:
            partner = m.group(1)
        m = re.match(r'^\t\t\t\t\tmodifier="(.+)"$', l)
        if m:
            mod = m.group(1)
            date = lines[k + 1].strip() if lines[k + 1].strip().startswith("date=") else ""
            val = ""
            for q in range(k + 1, k + 5):
                if lines[q].strip().startswith("current_opinion="):
                    val = lines[q].strip().split("=")[1]
            entries.append((tag, partner, mod, val, date))
        k += 1

mine = [e for e in entries if e[2].startswith("rip_church_opinion") or e[2].startswith("rip_gcr_probe")]
print("\n== every rip_church_opinion_* / rip_gcr_probe_* entry (owner = the country whose active_relations lists it)")
for e in sorted(mine):
    print("  owner %s (%s) -> partner %s : %s %s %s" % (e[0], info[e[0]]["religion"], e[1], e[2], e[3], e[4]))
print("  total:", len(mine))

print("\n== rip_church_opinion_gc_ecumenical toward/from the player %s" % PLAYER)
print("  player religion: %s | ecumenical flag: %s | flags: %s" % (
    info[PLAYER]["religion"], "rip_church_ecumenical" in info[PLAYER]["flags"],
    ", ".join(f for f in info[PLAYER]["flags"] if f.startswith("rip_"))))
have = collections.defaultdict(set)
for e in entries:
    if e[0] != PLAYER and e[1] == PLAYER:
        have[e[0]].add(e[2])
    if e[0] == PLAYER and e[1] != PLAYER:
        have[e[1]].add("player_side:" + e[2])
byrel = collections.defaultdict(list)
for tag, d in info.items():
    if tag == PLAYER or tag in ("REB", "PIR", "NAT"):
        continue
    if tag not in ("REB", "PIR", "NAT") and re.match(r"^[A-Z]{3}$", tag):
        byrel[d["religion"]].append(tag)
def verdict(tag):
    h = have.get(tag, set())
    return ("ECUMENICAL yes" if "rip_church_opinion_gc_ecumenical" in h else "ECUMENICAL no ") + \
           (" | player-side " + ("yes" if "player_side:rip_church_opinion_gc_ecumenical" in h else "no ")) + \
           " | other rip_church opinions: " + (", ".join(sorted(x for x in h if x.replace("player_side:", "") != "rip_church_opinion_gc_ecumenical")) or "-")
for tag in ["POL", "LIT", "AUS", "FRA", "BYZ", "NOV", "TVE", "TUR", "DAN", "SWE", "PAP", "RYA"]:
    if tag in info:
        print("  %s %-16s %s" % (tag, "(" + str(info[tag]["religion"]) + ")", verdict(tag)))
print("\n  by religion, countries WITH gc_ecumenical toward the player (either side):")
for r, tags in sorted(byrel.items(), key=lambda kv: str(kv[0])):
    yes = [t for t in tags if "rip_church_opinion_gc_ecumenical" in have.get(t, set()) or "player_side:rip_church_opinion_gc_ecumenical" in have.get(t, set())]
    print("   %-18s %3d countries, %3d with the modifier %s" % (r, len(tags), len(yes), ("(" + " ".join(sorted(yes)[:14]) + (" ..." if len(yes) > 14 else "") + ")") if yes else ""))

# provinces
print("\n== replica flags (rip_gcr_n_* = pre-fix nested text, rip_gcr_s_* = fixed sibling text) set on countries")
agg = collections.defaultdict(list)
for tag, d in info.items():
    for fl in d["flags"]:
        if fl.startswith("rip_gcr_n_") or fl.startswith("rip_gcr_s_"):
            agg[fl].append(tag)
for fl, tags in sorted(agg.items()):
    byr = collections.Counter(str(info[t]["religion"]) for t in tags)
    print("  %-34s %3d countries  %s  e.g. %s" % (fl, len(tags), dict(byr), " ".join(sorted(tags)[:10])))
for tag in ["POL", "LIT", "AUS", "FRA", "BYZ", "NOV", "TVE", "TUR"]:
    if tag in info:
        print("  %s (%s): %s" % (tag, info[tag]["religion"], ", ".join(f for f in info[tag]["flags"] if f.startswith("rip_gcr_")) or "-"))

print("\n== harness test provinces")
pstart = next(i for i, l in enumerate(lines) if l == "provinces={")
i = pstart + 1
cur = None
pa = None
blocks = {}
while i < len(lines):
    l = lines[i]
    if l == "}":
        break
    m = re.match(r"^-(\d+)=\{$", l)
    if m:
        cur = m.group(1); pa = i
    elif l == "}" and False:
        pass
    elif re.match(r"^\}$", l):
        pass
    elif l == "\t" and False:
        pass
    i += 1
# simpler: locate by flag line and scan back to the province header
def province_of(idx):
    j = idx
    while j > pstart and not re.match(r"^-(\d+)=\{$", lines[j]):
        j -= 1
    return j
for flag in ("rip_gcr_test_a_mod_effect", "rip_gcr_test_b_flag_only"):
    idxs = [k for k, l in enumerate(lines) if l.strip().startswith(flag + "=") and k > pstart and re.match(r"^-\d+=\{$", lines[province_of(k)])]
    for k in idxs:
        h = province_of(k)
        pid = re.match(r"^-(\d+)=\{$", lines[h]).group(1)
        e = h + 1
        while e < len(lines) and lines[e] != "}":
            e += 1
        blk = lines[h:e]
        name = next((x.strip() for x in blk if x.strip().startswith("name=")), "")
        rel = next((x.strip() for x in blk if x.startswith("\t\treligion=") or x.startswith("\treligion=")), "")
        own = next((x.strip() for x in blk if x.startswith("\towner=")), "")
        mods = [x.strip() for x in blk if x.strip().startswith('modifier="') and "rip_" in x]
        pflags = [x.strip() for x in blk if "rip_church_rite" in x or "rip_gcr" in x]
        print("  province %s %s %s %s [test %s]" % (pid, name, own, rel, flag))
        print("     modifiers: %s" % (", ".join(m.split('"')[1] for m in mods) or "-"))
        print("     flags    : %s" % (", ".join(pflags) or "-"))
