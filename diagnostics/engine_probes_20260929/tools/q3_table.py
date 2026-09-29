"""Run 1 Q3 verdict table: per effect code x body kind, from one save. usage: q3_table.py save.eu4"""
import re, sys, subprocess, os

path = sys.argv[1]
lines = open(path, encoding="latin-1").read().split("\n")
start = lines.index("countries={")
i = start + 1
blocks = {}
cur = None
while lines[i] != "}":
    m = re.match(r"^\t([A-Z0-9]{3})=\{$", lines[i])
    if m:
        cur = m.group(1); a = i
    elif lines[i] == "\t}" and cur:
        blocks[cur] = (a, i); cur = None
    i += 1


def scalar(tag, name):
    a, b = blocks[tag]
    for k in range(a, b):
        if lines[k].startswith("\t\t" + name + "="):
            return lines[k].split("=", 1)[1]


def sub(tag, name):
    a, b = blocks[tag]
    for k in range(a, b):
        if lines[k] == "\t\t" + name + "={":
            out = []
            k += 1
            while lines[k] != "\t\t}":
                out.append(lines[k]); k += 1
            return out
    return []


def flagset(tag):
    return {l.strip().split("=")[0] for l in sub(tag, "flags") if "=" in l}


def cmods(tag):
    a, b = blocks[tag]
    return {m.group(1) for k in range(a, b) if lines[k] == "\t\tmodifier={" for m in [re.match(r'^\t\t\tmodifier="(.+)"$', lines[k + 1])] if m}


def opins(owner, partner):
    a, b = blocks[owner]
    k = a
    while k < b and lines[k] != "\t\tactive_relations={":
        k += 1
    out = set()
    p = None
    while k < b and lines[k] != "\t\t}":
        m = re.match(r"^\t\t\t([A-Z0-9]{3})=\{$", lines[k])
        if m:
            p = m.group(1)
        m = re.match(r'^\t\t\t\t\tmodifier="(.+)"$', lines[k])
        if m and p == partner:
            out.add(m.group(1))
        k += 1
    return out


def prov(pid):
    i = lines.index("-%d={" % pid)
    j = i
    while lines[j] != "\t}":
        j += 1
    return lines[i:j + 1]


def pinfo(pid):
    blk = prov(pid)
    d = {}
    mods = set()
    for k, l in enumerate(blk):
        m = re.match(r"^\t\t([a-z_]+)=(.*)$", l)
        if m and not m.group(2).startswith("{"):
            d.setdefault(m.group(1), m.group(2))
        if l == "\t\tmodifier={":
            mm = re.match(r'^\t\t\tmodifier="(.+)"$', blk[k + 1])
            if mm:
                mods.add(mm.group(1))
    return d, mods


KS = sys.argv[2].split(",") if len(sys.argv) > 2 else ["if", "ei", "el", "ct", "se"]
COUNTRY = {"if": "POR", "ei": "CAS", "el": "ARA", "ct": "NAV", "se": "GRA"}
CODES = ["cm", "tre", "pre", "stab", "dip", "pm", "rel", "aut", "evt", "opr", "opt", "rev", "rbk", "nst", "hid", "ses", "pur"]
NAMES = {"cm": "add_country_modifier", "tre": "add_treasury 100000", "pre": "add_prestige -300", "stab": "add_stability -6",
         "dip": "add_dip_power 900", "pm": "add_province_modifier (capital_scope)", "rel": "change_religion sunni (capital_scope)",
         "aut": "add_local_autonomy 50 (capital_scope)", "evt": "country_event days=1 -> flag", "opr": "add_opinion who=ROOT",
         "opt": "add_opinion who=FRA", "rev": "reverse_add_opinion who=ROOT", "rbk": "ROOT={add_opinion who=PREV}",
         "nst": "add_opinion in nested if", "hid": "add_opinion in hidden_effect", "ses": "add_opinion via scripted effect",
         "pur": "add_opinion, no flag in body"}
OPMOD = {"opr": ("root", "own", "MOS"), "opt": ("tag", "own", "FRA"), "rev": ("rev", "MOS", None), "rbk": ("rootblk", "MOS", None),
         "nst": ("nest", "own", "MOS"), "hid": ("hid", "own", "MOS"), "ses": ("se", "own", "MOS"), "pur": ("pure", "own", "MOS")}


def verdict(code, K):
    t = COUNTRY[K]
    fl = flagset(t)
    ran = ("rip_prb_ran_%s_%s" % (code, K)) in fl or code == "pur"
    if code == "cm":
        ok = ("rip_prb_cm_%s" % K) in cmods(t)
        ev = "modifier present" if ok else "modifier absent"
    elif code == "tre":
        v = float(scalar(t, "treasury")); ok = v > 90000; ev = "treasury=%.0f" % v
    elif code == "pre":
        v = float(scalar(t, "prestige")); ok = v < -90; ev = "prestige=%.1f" % v
    elif code == "stab":
        ok = ("rip_prb_rb_stab_%s" % K) in fl if K != "se" else float(scalar(t, "stability")) <= -2
        ev = "stability=%s (same-tick readback flag %s)" % (scalar(t, "stability"), ("rip_prb_rb_stab_%s" % K) in fl)
    elif code == "dip":
        pw = sub(t, "powers")[0].split()
        ok = float(pw[1]) > 250; ev = "dip_power=%s" % pw[1]
    elif code == "pm":
        d, m = pinfo(int(scalar(t, "capital")))
        ok = ("rip_prb_pm_%s" % K) in m; ev = "province modifier %s" % ("present" if ok else "absent")
    elif code == "rel":
        d, m = pinfo(int(scalar(t, "capital")))
        ok = d.get("religion") == "sunni" and d.get("original_religion") == "catholic" if t != "GRA" else None
        ev = "capital religion=%s (was catholic; GRA already sunni)" % d.get("religion")
        if t == "GRA":
            ok = None
    elif code == "aut":
        d, m = pinfo(int(scalar(t, "capital")))
        ok = float(d.get("local_autonomy", 0)) > 40; ev = "capital local_autonomy=%s" % d.get("local_autonomy")
    elif code == "evt":
        ok = ("rip_prb_evt_fired_%s" % K) in fl; ev = "delayed event flag %s" % ("set" if ok else "absent")
    else:
        c, a, b = OPMOD[code]
        mod = "rip_prb_op_%s_%s" % (c, K)
        if a == "own":
            got = mod in opins(t, b)
            ev = "%s -> %s has %s" % (t, b, mod)
        else:
            got = mod in opins("MOS", t)
            ev = "MOS -> %s has %s" % (t, mod)
        ok = got
        ev = ("present: " if ok else "ABSENT: ") + ev
    return ran, ok, ev


print("save", path.replace("\\", "/").split("/")[-1], lines[1])
print("effect | " + " | ".join("%s(%s)" % (K, COUNTRY[K]) for K in KS))
for code in CODES:
    cells = []
    for K in KS:
        ran, ok, ev = verdict(code, K)
        cells.append(("ran" if ran else "NOT-RUN") + "/" + ("works" if ok else ("n/a" if ok is None else "DROPPED")))
    print("%-38s | %s" % (NAMES[code], " | ".join("%-14s" % c for c in cells)))
print()
for K in [k for k in ("se",) if k in KS]:
    for code in CODES:
        ran, ok, ev = verdict(code, K)
        print("  se detail %-4s %s" % (code, ev))
