"""Contracts for the Carpathian Captaincy: the UZH reform and its button-only mechanic.

Static checks over script, sprites and localisation. They prove the files agree with each other and with
the design written in docs/BORDER_MECHANICS_20261019.uk.md; they do not prove the engine draws the panel.
What was measured in EU4 1.37.5 (a load without a single new error.log line) is in that document.

  * uzh_carpathian_captaincy_reform sits at M5 and R5 (military_doctrines) and nowhere else, is shown only
    to UZH and to a holder (the documented tighter potential), carries exactly the passive bundle of the
    design and the mechanic, and its removed_effect ends the posts and the Opryshky but NOT the salt pledge
    (through uzh_captaincy_clear_effect, which a yearly sweep also calls for a country that lost the reform by a
    change of government type, where removed_effect does not run).
  * The mechanic has three buttons, one per monarch power (military, administrative, diplomatic), each paid
    50 in both trigger and effect, all on one ten-year cooldown token with a named cooldown, keyed on the
    reform and never on the tag, with no powers, no .gui, no else/else_if and no raw flag in a trigger.
  * The three orders last 7, 10 and 7 years: neither of the two buffs is up more than 70% of the time.
  * Every number the English text states is the number the script applies.
  * The three modifiers exist in the UZH modifier file with the designed numbers and a name and a
    description; the Opryshky Uprising disaster carries a damper for the enlisted Opryshky.
  * Three 82x82 sprites and the 57x57 reform card are defined, exist, differ, and are not vanilla's.
  * Everything the player can read has text in English, French, German and Spanish.

Standard library only. Self-test: twenty-six planted violations must each be caught.
"""
import re
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from clausewitz_testlib import ROOT, read, named_block, matching_brace, normalized, _mask_comments_and_strings  # noqa: E402

LANGUAGES = ("english", "french", "german", "spanish")
REFORM = "uzh_carpathian_captaincy_reform"
MECHANIC = "uzh_carpathian_captaincy_mechanic"
MECH_FILE = "common/government_mechanics/rip_uzh_carpathian_captaincy.txt"
REFORM_FILE = "common/government_reforms/RIP_UZH_government_reforms.txt"
GFX = "interface/rip_captaincy_icons.gfx"
EN_LOC = "localisation/rip_border_mechanics_l_english.yml"
TOKEN = "uzh_carpathian_captaincy_session"
COOLDOWN_DESC = "uzh_carpathian_captaincy_session_cd"

# button -> (power, sprite, modifier, duration in days)
BUTTONS = {
    "uzh_man_the_border_posts": ("mil", "GFX_rip_captaincy_posts", "uz_captaincy_posts_manned", 2555),
    "uzh_pledge_the_salt_chambers": ("adm", "GFX_rip_captaincy_salt", "uz_captaincy_salt_pledged", 3650),
    "uzh_enlist_the_opryshky": ("dip", "GFX_rip_captaincy_opryshky", "uz_captaincy_opryshky_enlisted", 2555),
}
MODIFIERS = {
    "uz_captaincy_posts_manned": {"hostile_attrition": "1", "garrison_size": "0.25", "land_maintenance_modifier": "0.05"},
    "uz_captaincy_salt_pledged": {"global_tax_modifier": "-0.1"},
    "uz_captaincy_opryshky_enlisted": {"land_maintenance_modifier": "-0.1", "movement_speed": "0.1", "global_unrest": "1"},
}
PASSIVE = {"global_manpower_modifier": "0.1", "governing_capacity_modifier": "-0.05"}
SALT_LUMP = "0.4"
COOLDOWN_YEARS = 10
MAX_UPTIME = 0.7


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
    """The text between the outer braces of a block."""
    return block[block.index("{") + 1: block.rindex("}")]


def loc_text(language, extra=None):
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
    masks = struct.unpack("<4I", data[92:108])
    return width, height, bits, masks, data[128:]


def block_of(text, name):
    """A reform or modifier block by name, '' when absent."""
    try:
        return named_block(text, name)
    except Exception:
        return ""


# --------------------------------------------------------------------------
# Checks: each returns a list of problems, so a planted violation can be caught
# --------------------------------------------------------------------------

def check_reform(reform_text, governments):
    problems = []
    block = block_of(reform_text, REFORM)
    if not block:
        return [f"{REFORM} is not defined"]
    n = normalized(block)
    potential = normalized(block_of(block, "potential"))
    trigger = normalized(block_of(block, "trigger"))
    gate = f"potential = {{ OR = {{ has_reform = {REFORM} tag = UZH }} }}"
    if potential != gate:
        problems.append(f"potential must be exactly OR(has_reform self, tag = UZH), found: {potential}")
    if trigger != f"trigger = {{ OR = {{ has_reform = {REFORM} tag = UZH }} }}":
        problems.append(f"trigger must be exactly OR(has_reform self, tag = UZH), found: {trigger}")
    modifiers = dict(re.findall(r"(\w+)\s*=\s*(-?[\d.]+)", body(block_of(block, "modifiers"))))
    if modifiers != PASSIVE:
        problems.append(f"passive bundle is {modifiers}, the design is {PASSIVE}")
    abilities = re.findall(r"\w+", body(block_of(block, "government_abilities")))
    if abilities != [MECHANIC]:
        problems.append(f"government_abilities is {abilities}, expected [{MECHANIC}]")
    removed = body(block_of(block, "removed_effect"))
    if normalized(removed) != "hidden_effect = { uzh_captaincy_clear_effect = yes }":
        problems.append(f"removed_effect must be exactly hidden_effect = {{ uzh_captaincy_clear_effect = yes }}, found: {normalized(removed)}")
    if "uz_captaincy_salt_pledged" in removed:
        problems.append("removed_effect lifts the salt pledge: a debt must not vanish with the reform")
    for key, want in (("allow_normal_conversion", "no"), ("valid_for_nation_designer", "no"), ("valid_for_new_country", "no")):
        if f"{key} = {want}" not in n:
            problems.append(f"{key} = {want} is missing")
    if not re.search(r'icon = "rip_gfx_reform_uzh_carpathian_captaincy_icon"', block):
        problems.append("the reform card does not use its own icon")

    # tiers: military_doctrines of monarchy and republic, and nowhere else
    homes = []
    for government in ("monarchy", "republic", "theocracy", "tribal", "native"):
        levels = block_of(named_block(governments, government), "reform_levels")
        for number, (_, tier) in enumerate(children(levels), 1):
            if re.search(rf"\b{REFORM}\b", re.sub(r"#[^\n]*", "", tier)):
                homes.append(f"{government}:{number}")
    if homes != ["monarchy:5", "republic:5"]:
        problems.append(f"registered at {homes}, expected monarchy:5 and republic:5 (military_doctrines)")
    return problems


def check_buttons(mech):
    problems = []
    found = interactions(mech)
    names = [name for name, _ in found]
    if names != list(BUTTONS):
        return [f"buttons are {names}, expected {list(BUTTONS)}"]
    plain = re.sub(r"#[^\n]*", "", mech)
    for forbidden, why in (("tag = UZH", "the mechanic must key on the reform, not the tag"),
                           ("powers = {", "no parallel militarisation resource (docs/REGIONAL_REFORM_AUDIT.uk.md)"),
                           ("gui =", "no own window: the default mechanic list draws the buttons"),
                           ("else = {", "else/else_if bodies drop effects in 1.37.5"),
                           ("else_if", "else/else_if bodies drop effects in 1.37.5"),
                           ("has_country_flag", "a blocked button would show the raw flag name"),
                           ("has_dlc", "the sibling mechanics carry no DLC gate")):
        if forbidden in plain:
            problems.append(f"{forbidden!r} in the mechanic: {why}")
    if not re.search(rf"available = \{{\s*has_reform = {REFORM}\s*\}}", plain):
        problems.append("available is not exactly has_reform = the reform")
    powers_seen = set()
    icons = []
    for name, block in found:
        power, sprite, modifier, days = BUTTONS[name]
        trig, eff = named_block(block, "trigger"), named_block(block, "effect")
        icon = re.search(r"(?m)^\s*icon\s*=\s*(\w+)", block)
        icons.append(icon.group(1) if icon else None)
        if icons[-1] != sprite:
            problems.append(f"{name} uses {icons[-1]}, expected {sprite}")
        if not normalized(trig).startswith(f"trigger = {{ has_reform = {REFORM}"):
            problems.append(f"{name}: the trigger does not open with has_reform = the reform")
        for label, part in (("trigger", trig), ("effect", eff)):
            cost = re.findall(rf"\b(mil|adm|dip)_power_cost = (\d+)", part)
            if cost != [(power, "50")]:
                problems.append(f"{name}: {label} cost is {cost}, expected [{power}_power_cost = 50]")
        powers_seen.add(power)
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
        uptime = days / (COOLDOWN_YEARS * 365)
        if name != "uzh_pledge_the_salt_chambers" and uptime > MAX_UPTIME + 1e-9:
            problems.append(f"{name}: the buff is up {uptime:.0%} of the time, over {MAX_UPTIME:.0%}")
    if powers_seen != {"mil", "adm", "dip"}:
        problems.append(f"the three buttons spend {sorted(powers_seen)}, expected one each of mil, adm, dip")
    if len(set(icons)) != len(icons):
        problems.append("two buttons share an icon")
    if any(i and i.startswith("GFX_cossacks_ability_") for i in icons):
        problems.append("a button still borrows vanilla's Cossack ability icon")

    # the salt button: a loan, only with a salt province, only when short of money for the AI
    salt = dict(found)["uzh_pledge_the_salt_chambers"]
    salt_trigger = named_block(salt, "trigger")
    if not re.search(r"custom_trigger_tooltip = \{\s*tooltip = uzh_captaincy_salt_province_tt\s*any_owned_province = \{ trade_goods = salt \}\s*\}", salt_trigger):
        problems.append("the salt button does not gate on a salt province through custom_trigger_tooltip")
    if f"add_years_of_income = {SALT_LUMP}" not in named_block(salt, "effect"):
        problems.append(f"the salt advance is not {SALT_LUMP} of a year's income")
    ai = normalized(named_block(salt, "ai_chance"))
    if "is_in_deficit = yes" not in ai or "num_of_loans = 1" not in ai or "factor = 0" not in ai:
        problems.append("the salt button's AI is not limited to a realm short of money")

    # the Opryshky: manpower, nobles guarded by has_estate, raids ended, damper on the disaster
    opr = named_block(dict(found)["uzh_enlist_the_opryshky"], "effect")
    if "add_manpower = 2" not in opr:
        problems.append("the Opryshky do not bring 2 (thousand) recruits")
    if not re.search(r"if = \{\s*limit = \{ has_estate = estate_nobles \}\s*add_estate_loyalty = \{\s*estate = estate_nobles\s*loyalty = -5\s*\}\s*\}", opr):
        problems.append("the noble loyalty price is not guarded by has_estate = estate_nobles")
    if not re.search(r"hidden_effect = \{\s*remove_country_modifier = uz_opryshky_raids\s*\}", opr):
        problems.append("the Opryshky do not end the raids quietly (hidden_effect)")
    return problems


def check_cleanup(effects, on_actions):
    """Lifecycle: the posts and the Opryshky end with the reform, the salt pledge does not, and a country that lost the
    reform without removed_effect running (a change of government type, measured in EU4 1.37.5) is cleared once a year."""
    problems = []
    clear = block_of(effects, "uzh_captaincy_clear_effect")
    if not clear:
        return ["uzh_captaincy_clear_effect is not defined"]
    for name in ("uz_captaincy_posts_manned", "uz_captaincy_opryshky_enlisted"):
        if f"remove_country_modifier = {name}" not in clear:
            problems.append(f"uzh_captaincy_clear_effect does not end {name}")
    if "uz_captaincy_salt_pledged" in clear:
        problems.append("uzh_captaincy_clear_effect lifts the salt pledge: a debt must not vanish with the reform")
    sweep = normalized(block_of(effects, "uzh_captaincy_sweep_effect"))
    want = ("uzh_captaincy_sweep_effect = { if = { limit = { OR = { has_country_modifier = uz_captaincy_posts_manned "
            "has_country_modifier = uz_captaincy_opryshky_enlisted } NOT = { has_reform = uzh_carpathian_captaincy_reform } } "
            "uzh_captaincy_clear_effect = yes } }")
    if sweep != want:
        problems.append(f"uzh_captaincy_sweep_effect is {sweep}, expected the modifier look-ups and the reform test only")
    if re.search(r"\belse(_if)?\b", re.sub(r"#[^\n]*", "", effects)):
        problems.append("else/else_if in the clean-up effects: bodies drop effects in 1.37.5")
    yearly = normalized(block_of(on_actions, "on_yearly_pulse"))
    if "uzh_captaincy_sweep_effect = yes" not in yearly:
        problems.append("on_yearly_pulse does not call uzh_captaincy_sweep_effect")
    return problems


def check_modifiers(modifier_text, disasters, loc):
    problems = []
    for name, want in MODIFIERS.items():
        block = block_of(modifier_text, name)
        if not block:
            problems.append(f"modifier {name} is missing from RIP_UZH_modifiers.txt")
            continue
        have = dict(re.findall(r"(\w+)\s*=\s*(-?[\d.]+)", body(block)))
        if have != want:
            problems.append(f"{name} is {have}, the design is {want}")
        for key in (name, f"desc_{name}"):
            if loc_value(loc, key) is None:
                problems.append(f"no English text for {key}")
    damper = re.search(r"modifier = \{\s*factor = (-[\d.]+)\s*has_country_modifier = uz_captaincy_opryshky_enlisted\s*\}", disasters)
    if not damper or damper.group(1) != "-0.25":
        problems.append("the Opryshky Uprising has no -0.25 damper for the enlisted Opryshky")
    return problems


def check_text(loc, mech):
    """Every number the English text states is the number the script applies."""
    problems = []
    found = dict(interactions(mech))
    posts = loc_value(loc, "uzh_man_the_border_posts_desc") or ""
    salt = loc_value(loc, "uzh_pledge_the_salt_chambers_desc") or ""
    opr = loc_value(loc, "uzh_enlist_the_opryshky_desc") or ""
    for label, text, power in (("posts", posts, "military"), ("salt", salt, "administrative"), ("opryshky", opr, "diplomatic")):
        if f"Spend 50 {power} power" not in text:
            problems.append(f"the {label} text does not state the cost: 50 {power} power")
        if "ten-year cooldown" not in text:
            problems.append(f"the {label} text does not state the shared ten-year cooldown")
    for want in ("seven years", "+1 attrition", "a quarter", "by 5%"):
        if want not in posts:
            problems.append(f"the posts text lacks {want!r}")
    for want in ("40% of a year's income", "falls by 10% for ten years", "salt"):
        if want not in salt:
            problems.append(f"the salt text lacks {want!r}")
    for want in ("2,000 recruits", "seven years", "10% lower land maintenance", "10% faster", "+1 unrest", "5 points of noble loyalty", "Opryshky Uprising"):
        if want not in opr:
            problems.append(f"the Opryshky text lacks {want!r}")
    cd = loc_value(loc, COOLDOWN_DESC) or ""
    if "§Y10§!" not in cd:
        problems.append("the cooldown text does not name ten years")
    if f"add_years_of_income = {SALT_LUMP}" not in named_block(found["uzh_pledge_the_salt_chambers"], "effect"):
        problems.append("text says 40% of a year's income but the script advances something else")
    return problems


def check_localisation():
    problems = []
    keys = ["uzh_carpathian_captaincy_reform", "uzh_carpathian_captaincy_reform_desc", f"ability_{MECHANIC}",
            COOLDOWN_DESC, "uzh_captaincy_salt_province_tt"]
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
    desc = loc_value(english, "uzh_carpathian_captaincy_reform_desc") or ""
    if "!" in desc:
        problems.append("the reform description carries an exclamation mark (docs/STYLE_GLOSSARY.md, section 3)")
    return problems


def check_sprites():
    problems = []
    gfx = read(GFX)
    seen = []
    for name, (_, sprite, _, _) in BUTTONS.items():
        match = re.search(rf'name = "{sprite}" texturefile = "([^"]+)"', gfx)
        if not match:
            problems.append(f"{GFX} does not define {sprite}")
            continue
        info = read_dds(ROOT / match.group(1))
        if info is None:
            problems.append(f"{match.group(1)} is missing or not a DDS file")
            continue
        width, height, bits, masks, pixels = info
        if (width, height, bits) != (82, 82, 32):
            problems.append(f"{match.group(1)} is {width}x{height} at {bits} bits, expected 82x82 uncompressed 32 bit")
        alpha = pixels[3::4]
        if min(alpha) == max(alpha) or 0 not in alpha:
            problems.append(f"{match.group(1)} has no shaped alpha")
        seen.append(pixels)
    if len({bytes(p) for p in seen}) != len(seen):
        problems.append("two of the three button sprites are the same picture")
    card = re.search(r'name = "government_reform_rip_gfx_reform_uzh_carpathian_captaincy_icon" texturefile = "([^"]+)" norefcount = yes', gfx)
    if not card:
        problems.append("the reform card sprite is not defined with norefcount")
    else:
        info = read_dds(ROOT / card.group(1))
        if info is None or info[:3] != (57, 57, 32):
            problems.append("the reform card sprite is not a 57x57 32 bit DDS")
    return problems


def run_checks(s):
    problems = []
    problems += check_reform(s["reforms"], s["governments"])
    problems += check_buttons(s["mech"])
    problems += check_cleanup(s["effects"], s["on_actions"])
    problems += check_modifiers(s["modifiers"], s["disasters"], s["loc"])
    problems += check_text(s["loc"], s["mech"])
    return problems


def sources():
    return {
        "reforms": read(REFORM_FILE),
        "governments": read("common/governments/00_governments.txt"),
        "mech": read(MECH_FILE),
        "effects": read("common/scripted_effects/rip_uzh_captaincy_effects.txt"),
        "on_actions": read("common/on_actions/rip_reform_mechanics_on_actions.txt"),
        "modifiers": read("common/event_modifiers/RIP_UZH_modifiers.txt"),
        "disasters": read("common/disasters/uzh_disasters.txt"),
        "loc": loc_text("english"),
    }


# --------------------------------------------------------------------------
# Self-test: planted violations
# --------------------------------------------------------------------------

def planted(base):
    """(label, key of the source to damage, old, new) - each must make run_checks report something."""
    return [
        ("posts cost 40", "mech", "\t\t\teffect = {\n\t\t\t\tmil_power_cost = 50", "\t\t\teffect = {\n\t\t\t\tmil_power_cost = 40"),
        ("shared token dropped", "mech", f"cooldown_token = {TOKEN}", "cooldown_token = a_private_token"),
        ("cooldown 5 years", "mech", "cooldown_years = 10", "cooldown_years = 5"),
        ("posts last ten years", "mech", "duration = 2555", "duration = 3650"),
        ("keyed on the tag", "mech", "has_reform = uzh_carpathian_captaincy_reform\n\t\t\t\tdip_power_cost = 50", "tag = UZH\n\t\t\t\tdip_power_cost = 50"),
        ("an else branch", "mech", "\t\t\t\tadd_manpower = 2\n", "\t\t\t\tadd_manpower = 2\n\t\t\t\tif = { limit = { always = yes } } else = { add_prestige = 1 }\n"),
        ("a raw flag in a trigger", "mech", "NOT = { has_country_modifier = uz_captaincy_posts_manned }", "has_country_flag = some_flag"),
        ("a bar added", "mech", "interactions = {", "powers = { x = { } }\n\tinteractions = {"),
        ("salt without the tooltip wrapper", "mech", "custom_trigger_tooltip = {\n\t\t\t\t\ttooltip = uzh_captaincy_salt_province_tt\n\t\t\t\t\tany_owned_province = { trade_goods = salt }\n\t\t\t\t}", "any_owned_province = { trade_goods = salt }"),
        ("salt advance changed", "mech", "add_years_of_income = 0.4", "add_years_of_income = 0.9"),
        ("noble loyalty unguarded", "mech", "limit = { has_estate = estate_nobles }", "limit = { always = yes }"),
        ("opryshky raids visible", "mech", "hidden_effect = {\n\t\t\t\t\tremove_country_modifier = uz_opryshky_raids\n\t\t\t\t}", "remove_country_modifier = uz_opryshky_raids"),
        ("two buttons share an icon", "mech", "icon = GFX_rip_captaincy_opryshky", "icon = GFX_rip_captaincy_salt"),
        ("posts modifier numbers", "modifiers", "garrison_size = 0.25", "garrison_size = 0.5"),
        ("salt modifier numbers", "modifiers", "global_tax_modifier = -0.1\n}\n\nuz_captaincy_opryshky", "global_tax_modifier = -0.3\n}\n\nuz_captaincy_opryshky"),
        ("damper removed", "disasters", "has_country_modifier = uz_captaincy_opryshky_enlisted", "has_country_modifier = uz_amnesty_rollout"),
        ("potential widened", "reforms", "potential = {\n\t\tOR = {\n\t\t\thas_reform = uzh_carpathian_captaincy_reform\n\t\t\ttag = UZH\n\t\t}\n\t}", "potential = {\n\t\tuzh_carpathian_captaincy_reform_visible = yes\n\t}"),
        ("passive bundle changed", "reforms", "global_manpower_modifier = 0.1\n\t\tgoverning_capacity_modifier = -0.05\n\t}\n\tcustom_attributes = {\n\t\tlocked_government_type = yes\n\t}\n\tgovernment_abilities = {\n\t\tuzh_carpathian_captaincy_mechanic", "global_manpower_modifier = 0.3\n\t\tgoverning_capacity_modifier = -0.05\n\t}\n\tcustom_attributes = {\n\t\tlocked_government_type = yes\n\t}\n\tgovernment_abilities = {\n\t\tuzh_carpathian_captaincy_mechanic"),
        ("salt debt lifted on removal", "effects", "\t\tremove_country_modifier = uz_captaincy_opryshky_enlisted\n\t}\n}", "\t\tremove_country_modifier = uz_captaincy_opryshky_enlisted\n\t}\n\tremove_country_modifier = uz_captaincy_salt_pledged\n}"),
        ("the Opryshky outlive the reform", "effects", "\t\tremove_country_modifier = uz_captaincy_opryshky_enlisted\n", "\t\tadd_prestige = 0\n"),
        ("removed_effect no longer clears", "reforms", "uzh_captaincy_clear_effect = yes", "add_prestige = 0"),
        ("the sweep ignores the reform", "effects", "NOT = { has_reform = uzh_carpathian_captaincy_reform }", "always = yes"),
        ("the yearly hook is lost", "on_actions", "uzh_captaincy_sweep_effect = yes", "add_prestige = 0"),
        ("tier lost", "governments", "\t\t\t\t# RIP - the Carpathian march\n\t\t\t\tuzh_carpathian_captaincy_reform\n\t\t\t\t# RIP - the Grand Duchy reworked", "\t\t\t\t# RIP - the Grand Duchy reworked"),
        ("text number drifts", "loc", "10% lower land maintenance", "20% lower land maintenance"),
        ("text cost drifts", "loc", "Spend 50 diplomatic power to pardon", "Spend 40 diplomatic power to pardon"),
    ]


def self_test(base):
    stale, missed, caught = [], [], 0
    for label, key, old, new in planted(base):
        text = base[key].replace("\r\n", "\n")
        if old not in text:
            stale.append(label)
            continue
        mutated = dict(base)
        mutated[key] = text.replace(old, new, 1)
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
        print("CARPATHIAN CAPTAINCY CHECK: FAIL")
        for problem in problems:
            print("  -", problem)
        return 1
    caught = self_test({k: v.replace("\r\n", "\n") for k, v in base.items()})
    print(f"CARPATHIAN CAPTAINCY PASS: reform at M5/R5, three buttons priced 50 on one ten-year token, uptime <= 70%, "
          f"text equals script, three modifiers, damper, sprites, 4 languages; {caught} planted violations caught")
    print("LIMIT: static contracts. In EU4 1.37.5 the load, the fixture battery, the exact trigger and effect bodies of the three "
          "buttons, removed_effect (it runs on remove_government_reform, not on a government swap) and the yearly sweep (called "
          "directly) were measured (docs/BORDER_MECHANICS_20261019.uk.md, section 7); button tooltips, the sweep on a real yearly "
          "pulse, AI choices and campaign balance were not.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
