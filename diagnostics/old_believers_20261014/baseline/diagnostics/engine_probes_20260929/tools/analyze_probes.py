"""Reads an uncompressed EU4txt save produced by the engine-probe harness and prints raw evidence per question.

usage: analyze_probes.py <save.eu4> [--all-flags]
"""
import re, sys, collections

path = sys.argv[1]
with open(path, encoding="latin-1") as f:
    lines = f.read().split("\n")
date = next(l for l in lines[:6] if l.startswith("date="))
print("save:", path.replace("\\", "/").split("/")[-1], "|", date)

# ---- country blocks
start = lines.index("countries={")
i = start + 1
blocks = {}
cur = None
while lines[i] != "}":
    m = re.match(r"^\t([A-Z0-9]{3})=\{$", lines[i])
    if m:
        cur = m.group(1)
        a = i
    elif lines[i] == "\t}" and cur:
        blocks[cur] = (a, i)
        cur = None
    i += 1


def scalar(tag, name):
    a, b = blocks[tag]
    pat = "\t\t" + name + "="
    for k in range(a, b):
        if lines[k].startswith(pat):
            return lines[k][len(pat):]
    return None


def sub(tag, name, depth=2):
    """lines inside a depth-2 block `name={ ... }` of the country"""
    a, b = blocks[tag]
    head = "\t" * depth + name + "={"
    close = "\t" * depth + "}"
    out = []
    k = a
    while k < b:
        if lines[k] == head:
            k += 1
            while lines[k] != close:
                out.append(lines[k])
                k += 1
            return out
        k += 1
    return None


def flags(tag):
    r = {}
    for l in sub(tag, "flags") or []:
        if "=" in l:
            n, d = l.strip().split("=", 1)
            r[n] = d
    return r


def modifiers(tag):
    a, b = blocks[tag]
    r = []
    for k in range(a, b):
        if lines[k] == "\t\tmodifier={":
            m = re.match(r'^\t\t\tmodifier="(.+)"$', lines[k + 1])
            if m:
                r.append((m.group(1), lines[k + 2].strip()))
    return r


def opinions_all():
    out = []
    for tag, (a, b) in blocks.items():
        k = a
        while k < b and lines[k] != "\t\tactive_relations={":
            k += 1
        partner = None
        while k < b and lines[k] != "\t\t}":
            m = re.match(r"^\t\t\t([A-Z0-9]{3})=\{$", lines[k])
            if m:
                partner = m.group(1)
            m = re.match(r'^\t\t\t\t\tmodifier="(.+)"$', lines[k])
            if m and m.group(1).startswith("rip_prb_"):
                d = lines[k + 1].strip()
                cur_op = ""
                for q in range(k + 1, k + 5):
                    if lines[q].strip().startswith("current_opinion="):
                        cur_op = lines[q].strip().split("=")[1]
                out.append((tag, partner, m.group(1), cur_op, d))
            k += 1
    return out


def province(pid):
    try:
        i = lines.index("-%d={" % pid)
    except ValueError:
        return None
    j = i
    while lines[j] != "\t}":
        j += 1
    return lines[i:j + 1]


def pfields(blk):
    d = {}
    for l in blk:
        m = re.match(r"^\t\t([a-z_]+)=(.*)$", l)
        if m and not m.group(2).startswith("{"):
            d.setdefault(m.group(1), m.group(2))
    fl = {}
    mods = []
    for k, l in enumerate(blk):
        if l == "\t\tflags={":
            q = k + 1
            while blk[q] != "\t\t}":
                if "=" in blk[q]:
                    n, dt = blk[q].strip().split("=", 1)
                    fl[n] = dt
                q += 1
        if l == "\t\tmodifier={":
            m = re.match(r'^\t\t\tmodifier="(.+)"$', blk[k + 1])
            if m:
                mods.append((m.group(1), blk[k + 2].strip()))
    return d, fl, mods


TARGETS = ["MOS", "POL", "BYZ", "POR", "CAS", "ARA", "NAV", "GRA"]
print("\n==== country resources / religion")
for t in TARGETS:
    pw = sub(t, "powers")
    print("  %s religion=%s treasury=%s prestige=%s stability=%s papal_influence=%s powers(adm dip mil)=%s capital=%s" % (
        t, scalar(t, "religion"), scalar(t, "treasury"), scalar(t, "prestige"), scalar(t, "stability"),
        scalar(t, "papal_influence"), (pw[0].strip() if pw else None), scalar(t, "capital")))
for t in ["SWE", "DAN", "FRA", "LIT", "CAS", "BUR", "ENG", "TUR"]:
    if t in blocks:
        pw = sub(t, "powers")
        print("  (untouched) %s religion=%s treasury=%s prestige=%s stability=%s papal_influence=%s powers=%s" % (
            t, scalar(t, "religion"), scalar(t, "treasury"), scalar(t, "prestige"), scalar(t, "stability"),
            scalar(t, "papal_influence"), (pw[0].strip() if pw else None)))

print("\n==== country flags rip_prb_* (name=date) per target")
for t in TARGETS:
    fl = flags(t)
    mine = sorted((n, d) for n, d in fl.items() if n.startswith("rip_prb_"))
    print("  %s: %d flags" % (t, len(mine)))
    for n, d in mine:
        print("      %s=%s" % (n, d))

print("\n==== country modifiers rip_prb_* / all non-RIP modifiers per target")
for t in TARGETS:
    ms = modifiers(t)
    print("  %s: %s" % (t, ", ".join("%s(%s)" % m for m in ms if m[0].startswith("rip_prb_")) or "-"))

print("\n==== opinion entries rip_prb_* (owner -> partner : modifier value date)")
ops = opinions_all()
for o in sorted(ops):
    print("  %s -> %s : %s %s %s" % o)
print("  total", len(ops))

print("\n==== provinces")
pids = {}
for t in TARGETS:
    c = scalar(t, "capital")
    if c and c.isdigit():
        pids[t + " capital"] = int(c)
pids["SWE Stockholm (1)"] = 1
for label, pid in pids.items():
    blk = province(pid)
    if not blk:
        print("  %s (%d): not found" % (label, pid))
        continue
    d, fl, mods = pfields(blk)
    print("  %s (%d): owner=%s religion=%s original_religion=%s local_autonomy=%s" % (label, pid, d.get("owner"), d.get("religion"), d.get("original_religion"), d.get("local_autonomy")))
    for n, dt in sorted(fl.items()):
        if n.startswith("rip_prb_"):
            print("      flag %s=%s" % (n, dt))
    print("      modifiers: %s" % (", ".join("%s(%s)" % m for m in mods if m[0].startswith("rip_prb_")) or "-"))
