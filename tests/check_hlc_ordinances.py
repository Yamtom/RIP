"""Contracts for the Galician Chancery Ordinances and the Incorporated Appanage.

Static checks over script and localisation. They prove the sources agree with each
other and with the installed vanilla; they do not run EU4 triggers. What was measured
in the game (one on_action key defined in many files runs every definition) is kept
in diagnostics/hlc_ordinances_20261017/on_action_merge_probe.txt and only its
numbers are read here.

  * PRICE   each toggle checks and pays 50 monarch power of the right kind only when
            enacting; rescinding is free, including when the treasury is below 50.
  * SLOTS   at most two of the three ordinances in force: only the enact arm requires
            hlc_ordinance_slot_free inside a custom_trigger_tooltip with a sentence.
  * AI      each toggle has a real ai_chance; the AI enacts when useful and rescinds
            when its ordinance becomes a burden; the situations are defined, used,
            and made of names the installed vanilla has.
  * CLEAN-UP  removed_effect hands over to one effect that clears all three flags and
            modifiers, and a yearly sweep calls it for any country that holds them
            without the crown authority; the sweep is made of look-ups only.
  * ON_ACTION  the settlement hook is one definition of a key that 00_on_actions.txt
            also defines, the mod's copy keeps the five vanilla handlers, and the
            measured merge rule is on record.
  * LOYALTY  the settlement gift goes to the nobles only, below a ceiling, once a year
            by a hidden timer.
  * APPANAGE  the chain attribute -> trigger -> action -> subject type -> privilege has
            a producer for every reader, the action is guarded and its AI decides, and
            every text quotes the numbers vanilla really applies.
  * TEXT    every new key is in the four languages and the fallbacks equal the English.

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
ORDINANCES = ("chancery", "settlement", "cadastral")
POWER = {"chancery": "dip", "settlement": "adm", "cadastral": "adm"}
MECHANIC = "hlc_austrian_reorganization_mechanic"
EVIDENCE = "diagnostics/hlc_ordinances_20261017/on_action_merge_probe.txt"
VANILLA_CONVERTED_HANDLERS = (
    "on_province_culture_converted_estate_privilges_effect",
    "judaism_on_province_culture_converted_effect",
    "imperial_modifiers_on_province_change_culture_or_change_owner_effect",
    "on_province_culture_change_effect",
    "on_province_culture_converted_effect",
)
SITUATIONS = (
    "hlc_ordinance_slot_free", "hlc_ordinance_over_limit", "hlc_ordinance_settlement_wanted",
    "hlc_ordinance_settlement_spent", "hlc_ordinance_cadastre_wanted", "hlc_ordinance_cadastre_dangerous",
    "hlc_ordinance_room_needed",
)
# Names the mechanic, the AI situations and the appanage action lean on. An unknown
# name silently never matches, so each has to be something the installed game uses.
VANILLA_NAMES = (
    "num_of_owned_provinces_with", "has_owner_culture", "has_owner_accepted_culture", "is_city",
    "estate_loyalty", "has_estate", "years_of_income", "num_of_loans", "calc_true_if",
    "governing_capacity_percentage", "liberty_desire", "had_country_flag", "adm_tech", "is_at_war",
    "all_subject_country", "is_subject_of_type", "adm_power_cost", "dip_power_cost",
    "has_country_modifier", "hidden_effect", "add_country_modifier", "custom_trigger_tooltip",
)
# New or reworded keys: all four languages, and the fallbacks equal the English.
NEW_KEYS = (
    "hlc_ordinance_slot_free_tt", "hlc_incorporate_appanage_limit_tt",
    "hlc_ordinance_cooldown_desc", "hlc_settlement_loyalty_timer",
    "desc_hlc_settlement_loyalty_timer",
)
REWORDED_KEYS = (
    "hlc_enact_chancery_ordinance_desc", "hlc_enact_settlement_ordinance_desc", "hlc_enact_cadastral_ordinance_desc",
    "desc_hlc_settlement_ordinance_modifier", "hlc_incorporate_appanage_tooltip", "hlc_incorporate_appanage_desc",
    "estate_nobles_hlc_strong_appanages_desc", "estate_nobles_hlc_strong_appanages_trigger_tooltip",
    "mechanic_hlc_enables_incorporated_appanages_yes", "hlc_austrian_bureaucracy_reform_desc", "hlc_crown_authority_reform_desc",
)


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


def buttons(mech):
    return dict(children(named_block(named_block(mech, MECHANIC), "interactions")))


def edit_button(mech, name, change):
    """The mechanic with one button's text changed by `change`."""
    block = buttons(mech)[name]
    broken = change(block)
    assert broken != block, f"sabotage of {name} changed nothing"
    return mech.replace(block, broken, 1)


def loc_text(language):
    return "\n".join(path.read_text(encoding="utf-8-sig")
                     for path in sorted((ROOT / "localisation").rglob(f"*l_{language}.yml")))


def loc_keys(text):
    return set(re.findall(r"(?m)^ ([^\s:#]+):\d+ ", text))


def loc_value(text, key):
    match = re.search(rf'(?m)^ {re.escape(key)}:\d+ "(.*)"\s*$', text)
    return match.group(1) if match else None


def base_factor(block):
    match = re.search(r"factor = ([0-9.]+)", normalized(named_block(block, "ai_chance")))
    return float(match.group(1)) if match else None


def block_or_empty(text, name, occurrence=1):
    try:
        return named_block(text, name, occurrence)
    except KeyError:
        return ""


def toggle_trigger_parts(button):
    trigger = block_or_empty(button, "trigger")
    choices = block_or_empty(trigger, "OR")
    branches = dict(children(choices)) if choices else {}
    enact = branches.get("AND", "")
    active = normalized(choices)
    if enact:
        active = active.replace(normalized(enact), "", 1)
    return choices, enact, active


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

def check_price(mech):
    problems = []
    found = buttons(mech)
    for ordinance in ORDINANCES:
        power = POWER[ordinance]
        other = "adm" if power == "dip" else "dip"
        button = found.get(f"hlc_enact_{ordinance}_ordinance", "")
        flag = f"has_country_flag = hlc_{ordinance}_ordinance_active"
        modifier = f"hlc_{ordinance}_ordinance_modifier"
        choices, enact, active = toggle_trigger_parts(button)
        if flag not in active:
            problems.append(f"{ordinance}: toggle cannot be triggered while the ordinance is active")
        if f"{power}_power_cost = 50" not in normalized(enact):
            problems.append(f"{ordinance}: the enact trigger lacks {power}_power_cost = 50")
        if f"{other}_power_cost" in normalized(enact):
            problems.append(f"{ordinance}: the enact trigger charges the wrong kind of power ({other})")
        if "_power_cost" in active:
            problems.append(f"{ordinance}: rescinding is incorrectly gated by monarch power")
        effect = block_or_empty(button, "effect")
        rescind = block_or_empty(effect, "if")
        enact_effect = block_or_empty(effect, "else")
        limit = normalized(block_or_empty(rescind, "limit"))
        if flag not in limit:
            problems.append(f"{ordinance}: the free-rescind branch is not limited to an active ordinance")
        if f"clr_country_flag = hlc_{ordinance}_ordinance_active" not in normalized(rescind):
            problems.append(f"{ordinance}: rescinding does not clear its active flag")
        if f"remove_country_modifier = {modifier}" not in normalized(rescind):
            problems.append(f"{ordinance}: rescinding does not remove its modifier")
        if "_power_cost" in normalized(rescind):
            problems.append(f"{ordinance}: rescinding must be free")
        if f"{power}_power_cost = 50" not in normalized(enact_effect):
            problems.append(f"{ordinance}: the enact effect lacks {power}_power_cost = 50")
        if f"{other}_power_cost" in normalized(enact_effect):
            problems.append(f"{ordinance}: the enact effect charges the wrong kind of power ({other})")
        if f"set_country_flag = hlc_{ordinance}_ordinance_active" not in normalized(enact_effect):
            problems.append(f"{ordinance}: enacting does not set its active flag")
        if f"name = {modifier}" not in normalized(enact_effect) or "duration = -1" not in normalized(enact_effect):
            problems.append(f"{ordinance}: enacting does not add its permanent modifier")
    return problems


def check_slots(mech, triggers):
    problems = []
    found = buttons(mech)
    flags = [f"has_country_flag = hlc_{o}_ordinance_active" for o in ORDINANCES]
    for ordinance in ORDINANCES:
        button = found.get(f"hlc_enact_{ordinance}_ordinance", "")
        _, enact, active = toggle_trigger_parts(button)
        if "tooltip = hlc_ordinance_slot_free_tt hlc_ordinance_slot_free = yes" not in normalized(enact):
            problems.append(f"{ordinance}: the enact arm does not require hlc_ordinance_slot_free inside a custom_trigger_tooltip")
        if "hlc_ordinance_slot_free" in active:
            problems.append(f"{ordinance}: rescind must stay available when the slots are full")
    slot = normalized(block_or_empty(triggers, "hlc_ordinance_slot_free"))
    if not (slot.startswith("hlc_ordinance_slot_free = { NOT = { calc_true_if = {")
            and all(flag in slot for flag in flags) and "amount = 2" in slot):
        problems.append("hlc_ordinance_slot_free is not NOT = { calc_true_if over the three flags, amount = 2 }")
    if not all(flag in normalized(block_or_empty(triggers, "hlc_ordinance_over_limit")) for flag in flags):
        problems.append("hlc_ordinance_over_limit does not name all three flags")
    return problems


def check_ai(mech, triggers, vanilla_knows=None):
    problems = []
    needs = {
        "chancery": ("hlc_ordinance_over_limit", "hlc_ordinance_room_needed"),
        "settlement": ("hlc_ordinance_settlement_wanted", "hlc_ordinance_over_limit",
                       "hlc_ordinance_settlement_spent"),
        "cadastral": ("hlc_ordinance_cadastre_wanted", "hlc_ordinance_over_limit",
                      "hlc_ordinance_cadastre_dangerous"),
    }
    found = buttons(mech)
    if len(found) != 3:
        problems.append(f"the mechanic has {len(found)} toggle buttons, expected 3")
    for ordinance in ORDINANCES:
        name = f"hlc_enact_{ordinance}_ordinance"
        block = found.get(name, "")
        factor = base_factor(block) if "ai_chance" in block else None
        if not factor:
            problems.append(f"{name}: ai_chance is missing or its base factor is 0, so the AI can never press it")
            continue
        ai = normalized(named_block(block, "ai_chance"))
        flag = f"has_country_flag = hlc_{ordinance}_ordinance_active"
        if f"factor = 0 {flag} NOT = {{ OR = {{ hlc_ordinance_over_limit = yes" not in ai:
            problems.append(f"{name}: the AI may rescind without a reason")
        if f"NOT = {{ {flag} }}" not in ai:
            problems.append(f"{name}: the AI does not distinguish the enact arm from the rescind arm")
        for need in needs[ordinance]:
            if f"{need} = yes" not in ai:
                problems.append(f"{name}: the AI ignores {need}")
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
        for needle in (f"clr_country_flag = hlc_{ordinance}_ordinance_active",
                       f"has_country_modifier = hlc_{ordinance}_ordinance_modifier",
                       f"remove_country_modifier = hlc_{ordinance}_ordinance_modifier"):
            if needle not in clear:
                problems.append(f"hlc_clear_ordinances_effect lacks {needle}")
    sweep = block_or_empty(effects, "hlc_ordinance_sweep_effect")
    swept = normalized(sweep)
    if "NOT = { has_reform = hlc_crown_authority_reform }" not in swept or "hlc_clear_ordinances_effect = yes" not in swept:
        problems.append("hlc_ordinance_sweep_effect does not clear the ordinances of a country without the crown authority")
    for ordinance in ORDINANCES:
        if (f"has_country_flag = hlc_{ordinance}_ordinance_active" not in swept
                or f"has_country_modifier = hlc_{ordinance}_ordinance_modifier" not in swept):
            problems.append(f"hlc_ordinance_sweep_effect does not look for the {ordinance} ordinance's flag and modifier")
    # Scoping. The sweep runs for every country every year: it must be look-ups only.
    limits = [normalized(body) for _, body in keyed_blocks(sweep, "limit")]
    if len(limits) < 2:
        problems.append("hlc_ordinance_sweep_effect lost one of its two limits")
    for limit in limits:
        leftover = re.sub(r"\b(?:limit|has_country_flag|has_country_modifier|has_reform|OR|NOT|yes)\b|[={}]|\bhlc_\w+", " ", limit)
        if leftover.strip():
            problems.append(f"a sweep limit holds more than flag/modifier/reform look-ups: {leftover.split()}")
    if re.search(r"\b(?:every|any|random|all)_\w+\s*=|\bwhile\s*=|export_to_variable|check_variable", swept):
        problems.append("the sweep iterates a scope or touches a variable, so it is not free for a non-HLC country")
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
    if not re.match(r"limit = \{ owner = \{ has_country_flag = hlc_settlement_ordinance_active", limit):
        problems.append("the settlement limit does not read the owner's ordinance flag (the hook runs in province scope)")
    outside = body.split(limit, 1)[1].split("owner = {", 1)[0] if limit and limit in body else body
    if "estate" in outside or "loyalty" in outside:
        problems.append("an estate effect runs in province scope, outside owner")
    if not re.search(r"(?m)^hlc_settlement_loyalty_timer\s*=\s*\{\s*\}", _mask_comments_and_strings(modifiers)):
        problems.append("hlc_settlement_loyalty_timer is not an empty event modifier")
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


def check_text(texts, mech, action, privilege):
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
        # Every tooltip sentence the mechanic, the action and the privilege name has text.
        source = re.sub(r"#[^\n]*", "", mech + action + privilege)
        named = set(re.findall(r"tooltip = (\w+)", source))
        named.update(re.findall(r"cooldown_desc = (\w+)", source))
        missing = sorted(name for name in named if name not in keys and name not in {"FROM_IS_REBELLIOUS_TT"})
        if missing:
            problems.append(f"{language}: tooltip keys {missing} have no text")
    for ordinance in ORDINANCES:
        enact = loc_value(english, f"hlc_enact_{ordinance}_ordinance_desc") or ""
        power = "diplomatic" if POWER[ordinance] == "dip" else "administrative"
        if f"Enacting costs §Y50§! {power} power" not in enact:
            problems.append(f"the {ordinance} enact text does not state its price")
        if "at most §Ytwo§!" not in enact or "§Y5§!-year cooldown" not in enact:
            problems.append(f"the {ordinance} toggle text does not state the two-slot rule and five-year cooldown")
        if "rescinding costs nothing" not in enact or "same button" not in enact:
            problems.append(f"the {ordinance} toggle text does not explain free rescinding")
    modifier = loc_value(english, "desc_hlc_settlement_ordinance_modifier") or ""
    if "+2" not in modifier or "60%" not in modifier or "manual" not in modifier:
        problems.append("the settlement modifier text does not state the real rule (manual, +2, below 60%)")
    if "two of three ordinances" not in (loc_value(english, "hlc_crown_authority_reform_desc") or ""):
        problems.append("the crown authority's description does not tell the player about the two slots")
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
    for path in sorted((root / "localisation").glob("*_l_english.yml")):
        match = re.search(r' incorporate_vassal_desc:\d+ "(.*)"', path.read_text(encoding="utf-8-sig", errors="replace"))
        if match:
            desc = match.group(1)
            break
    return {
        "default": block_or_empty(subject_text, "default"),
        "incorporated": block_or_empty(subject_text, "incorporated_vassal", 2),
        "penalty": block_or_empty(modifier_text, "base_incorporated_vassal_cost"),
        "desc": desc,
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
    problems += check_price(s["mech"])
    problems += check_slots(s["mech"], s["triggers"])
    problems += check_ai(s["mech"], s["triggers"], vanilla_knows())
    problems += check_cleanup(s["reform"], s["effects"], s["west"])
    problems += check_on_action(s["west"], s["mod_00"], vanilla_00)
    problems += check_evidence(s["evidence"])
    problems += check_loyalty(s["estate_effects"], s["modifiers"])
    problems += check_appanage(s["action"], s["privilege"], s["path_triggers"], s["reform"], texts["english"][0], vanilla)
    problems += check_text(texts, s["mech"], s["action"], s["privilege"])
    return problems


def planted_violations(s, texts, vanilla):
    """Break the sources in memory, one defect at a time, and make sure each break is seen."""
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

    def text(**overrides):
        return check_text({**texts, **overrides}, mech, action, privilege)

    ai_block = lambda b: b.replace(named_block(b, "ai_chance"), "\t\t\tai_chance = {\n\t\t\t\tfactor = 0\n\t\t\t}")
    cases = {
        # price
        "chancery enact without its price": check_price(mech.replace("dip_power_cost = 50", "# free")),
        "settlement paid in the wrong power": check_price(edit_button(mech, "hlc_enact_settlement_ordinance", lambda b: b.replace("adm_power_cost", "dip_power_cost"))),
        "rescinding made to cost power": check_price(edit_button(mech, "hlc_enact_cadastral_ordinance", lambda b: b.replace("clr_country_flag", "adm_power_cost = 10\n\t\t\t\tclr_country_flag", 1))),
        # slots
        "cadastre enacted without the slot rule": check_slots(edit_button(mech, "hlc_enact_cadastral_ordinance", lambda b: b.replace("hlc_ordinance_slot_free = yes", "always = yes")), s["triggers"]),
        "slot rule that allows three": check_slots(mech, s["triggers"].replace("amount = 2", "amount = 3")),
        "slot sentence that is not a sentence": check_slots(mech.replace("tooltip = hlc_ordinance_slot_free_tt", "tooltip = nothing", 1), s["triggers"]),
        "rescind blocked by the slot rule": check_slots(edit_button(
            mech, "hlc_enact_settlement_ordinance",
            lambda b: replace_in_nested_block(
                b, ("trigger", "OR"),
                "has_country_flag = hlc_settlement_ordinance_active",
                "has_country_flag = hlc_settlement_ordinance_active\n\t\t\t\t\thlc_ordinance_slot_free = yes",
            ),
        ), s["triggers"]),
        # AI
        "settlement toggle the AI can never press": check_ai(edit_button(mech, "hlc_enact_settlement_ordinance", ai_block), s["triggers"]),
        "cadastre toggle ignores noble loyalty": check_ai(edit_button(mech, "hlc_enact_cadastral_ordinance", lambda b: b.replace("hlc_ordinance_cadastre_dangerous = yes", "always = no")), s["triggers"]),
        "chancery toggle ignores the slot limit": check_ai(edit_button(mech, "hlc_enact_chancery_ordinance", lambda b: b.replace("hlc_ordinance_over_limit = yes", "always = no")), s["triggers"]),
        "AI toggles an active ordinance without need": check_ai(edit_button(
            mech, "hlc_enact_chancery_ordinance",
            lambda b: replace_in_nested_block(
                b, ("ai_chance",),
                "NOT = { has_country_flag = hlc_chancery_ordinance_active }",
                "has_country_flag = hlc_chancery_ordinance_active",
            ),
        ), s["triggers"]),
        "cadastre enact that ignores its situation": check_ai(edit_button(mech, "hlc_enact_cadastral_ordinance", lambda b: b.replace("hlc_ordinance_cadastre_wanted = yes", "always = yes")), s["triggers"]),
        "undefined AI situation": check_ai(mech, s["triggers"].replace("hlc_ordinance_settlement_spent = {", "hlc_ordinance_settlement_gone = {")),
        "AI situation nothing reads": check_ai(edit_button(mech, "hlc_enact_chancery_ordinance", lambda b: b.replace("hlc_ordinance_room_needed = yes", "always = no")), s["triggers"]),
        "AI trigger the game does not have": check_ai(mech, s["triggers"], lambda name: name != "has_owner_accepted_culture"),
        # clean-up
        "crown authority no longer clears": cleanup(reform=s["reform"].replace("hlc_clear_ordinances_effect = yes", "# nothing")),
        "clear effect leaves a modifier behind": cleanup(effects=s["effects"].replace("remove_country_modifier = hlc_cadastral_ordinance_modifier", "# nothing")),
        "clear effect leaves a flag behind": cleanup(effects=s["effects"].replace("clr_country_flag = hlc_settlement_ordinance_active", "# nothing")),
        "yearly sweep not wired": cleanup(west=s["west"].replace("hlc_ordinance_sweep_effect = yes", "# nothing")),
        "sweep that iterates every province": cleanup(effects=s["effects"].replace("hlc_clear_ordinances_effect = yes\n\t}", "hlc_clear_ordinances_effect = yes\n\t\tevery_owned_province = { limit = { always = yes } }\n\t}", 1)),
        "sweep with a dear limit": cleanup(effects=s["effects"].replace("NOT = { has_reform = hlc_crown_authority_reform }", "NOT = { has_reform = hlc_crown_authority_reform }\n\t\t\tnum_of_owned_provinces_with = { value = 1 always = yes }", 1)),
        "sweep that never dates the bureaucracy": cleanup(effects=s["effects"].replace("set_country_flag = hlc_austrian_bureaucracy_dated", "# nothing")),
        "sweep that forgets the stray modifier": cleanup(effects=s["effects"].replace("has_country_modifier = hlc_cadastral_ordinance_modifier\n\t\t\t}\n\t\t\tNOT", "always = no\n\t\t\t}\n\t\t\tNOT", 1)),
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
        "timer never added hidden": loyalty(effects=replace_in_nested_block(
            s["estate_effects"],
            ("hlc_settlement_ordinance_conversion_effect", "hidden_effect", "add_country_modifier"),
            "hidden = yes",
            "hidden = no",
        )),
        "timer modifier undefined": loyalty(modifiers=sub("modifiers", "hlc_settlement_loyalty_timer = {", "hlc_settlement_loyalty_timer_x = {")),
        "bigger gift": loyalty(effects=sub("estate_effects", "estate_nobles LOYALTY = 2", "estate_nobles LOYALTY = 5")),
        "gift outside the owner scope": loyalty(effects=sub("estate_effects", "\t\towner = {\n\t\t\trip_estate_mood_effect = { ESTATE = estate_nobles LOYALTY = 2 }", "\t\trip_estate_mood_effect = { ESTATE = estate_nobles LOYALTY = 2 }\n\t\towner = {")),
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
        "new key missing in Spanish": text(spanish=(texts["spanish"][0].replace(" hlc_incorporate_appanage_limit_tt:0 ", " hlc_x:0 "), texts["spanish"][1])),
        "fallback that drifts from English": text(french=(texts["french"][0], (texts["french"][1] or "").replace("Fewer than two Chancery Ordinances", "Fewer than three Chancery Ordinances"))),
        "enact text without its price": text(english=(en.replace("Enacting costs §Y50§! diplomatic power", "Enacting costs nothing"), None)),
        "settlement text that over-promises": text(english=(en.replace("The first manual conversion in a year", "Every conversion"), None)),
        "tooltip sentence with no text": check_text(texts, mech.replace("tooltip = hlc_ordinance_slot_free_tt", "tooltip = hlc_ordinance_unwritten_tt", 1), action, privilege),
    }
    if vanilla is not None:
        cases["vanilla's governing capacity penalty changes"] = appanage(vanilla_={**vanilla, "penalty": "base_incorporated_vassal_cost = { governing_capacity = -50 }"})
        cases["vanilla's annexation discount changes"] = appanage(vanilla_={**vanilla, "incorporated": vanilla["incorporated"].replace("6.0", "7.0")})
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
    print(f"HLC ORDINANCES CHECK: PASS (3 toggles priced, slotted and given an AI; clean-up, on_action, loyalty cap and "
          f"appanage chain; {len(LANGUAGES)} languages; {planted} planted violations caught){note}")
    print("LIMIT: static contracts. Only the on_action merge rule was measured in the game (see the evidence file); "
          "the ordinance buttons, the AI and the appanage action were not exercised.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
