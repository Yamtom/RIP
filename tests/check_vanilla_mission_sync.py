"""Three-point sync of the two full-file mission overrides with installed vanilla 1.37.5.

`missions/DOM_Russia_Missions.txt` and `missions/TR_Russian_Minors_Missions.txt`
replace the vanilla files of the same name, so nothing the game patches in
them reaches the mod unless somebody carries it over.

What the check proves
  1. DOM Russia: after the vanilla dynamic-effect macros (country_event_with_insight,
     simple_dynamic_effect, ...) are expanded back into the plain form the mod
     file uses, every series and every mission of vanilla 1.37.5 exists in the
     mod, series headers (slot, potential, DLC gates) are identical, and every
     mission whose body differs is on the reviewed list below with its reason.
     A new vanilla patch, or an unreviewed edit, shows up as a mission that
     differs without being listed.
  2. TR Russian minors: every series potential of the mod carries the vanilla
     1.37.5 custom-nation clause (is_playing_custom_nation in russia_region,
     not a nomad technology group), identical to vanilla's.

DOM_Russia_Missions.txt does not exist in the 1.30.3 donor (Domination arrived
later), so the third point for it is the donor-less comparison above. The
donor-to-1.37.5 drift of TR_Russian_Minors_Missions.txt is recorded in
docs/MISSIONS_VANILLA_SYNC_20261124.uk.md.

Static only. Without an installed EU4 1.37.x the vanilla half skips instead of
guessing; the mod-only half (the TR clause) always runs.
"""
from __future__ import annotations

import re
import sys

from clausewitz_testlib import read, vanilla_read, vanilla_root

MACROS = (
    "country_event_with_insight",
    "simple_dynamic_effect",
    "simple_dynamic_effect_without_alternative",
    "complex_dynamic_effect_without_alternative",
    "complex_dynamic_effect",
)

# Missions whose body differs from expanded vanilla on purpose. Anything else
# that differs is vanilla drift that was not ported, or an unreviewed edit.
REVIEWED_DOM_DEVIATIONS = {
    # Claim pacing: distant rewards grant temporary claims instead of the
    # permanent add_russian_claim (tests/check_claim_pacing.py owns the numbers).
    "mos_rus_window_on_the_west": "claim pacing",
    "mos_rus_conquer_finland": "claim pacing (staged Scandinavian areas)",
    "mos_rus_subjugate_scandinavia": "same effect, mod keeps the tooltip inside hidden_effect",
    "mos_rus_conquer_novgorod": "claim pacing",
    "nov_rus_window_on_the_west": "claim pacing",
    "nov_rus_conquer_finland": "claim pacing (staged Scandinavian areas)",
    "nov_rus_conquer_muscovy": "claim pacing",
    "nov_rus_take_danzig": "claim pacing",
    "nov_rus_involve_in_asian_trade": "claim pacing (focused Central Asian/Lahore routes)",
    "mos_rus_conquer_kazan": "claim pacing",
    "mos_rus_expand_eastwards": "claim pacing",
    "mos_rus_colonize_west_siberia": "claim pacing",
    "mos_rus_colonize_central_siberia": "claim pacing",
    "mos_rus_colonize_eastern_siberia": "claim pacing",
    # Mod content.
    "mos_rus_protect_south_slavs": "rip_create_rus_slavic_culture_group replaces the inline culture group",
    "mos_rus_build_up_army": "rip_russia_balance.1 replaces vanilla's permanent-claim flavor_rus.100",
    "mos_rus_land_of_churches": "russian_orthodox faith, church fervor and icon variables",
    "mos_rus_russian_patriarchate": "rip_faith_is_eastern_orthodox and the Byzantine gate",
    # Same effect, written out by hand in the mod file.
    "rus_solidify_serfdom": "macro expansion repeats the tooltip inside hidden_effect",
    "rus_early_industrialization": "ten explicit random_owned_province instead of the for-macro",
    "rus_dissolve_the_streltsy": "kill-counter flag merged into the same hidden_effect",
}

CUSTOM_NATION_CLAUSE = (
    "AND = { is_playing_custom_nation = yes capital_scope = { region = russia_region } "
    "NOT = { technology_group = nomad_group } }"
)


# --------------------------------------------------------------------------
# A small Clausewitz reader: enough for series and missions, with quoted
# strings kept whole.
# --------------------------------------------------------------------------

def strip_comments(text: str) -> str:
    lines = []
    for line in text.splitlines():
        quoted = False
        kept = []
        for char in line:
            if char == '"':
                quoted = not quoted
            if char == "#" and not quoted:
                break
            kept.append(char)
        lines.append("".join(kept))
    return "\n".join(lines)


def match_brace(text: str, opening: int) -> int:
    depth = 0
    quoted = False
    for index in range(opening, len(text)):
        char = text[index]
        if char == '"':
            quoted = not quoted
        elif not quoted:
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return index
    raise ValueError("unbalanced braces")


def parse(text: str):
    tokens = re.findall(r'"[^"]*"|[{}=]|[^\s{}="]+', strip_comments(text))
    position = 0

    def block():
        nonlocal position
        items = []
        while position < len(tokens):
            token = tokens[position]
            if token == "}":
                position += 1
                return items
            if token == "{":
                position += 1
                items.append((None, block()))
            elif position + 1 < len(tokens) and tokens[position + 1] == "=":
                key = token
                position += 2
                if position < len(tokens) and tokens[position] == "{":
                    position += 1
                    items.append((key, block()))
                else:
                    items.append((key, tokens[position]))
                    position += 1
            else:
                items.append((None, token))
                position += 1
        return items

    return block()


def dump(items) -> str:
    out = []
    for key, value in items:
        head = f"{key} = " if key else ""
        if isinstance(value, list):
            out.append(f"{head}{{ {dump(value)} }}")
        else:
            out.append(f"{head}{value}")
    return " ".join(out)


def series_map(text: str):
    result = {}
    for name, body in parse(text):
        if not isinstance(body, list):
            continue
        head, missions = {}, {}
        for key, value in body:
            is_mission = isinstance(value, list) and any(k in ("icon", "position") for k, _ in value)
            if is_mission and key not in ("potential", "potential_on_load", "trigger", "effect"):
                missions[key] = dump(value)
            else:
                head[key] = dump(value) if isinstance(value, list) else value
        result[name] = {"head": head, "missions": missions}
    return result


# --------------------------------------------------------------------------
# Expanding vanilla's dynamic-effect macros back to plain script.
# --------------------------------------------------------------------------

def macro_definitions() -> dict[str, str] | None:
    root = vanilla_root()
    if root is None:
        return None
    definitions = {}
    for path in sorted((root / "common" / "scripted_effects").glob("*.txt")):
        text = strip_comments(path.read_text(encoding="utf-8-sig", errors="replace"))
        for match in re.finditer(r"(?m)^([A-Za-z0-9_]+)\s*=\s*\{", text):
            if match.group(1) in MACROS:
                opening = match.end() - 1
                definitions[match.group(1)] = text[opening + 1: match_brace(text, opening)]
    missing = set(MACROS) - set(definitions)
    assert not missing, f"vanilla scripted effects not found: {sorted(missing)}"
    return definitions


def macro_arguments(body: str) -> dict[str, str]:
    arguments = {}
    cursor = 0
    pair = re.compile(r"\s*([A-Za-z0-9_]+)\s*=\s*")
    while True:
        match = pair.match(body, cursor)
        if not match:
            return arguments
        key, cursor = match.group(1), match.end()
        if body[cursor] == '"':
            end = body.index('"', cursor + 1)
            arguments[key] = body[cursor + 1: end]
            cursor = end + 1
        elif body[cursor] == "{":
            end = match_brace(body, cursor)
            arguments[key] = body[cursor + 1: end]
            cursor = end + 1
        else:
            bare = re.compile(r"[^\s{}]+").match(body, cursor)
            arguments[key] = bare.group(0)
            cursor = bare.end()


def substitute(definition: str, arguments: dict[str, str]) -> str:
    def optional(text: str) -> str:
        out, index = [], 0
        while index < len(text):
            if text.startswith("[[", index):
                close = text.index("]", index)
                name = text[index + 2: close]
                depth, end = 1, close + 1
                while end < len(text) and depth:
                    depth += {"[": 1, "]": -1}.get(text[end], 0)
                    end += 1
                negated = name.startswith("!")
                if (name.lstrip("!") in arguments) != negated:
                    out.append(optional(text[close + 1: end - 1]))
                index = end
            else:
                out.append(text[index])
                index += 1
        return "".join(out)

    return re.sub(r"\$([A-Za-z0-9_]+)\$", lambda m: arguments.get(m.group(1), ""), optional(definition))


def expand(text: str, definitions: dict[str, str]) -> str:
    text = strip_comments(text)
    changed = True
    while changed:
        changed = False
        for name, definition in definitions.items():
            pattern = re.compile(r"\b" + name + r"\s*=\s*\{")
            match = pattern.search(text)
            while match:
                opening = match.end() - 1
                closing = match_brace(text, opening)
                arguments = macro_arguments(text[opening + 1: closing])
                text = text[: match.start()] + substitute(definition, arguments) + text[closing + 1:]
                changed = True
                match = pattern.search(text)
    return text


# --------------------------------------------------------------------------
# The two contracts.
# --------------------------------------------------------------------------

def dom_drift(mod_text: str, vanilla_text: str, definitions: dict[str, str]) -> list[str]:
    """Problems found comparing the mod's DOM Russia file with expanded vanilla."""
    problems: list[str] = []
    mod = series_map(mod_text)
    vanilla = series_map(expand(vanilla_text, definitions))
    for name in sorted(set(vanilla) - set(mod)):
        problems.append(f"series {name}: in vanilla 1.37.5, missing from the mod")
    for name in sorted(set(mod) - set(vanilla)):
        problems.append(f"series {name}: in the mod, absent from vanilla 1.37.5")
    for name in sorted(set(mod) & set(vanilla)):
        for key in sorted(set(mod[name]["head"]) | set(vanilla[name]["head"])):
            if mod[name]["head"].get(key) != vanilla[name]["head"].get(key):
                problems.append(f"series {name}: header field {key} differs from vanilla")
        mod_missions, vanilla_missions = mod[name]["missions"], vanilla[name]["missions"]
        for mission in sorted(set(vanilla_missions) - set(mod_missions)):
            problems.append(f"{name}/{mission}: in vanilla 1.37.5, missing from the mod")
        for mission in sorted(set(mod_missions) - set(vanilla_missions)):
            problems.append(f"{name}/{mission}: in the mod, absent from vanilla 1.37.5")
        for mission in sorted(set(mod_missions) & set(vanilla_missions)):
            if mod_missions[mission] != vanilla_missions[mission] and mission not in REVIEWED_DOM_DEVIATIONS:
                problems.append(f"{name}/{mission}: body differs from vanilla and is not on the reviewed list")
    return problems


def minors_clause_problems(mod_text: str, vanilla_text: str | None) -> list[str]:
    """Problems with the custom-nation clause in every TR series potential."""
    problems: list[str] = []
    mod = parse(mod_text)
    series = [(name, body) for name, body in mod if isinstance(body, list)]
    if len(series) != 5:
        problems.append(f"expected 5 TR series, found {len(series)}")
    for name, body in series:
        potentials = [value for key, value in body if key == "potential"]
        if len(potentials) != 1:
            problems.append(f"{name}: expected one potential block")
            continue
        ors = [value for key, value in potentials[0] if key == "OR"]
        if len(ors) != 1:
            problems.append(f"{name}: potential has no single OR block")
            continue
        clauses = [dump([("AND", value)]) for key, value in ors[0] if key == "AND"]
        if clauses != [CUSTOM_NATION_CLAUSE]:
            problems.append(f"{name}: custom-nation clause missing or altered")
    if vanilla_text is not None:
        vanilla_clauses = set()
        for name, body in parse(vanilla_text):
            for key, value in body:
                if key == "potential":
                    for okey, ovalue in value:
                        if okey == "OR":
                            vanilla_clauses |= {dump([("AND", v)]) for k, v in ovalue if k == "AND"}
        if vanilla_clauses != {CUSTOM_NATION_CLAUSE}:
            problems.append("vanilla 1.37.5 no longer carries the clause the mod copies; re-review the TR series")
    return problems


def self_test(mod_dom: str, vanilla_dom: str, definitions, mod_tr: str) -> list[str]:
    """Damaged variants must be caught; returns the list of misses."""
    misses = []

    def expect(label: str, problems: list[str]) -> None:
        if not problems:
            misses.append(label)

    # Drop a vanilla series from the mod.
    first_series = re.search(r"(?m)^mos_rus_handle_succession\s*=\s*\{", mod_dom)
    damaged = mod_dom[: first_series.start()] + "mos_rus_removed_series = {" + mod_dom[first_series.end():]
    expect("renamed series", dom_drift(damaged, vanilla_dom, definitions))

    # Edit a mission that is not on the reviewed list.
    start = mod_dom.index("mos_the_civil_war = {")
    damaged = mod_dom[:start] + re.sub(r"position = 1\b", "position = 9", mod_dom[start:], count=1)
    assert damaged != mod_dom, "mutation did not apply"
    expect("moved position of an unreviewed mission", dom_drift(damaged, vanilla_dom, definitions))

    # Corrupt a header.
    damaged = mod_dom.replace('has_dlc = "Domination"', 'has_dlc = "Dominaton"', 1)
    expect("misspelt DLC gate", dom_drift(damaged, vanilla_dom, definitions))

    # A reviewed deviation must not hide a missing mission.
    damaged = mod_dom.replace("rus_the_glorious_revolution = {", "rus_the_glorious_revolution_x = {", 1)
    expect("renamed mission", dom_drift(damaged, vanilla_dom, definitions))

    # The TR clause: removed, region changed, nomad guard dropped.
    clause = re.search(r"\t+AND = \{\r?\n\t+is_playing_custom_nation = yes.*?\n\t+\}\r?\n\t+\}\r?\n", mod_tr, re.S)
    assert clause, "TR clause not found in the mod text"
    expect("clause removed from one series", minors_clause_problems(mod_tr.replace(clause.group(0), "", 1), None))
    expect("clause region changed", minors_clause_problems(mod_tr.replace("region = russia_region", "region = ural_region", 1), None))
    expect("nomad guard dropped", minors_clause_problems(mod_tr.replace("technology_group = nomad_group", "technology_group = western", 1), None))
    return misses


def main() -> int:
    mod_tr = read("missions/TR_Russian_Minors_Missions.txt")
    mod_dom = read("missions/DOM_Russia_Missions.txt")
    vanilla_tr = vanilla_read("missions/TR_Russian_Minors_Missions.txt")
    vanilla_dom = vanilla_read("missions/DOM_Russia_Missions.txt")

    failures = minors_clause_problems(mod_tr, vanilla_tr)
    note = "vanilla half skipped (no installed EU4 1.37.x)"
    if vanilla_dom is not None:
        definitions = macro_definitions()
        failures += dom_drift(mod_dom, vanilla_dom, definitions)
        for label in self_test(mod_dom, vanilla_dom, definitions, mod_tr):
            failures.append(f"self-test: damaged variant not caught: {label}")
        note = (f"{len(series_map(mod_dom))} DOM series equal to expanded vanilla 1.37.5 apart from "
                f"{len(REVIEWED_DOM_DEVIATIONS)} reviewed missions; 7 damaged variants caught")
    if failures:
        print("VANILLA MISSION SYNC FAILED:")
        for item in failures:
            print(" ", item)
        return 1
    print(f"VANILLA MISSION SYNC PASS: TR custom-nation clause on 5 series; {note}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
