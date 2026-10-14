"""Generates the scratch harness mod for engine probes Q1..Q4 (never shipped, lives outside the repo)."""
import os, sys

OUT = sys.argv[1]


def w(rel, text, bom=False):
    p = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8-sig" if bom else "utf-8", newline="\n") as f:
        f.write(text)


w("descriptor.mod", 'name="RIP engine probes harness"\nsupported_version="v1.37.5.0"\n')

# ---------------------------------------------------------------- Q3 model
# body kinds: if body, else_if body, else body, control (top level, unconditional),
# and an else_if chain that lives inside a scripted effect
KS = ["if", "ei", "el", "ct", "se"]
COUNTRY = {"if": "POR", "ei": "CAS", "el": "ARA", "ct": "NAV", "se": "GRA"}
EVT = {"if": 31, "ei": 32, "el": 33, "ct": 34, "se": 35}

# (code, flag_in_body, body template)
EFFECTS = [
    ("cm",   True,  "add_country_modifier = {{ name = rip_prb_cm_{K} duration = -1 }}"),
    ("tre",  True,  "add_treasury = 100000"),
    ("pre",  True,  "add_prestige = -300"),
    ("stab", True,  "add_stability = -6"),
    ("dip",  True,  "add_dip_power = 900"),
    ("pm",   True,  "capital_scope = {{ add_province_modifier = {{ name = rip_prb_pm_{K} duration = -1 }} }}"),
    ("rel",  True,  "capital_scope = {{ change_religion = sunni }}"),
    ("aut",  True,  "capital_scope = {{ add_local_autonomy = 50 }}"),
    ("evt",  True,  "country_event = {{ id = rip_prb.{E} days = 1 }}"),
    ("opr",  True,  "add_opinion = {{ who = ROOT modifier = rip_prb_op_root_{K} }}"),
    ("opt",  True,  "add_opinion = {{ who = FRA modifier = rip_prb_op_tag_{K} }}"),
    ("rev",  True,  "reverse_add_opinion = {{ who = ROOT modifier = rip_prb_op_rev_{K} }}"),
    ("rbk",  True,  "ROOT = {{ add_opinion = {{ who = PREV modifier = rip_prb_op_rootblk_{K} }} }}"),
    ("nst",  True,  "if = {{ limit = {{ always = yes }} add_opinion = {{ who = ROOT modifier = rip_prb_op_nest_{K} }} }}"),
    ("hid",  True,  "hidden_effect = {{ add_opinion = {{ who = ROOT modifier = rip_prb_op_hid_{K} }} }}"),
    ("ses",  True,  "rip_prb_addop_effect = {{ K = {K} }}"),
    ("pur",  False, "add_opinion = {{ who = ROOT modifier = rip_prb_op_pure_{K} }}"),
]


def chain(kind, K, code, flag, body, E, indent="\t\t"):
    body = body.format(K=K, E=E)
    flagline = ("set_country_flag = rip_prb_ran_%s_%s " % (code, K)) if flag else ""
    inner = flagline + body
    if kind == "if":
        return indent + "if = { limit = { always = yes } %s }\n" % inner
    if kind == "ct":
        return indent + inner + "\n"
    if kind in ("ei", "se"):
        return (indent + "if = { limit = { always = no } set_country_flag = rip_prb_never }\n" +
                indent + "else_if = { limit = { always = yes } %s }\n" % inner)
    if kind == "el":
        return (indent + "if = { limit = { always = no } set_country_flag = rip_prb_never }\n" +
                indent + "else = { %s }\n" % inner)
    raise SystemExit(kind)


# ---------------------------------------------------------------- generated static files
ev_mod = ["# Test harness only.\n"]
for K in KS:
    ev_mod.append("rip_prb_cm_%s = { land_forcelimit_modifier = 0.01 }\n" % K)
    ev_mod.append("rip_prb_pm_%s = { local_defensiveness = 0.01 }\n" % K)
w("common/event_modifiers/rip_prb_modifiers.txt", "".join(ev_mod))

op = ["# Test harness only.\n"]
for K in KS:
    for c in ("root", "tag", "rev", "rootblk", "nest", "hid", "se", "pure"):
        op.append("rip_prb_op_%s_%s = { opinion = 10 }\n" % (c, K))
w("common/opinion_modifiers/rip_prb_opinions.txt", "".join(op))

# scripted effects: the add_opinion helper and the else_if chain wrapped in a scripted effect
se = ["# Test harness only.\nrip_prb_addop_effect = {\n\tadd_opinion = { who = ROOT modifier = rip_prb_op_se_$K$ }\n}\n\n"]
se.append("rip_prb_se_chain_effect = {\n")
for code, flag, body in EFFECTS:
    b = body.format(K="$K$", E=EVT["se"])
    flagline = ("set_country_flag = rip_prb_ran_%s_$K$ " % code) if flag else ""
    se.append("\tif = { limit = { always = no } set_country_flag = rip_prb_never }\n")
    se.append("\telse_if = { limit = { always = yes } %s%s }\n" % (flagline, b))
se.append("}\n")
w("common/scripted_effects/rip_prb_effects.txt", "".join(se))


# ---------------------------------------------------------------- events
def hidden_country_event(eid, immediate, comment=""):
    return ("%scountry_event = {\n\tid = rip_prb.%d\n\ttitle = rip_prb.t\n\tdesc = rip_prb.d\n\tpicture = RELIGION_eventPicture\n"
            "\thidden = yes\n\tis_triggered_only = yes\n\n\timmediate = {\n%s\t}\n\n\toption = { name = rip_prb.a }\n}\n\n") % (comment, eid, immediate)


def hidden_province_event(eid, immediate, trigger=None, comment=""):
    if trigger:
        trig = "\tfire_only_once = yes\n\ttrigger = { %s }\n\tmean_time_to_happen = { days = 1 }\n" % trigger
    else:
        trig = "\tis_triggered_only = yes\n"
    return ("%sprovince_event = {\n\tid = rip_prb.%d\n\ttitle = rip_prb.t\n\tdesc = rip_prb.d\n\tpicture = RELIGION_eventPicture\n"
            "\thidden = yes\n%s\n\timmediate = {\n%s\t}\n\n\toption = { name = rip_prb.a }\n}\n\n") % (comment, eid, trig, immediate)


def rec_country(flag, days, tagpref, indent="\t\t"):
    return (indent + "if = { limit = { had_country_flag = { flag = %s days = %d } } set_country_flag = %s_%d_T }\n" % (flag, days, tagpref, days) +
            indent + "if = { limit = { NOT = { had_country_flag = { flag = %s days = %d } } } set_country_flag = %s_%d_F }\n" % (flag, days, tagpref, days))


def rec_prov(flag, days, tagpref, indent="\t\t\t"):
    return (indent + "if = { limit = { had_province_flag = { flag = %s days = %d } } set_province_flag = %s_%d_T }\n" % (flag, days, tagpref, days) +
            indent + "if = { limit = { NOT = { had_province_flag = { flag = %s days = %d } } } set_province_flag = %s_%d_F }\n" % (flag, days, tagpref, days))


ev = ["namespace = rip_prb\n\n"]

# ---- Q1: flag dates. Long chain (day 0 / 40 / 50) and short chain (day 0 / 12 / 18)
ev.append(hidden_country_event(11,
    "\t\tset_country_flag = rip_prb_F\n\t\tset_country_flag = rip_prb_G\n\t\tset_country_flag = rip_prb_Fs\n\t\tset_country_flag = rip_prb_Gs\n"
    "\t\tcapital_scope = {\n\t\t\tset_province_flag = rip_prb_PF\n\t\t\tset_province_flag = rip_prb_PG\n\t\t\tset_province_flag = rip_prb_PFs\n\t\t\tset_province_flag = rip_prb_PGs\n\t\t}\n"
    "\t\tset_country_flag = rip_prb_q1_day0_done\n"
    "\t\tcountry_event = { id = rip_prb.12 days = 40 }\n\t\tcountry_event = { id = rip_prb.14 days = 12 }\n",
    "# Q1 day 0: set the flags, schedule the two chains.\n"))

imm = ""
for fl, pref in (("rip_prb_F", "rip_prb_t1_F"), ("rip_prb_G", "rip_prb_t1_G")):
    for d in (30, 45):
        imm += rec_country(fl, d, pref)
imm += "\t\tcapital_scope = {\n"
for fl, pref in (("rip_prb_PF", "rip_prb_t1_PF"), ("rip_prb_PG", "rip_prb_t1_PG")):
    for d in (30, 45):
        imm += rec_prov(fl, d, pref)
imm += "\t\t}\n"
imm += ("\t\tset_country_flag = rip_prb_F\n\t\tclr_country_flag = rip_prb_G\n\t\tset_country_flag = rip_prb_G\n\t\tset_country_flag = rip_prb_H\n"
        "\t\tcapital_scope = {\n\t\t\tset_province_flag = rip_prb_PF\n\t\t\tclr_province_flag = rip_prb_PG\n\t\t\tset_province_flag = rip_prb_PG\n\t\t\tset_province_flag = rip_prb_PH\n\t\t}\n"
        "\t\tset_country_flag = rip_prb_q1_day40_done\n\t\tcountry_event = { id = rip_prb.13 days = 10 }\n")
ev.append(hidden_country_event(12, imm, "# Q1 day 40: record T1 (first date kept?), then re-set F, clr+set G, fresh H, schedule day 50.\n"))

imm = ""
for fl, pref in (("rip_prb_F", "rip_prb_t2_F"), ("rip_prb_G", "rip_prb_t2_G"), ("rip_prb_H", "rip_prb_t2_H")):
    for d in (5, 15, 30, 45):
        imm += rec_country(fl, d, pref)
imm += "\t\tcapital_scope = {\n"
for fl, pref in (("rip_prb_PF", "rip_prb_t2_PF"), ("rip_prb_PG", "rip_prb_t2_PG"), ("rip_prb_PH", "rip_prb_t2_PH")):
    for d in (5, 15, 30, 45):
        imm += rec_prov(fl, d, pref)
imm += "\t\t}\n\t\tset_country_flag = rip_prb_q1_day50_done\n"
ev.append(hidden_country_event(13, imm, "# Q1 day 50: record T2.\n"))

imm = ""
for fl, pref in (("rip_prb_Fs", "rip_prb_s1_F"), ("rip_prb_Gs", "rip_prb_s1_G")):
    for d in (8, 15):
        imm += rec_country(fl, d, pref)
imm += "\t\tcapital_scope = {\n"
for fl, pref in (("rip_prb_PFs", "rip_prb_s1_PF"), ("rip_prb_PGs", "rip_prb_s1_PG")):
    for d in (8, 15):
        imm += rec_prov(fl, d, pref)
imm += "\t\t}\n"
imm += ("\t\tset_country_flag = rip_prb_Fs\n\t\tclr_country_flag = rip_prb_Gs\n\t\tset_country_flag = rip_prb_Gs\n\t\tset_country_flag = rip_prb_Hs\n"
        "\t\tcapital_scope = {\n\t\t\tset_province_flag = rip_prb_PFs\n\t\t\tclr_province_flag = rip_prb_PGs\n\t\t\tset_province_flag = rip_prb_PGs\n\t\t\tset_province_flag = rip_prb_PHs\n\t\t}\n"
        "\t\tset_country_flag = rip_prb_q1_day12_done\n\t\tcountry_event = { id = rip_prb.15 days = 6 }\n")
ev.append(hidden_country_event(14, imm, "# Q1 short chain day 12.\n"))

imm = ""
for fl, pref in (("rip_prb_Fs", "rip_prb_s2_F"), ("rip_prb_Gs", "rip_prb_s2_G"), ("rip_prb_Hs", "rip_prb_s2_H")):
    for d in (3, 8, 12, 15):
        imm += rec_country(fl, d, pref)
imm += "\t\tcapital_scope = {\n"
for fl, pref in (("rip_prb_PFs", "rip_prb_s2_PF"), ("rip_prb_PGs", "rip_prb_s2_PG"), ("rip_prb_PHs", "rip_prb_s2_PH")):
    for d in (3, 8, 12, 15):
        imm += rec_prov(fl, d, pref)
imm += "\t\t}\n\t\tset_country_flag = rip_prb_q1_day18_done\n"
ev.append(hidden_country_event(15, imm, "# Q1 short chain day 18.\n"))

# ---- Q2: papal influence
THR = (10, 20, 30, 40, 45, 50, 55, 60)


def rec_papal(pref, indent="\t\t"):
    s = ""
    for t in THR:
        s += indent + "if = { limit = { papal_influence = %d } set_country_flag = %s_ge%d }\n" % (t, pref, t)
    s += indent + "if = { limit = { religion = greek_catholic } set_country_flag = %s_rel_gc }\n" % pref
    s += indent + "if = { limit = { religion = catholic } set_country_flag = %s_rel_cath }\n" % pref
    s += indent + "if = { limit = { religion = orthodox } set_country_flag = %s_rel_orth }\n" % pref
    return s


imm = ("\t\tset_country_flag = rip_prb_q2_start\n"
       "\t\tenable_religion = greek_catholic\n\t\tchange_religion = greek_catholic\n"
       "\t\tset_country_flag = rip_prb_q2_gc_set\n"
       + rec_papal("rip_prb_q2_pre") +
       "\t\tadd_papal_influence = 50\n"
       + rec_papal("rip_prb_q2_d0") +
       "\t\tPOL = {\n" + rec_papal("rip_prb_q2_pre", "\t\t\t") + "\t\t\tadd_papal_influence = 50\n" + rec_papal("rip_prb_q2_d0", "\t\t\t") + "\t\t}\n"
       "\t\tBYZ = {\n" + rec_papal("rip_prb_q2_pre", "\t\t\t") + "\t\t\tadd_papal_influence = 50\n" + rec_papal("rip_prb_q2_d0", "\t\t\t") + "\t\t}\n"
       "\t\tcountry_event = { id = rip_prb.22 days = 10 }\n"
       "\t\tcountry_event = { id = rip_prb.23 days = 30 }\n")
ev.append(hidden_country_event(21, imm, "# Q2 day 0: make MOS greek_catholic, add papal influence to MOS (GC), POL (catholic control), BYZ (orthodox control).\n"))
imm = (rec_papal("rip_prb_q2_d10") + "\t\tset_country_flag = rip_prb_q2_d10_done\n"
       "\t\tPOL = {\n" + rec_papal("rip_prb_q2_d10", "\t\t\t") + "\t\t\tset_country_flag = rip_prb_q2_d10_done\n\t\t}\n"
       "\t\tBYZ = {\n" + rec_papal("rip_prb_q2_d10", "\t\t\t") + "\t\t\tset_country_flag = rip_prb_q2_d10_done\n\t\t}\n")
ev.append(hidden_country_event(22, imm, "# Q2 day 10 record.\n"))
imm = (rec_papal("rip_prb_q2_d30") + "\t\tset_country_flag = rip_prb_q2_d30_done\n"
       "\t\tPOL = {\n" + rec_papal("rip_prb_q2_d30", "\t\t\t") + "\t\t\tset_country_flag = rip_prb_q2_d30_done\n\t\t}\n"
       "\t\tBYZ = {\n" + rec_papal("rip_prb_q2_d30", "\t\t\t") + "\t\t\tset_country_flag = rip_prb_q2_d30_done\n\t\t}\n")
ev.append(hidden_country_event(23, imm, "# Q2 day 30 record.\n"))

# ---- Q3: effects in if / else_if / else bodies
imm = ""
for K in KS:
    if K == "se":
        imm += "\t\t%s = {\n\t\t\trip_prb_se_chain_effect = { K = se }\n\t\t\tset_country_flag = rip_prb_q3_done_se\n\t\t}\n" % COUNTRY[K]
        continue
    imm += "\t\t%s = {\n" % COUNTRY[K]
    for code, flag, body in EFFECTS:
        imm += chain(K, K, code, flag, body, EVT[K], "\t\t\t")
    # readback in the same tick, outside every branch: did the resource effects land at once?
    imm += "\t\t\tif = { limit = { treasury = 100000 } set_country_flag = rip_prb_rb_tre_%s }\n" % K
    imm += "\t\t\tif = { limit = { NOT = { prestige = -99 } } set_country_flag = rip_prb_rb_pre_%s }\n" % K
    imm += "\t\t\tif = { limit = { NOT = { stability = -2 } } set_country_flag = rip_prb_rb_stab_%s }\n" % K
    imm += "\t\t\tif = { limit = { dip_power = 800 } set_country_flag = rip_prb_rb_dip_%s }\n" % K
    imm += "\t\t\tset_country_flag = rip_prb_q3_done_%s\n\t\t}\n" % K
ev.append(hidden_country_event(30, imm, "# Q3: per body kind one country; every effect in its own chain.\n"))
for K in KS:
    ev.append(hidden_country_event(EVT[K], "\t\tset_country_flag = rip_prb_evt_fired_%s\n" % K, "# Q3 delayed event for body kind %s.\n" % K))

# ---- Q4: dated starters (province events with is_year / is_month / MTTH)
ev.append(hidden_province_event(41, "\t\tset_province_flag = rip_prb_q4_nov_fired\n\t\tprovince_event = { id = rip_prb.42 days = 12 }\n",
    "province_id = 295 is_year = 1444 is_month = 10", "# Q4 starter: is_month = 10 (November?) on the MOS capital.\n"))
ev.append(hidden_province_event(42, "\t\tset_province_flag = rip_prb_q4_X_fired\n", None, "# Q4 X, scheduled 12 days after starter 41.\n"))
ev.append(hidden_province_event(43, "\t\tset_province_flag = rip_prb_q4_dec_fired\n\t\tprovince_event = { id = rip_prb.44 days = 12 }\n",
    "province_id = 295 is_year = 1444 is_month = 11", "# Q4 starter: is_month = 11 (December?) on the MOS capital; must not fire before December.\n"))
ev.append(hidden_province_event(44, "\t\tset_province_flag = rip_prb_q4_Xdec_fired\n", None, "# Q4 X for starter 43.\n"))
ev.append(hidden_province_event(45, "\t\tset_province_flag = rip_prb_q4_oct_fired\n",
    "province_id = 295 is_year = 1444 is_month = 9", "# Q4 control: is_month = 9 must not fire in the run.\n"))
ev.append(hidden_province_event(46, "\t\tset_province_flag = rip_prb_q4_jan_fired\n",
    "province_id = 295 is_year = 1444 is_month = 0", "# Q4: is_month = 0 (January) fires from 1445.1.1 if 0 = January.\n"))
ev.append(hidden_province_event(47, "\t\tset_province_flag = rip_prb_q4_nov_fired\n\t\tprovince_event = { id = rip_prb.48 days = 12 }\n",
    "province_id = 1 is_year = 1444 is_month = 10", "# Q4: same starter on an unrelated province (Stockholm, owned by SWE).\n"))
ev.append(hidden_province_event(48, "\t\tset_province_flag = rip_prb_q4_X_fired\n", None, "# Q4 X for starter 47.\n"))
w("events/rip_prb.txt", "".join(ev))

w("localisation/rip_prb_l_english.yml", 'l_english:\n rip_prb.t:0 "Probe"\n rip_prb.d:0 "Probe"\n rip_prb.a:0 "Probe"\n', bom=True)
print("harness written to", OUT)
