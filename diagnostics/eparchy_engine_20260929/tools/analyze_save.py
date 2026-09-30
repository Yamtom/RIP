"""Reads one uncompressed EU4txt autosave and prints the state of the seat provinces and the harness flags.

    python analyze_save.py <save.eu4> [province ids...]

Per province: date of the save, owner / controller / religion, local autonomy, every province modifier with its date, every
province flag with its date. Then the country-level rip_ee_* flags of every country that has any.
"""
import re
import sys

PROVS = [int(x) for x in sys.argv[2:]] or [2424, 2961, 279, 1952]
with open(sys.argv[1], encoding="latin-1") as f:
    lines = f.read().split("\n")

date = next((l for l in lines[:5] if l.startswith("date=")), "?")
print("save", sys.argv[1].replace("\\", "/").split("/")[-1], date)


def block_end(i):
    """Index of the first line after the block that opens on line i (brace balance over the lines)."""
    depth = 0
    j = i
    while True:
        l = lines[j]
        depth += l.count("{") - l.count("}")
        j += 1
        if depth <= 0:
            return j


# province blocks start at column 0 as "-ID={"
starts = {}
for i, l in enumerate(lines):
    m = re.match(r"^-(\d+)=\{", l)
    if m and int(m.group(1)) in PROVS and int(m.group(1)) not in starts:
        starts[int(m.group(1))] = i

for pid in PROVS:
    if pid not in starts:
        print("province %d: block not found" % pid)
        continue
    i = starts[pid]
    e = block_end(i)
    blk = lines[i:e]
    top = {}
    mods, flags = [], []
    k = 1
    while k < len(blk) - 1:
        l = blk[k]
        m = re.match(r"^\t\t([a-z_]+)=(.*)$", l)
        if m:
            key, val = m.group(1), m.group(2)
            if key == "history":
                k = k + (block_end(i + k) - (i + k))
                continue
            if key == "modifier" and val.strip() == "{":
                j = block_end(i + k) - i
                body = " ".join(x.strip() for x in blk[k + 1:j - 1])
                mods.append(body)
                k = j
                continue
            if key == "flags" and val.strip() == "{":
                j = block_end(i + k) - i
                for x in blk[k + 1:j - 1]:
                    x = x.strip()
                    if x:
                        flags.append(x)
                k = j
                continue
            if val.strip() == "{":
                k = block_end(i + k) - i
                continue
            top[key] = val
        k += 1
    print("\nprovince %d %s" % (pid, top.get("name", "")))
    for key in ("owner", "controller", "religion", "original_religion", "is_city", "local_autonomy", "missionary_strength"):
        if key in top:
            print("   %-18s %s" % (key, top[key]))
    for x in mods:
        print("   modifier      ", x)
    for x in flags:
        print("   flag          ", x)

# country blocks: "\tTAG={" at one tab
import os
TAGS = [x for x in os.environ.get("COUNTRIES", "UZH,POL,LIT,HLC,HAB,MOS").split(",") if x]
cstarts = {}
for i, l in enumerate(lines):
    m = re.match(r"^\t([A-Z0-9]{3})=\{$", l)
    if m and m.group(1) in TAGS and m.group(1) not in cstarts:
        cstarts[m.group(1)] = i
for tag in TAGS:
    if tag not in cstarts:
        continue
    i = cstarts[tag]
    e = block_end(i)
    blk = lines[i:e]
    print("\ncountry %s" % tag)
    k = 1
    while k < len(blk) - 1:
        l = blk[k]
        m = re.match(r"^\t\t([a-z_]+)=(.*)$", l)
        if m:
            key, val = m.group(1), m.group(2)
            if val.strip() == "{":
                if key == "flags":
                    j = block_end(i + k) - i
                    fl = [x.strip() for x in blk[k + 1:j - 1] if x.strip()]
                    print("   flags (%d): %s" % (len(fl), " ".join(fl)[:3000]))
                k = block_end(i + k) - i
                continue
            if key in ("religion", "government", "overlord", "is_at_war", "papal_influence", "patriarch_authority", "capital", "stability"):
                print("   %-20s %s" % (key, val))
        k += 1
