"""Contracts for the Galician Crown Ordinances and the Incorporated Appanage.

Static checks over script and localisation. They prove the sources agree with each
other and with the installed vanilla; they do not run EU4 triggers. What was measured
in the game (one on_action key defined in many files runs every definition) is kept
in diagnostics/hlc_ordinances_20261017/on_action_merge_probe.txt and only its
numbers are read here.

  * LAYOUT  exactly six buttons, two rows of three, six DIFFERENT ordinances: chancery,
            settlement, cadastral on top; urbarial, toleration, frontier guard below.
            The author asked for six abilities. An earlier layout gave three ordinances an
            enact and a rescind button apiece - the same three pictures twice, which the
            author did not accept as six - and a later one folded each pair into one toggle.
            Both are defects to this test: there is no rescind button and no toggle.
  * PRICE   each button checks and pays 50 monarch power of the right kind and adds a
            ten-year country modifier; nothing is paid or set outside the effect.
  * TERM    the modifier (3650 days) is the only record of "in force": no flag is set, and
            the button is blocked while its modifier stands, in a sentence tooltip.
  * SLOTS   at most three of the six in force: every button requires
            hlc_ordinance_slot_free inside a custom_trigger_tooltip with a sentence.
  * NO COOLDOWN  every button says cooldown_years = 0 and has no cooldown_token or cooldown_desc: seen in
            EU4 1.37.5 (2026-10-22) that enacting one ordinance put its "can only be used once every 10
            years" line on the other five and greyed all six, whatever their tokens - the term is the
            modifier alone.
  * AI      each button has a real ai_chance; the AI enacts what its realm needs; the
            situations are defined, used, and made of names the installed vanilla has.
  * CLEAN-UP  removed_effect hands over to one effect that clears the six modifiers (and the
            flags of the older permanent ordinances); a yearly sweep calls it for any country
            that holds them without the crown authority and moves an older save's permanent
            ordinances onto the ten-year term; the sweep is made of look-ups only.
  * ON_ACTION  the settlement hook is one definition of a key that 00_on_actions.txt
            also defines, the mod's copy keeps the five vanilla handlers, and the
            measured merge rule is on record.
  * LOYALTY  the settlement gift goes to the nobles only, below a ceiling, once a year
            by a hidden timer, and only while the settlement modifier stands.
  * APPANAGE  the chain attribute -> trigger -> action -> subject type -> privilege has
            a producer for every reader, the action is guarded and its AI decides, and
            every text quotes the numbers vanilla really applies.
  * TEXT    every new key is in the four languages and the fallbacks equal the English;
            no ordinance key is left without a reader.

planted_violations() breaks the sources in memory, one defect at a time, and requires
every break to be reported.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from clausewitz_testlib import (  # noqa: E402
    ROOT, read, named_block, keyed_blocks, matching_brace, normalized, vanilla_read, vanilla_grep,
    vanilla_root, _mask_comments_and_strings,
)

LANGUAGES = ("english", "french", "german", "spanish")
ORDINANCES = ("chancery", "settlement", "cadastral", "urbarial", "toleration", "frontier")
POWER = {"chancery": "dip", "settlement": "adm", "cadastral": "adm", "urbarial": "adm", "toleration": "dip", "frontier": "mil"}
POWER_WORD = {"dip": "diplomatic", "adm": "administrative", "mil": "military"}
MECHANIC = "hlc_austrian_reorganization_mechanic"
ENACT = {o: f"hlc_enact_{o}_ordinance" for o in ORDINANCES}
BUTTON_ORDER = [ENACT[o] for o in ORDINANCES]
ICONS = {
    ENACT["chancery"]: "GFX_rip_chancery_ordinance", ENACT["settlement"]: "GFX_rip_settlement_ordinance",
    ENACT["cadastral"]: "GFX_rip_cadastre_ordinance", ENACT["urbarial"]: "GFX_rip_urbarial_ordinance",
    ENACT["toleration"]: "GFX_rip_toleration_ordinance", ENACT["frontier"]: "GFX_rip_frontier_ordinance",
}
LEGACY_FLAGGED = ("chancery", "settlement", "cadastral")
EVIDENCE = "diagnostics/hlc_ordinances_20261017/on_action_merge_probe.txt"
VANILLA_CONVERTED_HANDLERS = (
    "on_province_culture_converted_estate_privilges_effect",
    "judaism_on_province_culture_converted_effect",
    "imperial_modifiers_on_province_change_culture_or_change_owner_effect",
    "on_province_culture_change_effect",
    "on_province_culture_converted_effect",
)
SITUATIONS = (
    "hlc_ordinance_slot_free", "hlc_ordinance_settlement_wanted", "hlc_ordinance_cadastre_wanted",
    "hlc_ordinance_urbarial_wanted", "hlc_ordinance_toleration_wanted", "hlc_ordinance_frontier_wanted",
)
# What a realm needs before the AI enacts. The chancery, the plainest ordinance, is taken as readily only when nothing else is called for.
ENACT_NEEDS = {
    "chancery": SITUATIONS[1:],
    "settlement": ("hlc_ordinance_settlement_wanted",),
    "cadastral": ("hlc_ordinance_cadastre_wanted",),
    "urbarial": ("hlc_ordinance_urbarial_wanted",),
    "toleration": ("hlc_ordinance_toleration_wanted",),
    "frontier": ("hlc_ordinance_frontier_wanted",),
}
# Names the mechanic, the AI situations and the appanage action lean on. An unknown
# name silently never matches, so each has to be something the installed game uses.
VANILLA_NAMES = (
    "num_of_owned_provinces_with", "has_owner_culture", "has_owner_accepted_culture", "has_owner_religion", "is_city",
    "estate_loyalty", "has_estate", "years_of_income", "num_of_loans", "calc_true_if", "unrest",
    "governing_capacity_percentage", "liberty_desire", "had_country_flag", "adm_tech", "is_at_war",
    "all_subject_country", "is_subject_of_type", "adm_power_cost", "dip_power_cost", "mil_power_cost",
    "has_country_modifier", "hidden_effect", "add_country_modifier", "custom_trigger_tooltip",
)
# New or reworded keys: all four languages, and the fallbacks equal the English.
NEW_KEYS = (
    "ability_hlc_austrian_reorganization_mechanic", "hlc_ordinance_slot_free_tt", "hlc_incorporate_appanage_limit_tt",
    "hlc_settlement_loyalty_timer", "desc_hlc_settlement_loyalty_timer",
) + tuple(f"hlc_enact_{o}_ordinance{suffix}" for o in ORDINANCES for suffix in ("", "_desc")) \
  + tuple(f"hlc_{o}_ordinance_modifier" for o in ORDINANCES) + tuple(f"desc_hlc_{o}_ordinance_modifier" for o in ORDINANCES) \
  + tuple(f"hlc_{o}_ordinance_not_in_force_tt" for o in ORDINANCES)
REWORDED_KEYS = (
    "hlc_incorporate_appanage_tooltip", "hlc_incorporate_appanage_desc",
    "estate_nobles_hlc_strong_appanages_desc", "estate_nobles_hlc_strong_appanages_trigger_tooltip",
    "mechanic_hlc_enables_incorporated_appanages_yes", "hlc_austrian_bureaucracy_reform_desc", "hlc_crown_authority_reform_desc",
)
RETIRED_KEYS = tuple(f"hlc_rescind_{o}_ordinance{suffix}" for o in LEGACY_FLAGGED for suffix in ("", "_desc")) \
    + tuple(f"hlc_{o}_ordinance_in_force_tt" for o in LEGACY_FLAGGED) + ("hlc_ordinance_cooldown_desc",)
# Every English key of this family has a reader in the mechanic; a key nothing reads is a leftover.
ORDINANCE_KEY = re.compile(r"^(?:hlc_enact_\w+_ordinance(?:_desc)?|hlc_\w+_ordinance_(?:not_)?in_force_tt|hlc_ordinance_\w+)$")


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


def button_list(mech):
    return children(named_block(named_block(mech, MECHANIC), "interactions"))


def buttons(mech):
    return dict(button_list(mech))


def edit_button(mech, name, change):
    """The mechanic with one button's text changed by `change`."""
    block = buttons(mech)[name]
    broken = change(block)
    assert broken != block, f"sabotage of {name} changed nothing"
    return mech.replace(block, broken, 1)


def sub_once(text, old, new, count=1):
    assert old in text, f"sabotage anchor missing: {old!r}"
    return text.replace(old, new, count)


def loc_text(language):
    return "\n".join(path.read_text(encoding="utf-8-sig")
                     for path in sorted((ROOT / "localisation").rglob(f"*l_{language}.yml")))


def loc_keys(text):
    return set(re.findall(r"(?m)^ ([^\s:#]+):\d+ ", text))


def loc_value(text, key):
    match = re.search(rf'(?m)^ {re.escape(key)}:\d+ "(.*)"\s*$', text)
    return match.group(1) if match else None


def base_factor(block):
    match = re.search(r"factor = ([0-9.]+)", normalized(block_or_empty(block, "ai_chance")))
    return float(match.group(1)) if match else None


def block_or_empty(text, name, occurrence=1):
    try:
        return named_block(text, name, occurrence)
    except KeyError:
        return ""


def replace_in_nested_block(text, path, old, new):
    """Replace a code token in a named nested block, ignoring comments and strings."""
    block = named_block(text, path[0])
    if len(path) == 1:
        match = re.search(re.escape(old), _mask_comments_and_strings(block))
        assert match, f"mutation anchor missing in {path[0]}: {old!r}"
        changed = block[:match.start()] + new + block[match.end():]
    else:
        changed = replace_in_nested_block(block, path[1:], old, new)
    assert changed != block, f"mutation of {path[0]} changed nothing"
    return text.replace(block, changed, 1)


# --------------------------------------------------------------------------
# Checks: each returns a list of problems, so a planted violation can be caught
# --------------------------------------------------------------------------

def check_layout(mech):
    """Six different buttons in the order of the two rows, each with its own sprite, and nothing that takes an ordinance back."""
    found = button_list(mech)
    names = [name for name, _ in found]
    if names != BUTTON_ORDER:
        return [f"the mechanic's buttons are {names}, expected the six different ordinances: {BUTTON_ORDER}"]
    problems = []
    icons = []
    for name, block in found:
        icon = re.search(r"(?m)^\s*icon\s*=\s*(\w+)", block)
        icons.append(icon.group(1) if icon else None)
        if not icon or icon.group(1) != ICONS[name]:
            problems.append(f"{name} wears {icon.group(1) if icon else 'no icon'}, expected {ICONS[name]}")
    if len(set(icons)) != 6:
        problems.append("two ordinance buttons wear the same picture: six abilities must look like six")
    if re.search(r"rescind|toggle", _mask_comments_and_strings(mech), re.I):
        problems.append("a rescind or toggle button is back: the crown cannot take an ordinance back, it waits it out")
    return problems


def check_price(mech):
    problems = []
    found = buttons(mech)
    for ordinance in ORDINANCES:
        power = POWER[ordinance]
        wrong = [p for p in ("adm", "dip", "mil") if p != power]
        modifier = f"hlc_{ordinance}_ordinance_modifier"
        block = found.get(ENACT[ordinance], "")
        trigger, effect = normalized(block_or_empty(block, "trigger")), normalized(block_or_empty(block, "effect"))
        if f"{power}_power_cost = 50" not in trigger:
            problems.append(f"{ordinance}: the trigger lacks {power}_power_cost = 50")
        if f"{power}_power_cost = 50" not in effect:
            problems.append(f"{ordinance}: the effect lacks {power}_power_cost = 50")
        if any(f"{other}_power_cost" in trigger or f"{other}_power_cost" in effect for other in wrong):
            problems.append(f"{ordinance}: enacting charges the wrong kind of power")
        if f"NOT = {{ has_country_modifier = {modifier} }}" not in trigger:
            problems.append(f"{ordinance}: enact is not blocked while the ordinance stands")
        if f"name = {modifier} duration = 3650" not in effect:
            problems.append(f"{ordinance}: enacting does not add its ten-year (3650 days) modifier")
        if "duration = -1" in effect:
            problems.append(f"{ordinance}: the ordinance would never end")
        if "set_country_flag" in effect or "clr_country_flag" in effect:
            problems.append(f"{ordinance}: a flag is set; the modifier is the only record of 'in force'")
        if "has_reform = hlc_crown_authority_reform" not in trigger:
            problems.append(f"{ordinance}: the button does not require the crown authority")
    return problems


def check_slots(mech, triggers):
    problems = []
    found = buttons(mech)
    modifiers = [f"has_country_modifier = hlc_{o}_ordinance_modifier" for o in ORDINANCES]
    for ordinance in ORDINANCES:
        enact = normalized(block_or_empty(found.get(ENACT[ordinance], ""), "trigger"))
        if "tooltip = hlc_ordinance_slot_free_tt hlc_ordinance_slot_free = yes" not in enact:
            problems.append(f"{ordinance}: the button does not require hlc_ordinance_slot_free inside a custom_trigger_tooltip")
    slot = normalized(block_or_empty(triggers, "hlc_ordinance_slot_free"))
    if not (slot.startswith("hlc_ordinance_slot_free = { NOT = { calc_true_if = {")
            and all(modifier in slot for modifier in modifiers) and "amount = 3" in slot):
        problems.append("hlc_ordinance_slot_free is not NOT = { calc_true_if over the six modifiers, amount = 3 }")
    if re.search(r"has_country_flag", _mask_comments_and_strings(triggers)):
        problems.append("a scripted trigger reads an ordinance flag: the modifier is the record of 'in force'")
    return problems


def check_cooldown(mech):
    """No engine cooldown on any ordinance: the engine shares it between the six buttons (seen in EU4 1.37.5)."""
    problems = []
    found = buttons(mech)
    for ordinance in ORDINANCES:
        text = normalized(found.get(ENACT[ordinance], "")) + " "
        if "cooldown_years = 0 " not in text:
            problems.append(f"{ordinance}: must say cooldown_years = 0 (the term is the modifier; an engine cooldown locks all six buttons)")
        for key in ("cooldown_token", "cooldown_desc"):
            if f"{key} =" in text:
                problems.append(f"{ordinance}: still has {key}, which the engine shares between the six buttons")
        if re.search(r"cooldown_years = [1-9]", text):
            problems.append(f"{ordinance}: has an engine cooldown of years, which blocks the other five ordinances too")
    return problems


def check_ai(mech, triggers, vanilla_knows=None):
    problems = []
    found = buttons(mech)
    for ordinance in ORDINANCES:
        name = ENACT[ordinance]
        block = found.get(name, "")
        factor = base_factor(block) if "ai_chance" in block else None
        if not factor:
            problems.append(f"{name}: ai_chance is missing or its base factor is 0, so the AI can never press it")
            continue
        ai = normalized(block_or_empty(block, "ai_chance"))
        for need in ENACT_NEEDS[ordinance]:
            if f"{need} = yes" not in ai:
                problems.append(f"{name}: the AI ignores {need}")
        if ordinance == "chancery":
            wanted = " ".join(f"{need} = yes" for need in ENACT_NEEDS["chancery"])
            if f"factor = 0.25 OR = {{ {wanted} }}" not in ai:
                problems.append(f"{name}: the AI takes the chancery as readily when another ordinance is called for")
        elif f"factor = 0 NOT = {{ {ENACT_NEEDS[ordinance][0]} = yes }}" not in ai:
            problems.append(f"{name}: the AI enacts without the situation that calls for it")
    if "factor = 4 num_of_owned_provinces_with = { value = 6" not in normalized(block_or_empty(found.get(ENACT["settlement"], ""), "ai_chance")):
        problems.append("the AI does not weigh the settlement ordinance by the number of unaccepted cities")
    if "factor = 3 num_of_owned_provinces_with = { value = 8" not in normalized(block_or_empty(found.get(ENACT["toleration"], ""), "ai_chance")):
        problems.append("the AI does not weigh the toleration ordinance by the number of cities of other faiths")
    defined = {name for name, _ in children("x = {\n" + triggers + "\n}")}
    in_use = normalized(mech) + " " + normalized(triggers)
    for name in SITUATIONS:
        if name not in defined:
            problems.append(f"{name} is not defined")
        elif len(re.findall(rf"\b{name}\b", in_use)) < 2:
            problems.append(f"{name} is defined and never used")
    if vanilla_knows is not None:
        for name in VANILLA_NAMES:
            if not vanilla_knows(name):
                problems.append(f"the installed game never uses `{name}`: it would silently never match")
    return problems


def check_cleanup(reform, effects, on_actions):
    problems = []
    removed = normalized(block_or_empty(block_or_empty(reform, "hlc_crown_authority_reform"), "removed_effect"))
    if "hlc_clear_ordinances_effect = yes" not in removed:
        problems.append("hlc_crown_authority_reform removed_effect does not call hlc_clear_ordinances_effect")
    clear = normalized(block_or_empty(effects, "hlc_clear_ordinances_effect"))
    for ordinance in ORDINANCES:
        for needle in (f"has_country_modifier = hlc_{ordinance}_ordinance_modifier", f"remove_country_modifier = hlc_{ordinance}_ordinance_modifier"):
            if needle not in clear:
                problems.append(f"hlc_clear_ordinances_effect lacks {needle}")
    for ordinance in LEGACY_FLAGGED:
        if f"clr_country_flag = hlc_{ordinance}_ordinance_active" not in clear:
            problems.append(f"hlc_clear_ordinances_effect lacks the flag of the older {ordinance} ordinance")
    sweep = block_or_empty(effects, "hlc_ordinance_sweep_effect")
    swept = normalized(sweep)
    if "NOT = { has_reform = hlc_crown_authority_reform }" not in swept or "hlc_clear_ordinances_effect = yes" not in swept:
        problems.append("hlc_ordinance_sweep_effect does not clear the ordinances of a country without the crown authority")
    for ordinance in ORDINANCES:
        if f"has_country_modifier = hlc_{ordinance}_ordinance_modifier" not in swept:
            problems.append(f"hlc_ordinance_sweep_effect does not look for the {ordinance} ordinance's modifier")
    if "NOT = { has_country_flag = hlc_ordinances_migrated }" not in swept:
        problems.append("the sweep does not run the migration once per country (hlc_ordinances_migrated)")
    for ordinance in LEGACY_FLAGGED:
        # The older flags are cleared, never tested: nothing sets them any more and check_script_layer calls that a defect.
        if re.search(rf"has_country_flag\s*=\s*hlc_{ordinance}_ordinance_active", effects):
            problems.append(f"the older {ordinance} flag is tested again, though nothing sets it (check_script_layer warns)")
    if "hlc_ordinance_migrate_effect = yes" not in swept:
        problems.append("the sweep does not move an older save's permanent ordinances onto the ten-year term")
    migrate = normalized(block_or_empty(effects, "hlc_ordinance_migrate_effect"))
    for needle in ("NOT = { has_country_flag = hlc_ordinances_migrated }", "set_country_flag = hlc_ordinances_migrated"):
        if needle not in migrate:
            problems.append(f"hlc_ordinance_migrate_effect lacks {needle}")
    for ordinance in LEGACY_FLAGGED:
        needles = (f"clr_country_flag = hlc_{ordinance}_ordinance_active", f"has_country_modifier = hlc_{ordinance}_ordinance_modifier",
                   f"remove_country_modifier = hlc_{ordinance}_ordinance_modifier", f"name = hlc_{ordinance}_ordinance_modifier duration = 3650")
        for needle in needles:
            if needle not in migrate:
                problems.append(f"hlc_ordinance_migrate_effect lacks {needle}")
    # Scoping. The sweep runs for every country every year: it must be look-ups only.
    limits = [normalized(body) for _, body in keyed_blocks(sweep, "limit")]
    if len(limits) < 3:
        problems.append("hlc_ordinance_sweep_effect lost one of its three limits")
    for limit in limits:
        leftover = re.sub(r"\b(?:limit|has_country_flag|has_country_modifier|has_reform|OR|NOT|yes)\b|[={}]|\bhlc_\w+", " ", limit)
        if leftover.strip():
            problems.append(f"a sweep limit holds more than flag/modifier/reform look-ups: {leftover.split()}")
    if re.search(r"\b(?:every|any|random|all)_\w+\s*=|\bwhile\s*=|export_to_variable|check_variable", swept):
        problems.append("the sweep iterates a scope or touches a variable, so it is not free for a non-HLC country")
    if "else" in re.findall(r"\b(else_if|else)\b", _mask_comments_and_strings(block_or_empty(effects, "hlc_ordinance_migrate_effect") + sweep + clear)):
        problems.append("an else/else_if body in a scripted effect: the engine drops some effects there")
    if "hlc_ordinance_sweep_effect = yes" not in normalized(block_or_empty(on_actions, "on_yearly_pulse")):
        problems.append("west_ukraine_on_actions.txt on_yearly_pulse does not run hlc_ordinance_sweep_effect")
    # The AI's ten-year wait for the appanage action is counted from a flag only the sweep sets.
    if "set_country_flag = hlc_austrian_bureaucracy_dated" not in swept:
        problems.append("nothing sets hlc_austrian_bureaucracy_dated, so the appanage AI would never start")
    return problems


def check_on_action(west, mod_00, vanilla_00):
    problems = []
    if "hlc_settlement_ordinance_conversion_effect = yes" not in normalized(block_or_empty(west, "on_province_culture_converted")):
        problems.append("west_ukraine_on_actions.txt no longer hangs the settlement effect on on_province_culture_converted")
    if _mask_comments_and_strings(west).count("hlc_settlement_ordinance_conversion_effect = yes") != 1:
        problems.append("the settlement effect is hooked a number of times other than once")
    if "MERGES" not in west or "on_action_merge_probe.txt" not in west:
        problems.append("west_ukraine_on_actions.txt does not record the measured merge rule")
    # The mod's copy of vanilla's file replaces it by name, so it has to keep every vanilla handler.
    ours = normalized(block_or_empty(mod_00, "on_province_culture_converted"))
    for handler in VANILLA_CONVERTED_HANDLERS:
        if f"{handler} = yes" not in ours:
            problems.append(f"the mod's 00_on_actions.txt lost the vanilla handler {handler}")
    if vanilla_00 is not None:
        if ours != normalized(block_or_empty(vanilla_00, "on_province_culture_converted")):
            problems.append("the mod's on_province_culture_converted differs from vanilla's")
        if not re.search(r"#\s*province, manually conversion\s*\n\s*on_province_culture_converted\s*=", vanilla_00):
            problems.append("vanilla no longer marks on_province_culture_converted as manual conversion: re-read the tooltips")
    return problems


def check_evidence(text):
    """The numbers recorded for the measured merge rule."""
    if text is None:
        return [f"{EVIDENCE} is missing"]
    problems = []
    for kind in ("STARTUP", "MONTHLY"):
        for tag in "AMZ":
            match = re.search(rf"(?m)^PROBE_{kind}_{tag}: (\d+)\s*$", text)
            if not match or int(match.group(1)) <= 0:
                problems.append(f"{EVIDENCE}: PROBE_{kind}_{tag} did not fire")
    if "MERGED" not in text:
        problems.append(f"{EVIDENCE} does not state its conclusion")
    return problems


def check_loyalty(effects, modifiers):
    problems = []
    effect = block_or_empty(effects, "hlc_settlement_ordinance_conversion_effect")
    if not effect:
        return ["hlc_settlement_ordinance_conversion_effect is missing"]
    body = normalized(effect)
    for estate in ("estate_burghers", "estate_clergy", "estate_magnates"):
        if estate in body:
            problems.append(f"the settlement ordinance still steadies {estate}: only the nobles receive resettled land")
    gifts = re.findall(r"rip_estate_mood_effect = \{ ESTATE = (\w+) LOYALTY = (-?\d+) \}", body)
    if gifts != [("estate_nobles", "2")]:
        problems.append(f"the settlement effect must give exactly +2 to estate_nobles, found {gifts}")
    limit = normalized(block_or_empty(effect, "limit"))
    if not re.search(r"NOT = \{ estate_loyalty = \{ estate = estate_nobles loyalty = 60 \} \}", limit):
        problems.append("the settlement gift has no ceiling at 60% noble loyalty")
    if "NOT = { has_country_modifier = hlc_settlement_loyalty_timer }" not in limit:
        problems.append("the settlement gift is not limited by its hidden timer")
    if not re.search(r"hidden_effect = \{ add_country_modifier = \{ name = hlc_settlement_loyalty_timer duration = 365 hidden = yes \} \}", body):
        problems.append("the hidden one-year timer is never added")
    if not re.match(r"limit = \{ owner = \{ has_country_modifier = hlc_settlement_ordinance_modifier", limit):
        problems.append("the settlement limit does not read the owner's ordinance modifier (the hook runs in province scope)")
    outside = body.split(limit, 1)[1].split("owner = {", 1)[0] if limit and limit in body else body
    if "estate" in outside or "loyalty" in outside:
        problems.append("an estate effect runs in province scope, outside owner")
    if not re.search(r"(?m)^hlc_settlement_loyalty_timer\s*=\s*\{\s*\}", _mask_comments_and_strings(modifiers)):
        problems.append("hlc_settlement_loyalty_timer is not an empty event modifier")
    return problems


def check_modifiers(modifiers):
    """Each ordinance has a modifier that pays for its good with something it costs, in names the installed game knows."""
    problems = []
    known = {
        "chancery": {"advisor_cost": 0.1, "diplomatic_reputation": 1.0, "improve_relation_modifier": 0.1},
        "settlement": {"global_unrest": 1.0, "culture_conversion_cost": -0.1},
        "cadastral": {"global_tax_modifier": 0.05, "nobles_loyalty_modifier": -0.05},
        "urbarial": {"global_unrest": -0.5, "global_manpower_modifier": 0.05, "nobles_loyalty_modifier": -0.05},
        "toleration": {"tolerance_heretic": 1.0, "tolerance_heathen": 1.0, "global_unrest": -0.5, "church_loyalty_modifier": -0.05},
        "frontier": {"defensiveness": 0.1, "hostile_attrition": 1.0, "land_maintenance_modifier": 0.05},
    }
    for ordinance, expected in known.items():
        body = block_or_empty(modifiers, f"hlc_{ordinance}_ordinance_modifier")
        if not body:
            problems.append(f"hlc_{ordinance}_ordinance_modifier is not defined")
            continue
        found = {k: float(v) for k, v in re.findall(r"(?m)^\s*(\w+)\s*=\s*(-?[\d.]+)\s*$", body[body.index("{") + 1: body.rindex("}")])}
        if found != expected:
            problems.append(f"hlc_{ordinance}_ordinance_modifier is {found}, the design says {expected}")
        gain = [v for v in found.values() if v > 0 and not (ordinance == "chancery")]
        cost = [v for v in found.values() if v < 0]
        if ordinance not in ("settlement", "chancery", "frontier") and not cost:
            problems.append(f"{ordinance}: an ordinance that costs nothing is a free bonus")
    return problems


def check_appanage(action, privilege, path_triggers, reform, loc_en, vanilla):
    problems = []
    allowed = normalized(block_or_empty(action, "is_allowed"))
    inner = allowed[allowed.index("{") + 1: allowed.rindex("}")].strip() if "{" in allowed else ""
    if not inner:
        problems.append("hlc_incorporate_appanage has an empty is_allowed")
    if "liberty_desire = 50" not in inner:
        problems.append("is_allowed does not refuse a vassal the engine could not annex anyway (liberty desire 50)")
    if ("tooltip = hlc_incorporate_appanage_limit_tt" not in inner
            or "is_subject_of_type = incorporated_vassal" not in inner or "amount = 5" not in inner):
        problems.append("is_allowed has no readable cap of five incorporated vassals")
    ai = normalized(block_or_empty(action, "ai_will_do"))
    if not ai or "always = yes" in ai:
        problems.append("ai_will_do lets every AI incorporate every vassal at once")
    for needle in ("is_at_war = no", "NOT = { governing_capacity_percentage = 0.6 }", "liberty_desire = 25", "adm_tech = ",
                   "had_country_flag = { flag = hlc_austrian_bureaucracy_dated days = 3650 }"):
        if needle not in ai:
            problems.append(f"ai_will_do lacks {needle}")
    # The chain: attribute -> trigger -> action; the privilege reads the subject type the action makes.
    if "hlc_enables_incorporated_appanages = yes" not in block_or_empty(reform, "hlc_austrian_bureaucracy_reform"):
        problems.append("the Austrian bureaucracy no longer sets hlc_enables_incorporated_appanages")
    if "has_government_attribute = hlc_enables_incorporated_appanages" not in normalized(block_or_empty(path_triggers, "hlc_can_incorporate_appanages")):
        problems.append("hlc_can_incorporate_appanages does not read the attribute")
    if "hlc_can_incorporate_appanages = yes" not in normalized(block_or_empty(action, "is_visible")):
        problems.append("the action's is_visible does not call hlc_can_incorporate_appanages")
    if "subject_type = incorporated_vassal" not in normalized(block_or_empty(action, "on_accept")):
        problems.append("the action no longer makes an incorporated vassal")
    for part in ("is_valid", "can_select"):
        body = normalized(block_or_empty(privilege, part))
        if "is_subject_of_type = incorporated_vassal" not in body:
            problems.append(f"the privilege's {part} does not ask for an incorporated vassal")
        if "is_subject_of_type = vassal" in body:
            problems.append(f"the privilege's {part} still accepts any vassal, so the action is not needed")
    # Numbers: vanilla's own files first, then every text of the chain.
    if vanilla is not None:
        base = re.search(r"annex_cost_per_development\s*=\s*([0-9.]+)", vanilla["default"])
        inc = re.search(r"annex_cost_per_development\s*=\s*([0-9.]+)", vanilla["incorporated"])
        if not (base and inc) or round((float(inc.group(1)) - float(base.group(1))) / float(base.group(1)) * 100) != -25:
            problems.append("vanilla's incorporated_vassal is no longer 25% cheaper to annex than a vassal")
        if "governing_capacity = -100" not in normalized(vanilla["penalty"]):
            problems.append("vanilla's base_incorporated_vassal_cost is no longer -100 governing capacity")
        if "-25.0%" not in vanilla["desc"] or "-100.00" not in vanilla["desc"] or "10" not in vanilla["desc"]:
            problems.append("vanilla's incorporate_vassal_desc no longer quotes 25%, 100 and 10 years")
    for key, needles in {
        "hlc_incorporate_appanage_tooltip": ("25%", "100"),
        "hlc_incorporate_appanage_desc": ("-25.0%", "-100.00", "10", "Strong Appanages"),
        "mechanic_hlc_enables_incorporated_appanages_yes": ("-25.0%", "-100.00", "five", "50%", "Strong Appanages"),
        "estate_nobles_hlc_strong_appanages_trigger_tooltip": ("Incorporated Vassal",),
        "estate_nobles_hlc_strong_appanages_desc": ("Incorporated Vassal",),
        "hlc_austrian_bureaucracy_reform_desc": ("appanage",),
    }.items():
        value = loc_value(loc_en, key)
        if value is None:
            problems.append(f"{key} is missing")
            continue
        for needle in needles:
            if needle not in value:
                problems.append(f"{key} does not say {needle!r}")
    return problems


def check_text(texts, mech, action, privilege, vanilla=None):
    """texts: language -> (full localisation text, fallback-file text or None)."""
    problems = []
    english = texts["english"][0]
    for language, (full, fallback) in texts.items():
        keys = loc_keys(full)
        for key in NEW_KEYS + REWORDED_KEYS:
            if key not in keys:
                problems.append(f"{language}: missing {key}")
        if language != "english":
            if fallback is None:
                problems.append(f"{language}: the fallback file is missing")
                continue
            for key in NEW_KEYS + REWORDED_KEYS:
                if loc_value(fallback, key) != loc_value(english, key):
                    problems.append(f"{language}: the fallback of {key} differs from the English text")
            for key in RETIRED_KEYS:
                if loc_value(fallback, key) is not None:
                    problems.append(f"{language}: the retired key {key} is still in the fallback file")
        # Every tooltip sentence the mechanic, the action and the privilege name has text.
        source = re.sub(r"#[^\n]*", "", mech + action + privilege)
        named = set(re.findall(r"tooltip = (\w+)", source))
        missing = sorted(name for name in named if name not in keys and name not in {"FROM_IS_REBELLIOUS_TT"})
        if missing:
            problems.append(f"{language}: tooltip keys {missing} have no text")
    for key in RETIRED_KEYS:
        if loc_value(english, key) is not None:
            problems.append(f"english: the retired key {key} is still defined")
    # Every button reads its own text and states its price, its term and the slot rule.
    for ordinance in ORDINANCES:
        power = POWER_WORD[POWER[ordinance]]
        enact = loc_value(english, f"hlc_enact_{ordinance}_ordinance_desc") or ""
        if f"Costs §Y50§! {power} power" not in enact:
            problems.append(f"the {ordinance} text does not state its price")
        if "§Y10§! years" not in enact or "cannot be enacted again until its term has run out" not in enact:
            problems.append(f"the {ordinance} text does not state the ten-year term and that it cannot be enacted again before it ends")
        if "at most §Ythree§! of its six ordinances" not in enact:
            problems.append(f"the {ordinance} text does not state the three-slot rule")
        if re.search(r"same button|When (?:in)?active|Toggle|[Rr]escind", enact):
            problems.append(f"the {ordinance} text still speaks of rescinding or one toggle button")
        if not (loc_value(english, f"hlc_enact_{ordinance}_ordinance") or "").startswith("Enact the "):
            problems.append(f"hlc_enact_{ordinance}_ordinance is not named 'Enact the ...'")
    settlement = loc_value(english, "hlc_enact_settlement_ordinance_desc") or ""
    for needle in ("§G10%§!", "ordered by hand", "§Y60%§!"):
        if needle not in settlement:
            problems.append(f"the settlement enact text does not state the real rule ({needle!r} missing)")
    modifier = loc_value(english, "desc_hlc_settlement_ordinance_modifier") or ""
    if "+2" not in modifier or "60%" not in modifier or "manual" not in modifier:
        problems.append("the settlement modifier text does not state the real rule (manual, +2, below 60%)")
    crown = loc_value(english, "hlc_crown_authority_reform_desc") or ""
    if "six different ordinances" not in crown or "at most three" not in crown:
        problems.append("the crown authority's description does not tell the player about the six ordinances and the three slots")
    # No ordinance key without a reader.
    reader = chr(10).join(line.split("#", 1)[0] for line in (mech + action + privilege).splitlines())
    for key in sorted(loc_keys(english)):
        if not ORDINANCE_KEY.match(key):
            continue
        # A button's `_desc` is read through the button's own name.
        read_as = (key, key[:-5]) if key.endswith("_desc") else (key,)
        if not any(re.search("(?<![A-Za-z0-9_])" + re.escape(name) + "(?![A-Za-z0-9_])", reader) for name in read_as):
            problems.append(f"english: {key} is read by nothing in the mechanic")
    return problems


# --------------------------------------------------------------------------

def vanilla_knows():
    if vanilla_root() is None:
        return None

    def known(name):
        return bool(vanilla_grep(rf"\b{re.escape(name)}\b", "common"))
    return known


def vanilla_numbers():
    root = vanilla_root()
    if root is None:
        return None
    subject_text = vanilla_read("common/subject_types/00_subject_types.txt") or ""
    modifier_text = vanilla_read("common/event_modifiers/01_mission_modifiers.txt") or ""
    desc = ""
    cooldown = ""
    for path in sorted((root / "localisation").glob("*_l_english.yml")):
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        match = re.search(r' incorporate_vassal_desc:\d+ "(.*)"', text)
        if match and not desc:
            desc = match.group(1)
        match = re.search(r' INTERACTION_COOLDOWN_TOOLTIP:\d+ "(.*)"', text)
        if match and not cooldown:
            cooldown = match.group(1)
    return {
        "default": block_or_empty(subject_text, "default"),
        "incorporated": block_or_empty(subject_text, "incorporated_vassal", 2),
        "penalty": block_or_empty(modifier_text, "base_incorporated_vassal_cost"),
        "desc": desc,
        "cooldown": cooldown,
    }


def load():
    sources = {
        "mech": read("common/government_mechanics/rip_hlc_austrian_reorganization.txt"),
        "triggers": read("common/scripted_triggers/rip_hlc_ordinance_triggers.txt"),
        "effects": read("common/scripted_effects/rip_hlc_ordinance_effects.txt"),
        "estate_effects": read("common/scripted_effects/rip_estate_effects.txt"),
        "west": read("common/on_actions/west_ukraine_on_actions.txt"),
        "mod_00": read("common/on_actions/00_on_actions.txt"),
        "modifiers": read("common/event_modifiers/west_ukraine_modifiers.txt"),
        "reform": read("common/government_reforms/RIP_HLC_government_reforms.txt"),
        "action": read("common/new_diplomatic_actions/RIP_HLC_diplomatic_actions.txt"),
        "privilege": read("common/estate_privileges/RIP_HLC_estate_privileges.txt"),
        "path_triggers": read("common/scripted_triggers/rip_path_state_triggers.txt"),
    }
    evidence = ROOT / EVIDENCE
    sources["evidence"] = evidence.read_text(encoding="utf-8") if evidence.is_file() else None
    texts = {}
    for language in LANGUAGES:
        fallback = None
        if language != "english":
            path = ROOT / "localisation" / "replace" / f"zzz_RIP_untranslated_l_{language}.yml"
            fallback = path.read_text(encoding="utf-8-sig") if path.is_file() else None
        texts[language] = (loc_text(language), fallback)
    return sources, texts


def run_checks(s, texts, vanilla):
    vanilla_00 = vanilla_read("common/on_actions/00_on_actions.txt")
    problems = []
    problems += check_layout(s["mech"])
    problems += check_price(s["mech"])
    problems += check_slots(s["mech"], s["triggers"])
    problems += check_cooldown(s["mech"])
    problems += check_ai(s["mech"], s["triggers"], vanilla_knows())
    problems += check_cleanup(s["reform"], s["effects"], s["west"])
    problems += check_on_action(s["west"], s["mod_00"], vanilla_00)
    problems += check_evidence(s["evidence"])
    problems += check_loyalty(s["estate_effects"], s["modifiers"])
    problems += check_modifiers(s["modifiers"])
    problems += check_appanage(s["action"], s["privilege"], s["path_triggers"], s["reform"], texts["english"][0], vanilla)
    problems += check_text(texts, s["mech"], s["action"], s["privilege"], vanilla)
    return problems


def planted_cases(s, texts, vanilla):
    """Break the sources in memory, one defect at a time: defect name -> the problems the checks reported for it."""
    vanilla_00 = vanilla_read("common/on_actions/00_on_actions.txt")
    mech, action, privilege = s["mech"], s["action"], s["privilege"]
    en = texts["english"][0]

    def sub(key, old, new, count=1):
        assert old in s[key], f"sabotage anchor missing in {key}: {old!r}"
        return s[key].replace(old, new, count)

    def appanage(action_=None, privilege_=None, path_triggers=None, reform=None, loc=None, vanilla_=vanilla):
        return check_appanage(action_ or action, privilege_ or privilege, path_triggers or s["path_triggers"],
                              reform or s["reform"], loc or en, vanilla_)

    def loyalty(effects=None, modifiers=None):
        return check_loyalty(effects or s["estate_effects"], modifiers or s["modifiers"])

    def cleanup(reform=None, effects=None, west=None):
        return check_cleanup(reform or s["reform"], effects or s["effects"], west or s["west"])

    def on_action(west=None, mod_00=None, vanilla_00_=vanilla_00):
        return check_on_action(west or s["west"], mod_00 or s["mod_00"], vanilla_00_)

    def text(vanilla_=vanilla, mech_=mech, **overrides):
        return check_text({**texts, **overrides}, mech_, action, privilege, vanilla_)

    def everywhere(old, new):
        """The same wording change in every language and its fallback file, so only the content checks can see it."""
        out = {}
        for language, (full, fallback) in texts.items():
            assert old in full, f"sabotage anchor missing in the {language} text: {old!r}"
            out[language] = (full.replace(old, new), fallback.replace(old, new) if fallback else fallback)
        return out

    ai_block = lambda b: b.replace(named_block(b, "ai_chance"), "\t\t\tai_chance = {\n\t\t\t\tfactor = 0\n\t\t\t}")
    drop_button = lambda name: mech.replace(buttons(mech)[name], "", 1)
    cases = {
        # layout: six different buttons, two rows
        "a button missing": check_layout(drop_button(ENACT["frontier"])),
        "a rescind button back, wearing another ordinance's picture": check_layout(mech.replace(f"{ENACT['frontier']} = {{", "hlc_rescind_chancery_ordinance = {", 1)),
        "rows in another order": check_layout(mech.replace(f"{ENACT['cadastral']} = {{", "hlc_swap = {", 1)),
        "two buttons wearing one sprite": check_layout(edit_button(mech, ENACT["toleration"], lambda b: b.replace("GFX_rip_toleration_ordinance", "GFX_rip_urbarial_ordinance"))),
        "a vanilla icon back in the chancery": check_layout(edit_button(mech, ENACT["chancery"], lambda b: b.replace("GFX_rip_chancery_ordinance", "GFX_cossacks_ability_ADM"))),
        "a toggle button in a comment-free copy": check_layout(mech + "\n# toggle\nhlc_x = { toggle = yes }\n"),
        # price and term
        "chancery without its price": check_price(mech.replace("dip_power_cost = 50", "# free")),
        "price in the trigger only": check_price(edit_button(mech, ENACT["chancery"], lambda b: b.replace("\t\t\t\tdip_power_cost = 50\n\t\t\t\tadd_country_modifier", "\t\t\t\tadd_country_modifier", 1))),
        "settlement paid in the wrong power": check_price(edit_button(mech, ENACT["settlement"], lambda b: b.replace("adm_power_cost", "dip_power_cost"))),
        "frontier paid in the wrong power": check_price(edit_button(mech, ENACT["frontier"], lambda b: b.replace("mil_power_cost", "adm_power_cost"))),
        "enact that sets a flag again": check_price(edit_button(mech, ENACT["urbarial"], lambda b: b.replace("add_country_modifier", "set_country_flag = hlc_urbarial_ordinance_active\n\t\t\t\tadd_country_modifier", 1))),
        "enact not blocked while in force": check_price(edit_button(mech, ENACT["settlement"], lambda b: b.replace("NOT = { has_country_modifier = hlc_settlement_ordinance_modifier }", "always = yes", 1))),
        "ordinance that never ends": check_price(edit_button(mech, ENACT["cadastral"], lambda b: b.replace("duration = 3650", "duration = -1", 1))),
        "ordinance that ends after five years": check_price(edit_button(mech, ENACT["toleration"], lambda b: b.replace("duration = 3650", "duration = 1825", 1))),
        "button open to a country without the crown": check_price(edit_button(mech, ENACT["frontier"], lambda b: b.replace("has_reform = hlc_crown_authority_reform", "always = yes", 1))),
        # slots
        "urbarial enacted without the slot rule": check_slots(edit_button(mech, ENACT["urbarial"], lambda b: b.replace("hlc_ordinance_slot_free = yes", "always = yes")), s["triggers"]),
        "slot rule that allows four": check_slots(mech, s["triggers"].replace("amount = 3", "amount = 4")),
        "slot rule that forgets the frontier ordinance": check_slots(mech, s["triggers"].replace("has_country_modifier = hlc_frontier_ordinance_modifier", "always = no", 1)),
        "slot sentence that is not a sentence": check_slots(mech.replace("tooltip = hlc_ordinance_slot_free_tt", "tooltip = nothing", 1), s["triggers"]),
        "slot rule that reads a flag again": check_slots(mech, s["triggers"] + "\nhlc_x = { has_country_flag = hlc_chancery_ordinance_active }\n"),
        # cooldown
        "a cooldown token back on one ordinance": check_cooldown(edit_button(mech, ENACT["toleration"], lambda b: b.replace("cooldown_years = 0", "cooldown_years = 0\n\t\t\tcooldown_token = hlc_toleration_ordinance", 1))),
        "a cooldown name back on one ordinance": check_cooldown(edit_button(mech, ENACT["settlement"], lambda b: b.replace("cooldown_years = 0", "cooldown_years = 0\n\t\t\tcooldown_desc = hlc_ordinance_cooldown_desc", 1))),
        "a ten-year engine cooldown on one ordinance": check_cooldown(edit_button(mech, ENACT["cadastral"], lambda b: b.replace("cooldown_years = 0", "cooldown_years = 10", 1))),
        "an ordinance with no cooldown line at all": check_cooldown(edit_button(mech, ENACT["frontier"], lambda b: b.replace("cooldown_years = 0", "# nothing", 1))),
        # AI
        "settlement enact the AI can never press": check_ai(edit_button(mech, ENACT["settlement"], ai_block), s["triggers"]),
        "frontier enact the AI can never press": check_ai(edit_button(mech, ENACT["frontier"], ai_block), s["triggers"]),
        "urbarial enact that ignores its situation": check_ai(edit_button(mech, ENACT["urbarial"], lambda b: b.replace("hlc_ordinance_urbarial_wanted = yes", "always = yes")), s["triggers"]),
        "toleration enact that ignores its situation": check_ai(edit_button(mech, ENACT["toleration"], lambda b: b.replace("NOT = { hlc_ordinance_toleration_wanted = yes }", "always = no")), s["triggers"]),
        "frontier enact that ignores war": check_ai(edit_button(mech, ENACT["frontier"], lambda b: b.replace("hlc_ordinance_frontier_wanted = yes", "always = yes")), s["triggers"]),
        "cadastre enact that ignores its situation": check_ai(edit_button(mech, ENACT["cadastral"], lambda b: b.replace("hlc_ordinance_cadastre_wanted = yes", "always = yes")), s["triggers"]),
        "settlement enact that ignores its situation": check_ai(edit_button(mech, ENACT["settlement"], lambda b: b.replace("NOT = { hlc_ordinance_settlement_wanted = yes }", "always = no")), s["triggers"]),
        "settlement enact that ignores how many cities": check_ai(edit_button(mech, ENACT["settlement"], lambda b: b.replace("value = 6", "value = 1")), s["triggers"]),
        "toleration enact that ignores how many cities": check_ai(edit_button(mech, ENACT["toleration"], lambda b: b.replace("value = 8", "value = 1")), s["triggers"]),
        "chancery taken as readily as what the realm needs": check_ai(edit_button(mech, ENACT["chancery"], lambda b: b.replace("factor = 0.25", "factor = 1")), s["triggers"]),
        "chancery that forgets the frontier": check_ai(edit_button(mech, ENACT["chancery"], lambda b: b.replace("\t\t\t\t\t\thlc_ordinance_frontier_wanted = yes\n", "", 1)), s["triggers"]),
        "undefined AI situation": check_ai(mech, s["triggers"].replace("hlc_ordinance_urbarial_wanted = {", "hlc_ordinance_urbarial_gone = {")),
        "AI trigger the game does not have": check_ai(mech, s["triggers"], lambda name: name != "has_owner_religion"),
        # clean-up
        "crown authority no longer clears": cleanup(reform=s["reform"].replace("hlc_clear_ordinances_effect = yes", "# nothing")),
        "clear effect leaves a modifier behind": cleanup(effects=s["effects"].replace("remove_country_modifier = hlc_frontier_ordinance_modifier", "# nothing")),
        "clear effect leaves an old flag behind": cleanup(effects=s["effects"].replace("clr_country_flag = hlc_settlement_ordinance_active\n\tclr_country_flag = hlc_cadastral_ordinance_active\n\tif", "clr_country_flag = hlc_cadastral_ordinance_active\n\tif", 1)),
        "yearly sweep not wired": cleanup(west=s["west"].replace("hlc_ordinance_sweep_effect = yes", "# nothing")),
        "sweep that iterates every province": cleanup(effects=s["effects"].replace("hlc_clear_ordinances_effect = yes\n\t}", "hlc_clear_ordinances_effect = yes\n\t\tevery_owned_province = { limit = { always = yes } }\n\t}", 1)),
        "sweep with a dear limit": cleanup(effects=s["effects"].replace("NOT = { has_reform = hlc_crown_authority_reform }", "NOT = { has_reform = hlc_crown_authority_reform }\n\t\t\tnum_of_owned_provinces_with = { value = 1 always = yes }", 1)),
        "sweep that never dates the bureaucracy": cleanup(effects=s["effects"].replace("set_country_flag = hlc_austrian_bureaucracy_dated", "# nothing")),
        "sweep that forgets a stray modifier": cleanup(effects=s["effects"].replace("has_country_modifier = hlc_toleration_ordinance_modifier\n\t\t\t\thas_country_modifier = hlc_frontier_ordinance_modifier", "always = no\n\t\t\t\talways = no", 1)),
        "sweep that no longer migrates an older save": cleanup(effects=s["effects"].replace("hlc_ordinance_migrate_effect = yes\n\t}\n\t# Dates", "# nothing\n\t}\n\t# Dates", 1)),
        "migration that runs every year": cleanup(effects=s["effects"].replace("\t\tset_country_flag = hlc_ordinances_migrated\n", "", 1)),
        "an older flag tested again": cleanup(effects=s["effects"].replace("has_country_modifier = hlc_frontier_ordinance_modifier\n\t\t\t}\n\t\t\tNOT = { has_reform", "has_country_modifier = hlc_frontier_ordinance_modifier\n\t\t\t\thas_country_flag = hlc_chancery_ordinance_active\n\t\t\t}\n\t\t\tNOT = { has_reform", 1)),
        "migration that forgets the new term": cleanup(effects=s["effects"].replace("duration = 3650", "duration = -1", 1)),
        "an else in the clean-up": cleanup(effects=s["effects"].replace("hlc_ordinance_migrate_effect = yes\n\t}\n\t# Dates", "hlc_ordinance_migrate_effect = yes\n\t}\n\telse = { always = yes }\n\t# Dates", 1)),
        # on_action
        "settlement hook dropped": on_action(west=s["west"].replace("hlc_settlement_ordinance_conversion_effect = yes", "# nothing")),
        "settlement hook doubled": on_action(west=s["west"] + "\non_province_culture_converted = { hlc_settlement_ordinance_conversion_effect = yes }\n"),
        "merge rule no longer on record": on_action(west=s["west"].replace("MERGES", "replaces")),
        "vanilla handler lost from the mod's copy": on_action(mod_00=s["mod_00"].replace("\ton_province_culture_converted_effect = yes", "\t# gone", 1)),
        "mod's copy that drifts from vanilla": on_action(mod_00=s["mod_00"].replace("on_province_culture_change_effect = yes", "on_province_culture_change_effect = yes\n\tpdl_reconcile_base_reform_effect = yes", 1)) if vanilla_00 is not None else ["skipped"],
        "merge evidence missing": check_evidence(None),
        "merge evidence with a silent file": check_evidence((s["evidence"] or "").replace("PROBE_STARTUP_Z: 674", "PROBE_STARTUP_Z: 0")),
        # loyalty loop
        "loyalty to every estate again": loyalty(effects=sub("estate_effects", "rip_estate_mood_effect = { ESTATE = estate_nobles LOYALTY = 2 }", "rip_estate_mood_effect = { ESTATE = estate_nobles LOYALTY = 2 }\n\t\t\trip_estate_mood_effect = { ESTATE = estate_burghers LOYALTY = 1 }")),
        "loyalty without a ceiling": loyalty(effects=sub("estate_effects", "loyalty = 60", "loyalty = 100")),
        "loyalty without the yearly timer": loyalty(effects=sub("estate_effects", "NOT = { has_country_modifier = hlc_settlement_loyalty_timer }", "always = yes")),
        "loyalty that reads the retired flag": loyalty(effects=sub("estate_effects", "has_country_modifier = hlc_settlement_ordinance_modifier", "has_country_flag = hlc_settlement_ordinance_active")),
        "timer never added hidden": loyalty(effects=replace_in_nested_block(
            s["estate_effects"],
            ("hlc_settlement_ordinance_conversion_effect", "hidden_effect", "add_country_modifier"),
            "hidden = yes",
            "hidden = no",
        )),
        "timer modifier undefined": loyalty(modifiers=sub("modifiers", "hlc_settlement_loyalty_timer = {", "hlc_settlement_loyalty_timer_x = {")),
        "bigger gift": loyalty(effects=sub("estate_effects", "estate_nobles LOYALTY = 2", "estate_nobles LOYALTY = 5")),
        "gift outside the owner scope": loyalty(effects=sub("estate_effects", "\t\towner = {\n\t\t\trip_estate_mood_effect = { ESTATE = estate_nobles LOYALTY = 2 }", "\t\trip_estate_mood_effect = { ESTATE = estate_nobles LOYALTY = 2 }\n\t\towner = {")),
        # modifiers
        "a free ordinance": check_modifiers(s["modifiers"].replace("global_unrest = -0.5\n\tglobal_manpower_modifier = 0.05\n\tnobles_loyalty_modifier = -0.05", "global_unrest = -0.5\n\tglobal_manpower_modifier = 0.05", 1)),
        "a modifier with another number": check_modifiers(s["modifiers"].replace("defensiveness = 0.1", "defensiveness = 0.3", 1)),
        # appanage
        "AI always incorporates": appanage(action_=action.replace("had_country_flag = {\n\t\t\tflag = hlc_austrian_bureaucracy_dated\n\t\t\tdays = 3650\n\t\t}", "always = yes")),
        "AI without capacity headroom": appanage(action_=action.replace("NOT = { governing_capacity_percentage = 0.6 }", "always = yes")),
        "AI at war": appanage(action_=action.replace("is_at_war = no", "always = yes")),
        "empty is_allowed": appanage(action_=re.sub(r"is_allowed = \{.*?\n\t\}\n\n\ton_accept", "is_allowed = {\n\t}\n\n\ton_accept", action, flags=re.S)),
        "is_allowed without the liberty guard": appanage(action_=action.replace("NOT = { liberty_desire = 50 }", "always = yes")),
        "privilege for any vassal": appanage(privilege_=privilege.replace("is_subject_of_type = incorporated_vassal", "is_subject_of_type = vassal")),
        "attribute with no reader": appanage(path_triggers=s["path_triggers"].replace("has_government_attribute = hlc_enables_incorporated_appanages", "always = no")),
        "reform that stops opening the action": appanage(reform=s["reform"].replace("hlc_enables_incorporated_appanages = yes", "# nothing")),
        "tooltip with another number": appanage(loc=en.replace("§G25%§! cheaper", "§G30%§! cheaper")),
        # text
        "new key missing in English": text(english=(en.replace(" hlc_ordinance_slot_free_tt:0 ", " hlc_ordinance_slot_free_gone:0 "), None)),
        "an ordinance button without a name": text(english=(en.replace(" hlc_enact_toleration_ordinance_desc:0 ", " hlc_enact_toleration_ordinance_gone:0 "), None)),
        "new key missing in Spanish": text(spanish=(texts["spanish"][0].replace(" hlc_incorporate_appanage_limit_tt:0 ", " hlc_x:0 "), texts["spanish"][1])),
        "new ordinance key missing in German": text(german=(texts["german"][0].replace(" hlc_enact_frontier_ordinance:0 ", " hlc_x:0 "), texts["german"][1])),
        "fallback that drifts from English": text(french=(texts["french"][0], (texts["french"][1] or "").replace("Fewer than three of the crown's ordinances", "Fewer than four of the crown's ordinances"))),
        "retired key still in a fallback": text(spanish=(texts["spanish"][0], (texts["spanish"][1] or "") + ' hlc_rescind_cadastral_ordinance:0 "Rescind the Cadastral Ordinance"\n')),
        "retired key still in English": text(english=(en + ' hlc_chancery_ordinance_in_force_tt:0 "The Chancery Ordinance is in force."\n', None)),
        "text without its price": text(**everywhere("Costs §Y50§! military power", "Costs nothing")),
        "text without the three slots": text(**everywhere("The crown keeps at most §Ythree§! of its six ordinances in force at a time.", "The crown keeps all of its ordinances in force.")),
        "text without the term": text(**everywhere("The ordinance stands for §Y10§! years and cannot be enacted again until its term has run out. ", "")),
        "text that speaks of rescinding again": text(**everywhere("The passes are watched and invaders are worn down in them, at the price of a larger army to feed.", "The passes are watched. Rescind it when you wish.")),
        "settlement text that over-promises": text(**everywhere("the first conversion ordered by hand in a year", "every conversion")),
        "settlement modifier text without the real rule": text(**everywhere("The first manual conversion in a year", "Every conversion")),
        "crown description with the old two slots": text(**everywhere("each lasting ten years, and keep at most three of them in force at a time", "and must keep only two of three in force at a time")),
        "tooltip sentence with no text": check_text(texts, mech.replace("tooltip = hlc_ordinance_slot_free_tt", "tooltip = hlc_ordinance_unwritten_tt", 1), action, privilege),
        "the retired cooldown name back in English": text(english=(en + ' hlc_ordinance_cooldown_desc:0 "This Ordinance"\n', None)),
        "an ordinance key nothing reads": text(english=(en.replace(" hlc_ordinance_slot_free_tt:0 ", " hlc_ordinance_toggle_tt:0 \"x\"\n hlc_ordinance_slot_free_tt:0 ", 1), None)),
    }
    if vanilla is not None:
        cases["vanilla's governing capacity penalty changes"] = appanage(vanilla_={**vanilla, "penalty": "base_incorporated_vassal_cost = { governing_capacity = -50 }"})
        cases["vanilla's annexation discount changes"] = appanage(vanilla_={**vanilla, "incorporated": vanilla["incorporated"].replace("6.0", "7.0")})
    return cases


def planted_violations(s, texts, vanilla):
    """Names of the planted defects no check reported, and how many were planted."""
    cases = planted_cases(s, texts, vanilla)
    unseen = [name for name, found in cases.items() if not found]
    return unseen, len(cases)


def main():
    sources, texts = load()
    vanilla = vanilla_numbers()
    problems = run_checks(sources, texts, vanilla)
    unseen, planted = planted_violations(sources, texts, vanilla)
    problems += [f"planted violation not caught: {name}" for name in unseen]
    if problems:
        print("HLC ORDINANCES CHECK: FAIL")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    note = "" if vanilla is not None else " (vanilla comparisons skipped: no installed EU4)"
    print(f"HLC ORDINANCES CHECK: PASS (6 different buttons in two rows, priced, on a ten-year modifier term with no engine cooldown, slotted and given an AI; clean-up, "
          f"on_action, loyalty cap and appanage chain; {len(LANGUAGES)} languages; {planted} planted violations caught){note}")
    print("LIMIT: static contracts. Only the on_action merge rule was measured in the game (see the evidence file); "
          "the ordinance buttons, the AI, the cooldown tooltip and the appanage action were not exercised.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
