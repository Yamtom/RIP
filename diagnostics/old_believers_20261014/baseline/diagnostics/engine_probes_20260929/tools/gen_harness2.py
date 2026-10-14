"""Run 2 harness: isolates why add_opinion / delayed country_event vanished inside an else_if of a SCRIPTED EFFECT in run 1.
Scratch mod, never shipped, lives outside the repo.
"""
import os, sys

OUT = sys.argv[1]


def w(rel, text, bom=False):
    p = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8-sig" if bom else "utf-8", newline="\n") as f:
        f.write(text)


w("descriptor.mod", 'name="RIP engine probes harness 2"\nsupported_version="v1.37.5.0"\n')

COUNTRIES7 = ["POR", "CAS", "ARA", "NAV", "GRA", "ENG", "BUR"]
V = ["if", "ei", "el", "ct"]
FAM = ["in", "se", "sc", "pa"]           # inline in the event / scripted effect under a TAG scope / scripted effect with inner scope / parametrised
events = {}                              # id -> (comment, immediate)
evt_modifiers = []
op_modifiers = []
nextid = [100]


def new_event(immediate, comment):
    i = nextid[0]
    nextid[0] += 1
    events[i] = (comment, immediate)
    return i


def wrap(v, inner):
    """wrap a body in the branch kind under test"""
    if v == "if":
        return "if = { limit = { always = yes } %s }" % inner
    if v == "ei":
        return "if = { limit = { always = no } set_country_flag = rip_pr2_never }\n\t\telse_if = { limit = { always = yes } %s }" % inner
    if v == "el":
        return "if = { limit = { always = no } set_country_flag = rip_pr2_never }\n\t\telse = { %s }" % inner
    if v == "ct":
        return inner
    raise SystemExit(v)


def body(fam, v, K=""):
    """flag + country modifier + add_opinion + reverse_add_opinion + delayed event + immediate event"""
    key = "%s_%s" % (fam, v)
    dly = evt_ids[(fam, v, "dly")]
    imm = evt_ids[(fam, v, "imm")]
    kk = ("_" + K) if K else ""
    return ("set_country_flag = rip_pr2_ran_%s add_country_modifier = { name = rip_pr2_cm_%s duration = -1 } "
            "add_opinion = { who = ROOT modifier = rip_pr2_op_%s%s } "
            "reverse_add_opinion = { who = ROOT modifier = rip_pr2_rev_%s%s } "
            "country_event = { id = rip_pr2.%d days = 1 } country_event = { id = rip_pr2.%d }") % (key, key, key, kk, key, kk, dly, imm)


evt_ids = {}
for fam in FAM:
    for v in V:
        evt_ids[(fam, v, "dly")] = new_event("\t\tset_country_flag = rip_pr2_evt_%s_%s\n" % (fam, v), "# delayed (days = 1) event for %s_%s\n" % (fam, v))
        evt_ids[(fam, v, "imm")] = new_event("\t\tset_country_flag = rip_pr2_imm_%s_%s\n" % (fam, v), "# immediate event for %s_%s\n" % (fam, v))
        key = "%s_%s" % (fam, v)
        evt_modifiers.append("rip_pr2_cm_%s = { land_forcelimit_modifier = 0.01 }" % key)
        if fam == "pa":
            for K in ("a", "b", "c"):
                op_modifiers.append("rip_pr2_op_%s_%s = { opinion = 10 }" % (key, K))
                op_modifiers.append("rip_pr2_rev_%s_%s = { opinion = 10 }" % (key, K))
        else:
            op_modifiers.append("rip_pr2_op_%s = { opinion = 10 }" % key)
            op_modifiers.append("rip_pr2_rev_%s = { opinion = 10 }" % key)

# ---------------------------------------------------------------- scripted effects
se = ["# Test harness only.\n"]
for v in V:
    se.append("rip_pr2_se_%s = {\n\t%s\n}\n\n" % (v, wrap(v, body("se", v)).replace("\n\t\t", "\n\t")))
    se.append("rip_pr2_sc_%s = {\n\tSWE = {\n\t\t%s\n\t}\n}\n\n" % (v, wrap(v, body("sc", v))))
for v in ("if", "ei", "el"):
    se.append("rip_pr2_pa_%s = {\n\t%s\n}\n\n" % (v, wrap(v, body("pa", v, "$K$")).replace("\n\t\t", "\n\t")))

# multi-pair chain (as run 1) with one pair per effect, parametrised
CH = [
    ("cm",   "add_country_modifier = { name = rip_pr2_chcm_$K$ duration = -1 }"),
    ("tre",  "add_treasury = 1000"),
    ("opr",  "add_opinion = { who = ROOT modifier = rip_pr2_chop_$K$ }"),
    ("rev",  "reverse_add_opinion = { who = ROOT modifier = rip_pr2_chrev_$K$ }"),
    ("evt",  "country_event = { id = rip_pr2.%d days = 1 }"),
]
ch_evt = {v: new_event("\t\tset_country_flag = rip_pr2_evt_ch_%s\n" % v, "# chain delayed event %s\n" % v) for v in ("if", "ei")}
for v in ("ei", "if"):
    se.append("rip_pr2_ch_%s = {\n" % v)
    for code, b in CH:
        if code == "evt":
            b = b % ch_evt[v]
        inner = "set_country_flag = rip_pr2_chran_%s_%s %s" % (code, v, b)
        if v == "ei":
            se.append("\tif = { limit = { always = no } set_country_flag = rip_pr2_never }\n\telse_if = { limit = { always = yes } %s }\n" % inner)
        else:
            se.append("\tif = { limit = { always = yes } %s }\n" % inner)
    se.append("}\n\n")
for K in ("g", "p", "e", "b"):
    for c in ("chcm", "chop", "chrev"):
        pass
    evt_modifiers.append("rip_pr2_chcm_%s = { land_forcelimit_modifier = 0.01 }" % K)
    op_modifiers.append("rip_pr2_chop_%s = { opinion = 10 }" % K)
    op_modifiers.append("rip_pr2_chrev_%s = { opinion = 10 }" % K)

# effect-class matrix: one pair per effect, per branch kind (each kind on its own country)
CLSK = {"ei": "SAV", "ct": "MLO", "if": "VEN", "el": "GEN"}
cls_imm = new_event("\t\tset_country_flag = rip_pr2_cls_imm\n", "# class test: immediate event\n")
cls_dly5 = new_event("\t\tset_country_flag = rip_pr2_cls_dly5\n", "# class test: delayed (days = 5) event\n")
cls_prov = None
CLS = ["trust", "imm", "dly5", "rooteve", "prov", "rootflag", "tre", "opin", "rev", "cb", "flagonly"]
cls_root = {}
for kind in CLSK:
    cls_root[kind] = new_event("\t\tset_country_flag = rip_pr2_cls_rootevt_%s\n" % kind, "# class test: ROOT-targeted delayed event from kind %s (fires in MOS)\n" % kind)
cls_provevt = new_event("\t\tset_province_flag = rip_pr2_cls_provevt\n", "# class test: province event\n")
# province event needs the province_event form, replace it below
op_modifiers.append("# class-test opinion modifiers")
for kind in CLSK:
    op_modifiers.append("rip_pr2_op_cls_%s = { opinion = 10 }" % kind)
    op_modifiers.append("rip_pr2_rev_cls_%s = { opinion = 10 }" % kind)
for kind in CLSK:
    se.append("# class test, branch kind %s\n" % kind)
    effs = {
        "trust": "add_trust = { who = ROOT value = 10 mutual = no }",
        "imm": "country_event = { id = rip_pr2.%d }" % cls_imm,
        "dly5": "country_event = { id = rip_pr2.%d days = 5 }" % cls_dly5,
        "rooteve": "ROOT = { country_event = { id = rip_pr2.%d days = 1 } }" % cls_root[kind],
        "prov": "capital_scope = { province_event = { id = rip_pr2.%d days = 1 } }" % cls_provevt,
        "rootflag": "ROOT = { set_country_flag = rip_pr2_cls_rootflag_%s }" % kind,
        "tre": "add_treasury = 5000",
        "opin": "add_opinion = { who = ROOT modifier = rip_pr2_op_cls_%s }" % kind,
        "rev": "reverse_add_opinion = { who = ROOT modifier = rip_pr2_rev_cls_%s }" % kind,
        "cb": "add_casus_belli = { target = ROOT type = cb_insult months = 12 }",
        "flagonly": "set_country_flag = rip_pr2_cls_plain",
    }
    def pair(c):
        inner = "set_country_flag = rip_pr2_clsran_%s %s" % (c, effs[c])
        if kind == "ct":
            return "\t%s\n" % inner
        if kind == "if":
            return "\tif = { limit = { always = yes } %s }\n" % inner
        if kind == "ei":
            return "\tif = { limit = { always = no } set_country_flag = rip_pr2_never }\n\telse_if = { limit = { always = yes } %s }\n" % inner
        return "\tif = { limit = { always = no } set_country_flag = rip_pr2_never }\n\telse = { %s }\n" % inner
    # the safe set together; the two exotic effects (trust, casus belli) each in their own effect because run 2 crashed the engine
    se.append("rip_pr2_cls_%s_effect = {\n" % kind)
    for c in CLS:
        if c not in ("trust", "cb"):
            se.append(pair(c))
    se.append("}\n\n")
    for c in ("trust", "cb"):
        se.append("rip_pr2_clsx_%s_%s_effect = {\n%s}\n\n" % (c, kind, pair(c)))
w("common/scripted_effects/rip_pr2_effects.txt", "".join(se))
evt_modifiers.append("rip_pr2_papal = { papal_influence = 5 }")
w("common/event_modifiers/rip_pr2_modifiers.txt", "# Test harness only.\n" + "\n".join(evt_modifiers) + "\n")
w("common/opinion_modifiers/rip_pr2_opinions.txt", "# Test harness only.\n" + "\n".join(op_modifiers) + "\n")


# ---------------------------------------------------------------- events
def country_event(eid, immediate, comment=""):
    return ("%scountry_event = {\n\tid = rip_pr2.%d\n\ttitle = rip_pr2.t\n\tdesc = rip_pr2.d\n\tpicture = RELIGION_eventPicture\n"
            "\thidden = yes\n\tis_triggered_only = yes\n\n\timmediate = {\n%s\t}\n\n\toption = { name = rip_pr2.a }\n}\n\n") % (comment, eid, immediate)


def province_event(eid, immediate, comment=""):
    return ("%sprovince_event = {\n\tid = rip_pr2.%d\n\ttitle = rip_pr2.t\n\tdesc = rip_pr2.d\n\tpicture = RELIGION_eventPicture\n"
            "\thidden = yes\n\tis_triggered_only = yes\n\n\timmediate = {\n%s\t}\n\n\toption = { name = rip_pr2.a }\n}\n\n") % (comment, eid, immediate)


ev = ["namespace = rip_pr2\n\n"]

# runners are split so that a crash can be bisected: .1 = in/se matrix, .2 = sc + pa + ch, .3-.6 = class test per branch kind
imm = ""
for X in COUNTRIES7:
    imm += "\t\t%s = {\n" % X
    for v in V:
        imm += "\t\t\trip_pr2_se_%s = yes\n" % v
    for v in V:
        imm += "\t\t\t%s\n" % wrap(v, body("in", v)).replace("\n\t\t", "\n\t\t\t")
    imm += "\t\t\tset_country_flag = rip_pr2_matrix_done\n\t\t}\n"
imm += "\t\tset_country_flag = rip_pr2_master1_done\n"
ev.append(country_event(1, imm, "# Run 2 runner 1: inline and scripted-effect matrix over 7 countries.\n"))
imm = ""
for v in V:
    imm += "\t\trip_pr2_sc_%s = yes\n" % v
imm += "\t\tFRA = { rip_pr2_pa_if = { K = a } rip_pr2_pa_ei = { K = a } rip_pr2_pa_el = { K = a } }\n"
imm += "\t\tGRA = { rip_pr2_pa_ei = { K = b } }\n"
imm += "\t\tCAS = { rip_pr2_pa_ei = { K = c } }\n"
imm += "\t\tGRA = { rip_pr2_ch_ei = { K = g } }\n\t\tPOR = { rip_pr2_ch_ei = { K = p } }\n\t\tENG = { rip_pr2_ch_ei = { K = e } }\n\t\tBUR = { rip_pr2_ch_if = { K = b } }\n"
imm += "\t\tset_country_flag = rip_pr2_master2_done\n"
ev.append(country_event(2, imm, "# Run 2 runner 2: inner-scope, parametrised and multi-pair variants.\n"))
for n, (kind, tag) in enumerate(CLSK.items()):
    imm = "\t\t%s = { rip_pr2_cls_%s_effect = yes set_country_flag = rip_pr2_cls_done }\n" % (tag, kind)
    ev.append(country_event(3 + n, imm, "# Run 2 runner %d: effect-class test (safe set), branch kind %s on %s.\n" % (3 + n, kind, tag)))
    imm = "\t\t%s = { rip_pr2_clsx_trust_%s_effect = yes }\n" % (tag, kind)
    ev.append(country_event(7 + n, imm, "# Run 2 runner %d: add_trust alone, branch kind %s on %s.\n" % (7 + n, kind, tag)))
    imm = "\t\t%s = { rip_pr2_clsx_cb_%s_effect = yes }\n" % (tag, kind)
    ev.append(country_event(11 + n, imm, "# Run 2 runner %d: add_casus_belli alone, branch kind %s on %s.\n" % (11 + n, kind, tag)))

# Q4b: direct is_month / is_year probes, day 0 and again 61 days later
def month_probe(pref):
    s = ""
    for n in range(12):
        s += "\t\tif = { limit = { is_month = %d } set_country_flag = rip_pr2_%s_month_%d }\n" % (n, pref, n)
    for y in (1443, 1444, 1445):
        s += "\t\tif = { limit = { is_year = %d } set_country_flag = rip_pr2_%s_year_%d }\n" % (y, pref, y)
    return s

ev.append(country_event(90, month_probe("d0") + "\t\tset_country_flag = rip_pr2_month_d0_done\n\t\tcountry_event = { id = rip_pr2.99 days = 61 }\n",
                        "# Q4b day 0 (1444.11.11): direct is_month / is_year readings.\n"))
ev.append(country_event(99, month_probe("d61") + "\t\tset_country_flag = rip_pr2_month_d61_done\n", "# Q4b day 61 (1445.1.11).\n"))

# Q2b: papal influence accrual via a modifier
ev.append(country_event(91,
    "\t\tenable_religion = greek_catholic\n\t\tchange_religion = greek_catholic\n"
    "\t\tadd_country_modifier = { name = rip_pr2_papal duration = -1 }\n\t\tadd_papal_influence = 20\n\t\tset_country_flag = rip_pr2_q2b_start\n"
    "\t\tPOL = { add_country_modifier = { name = rip_pr2_papal duration = -1 } add_papal_influence = 20 }\n"
    "\t\tBYZ = { add_country_modifier = { name = rip_pr2_papal duration = -1 } add_papal_influence = 20 }\n",
    "# Q2b: GC vs Catholic vs Orthodox, both a lump and a monthly modifier.\n"))

# days chain
ev.append(country_event(92,
    "\t\tset_country_flag = rip_pr2_dchain_c1\n\t\tcountry_event = { id = rip_pr2.93 days = 10 }\n\t\tcountry_event = { id = rip_pr2.97 days = 1 }\n",
    "# days chain c1 (console-fired).\n"))
ev.append(country_event(93, "\t\tset_country_flag = rip_pr2_dchain_c2\n\t\tcountry_event = { id = rip_pr2.94 days = 10 }\n\t\tcountry_event = { id = rip_pr2.98 days = 1 }\n", "# c2.\n"))
ev.append(country_event(94, "\t\tset_country_flag = rip_pr2_dchain_c3\n\t\tcountry_event = { id = rip_pr2.95 days = 10 }\n", "# c3.\n"))
ev.append(country_event(95, "\t\tset_country_flag = rip_pr2_dchain_c4\n\t\tcountry_event = { id = rip_pr2.96 days = 1 }\n", "# c4.\n"))
ev.append(country_event(96, "\t\tset_country_flag = rip_pr2_dchain_c5\n", "# c5.\n"))
ev.append(country_event(97, "\t\tset_country_flag = rip_pr2_dchain_dA\n", "# dA: 1 day after c1.\n"))
ev.append(country_event(98, "\t\tset_country_flag = rip_pr2_dchain_dB\n", "# dB: 1 day after c2.\n"))

for eid in sorted(events):
    comment, immediate = events[eid]
    ev.append(country_event(eid, immediate, comment))
# province event for the class test (the placeholder above was registered as a country event; replace)
ev = [e for e in ev if not e.startswith("# class test: province event")]
ev.append(province_event(cls_provevt, "\t\tset_province_flag = rip_pr2_cls_provevt\n", "# class test: province event\n"))
w("events/rip_pr2.txt", "".join(ev))
w("localisation/rip_pr2_l_english.yml", 'l_english:\n rip_pr2.t:0 "Probe"\n rip_pr2.d:0 "Probe"\n rip_pr2.a:0 "Probe"\n', bom=True)
print("harness 2 written to", OUT, "events:", len(ev))
