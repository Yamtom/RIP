"""Scratch harness mod for the in-engine proof of the eparchy timeline, the Uzhhorod union and the repaired synod gates.

Never shipped; loaded AFTER RIP through dlc_load.json. Usage:

    python gen_harness.py <out dir> <profile> <rip tree>

<rip tree> is the mod root whose trigger files are copied and window-overridden (the NEW snapshot).
Profiles (all start on 1444.11.11 with the player MOS):

  seats     R1. Every eparchy row and the Uzhhorod union open in BOTH windows (the brief's "always = yes").
            2424 and 2961 are ceded to POL (Catholic owner, province stays Orthodox), 279 becomes Catholic and goes to LIT,
            UZH becomes Catholic. HLC becomes a Greek Catholic theocracy with the Halych reform and full patriarch
            authority, and the repaired gates are evaluated on it (rip_ee.2) before and after the authority.
  controls  R2. Negative controls and the Orthodox owner path: the lviv_union row is closed in both windows (so Lviv stays
            Orthodox and the two development rows, which are open, must stay silent); 2424 goes to LIT which carries
            rip_church_opposes_union (przemysl must stay silent); 279 to POL (lutsk fires); UZH stays Orthodox with its
            Catholic overlord HUN (popup fires, weight 20/50).
  late      R3. Only the late windows are open (date windows closed), the same seat setup as seats, no gate work.
  <profile>+patch  the same profile with hidden events given title/desc/picture (see PATCH below).
  player    R5. The player (MOS) becomes Catholic and owns all four seats; game.log then lists every event the player receives
            ("Selected event option 0 for event ..."), which counts the firings and forces option a.
  head      R4. Plain HEAD tree: no window overrides at all (HEAD has no such triggers), the same setup event as seats,
            gates evaluated in old form. Baseline for the gates and for error.log.
"""
import os
import re
import sys

OUT, PROFILE, RIP = sys.argv[1], sys.argv[2], sys.argv[3]
# "<profile>+patch": additionally ships harness copies of events/RIP_EparchyHistory.txt and events/RIP_UzhLocalUnion.txt in which
# every hidden event also carries title / desc / picture (the engine logs "is missing a title/desc/picture" for the hidden
# starters as shipped; the +patch variant tests whether that is what stops them firing).
PATCH = PROFILE.endswith("+patch")
PROFILE = PROFILE.replace("+patch", "")


def w(rel, text, bom=False, eol="\r\n"):
    p = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    text = text.replace("\r\n", "\n").replace("\n", eol)
    with open(p, "w", encoding="utf-8-sig" if bom else "utf-8", newline="") as f:
        f.write(text)


def read(rel):
    with open(os.path.join(RIP, rel), "rb") as f:
        return f.read().decode("utf-8")


def replace_block(text, name, body):
    """Replace the body of `name = { ... }` (top level scripted trigger) by `body`, keeping the rest byte for byte."""
    m = re.search(r"(?m)^%s\s*=\s*\{" % re.escape(name), text)
    if not m:
        raise SystemExit("trigger %s not found" % name)
    depth, i = 1, m.end()
    while depth:
        c = text[i]
        depth += (c == "{") - (c == "}")
        i += 1
    return text[:m.end()] + " " + body + " " + text[i - 1:]


ROWS = ["przemysl_union", "lviv_union", "lutsk_union",
        "lviv_greek_catholic_name_barbareum_1774", "lviv_galician_metropolitanate_1807"]
DEV = ROWS[3:]

# state of (date window, late window) per row and for the Uzhhorod union
OPEN = ("open", "open")
if PROFILE in ("seats", "player"):
    states = {r: OPEN for r in ROWS}
    uzh_states = OPEN
elif PROFILE == "controls":
    states = {r: OPEN for r in ROWS}
    states["lviv_union"] = ("closed", "closed")
    uzh_states = OPEN
elif PROFILE == "late":
    states = {r: ("closed", "open") for r in ROWS}
    uzh_states = ("closed", "open")
elif PROFILE == "head":
    states = None
    uzh_states = None
else:
    raise SystemExit("unknown profile " + PROFILE)

# "always = no" in both windows of one row crashed eu4.exe during loading (profile controls, twice); a false year test does not
VAL = {"open": "always = yes", "closed": "is_year = 9999"}

w("descriptor.mod", 'name="RIP eparchy engine harness"\nsupported_version="v1.37.5.0"\n', eol="\n")

if states is not None:
    t = read("common/scripted_triggers/rip_eparchy_triggers.txt")
    for r in ROWS:
        d, l = states[r]
        t = replace_block(t, "rip_eparchy_%s_date_window" % r, VAL[d])
        t = replace_block(t, "rip_eparchy_%s_late_window" % r, VAL[l])
    w("common/scripted_triggers/rip_eparchy_triggers.txt",
      "# HARNESS COPY of the RIP file, window triggers overridden (profile %s). Same file name, so it replaces RIP's.\n" % PROFILE + t)

    u = read("common/scripted_triggers/rip_uzh_union_triggers.txt")
    u = replace_block(u, "rip_uzh_union_date_window", VAL[uzh_states[0]])
    u = replace_block(u, "rip_uzh_union_late_window", VAL[uzh_states[1]])
    # the possible trigger carries its own date gate is_year = 1646 (true from 1646 on); open it as well
    m = re.search(r"(?s)rip_uzh_local_union_possible\s*=\s*\{.*?\n\}", u)
    block = m.group(0)
    assert block.count("is_year = 1646") == 1
    u = u.replace(block, block.replace("is_year = 1646", "always = yes # HARNESS: date gate opened"))
    w("common/scripted_triggers/rip_uzh_union_triggers.txt",
      "# HARNESS COPY of the RIP file, window triggers and the is_year = 1646 gate of possible overridden (profile %s).\n" % PROFILE + u)

if PATCH:
    for rel in ("events/RIP_EparchyHistory.txt", "events/RIP_UzhLocalUnion.txt"):
        src = read(rel).replace("\r\n", "\n")
        n = len(re.findall(r"(?m)^\s*hidden = yes\s*$", src))
        src = re.sub(r"(?m)^([ \t]*)hidden = yes[ \t]*$",
                     lambda m: "%shidden = yes\n%stitle = rip_ee.t\n%sdesc = rip_ee.d\n%spicture = RELIGION_eventPicture" % ((m.group(1),) * 4), src)
        w(rel, "# HARNESS COPY (+patch): hidden events given title/desc/picture; %d hidden events patched.\n" % n + src)


# ---------------------------------------------------------------- events
SEATS_SETUP = """
		2424 = { cede_province = POL }
		2961 = { cede_province = POL }
		279 = { change_religion = catholic cede_province = LIT }
		UZH = { change_religion = catholic }
"""
CONTROLS_SETUP = """
		2424 = { cede_province = LIT }
		LIT = { set_country_flag = rip_church_opposes_union }
		2961 = { cede_province = POL }
		279 = { change_religion = catholic cede_province = POL }
"""
PLAYER_SETUP = """
		change_religion = catholic
		2424 = { cede_province = ROOT }
		2961 = { cede_province = ROOT }
		279 = { change_religion = catholic cede_province = ROOT }
		1952 = { cede_province = ROOT }
"""
setup = CONTROLS_SETUP if PROFILE == "controls" else PLAYER_SETUP if PROFILE == "player" else SEATS_SETUP
do_gates = PROFILE in ("seats", "head")


def flag_pair(name, cond):
    return ("\t\tif = { limit = { %s } set_country_flag = rip_ee_%s_yes }\n"
            "\t\tif = { limit = { NOT = { %s } } set_country_flag = rip_ee_%s_no }\n" % (cond, name, cond, name))


def gates(tag):
    s = ""
    # the old papal conditions, evaluated in both trees: a greek_catholic country never reaches them
    s += flag_pair(tag + "_old_papal_40", "papal_influence = 40")
    s += flag_pair(tag + "_old_papal_60", "papal_influence = 60")
    # named triggers that exist in HEAD too (old body there, repaired body in NEW)
    s += flag_pair(tag + "_uzh_translate", "uzh_can_translate_the_see = yes")
    s += flag_pair(tag + "_uzh_presov", "uzh_can_split_presov_eparchy = yes")
    if PROFILE == "seats":
        s += flag_pair(tag + "_gc_low", "rip_gc_hierarchy_standing_low = yes")
        s += flag_pair(tag + "_gc_mid", "rip_gc_hierarchy_standing_mid = yes")
        s += flag_pair(tag + "_gc_high", "rip_gc_hierarchy_standing_high = yes")
        s += flag_pair(tag + "_any_low", "rip_hierarchy_standing_low = yes")
        s += flag_pair(tag + "_any_high", "rip_hierarchy_standing_high = yes")
    return s


events = """namespace = rip_ee

# Setup, fired at the player by the console at the start of the run.
country_event = {
	id = rip_ee.1
	title = rip_ee.t
	desc = rip_ee.d
	picture = RELIGION_eventPicture
	hidden = yes
	is_triggered_only = yes
	immediate = {
%s		set_country_flag = rip_ee_setup_done
""" % setup

if do_gates:
    events += """		HLC = { country_event = { id = rip_ee.2 days = 2 } }
		POL = { country_event = { id = rip_ee.3 days = 2 } }
"""
if PROFILE != "head":
    # the trigger probes run on the seat provinces 3 days in, after the setup cession has happened
    for pid in (2424, 2961, 279, 1952):
        events += "\t\t%d = { province_event = { id = rip_ee.10 days = 3 } }\n" % pid
events += """	}
	option = { name = rip_ee.a }
}
"""

if do_gates:
    events += """
# HLC becomes a Greek Catholic theocracy with the Halych reform (the effect of hlc_elevate_the_metropolitan),
# the repaired gates are read before and after the authority is granted.
country_event = {
	id = rip_ee.2
	title = rip_ee.t
	desc = rip_ee.d
	picture = RELIGION_eventPicture
	hidden = yes
	is_triggered_only = yes
	immediate = {
		change_religion = greek_catholic
		change_government = theocracy
		add_government_reform = hlc_halych_metropolitanate_reform
		add_stability = 3
		add_adm_power = 300
		set_country_flag = rip_ee_hlc_prepared
%(pre)s
		add_patriarch_authority = 1
		set_country_flag = rip_ee_hlc_pa_granted
%(post)s
	}
	option = { name = rip_ee.a }
}

# POL keeps the Catholic branch: papal influence still opens the shared gates.
country_event = {
	id = rip_ee.3
	title = rip_ee.t
	desc = rip_ee.d
	picture = RELIGION_eventPicture
	hidden = yes
	is_triggered_only = yes
	immediate = {
		add_stability = 3
		add_adm_power = 300
%(polpre)s
		add_papal_influence = 100
%(polpost)s
	}
	option = { name = rip_ee.a }
}
""" % {
        "pre": gates("pre"),
        "post": gates("post"),
        "polpre": (flag_pair("pol_pre_uzh_translate", "uzh_can_translate_the_see = yes") +
                   (flag_pair("pol_pre_any_high", "rip_hierarchy_standing_high = yes") if PROFILE == "seats" else "")),
        "polpost": (flag_pair("pol_post_uzh_translate", "uzh_can_translate_the_see = yes") +
                    flag_pair("pol_post_uzh_presov", "uzh_can_split_presov_eparchy = yes") +
                    (flag_pair("pol_post_any_high", "rip_hierarchy_standing_high = yes") if PROFILE == "seats" else "")),
    }

if PROFILE != "head":
    probe = """
# Trigger probe on a seat province: records the result of every named trigger that gates the dated events.
province_event = {
	id = rip_ee.10
	title = rip_ee.t
	desc = rip_ee.d
	picture = RELIGION_eventPicture
	hidden = yes
	is_triggered_only = yes
	immediate = {
"""
    probe += flag_pair("owner_catholic", "owner = { religion = catholic }").replace("country_flag", "province_flag")
    probe += flag_pair("is_orthodox", "religion = orthodox").replace("country_flag", "province_flag")
    probe += flag_pair("is_city_ctrl", "is_city = yes controlled_by = owner").replace("country_flag", "province_flag")
    for r in ROWS:
        for k in ("date_window", "late_window", "ready", "possible"):
            probe += flag_pair("%s_%s" % (r[:14], k), "rip_eparchy_%s_%s = yes" % (r, k)).replace("country_flag", "province_flag")
    for k in ("date_window", "late_window"):
        probe += flag_pair("uzh_" + k, "rip_uzh_union_%s = yes" % k).replace("country_flag", "province_flag")
    probe += flag_pair("uzh_possible", "rip_uzh_local_union_possible = yes").replace("country_flag", "province_flag")
    probe += flag_pair("uzh_sched_fresh", "rip_uzh_union_scheduled_fresh = yes").replace("country_flag", "province_flag")
    probe += """	}
	option = { name = rip_ee.a }
}
"""
    events += probe

w("events/rip_ee.txt", events)
w("localisation/rip_ee_l_english.yml", 'l_english:\n rip_ee.t:0 "Harness"\n rip_ee.d:0 "Harness"\n rip_ee.a:0 "Harness"\n', bom=True)
print("harness written:", OUT, "profile", PROFILE)
