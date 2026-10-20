"""Contracts for the Border Watch: one button-only mechanic on the two M5 border reforms of Pereiaslav and Podillia.

Static checks over script, sprites and localisation, written against docs/BORDER_MECHANICS_20261019.uk.md.
They prove the files agree with each other and with the steppe-raid event the Watch is built to answer; they
do not prove the engine draws the panel. What was measured in EU4 1.37.5 (the load, and the engine's refusal
of a scripted trigger inside `available`) is recorded in that document.

  * prl_border_fortress_reform and pdl_carpathian_bastion_reform - and no other reform - carry
    rip_border_watch_mechanic and clear it in removed_effect; their passive bundles are unchanged; the
    Podillian frontier path keeps cossacks_mechanic and gets no second panel.
  * `available` is a plain OR of the two reforms: the engine reads it before scripted triggers exist.
  * Three buttons, one per monarch power, each paid 50 in trigger and effect, on one ten-year cooldown
    token with a named cooldown, keyed on the reform and never on the tag, with no powers, no .gui, no
    else/else_if and no raw flag in a trigger; the two local orders work only on a city that borders a
    steppe power and say so through custom_trigger_tooltip.
  * The Watch never touches the Podillian border policy: it adds no second independent set of bonuses
    there (docs/REGIONAL_REFORM_AUDIT.uk.md).
  * events/SteppeRaiding.txt, steppe_raid.2 and only it, treats the tower line and the settled watch as a
    defended province and the patrols as a national defence.
  * The steppe-power definition equals the church layer's, word for word.
  * The three modifiers have the designed numbers, the right scope, text and a name; the clear-up effect
    ends all three and the flag the orders set; three 82x82 sprites exist and differ; four languages carry every key.
  * removed_effect runs when the reform is removed by remove_government_reform but not when a change of government
    type drops it (measured in EU4 1.37.5), so a yearly sweep from on_yearly_pulse clears a country that laid the Watch
    (flag rip_border_watch_laid) and holds neither reform.

Standard library only. Self-test: each planted violation must be caught.
"""
import re
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from clausewitz_testlib import ROOT, read, named_block, matching_brace, normalized, _mask_comments_and_strings  # noqa: E402

LANGUAGES = ("english", "french", "german", "spanish")
MECHANIC = "rip_border_watch_mechanic"
MECH_FILE = "common/government_mechanics/rip_border_watch.txt"
GFX = "interface/rip_captaincy_icons.gfx"
TOKEN = "rip_border_watch_order"
COOLDOWN_DESC = "rip_border_watch_order_cd"
CARRIERS = ("prl_border_fortress_reform", "pdl_carpathian_bastion_reform")
BASE_BUNDLES = {
    "prl_border_fortress_reform": {"fort_maintenance_modifier": "-0.15", "defensiveness": "0.2"},
    "pdl_carpathian_bastion_reform": {"fort_maintenance_modifier": "-0.15", "defensiveness": "0.2", "hostile_attrition": "1"},
}

# button -> (power, sprite, "province" | "country", modifier, duration in days)
BUTTONS = {
    "rip_post_the_watchtowers": ("adm", "GFX_rip_watch_towers", "province", "rip_watchtower_line", 2920),
    "rip_send_out_the_patrols": ("mil", "GFX_rip_watch_patrols", "country", "rip_steppe_patrols", 1825),
    "rip_settle_the_watch": ("dip", "GFX_rip_watch_settlers", "province", "rip_settled_watch", 7300),
}
MODIFIERS = {
    "rip_watchtower_line": {"local_defensiveness": "0.2", "local_hostile_attrition": "1"},
    "rip_settled_watch": {"local_manpower_modifier": "0.25", "local_defensiveness": "0.1", "local_tax_modifier": "-0.15"},
    "rip_steppe_patrols": {"hostile_attrition": "0.5", "movement_speed": "0.1", "land_maintenance_modifier": "0.05"},
}
COOLDOWN_YEARS = 10
FLAG = "rip_border_watch_laid"  # set by each order, read only by the yearly sweep (a hidden effect: no tooltip shows it)


# --------------------------------------------------------------------------
# Parsing helpers
# --------------------------------------------------------------------------

def children(block):
    """Top-level `name = { ... }` children of a block, in file order."""
    opening = block.index("{")
    inner = block[opening + 1: matching_brace(block, opening)]
    masked = _mask_comments_and_strings(inner)
    out, pos = [], 0
    pattern = re.compile(r"(\w+)\s*=\s*\{")
    while True:
        match = pattern.search(masked, pos)
        if not match:
            return out
        brace = inner.index("{", match.start(), match.end())
        close = matching_brace(inner, brace)
        out.append((match.group(1), inner[match.start(): close + 1]))
        pos = close + 1


def interactions(text):
    return children(named_block(named_block(text, MECHANIC), "interactions"))


def body(block):
    return block[block.index("{") + 1: block.rindex("}")]


def block_of(text, name):
    try:
        return named_block(text, name)
    except Exception:
        return ""


def loc_text(language):
    path = ROOT / "localisation" / ("rip_border_mechanics_l_english.yml" if language == "english"
                                      else f"replace/zzz_RIP_untranslated_border_l_{language}.yml")
    return path.read_text(encoding="utf-8-sig") if path.is_file() else ""


def loc_value(text, key):
    match = re.search(rf'(?m)^ {re.escape(key)}:\d+ "(.*)"\s*$', text)
    return match.group(1) if match else None


def read_dds(path):
    data = path.read_bytes()
    if data[:4] != b"DDS ":
        return None
    height, width = struct.unpack("<2I", data[12:20])
    bits = struct.unpack("<I", data[88:92])[0]
    return width, height, bits, data[128:]


def raid_event(text):
    start = text.index("\tid = steppe_raid.2")
    end = text.index("\tid = steppe_raid.3")
    return text[start:end]


# --------------------------------------------------------------------------
# Checks: each returns a list of problems, so a planted violation can be caught
# --------------------------------------------------------------------------

def check_reforms(prl, pdl, all_reforms):
    problems = []
    for reform, text in (("prl_border_fortress_reform", prl), ("pdl_carpathian_bastion_reform", pdl)):
        block = block_of(text, reform)
        if not block:
            problems.append(f"{reform} is missing")
            continue
        abilities = re.findall(r"\w+", body(block_of(block, "government_abilities")))
        if abilities != [MECHANIC]:
            problems.append(f"{reform}: government_abilities is {abilities}, expected [{MECHANIC}]")
        removed = normalized(body(block_of(block, "removed_effect")))
        if removed != "hidden_effect = { rip_border_watch_clear_effect = yes }":
            problems.append(f"{reform}: removed_effect is {removed!r}")
        bundle = dict(re.findall(r"(\w+)\s*=\s*(-?[\d.]+)", body(block_of(block, "modifiers"))))
        if bundle != BASE_BUNDLES[reform]:
            problems.append(f"{reform}: the passive bundle changed to {bundle}")
    cossacks = block_of(pdl, "pdl_frontier_republic_reform")
    if "cossacks_mechanic" not in cossacks or MECHANIC in cossacks:
        problems.append("pdl_frontier_republic_reform must keep cossacks_mechanic and carry no Watch (no second panel)")
    carriers = []
    code = re.sub(r"#[^\n]*", "", all_reforms)  # a comment above a reform belongs to the next block, not the previous one
    for name, reform_block in re.findall(r"(?m)^([A-Za-z0-9_]+)\s*=\s*\{(.*?)(?=^[A-Za-z0-9_]+\s*=\s*\{|\Z)", code, re.S):
        if MECHANIC in reform_block:
            carriers.append(name)
    if sorted(carriers) != sorted(CARRIERS):
        problems.append(f"the Watch is carried by {sorted(carriers)}, expected exactly {sorted(CARRIERS)}")
    return problems


def check_mechanic(mech):
    problems = []
    plain = re.sub(r"#[^\n]*", "", mech)
    available = normalized(block_of(named_block(mech, MECHANIC), "available"))
    want = "available = { OR = { has_reform = prl_border_fortress_reform has_reform = pdl_carpathian_bastion_reform } }"
    if available != want:
        problems.append(f"available must be a plain OR of the two reforms (the engine reads it before scripted triggers exist), found: {available}")
    for forbidden, why in (("tag =", "the mechanic must key on the reform, not the tag (PDL becomes VOL/UKR, PRL becomes HET)"),
                           ("powers = {", "no parallel resource"),
                           ("gui =", "no own window"),
                           ("else = {", "else/else_if bodies drop effects in 1.37.5"),
                           ("else_if", "else/else_if bodies drop effects in 1.37.5"),
                           ("has_country_flag", "a blocked button would show the raw flag name"),
                           ("has_dlc", "the sibling mechanics carry no DLC gate"),
                           ("pdl_border_policy", "the Watch must not touch the Podillian border policy"),
                           ("pdl_recent_border_policy", "the Watch must not touch the Podillian border policy"),
                           ("_defense_funded", "the Watch must not add a second set of bonuses to the Podillian policy"),
                           ("_settlement_supported", "the Watch must not add a second set of bonuses to the Podillian policy")):
        if forbidden in plain:
            problems.append(f"{forbidden!r} in the mechanic: {why}")
    found = interactions(mech)
    names = [name for name, _ in found]
    if names != list(BUTTONS):
        return problems + [f"buttons are {names}, expected {list(BUTTONS)}"]
    powers, icons = set(), []
    for name, block in found:
        power, sprite, scope, modifier, days = BUTTONS[name]
        trig, eff = named_block(block, "trigger"), named_block(block, "effect")
        icon = re.search(r"(?m)^\s*icon\s*=\s*(\w+)", block)
        icons.append(icon.group(1) if icon else None)
        if icons[-1] != sprite:
            problems.append(f"{name} uses {icons[-1]}, expected {sprite}")
        if not normalized(trig).startswith("trigger = { rip_border_watch_held = yes"):
            problems.append(f"{name}: the trigger does not open with rip_border_watch_held = yes")
        for label, part in (("trigger", trig), ("effect", eff)):
            cost = re.findall(rf"\b(mil|adm|dip)_power_cost = (\d+)", part)
            if cost != [(power, "50")]:
                problems.append(f"{name}: {label} cost is {cost}, expected [{power}_power_cost = 50]")
        powers.add(power)
        if f"cooldown_years = {COOLDOWN_YEARS}" not in block:
            problems.append(f"{name}: cooldown is not {COOLDOWN_YEARS} years")
        if f"cooldown_token = {TOKEN}" not in block:
            problems.append(f"{name}: not on the shared cooldown token")
        if f"cooldown_desc = {COOLDOWN_DESC}" not in block:
            problems.append(f"{name}: no named cooldown")
        if "ai_chance" not in block:
            problems.append(f"{name}: no ai_chance")
        if f"name = {modifier}" not in eff or f"duration = {days}" not in eff:
            problems.append(f"{name}: effect does not add {modifier} for {days} days")
        if f"set_country_flag = {FLAG}" not in eff:
            problems.append(f"{name}: the order does not set {FLAG}, so the yearly sweep would never clear what it laid")
        if scope == "province":
            if "hidden_effect" not in eff or "custom_tooltip" not in eff:
                problems.append(f"{name}: a local order needs custom_tooltip plus hidden_effect (the loop has no tooltip of its own)")
            if "limit = { rip_watch_" not in eff:
                problems.append(f"{name}: the local effect is not limited to the Watch's own province triggers")
            if "add_country_modifier" in eff:
                problems.append(f"{name}: a local order adds a country modifier")
        else:
            if "add_country_modifier" not in eff or "province" in eff:
                problems.append(f"{name}: the national order is not a plain country modifier")
    if powers != {"mil", "adm", "dip"}:
        problems.append(f"the three buttons spend {sorted(powers)}, expected one each of mil, adm, dip")
    if len(set(icons)) != len(icons):
        problems.append("two buttons share an icon")
    if any(i and i.startswith("GFX_cossacks_ability_") for i in icons):
        problems.append("a button still borrows vanilla's Cossack ability icon")

    towers = dict(found)["rip_post_the_watchtowers"]
    if not re.search(r"if = \{\s*limit = \{ has_province_modifier = rip_watchtower_line \}\s*remove_province_modifier = rip_watchtower_line\s*\}\s*add_province_modifier", named_block(towers, "effect")):
        problems.append("the tower line is added without removing the old one first (add_province_modifier does not refresh a running term)")
    if not re.search(r"custom_trigger_tooltip = \{\s*tooltip = rip_watch_exposed_province_tt\s*any_owned_province = \{ rip_watch_exposed_province = yes \}\s*\}", named_block(towers, "trigger")):
        problems.append("the towers do not gate on an exposed city through custom_trigger_tooltip")
    settle = dict(found)["rip_settle_the_watch"]
    if not re.search(r"custom_trigger_tooltip = \{\s*tooltip = rip_watch_unsettled_province_tt\s*any_owned_province = \{ rip_watch_unsettled_province = yes \}\s*\}", named_block(settle, "trigger")):
        problems.append("the settlement does not gate on an unsettled exposed city through custom_trigger_tooltip")
    if "random_owned_province" not in named_block(settle, "effect"):
        problems.append("the settlement does not pick one city")
    ai = normalized(named_block(settle, "ai_chance"))
    if "factor = 0 is_at_war = yes" not in ai:
        problems.append("the settlement's AI may settle the watch in a war")
    return problems


def check_triggers_and_effects(triggers, effects, church):
    problems = []
    held = normalized(block_of(triggers, "rip_border_watch_held"))
    if held != "rip_border_watch_held = { OR = { has_reform = prl_border_fortress_reform has_reform = pdl_carpathian_bastion_reform } }":
        problems.append(f"rip_border_watch_held is {held}")
    mine = re.sub(r"^\w+ = ", "", normalized(block_of(triggers, "rip_watch_steppe_power")))
    theirs = re.sub(r"^\w+ = ", "", normalized(block_of(church, "rip_church_steppe_power")))
    if not mine or mine != theirs:
        problems.append("rip_watch_steppe_power differs from the church layer's rip_church_steppe_power: the two layers define a steppe power differently")
    exposed = normalized(block_of(triggers, "rip_watch_exposed_province"))
    if exposed != "rip_watch_exposed_province = { is_city = yes any_neighbor_province = { owner = { NOT = { tag = ROOT } rip_watch_steppe_power = yes } } }":
        problems.append(f"rip_watch_exposed_province is {exposed}")
    unsettled = normalized(block_of(triggers, "rip_watch_unsettled_province"))
    if unsettled != "rip_watch_unsettled_province = { rip_watch_exposed_province = yes NOT = { has_province_modifier = rip_settled_watch } }":
        problems.append(f"rip_watch_unsettled_province is {unsettled}")
    clear = normalized(block_of(effects, "rip_border_watch_clear_effect"))
    for needle in ("remove_country_modifier = rip_steppe_patrols",
                   "limit = { has_province_modifier = rip_watchtower_line } remove_province_modifier = rip_watchtower_line",
                   "limit = { has_province_modifier = rip_settled_watch } remove_province_modifier = rip_settled_watch",
                   f"clr_country_flag = {FLAG}"):
        if needle not in clear:
            problems.append(f"the clear-up effect lacks: {needle}")
    sweep = normalized(block_of(effects, "rip_border_watch_sweep_effect"))
    want = (f"rip_border_watch_sweep_effect = {{ if = {{ limit = {{ has_country_flag = {FLAG} "
            f"NOT = {{ rip_border_watch_held = yes }} }} rip_border_watch_clear_effect = yes }} }}")
    if sweep != want:
        problems.append(f"rip_border_watch_sweep_effect is {sweep}, expected one flag look-up and the held test only")
    if re.search(r"\belse(_if)?\b", re.sub(r"#[^\n]*", "", effects)):
        problems.append("else/else_if in the clean-up effects: bodies drop effects in 1.37.5")
    return problems


def check_sweep(on_actions):
    """removed_effect does not run when a change of government type drops the reform (measured in EU4 1.37.5): the
    yearly sweep is the Watch's own clean-up, as hlc_ordinance_sweep_effect is for the Chancery Ordinances."""
    yearly = normalized(block_of(on_actions, "on_yearly_pulse"))
    if "rip_border_watch_sweep_effect = yes" not in yearly:
        return ["on_yearly_pulse does not call rip_border_watch_sweep_effect"]
    return []


def check_modifiers(modifier_text, loc):
    problems = []
    for name, want in MODIFIERS.items():
        block = block_of(modifier_text, name)
        if not block:
            problems.append(f"modifier {name} is missing")
            continue
        have = dict(re.findall(r"(\w+)\s*=\s*(-?[\d.]+)", body(block)))
        if have != want:
            problems.append(f"{name} is {have}, the design is {want}")
        scope = "province" if name != "rip_steppe_patrols" else "country"
        local = [k for k in have if k.startswith("local_")]
        if scope == "province" and len(local) != len(have):
            problems.append(f"{name} is a province modifier but has non-local keys")
        if scope == "country" and local:
            problems.append(f"{name} is a country modifier but has local keys")
        for key in (name, f"desc_{name}"):
            if loc_value(loc, key) is None:
                problems.append(f"no English text for {key}")
    return problems


def check_raid(raid):
    problems = []
    event = raid_event(raid)
    for name, want in (("has_province_modifier = rip_watchtower_line", 3), ("has_province_modifier = rip_settled_watch", 3),
                       ("has_country_modifier = rip_steppe_patrols", 1)):
        if event.count(name) != want:
            problems.append(f"steppe_raid.2 mentions {name} {event.count(name)} times, expected {want}")
        if raid.count(name) != event.count(name):
            problems.append(f"{name} appears outside steppe_raid.2: the Watch protects only the Ruthenian frontier victims")
    # the new names sit in the same lists as the church's frontier watch
    church = event.count("has_province_modifier = rip_church_frontier_watch")
    if church != 3:
        problems.append(f"steppe_raid.2 lists the church's frontier watch {church} times, expected 3")
    return problems


def check_text(loc, mech):
    problems = []
    found = dict(interactions(mech))
    for key, power in (("rip_post_the_watchtowers_desc", "administrative"), ("rip_send_out_the_patrols_desc", "military"),
                       ("rip_settle_the_watch_desc", "diplomatic")):
        text = loc_value(loc, key) or ""
        if f"Spend 50 {power} power" not in text:
            problems.append(f"{key} does not state the cost: 50 {power} power")
        if "ten-year cooldown" not in text:
            problems.append(f"{key} does not state the shared ten-year cooldown")
    towers = loc_value(loc, "rip_post_the_watchtowers_desc") or ""
    for want in ("+20% local defensiveness", "+1 local attrition", "eight years", "steppe power"):
        if want not in towers:
            problems.append(f"the towers text lacks {want!r}")
    patrols = loc_value(loc, "rip_send_out_the_patrols_desc") or ""
    for want in ("five years", "+0.5 attrition", "10% faster", "5%"):
        if want not in patrols:
            problems.append(f"the patrols text lacks {want!r}")
    settle = loc_value(loc, "rip_settle_the_watch_desc") or ""
    for want in ("+25% local manpower", "+10% local defensiveness", "-15% local tax", "twenty years", "steppe power"):
        if want not in settle:
            problems.append(f"the settlement text lacks {want!r}")
    if "§Y10§!" not in (loc_value(loc, COOLDOWN_DESC) or ""):
        problems.append("the cooldown text does not name ten years")
    for key, days in (("rip_post_the_watchtowers_tt", 2920), ("rip_settle_the_watch_tt", 7300)):
        words = {2920: "eight years", 7300: "twenty years"}[days]
        if words not in (loc_value(loc, key) or ""):
            problems.append(f"{key} does not say {words}")
    return problems


def check_localisation():
    problems = []
    keys = [f"ability_{MECHANIC}", COOLDOWN_DESC, "rip_watch_exposed_province_tt", "rip_watch_unsettled_province_tt",
            "rip_post_the_watchtowers_tt", "rip_settle_the_watch_tt"]
    for name in BUTTONS:
        keys += [name, f"{name}_desc"]
    for name in MODIFIERS:
        keys += [name, f"desc_{name}"]
    english = loc_text("english")
    for language in LANGUAGES:
        text = loc_text(language)
        if not text:
            problems.append(f"{language}: no localisation file")
            continue
        for key in keys:
            value = loc_value(text, key)
            if value is None:
                problems.append(f"{language}: missing {key}")
            elif language != "english" and value != loc_value(english, key):
                problems.append(f"{language}: {key} differs from the English source (run tools/build_border_mechanics_localisation.py)")
    return problems


def check_sprites():
    problems, seen = [], []
    gfx = read(GFX)
    for name, (_, sprite, _, _, _) in BUTTONS.items():
        match = re.search(rf'name = "{sprite}" texturefile = "([^"]+)"', gfx)
        if not match:
            problems.append(f"{GFX} does not define {sprite}")
            continue
        info = read_dds(ROOT / match.group(1))
        if info is None:
            problems.append(f"{match.group(1)} is missing or not a DDS file")
            continue
        width, height, bits, pixels = info
        if (width, height, bits) != (82, 82, 32):
            problems.append(f"{match.group(1)} is {width}x{height} at {bits} bits, expected 82x82 uncompressed 32 bit")
        alpha = pixels[3::4]
        if min(alpha) == max(alpha) or 0 not in alpha:
            problems.append(f"{match.group(1)} has no shaped alpha")
        seen.append(bytes(pixels))
    if len(set(seen)) != len(seen):
        problems.append("two of the three button sprites are the same picture")
    return problems


def check_typed_calls(scripts):
    """A province modifier is called only through the province API, the country modifier only through the country API."""
    problems = []
    for name, (_, _, scope, modifier, _) in BUTTONS.items():
        for path, text in scripts.items():
            if modifier not in text:
                continue
            bad = "country_modifier" if scope == "province" else "province_modifier"
            if re.search(rf"{bad}\s*=\s*\{{[^}}]*?name\s*=\s*{modifier}\b", text) or re.search(rf"{bad}\s*=\s*{modifier}\b", text):
                problems.append(f"{modifier} is called through the {bad} API in {path}")
    return problems


def run_checks(s):
    problems = []
    problems += check_reforms(s["prl"], s["pdl"], s["all_reforms"])
    problems += check_mechanic(s["mech"])
    problems += check_triggers_and_effects(s["triggers"], s["effects"], s["church"])
    problems += check_sweep(s["on_actions"])
    problems += check_modifiers(s["modifiers"], s["loc"])
    problems += check_raid(s["raid"])
    problems += check_text(s["loc"], s["mech"])
    problems += check_typed_calls(s["scripts"])
    return problems


def sources():
    scripts = {}
    for sub in ("common/government_mechanics", "common/scripted_effects", "events", "common/government_reforms"):
        for path in (ROOT / sub).rglob("*.txt"):
            scripts[path.relative_to(ROOT).as_posix()] = re.sub(r"#[^\n]*", "", path.read_text(encoding="cp1252", errors="replace"))
    reform_dir = ROOT / "common/government_reforms"
    return {
        "prl": read("common/government_reforms/RIP_PRL_government_reforms.txt"),
        "pdl": read("common/government_reforms/RIP_PDL_government_reforms.txt"),
        "all_reforms": "\n".join(p.read_text(encoding="cp1252", errors="replace") for p in sorted(reform_dir.glob("*.txt"))),
        "mech": read(MECH_FILE),
        "triggers": read("common/scripted_triggers/rip_border_watch_triggers.txt"),
        "effects": read("common/scripted_effects/rip_border_watch_effects.txt"),
        "on_actions": read("common/on_actions/rip_reform_mechanics_on_actions.txt"),
        "church": read("common/scripted_triggers/rip_church_policy_triggers.txt"),
        "modifiers": read("common/event_modifiers/rip_border_watch_modifiers.txt"),
        "raid": read("events/SteppeRaiding.txt"),
        "loc": loc_text("english"),
        "scripts": scripts,
    }


# --------------------------------------------------------------------------
# Self-test: planted violations
# --------------------------------------------------------------------------

def planted():
    """(label, source key, old, new) - each must make run_checks report something."""
    return [
        ("available uses the scripted trigger", "mech", "available = {\n\t\tOR = {\n\t\t\thas_reform = prl_border_fortress_reform\n\t\t\thas_reform = pdl_carpathian_bastion_reform\n\t\t}\n\t}", "available = {\n\t\trip_border_watch_held = yes\n\t}"),
        ("towers cost 40", "mech", "\t\t\teffect = {\n\t\t\t\tadm_power_cost = 50", "\t\t\teffect = {\n\t\t\t\tadm_power_cost = 40"),
        ("shared token dropped", "mech", f"cooldown_token = {TOKEN}", "cooldown_token = a_private_token"),
        ("cooldown 5 years", "mech", "cooldown_years = 10", "cooldown_years = 5"),
        ("towers last twenty years", "mech", "duration = 2920", "duration = 7300"),
        ("keyed on the tag", "mech", "rip_border_watch_held = yes\n\t\t\t\tmil_power_cost = 50", "tag = PDL\n\t\t\t\tmil_power_cost = 50"),
        ("a raw flag in a trigger", "mech", "NOT = { has_country_modifier = rip_steppe_patrols }", "has_country_flag = some_flag"),
        ("a second panel for Podillia's policy", "mech", "add_country_modifier = {\n\t\t\t\t\tname = rip_steppe_patrols", "add_country_modifier = {\n\t\t\t\t\tname = pdl_defense_funded"),
        ("towers without the tooltip wrapper", "mech", "custom_trigger_tooltip = {\n\t\t\t\t\ttooltip = rip_watch_exposed_province_tt\n\t\t\t\t\tany_owned_province = { rip_watch_exposed_province = yes }\n\t\t\t\t}", "any_owned_province = { rip_watch_exposed_province = yes }"),
        ("tower line without remove-then-add", "mech", "if = {\n\t\t\t\t\t\t\tlimit = { has_province_modifier = rip_watchtower_line }\n\t\t\t\t\t\t\tremove_province_modifier = rip_watchtower_line\n\t\t\t\t\t\t}\n", ""),
        ("settlement may run in a war", "mech", "factor = 0\n\t\t\t\t\tis_at_war = yes", "factor = 2\n\t\t\t\t\tis_at_war = yes"),
        ("two buttons share an icon", "mech", "icon = GFX_rip_watch_settlers", "icon = GFX_rip_watch_towers"),
        ("a bar added", "mech", "interactions = {", "powers = { x = { } }\n\tinteractions = {"),
        ("steppe power drifts from the church", "triggers", "has_reform = steppe_horde\n\t\ttechnology_group = nomad_group", "has_reform = steppe_horde"),
        ("exposed city drops is_city", "triggers", "\tis_city = yes\n", ""),
        ("clear-up forgets the patrols", "effects", "remove_country_modifier = rip_steppe_patrols", "add_prestige = 0"),
        ("tower modifier numbers", "modifiers", "local_defensiveness = 0.2\n\tlocal_hostile_attrition = 1", "local_defensiveness = 0.5\n\tlocal_hostile_attrition = 1"),
        ("patrols made local", "modifiers", "hostile_attrition = 0.5\n\tmovement_speed = 0.1\n\tland_maintenance_modifier = 0.05", "local_hostile_attrition = 0.5\n\tmovement_speed = 0.1\n\tland_maintenance_modifier = 0.05"),
        ("raid hook removed for the settled watch", "raid", "has_province_modifier = rip_settled_watch\n\t\t\t\t\t\t\thas_province_modifier = glinski", "has_province_modifier = glinski"),
        ("raid hook removed for the patrols", "raid", "\t\t\t\t\t\t\t\thas_country_modifier = rip_steppe_patrols\n", ""),
        ("PRL passive bundle changed", "prl", "fort_maintenance_modifier = -0.15\n\t\tdefensiveness = 0.2\n\t}\n\tgovernment_abilities", "fort_maintenance_modifier = -0.3\n\t\tdefensiveness = 0.2\n\t}\n\tgovernment_abilities"),
        ("the frontier path gets a second panel", "pdl", "government_abilities = {\n\t\tcossacks_mechanic\n\t}", "government_abilities = {\n\t\tcossacks_mechanic\n\t\trip_border_watch_mechanic\n\t}"),
        ("removed_effect lost", "pdl", "rip_border_watch_clear_effect = yes", "add_prestige = 0"),
        ("the patrols order forgets the flag", "mech", "hidden_effect = { set_country_flag = rip_border_watch_laid }", "hidden_effect = { add_prestige = 0 }"),
        ("the clear-up leaves the flag", "effects", "\tclr_country_flag = rip_border_watch_laid\n", ""),
        ("the sweep ignores the reforms", "effects", "NOT = { rip_border_watch_held = yes }", "always = yes"),
        ("the yearly hook is lost", "on_actions", "rip_border_watch_sweep_effect = yes", "add_prestige = 0"),
        ("text number drifts", "loc", "+20% local defensiveness", "+30% local defensiveness"),
        ("text cost drifts", "loc", "Spend 50 military power to send riders", "Spend 40 military power to send riders"),
    ]


def self_test(base):
    stale, missed, caught = [], [], 0
    for label, key, old, new in planted():
        text = base[key].replace("\r\n", "\n")
        if old not in text:
            stale.append(label)
            continue
        mutated = dict(base)
        mutated[key] = text.replace(old, new, 1)
        if key == "mech":
            mutated["scripts"] = dict(base["scripts"])
            mutated["scripts"][MECH_FILE] = mutated[key]
        if run_checks(mutated):
            caught += 1
        else:
            missed.append(label)
    if stale or missed:
        raise AssertionError(f"self-test: stale planted violations {stale}; not caught {missed}")
    return caught


def main():
    base = sources()
    problems = run_checks(base)
    problems += check_localisation()
    problems += check_sprites()
    if problems:
        print("BORDER WATCH CHECK: FAIL")
        for problem in problems:
            print("  -", problem)
        return 1
    caught = self_test({k: (v.replace("\r\n", "\n") if isinstance(v, str) else v) for k, v in base.items()})
    print(f"BORDER WATCH PASS: two carriers and no other, plain available, three buttons priced 50 on one ten-year token, "
          f"raid hook in steppe_raid.2 only, steppe power equals the church's, three modifiers, sprites, 4 languages; "
          f"{caught} planted violations caught")
    print("LIMIT: static contracts. In EU4 1.37.5 the load, the fixture battery, the exact trigger and effect bodies of the three "
          "buttons on a city next to a steppe power, removed_effect (it runs on remove_government_reform, not on a government "
          "swap) and the yearly sweep (called directly) were measured (docs/BORDER_MECHANICS_20261019.uk.md, section 7); button "
          "tooltips, the sweep on a real yearly pulse, raid outcomes, AI choices and campaign balance were not.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
