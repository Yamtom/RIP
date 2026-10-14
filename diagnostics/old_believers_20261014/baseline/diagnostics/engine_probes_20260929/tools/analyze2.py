"""Run 2 analysis. usage: analyze2.py save.eu4"""
import re, sys

path = sys.argv[1]
lines = open(path, encoding="latin-1").read().split("\n")
print("save", path.replace("\\", "/").split("/")[-1], lines[1])
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


_fl = {}


def flags(tag):
    if tag not in _fl:
        r = {}
        for l in sub(tag, "flags"):
            if "=" in l:
                n, d = l.strip().split("=", 1)
                r[n] = d
        _fl[tag] = r
    return _fl[tag]


_cm = {}


def cmods(tag):
    if tag not in _cm:
        a, b = blocks[tag]
        _cm[tag] = {m.group(1) for k in range(a, b) if lines[k] == "\t\tmodifier={" for m in [re.match(r'^\t\t\tmodifier="(.+)"$', lines[k + 1])] if m}
    return _cm[tag]


_op = {}


def opins(owner):
    """partner -> {modifier: value}"""
    if owner not in _op:
        a, b = blocks[owner]
        k = a
        while k < b and lines[k] != "\t\tactive_relations={":
            k += 1
        out = {}
        p = None
        while k < b and lines[k] != "\t\t}":
            m = re.match(r"^\t\t\t([A-Z0-9]{3})=\{$", lines[k])
            if m:
                p = m.group(1)
            m = re.match(r'^\t\t\t\t\tmodifier="(.+)"$', lines[k])
            if m and p:
                cur_op = ""
                for q in range(k + 1, k + 5):
                    if lines[q].strip().startswith("current_opinion="):
                        cur_op = lines[q].strip().split("=")[1]
                out.setdefault(p, {})[m.group(1)] = cur_op
            k += 1
        _op[owner] = out
    return _op[owner]


def has_op(owner, partner, mod):
    return mod in opins(owner).get(partner, {})


def prov(pid):
    i = lines.index("-%d={" % pid)
    j = i
    while lines[j] != "\t}":
        j += 1
    return lines[i:j + 1]


def pflags(pid):
    blk = prov(pid)
    r = {}
    for k, l in enumerate(blk):
        if l == "\t\tflags={":
            q = k + 1
            while blk[q] != "\t\t}":
                if "=" in blk[q]:
                    n, d = blk[q].strip().split("=", 1)
                    r[n] = d
                q += 1
    return r


V = ["if", "ei", "el", "ct"]
C7 = ["POR", "CAS", "ARA", "NAV", "GRA", "ENG", "BUR"]


def cell(tag, fam, v, K=""):
    key = "%s_%s" % (fam, v)
    kk = ("_" + K) if K else ""
    fl = flags(tag)
    s = ""
    s += "R" if ("rip_pr2_ran_%s" % key) in fl else "."
    s += "C" if ("rip_pr2_cm_%s" % key) in cmods(tag) else "."
    s += "O" if has_op(tag, "MOS", "rip_pr2_op_%s%s" % (key, kk)) else "."
    s += "V" if has_op("MOS", tag, "rip_pr2_rev_%s%s" % (key, kk)) else "."
    s += "D" if ("rip_pr2_evt_%s" % key) in fl else "."
    s += "I" if ("rip_pr2_imm_%s" % key) in fl else "."
    return s


print("legend: R=body ran (flag)  C=add_country_modifier  O=add_opinion who=ROOT  V=reverse_add_opinion  D=delayed country_event days=1  I=immediate country_event")
print("\n=== family in (inline in event immediate) and se (scripted effect called inside TAG = { }), per country")
print("%-10s" % "" + "".join("%-9s" % c for c in C7))
for fam in ("in", "se"):
    for v in V:
        print("%-10s" % ("%s_%s" % (fam, v)) + "".join("%-9s" % cell(c, fam, v) for c in C7))
print("\n=== family sc (scripted effect containing TAG = { } inner scope, called at event scope; scope SWE)")
for v in V:
    print("  sc_%s SWE %s" % (v, cell("SWE", "sc", v)))
print("\n=== family pa (parametrised scripted effect, K substituted in modifier names)")
for (t, v, K) in [("FRA", "if", "a"), ("FRA", "ei", "a"), ("FRA", "el", "a"), ("GRA", "ei", "b"), ("CAS", "ei", "c")]:
    print("  pa_%s on %s (K=%s) %s" % (v, t, K, cell(t, "pa", v, K)))

print("\n=== multi-pair chains (17 pairs style; here 5 pairs: cm, tre, add_opinion, reverse_add_opinion, delayed event)")
for (t, v, K) in [("GRA", "ei", "g"), ("POR", "ei", "p"), ("ENG", "ei", "e"), ("BUR", "if", "b")]:
    fl = flags(t)
    ran = "".join(("1" if ("rip_pr2_chran_%s_%s" % (c, v)) in fl else "0") for c in ("cm", "tre", "opr", "rev", "evt"))
    cm = ("rip_pr2_chcm_%s" % K) in cmods(t)
    tre = float(scalar(t, "treasury"))
    o = has_op(t, "MOS", "rip_pr2_chop_%s" % K)
    r = has_op("MOS", t, "rip_pr2_chrev_%s" % K)
    d = ("rip_pr2_evt_ch_%s" % v) in fl
    print("  chain_%s on %s: ran(cm,tre,opr,rev,evt)=%s | cm=%s treasury=%.0f(>+1000 works if >900 above base?) opinion=%s reverse=%s delayed_event=%s" % (v, t, ran, cm, tre, o, r, d))

print("\n=== effect-class test, one pair per effect in a scripted effect, per branch kind")
CLSK = {"ei": "SAV", "ct": "MLO", "if": "VEN", "el": "GEN"}
CLS = ["trust", "imm", "dly5", "rooteve", "prov", "rootflag", "tre", "opin", "rev", "cb", "flagonly"]
mosfl = flags("MOS")
print("%-10s" % "effect" + "".join("%-22s" % ("%s (%s)" % (k, t)) for k, t in CLSK.items()))
for c in CLS:
    row = "%-10s" % c
    for kind, t in CLSK.items():
        fl = flags(t)
        ran = ("rip_pr2_clsran_%s" % c) in fl
        if c == "trust":
            blk_rel = opins(t)  # trust is not an opinion entry; look in raw relation
            a, b = blocks[t]
            found = False
            k = a
            while k < b and lines[k] != "\t\tactive_relations={":
                k += 1
            p = None
            while k < b and lines[k] != "\t\t}":
                m = re.match(r"^\t\t\t([A-Z0-9]{3})=\{$", lines[k])
                if m:
                    p = m.group(1)
                if p == "MOS" and lines[k].strip().startswith("trust_value="):
                    found = lines[k].strip()
                k += 1
            ok = found
        elif c == "imm":
            ok = "rip_pr2_cls_imm" in fl
        elif c == "dly5":
            ok = "rip_pr2_cls_dly5" in fl
        elif c == "rooteve":
            ok = ("rip_pr2_cls_rootevt_%s" % kind) in mosfl
        elif c == "prov":
            ok = "rip_pr2_cls_provevt" in pflags(int(scalar(t, "capital")))
        elif c == "rootflag":
            ok = ("rip_pr2_cls_rootflag_%s" % kind) in mosfl
        elif c == "tre":
            ok = float(scalar(t, "treasury")) > 4000
        elif c == "opin":
            ok = has_op(t, "MOS", "rip_pr2_op_cls_%s" % kind)
        elif c == "rev":
            ok = has_op("MOS", t, "rip_pr2_rev_cls_%s" % kind)
        elif c == "cb":
            a, b = blocks[t]
            ok = any("cb_insult" in lines[k] for k in range(a, b))
        else:
            ok = "rip_pr2_cls_plain" in fl
        row += "%-22s" % (("ran/" if ran else "NOT-RUN/") + ("works" if ok else "DROPPED") + (" " + str(ok) if isinstance(ok, str) else ""))
    print(row)

print("\n=== Q4b direct month/year readings on MOS")
for pref in ("d0", "d61"):
    ms = [n for n in range(12) if ("rip_pr2_%s_month_%d" % (pref, n)) in mosfl]
    ys = [y for y in (1443, 1444, 1445) if ("rip_pr2_%s_year_%d" % (pref, y)) in mosfl]
    print("  %s: done flag=%s date=%s | is_month=N true for N in %s | is_year=Y true for Y in %s" % (
        pref, ("rip_pr2_month_%s_done" % pref) in mosfl, mosfl.get("rip_pr2_month_%s_done" % pref), ms, ys))

print("\n=== Q2b papal influence (lump 20 + monthly modifier papal_influence = 5)")
for t in ("MOS", "POL", "BYZ"):
    print("  %s religion=%s papal_influence=%s modifier present=%s" % (t, scalar(t, "religion"), scalar(t, "papal_influence"), "rip_pr2_papal" in cmods(t)))

print("\n=== days chain on MOS (flag dates)")
for n in ("c1", "c2", "c3", "c4", "c5", "dA", "dB"):
    print("  rip_pr2_dchain_%s = %s" % (n, mosfl.get("rip_pr2_dchain_%s" % n)))
