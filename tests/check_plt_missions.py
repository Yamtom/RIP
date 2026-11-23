"""Static contracts for Polotsk's national mission tree (missions/PLT_Polotsk_Missions.txt).

PLT lost the Third Rome tree (it opens with Moscow and Novgorod) and had only generic
missions. The tree that replaces it has three series in columns 1-3 (the Dvina, White
Ruthenia, the Grand Duchy); columns 4-5 stay generic. Asserted here:

  * layout: three series, slots 1-3, generic = no only there, one root per column, rows
    start at 1 without holes, every arrow runs down the column of its parent (the one
    cross-column arrow spans one row and one column), nothing reaches the Diaspora rows;
  * claims: territory is rewarded only with temporary claims (add_claim = ROOT) behind a
    guard, one area at a time, and each reward is the area the next mission asks the player
    to hold; the claimed areas contain neither Polotsk nor what the same mission requires;
  * the capstone asks for exactly what the decision to form Belarus asks for;
  * costs charged in a trigger are deducted in the effect;
  * no other series gates PLT, the old tree does not list it, the decisions that create PLT
    swap the missions;
  * every mission has a title and a description in English and an identical copy in the
    French, German and Spanish replace files; every modifier it applies exists, has a
    display name and a description, and is called through the API of its scope.

Static only: nothing here runs the game. A planted-violation suite at the end proves that
each contract fails on a spoiled copy of the tree.
"""
from __future__ import annotations

import re
import sys

from clausewitz_testlib import ROOT, _mask_comments_and_strings, named_block, read, vanilla_read

MISSIONS = "missions/PLT_Polotsk_Missions.txt"
ENGLISH = "localisation/RIP_shared_belarus_affairs_l_english.yml"
MODIFIERS = "common/event_modifiers/RIP_BELARUS_modifiers.txt"
DECISIONS = "decisions/PolesianBelarusianNations.txt"
SERIES = ("plt_missions_1", "plt_missions_2", "plt_missions_3")
TALL_DIASPORA_ROW = 24
ROOTS = {"plt_city_of_sophia": 1, "plt_old_principality": 2, "plt_vilnius_terms": 3}
NOT_MISSIONS = {"potential", "potential_on_load", "ai_weight"}

# Claim rewards: mission -> scopes that receive add_claim. Each column-2 reward is the area the
# next mission asks the player to hold; the Dvina road claims the two Livonian provinces.
EXPECTED_CLAIMS = {
    "plt_old_principality": {"white_ruthenia_area"},
    "plt_white_ruthenia": {"minsk_area"},
    "plt_minsk_lands": {"pripyat_area"},
    "plt_pripyat_marshes": {"smolensk_area"},
    "plt_riga_road": {"273", "38"},
}
HELD_BY_NEXT = {
    "plt_old_principality": "plt_white_ruthenia",
    "plt_white_ruthenia": "plt_minsk_lands",
    "plt_minsk_lands": "plt_pripyat_marshes",
}
# EU4 1.37.5 map/area.txt. Used when the installed game is absent; compared when it is present.
AREAS = {
    "white_ruthenia_area": {292, 771, 4246},
    "minsk_area": {276, 4115, 4242, 4544},
    "pripyat_area": {278, 1941, 4537, 4545},
    "smolensk_area": {293, 297, 4244, 4245},
    "pskov_area": {274, 275, 1960, 4148},
}
POLOTSK = 275
PROVINCE_SCOPE_KEYS = ("local_", "province_trade_power")


# ---------------------------------------------------------------- parsing

def children(text: str) -> list[tuple[str, str]]:
    """(name, body) of every `name = { ... }` that sits directly inside text."""
    masked = _mask_comments_and_strings(text)
    found, depth, name, start = [], 0, None, 0
    for match in re.finditer(r"([A-Za-z0-9_.:]+)\s*=\s*\{|\{|\}", masked):
        if match.group(0) == "}":
            depth -= 1
            if depth == 0 and name is not None:
                found.append((name, text[start:match.start()]))
                name = None
        else:
            if depth == 0 and match.group(1):
                name, start = match.group(1), match.end()
            depth += 1
    return found


def own_text(text: str) -> str:
    """text with everything inside nested blocks blanked, so only its own scalars remain."""
    out, depth = [], 0
    for char in _mask_comments_and_strings(text):
        if char == "{":
            depth += 1
            out.append(" ")
        elif char == "}":
            depth -= 1
            out.append(" ")
        else:
            out.append(char if depth == 0 or char in "\r\n" else " ")
    return "".join(out)


def child(body: str, *names: str) -> str:
    for name in names:
        body = next((inner for key, inner in children(body) if key == name), "")
    return body


def flat(text: str) -> str:
    return " ".join(_mask_comments_and_strings(text).split())


def parse(text: str) -> dict[str, dict]:
    series: dict[str, dict] = {}
    for sname, sbody in children(text):
        scalars = own_text(sbody)
        slot = re.search(r"\bslot\s*=\s*(\d+)", scalars)
        info = {
            "slot": int(slot[1]) if slot else None,
            "generic": (re.search(r"\bgeneric\s*=\s*(\w+)", scalars) or [None, None])[1],
            "potential": child(sbody, "potential"),
            "missions": {},
        }
        for mname, mbody in children(sbody):
            if mname in NOT_MISSIONS:
                continue
            position = re.search(r"\bposition\s*=\s*(\d+)", own_text(mbody))
            reqs = re.search(r"required_missions\s*=\s*\{([^}]*)\}", _mask_comments_and_strings(mbody))
            info["missions"][mname] = {
                "slot": info["slot"],
                "pos": int(position[1]) if position else None,
                "reqs": re.findall(r"[A-Za-z0-9_]+", reqs[1]) if reqs else [],
                "trigger": child(mbody, "trigger"),
                "effect": child(mbody, "effect"),
            }
        series[sname] = info
    return series


def missions_of(series: dict[str, dict]) -> dict[str, dict]:
    return {name: m for info in series.values() for name, m in info["missions"].items()}


def claim_scopes(effect: str) -> dict[str, str]:
    """scope (area name or province id) -> block, for every scope of an effect that grants add_claim."""
    return {name: body for name, body in children(effect)
            if re.search(r"\badd_claim\b", _mask_comments_and_strings(body))}


def areas() -> dict[str, set[int]]:
    text = vanilla_read("map/area.txt")
    if not text:
        return {name: set(ids) for name, ids in AREAS.items()}
    parsed = {}
    for match in re.finditer(r"(?m)^\s*([a-z0-9_]+_area)\s*=\s*\{([^}]*)\}", re.sub(r"#[^\n]*", "", text)):
        parsed[match[1]] = {int(pid) for pid in re.findall(r"\b\d+\b", match[2])}
    return parsed


def entries(path: str) -> dict[str, str]:
    return dict(re.findall(r'^ ([A-Za-z0-9_.\-]+):\d+ "(.*)"\s*$', read(path), re.M))


# ---------------------------------------------------------------- contracts

def layout_violations(text: str) -> list[str]:
    out = []
    series = parse(text)
    if tuple(series) != SERIES:
        return [f"series are {tuple(series)}, expected {SERIES}"]
    missions = missions_of(series)
    slots = {name: info["slot"] for name, info in series.items()}
    if sorted(slots.values()) != [1, 2, 3]:
        out.append(f"series must fill columns 1-3 exactly, got {slots}")
    for name, info in series.items():
        if info["generic"] != "no":
            out.append(f"{name}: a filled column must say generic = no")
        potential = _mask_comments_and_strings(info["potential"])
        if not re.search(r"\btag\s*=\s*PLT\b", potential):
            out.append(f"{name}: potential must be gated by tag = PLT")
        if "map_setup = map_setup_random" not in potential:
            out.append(f"{name}: potential must exclude the random map setup")
    if re.search(r"\bslot\s*=\s*[45]\b", _mask_comments_and_strings(text)):
        out.append("columns 4 and 5 belong to the generic missions")

    cells: dict[tuple[int, int], str] = {}
    for name, m in missions.items():
        if m["pos"] is None:
            out.append(f"{name}: no position")
            continue
        cell = (m["slot"], m["pos"])
        if cell in cells:
            out.append(f"{name}: shares cell {cell} with {cells[cell]}")
        cells[cell] = name
    for slot in (1, 2, 3):
        rows = sorted(p for (s, p) in cells if s == slot)
        if rows != list(range(1, len(rows) + 1)):
            out.append(f"column {slot}: rows {rows} must run 1..n without a hole")
        if rows and rows[-1] >= TALL_DIASPORA_ROW:
            out.append(f"column {slot}: row {rows[-1]} reaches the Diaspora rows")

    roots = {name: m["slot"] for name, m in missions.items() if not m["reqs"]}
    if roots != ROOTS:
        out.append(f"roots are {roots}, expected {ROOTS}")
    cross = []
    for name, m in missions.items():
        for src_name in m["reqs"]:
            src = missions.get(src_name)
            if src is None:
                out.append(f"{name}: requires unknown mission {src_name}")
            elif src["pos"] is None or m["pos"] is None or src["pos"] >= m["pos"]:
                out.append(f"{src_name} -> {name}: arrows must run down")
            elif src["slot"] == m["slot"]:
                if m["pos"] - src["pos"] != 1:
                    out.append(f"{src_name} -> {name}: a card sits between parent and child")
            else:
                cross.append((src_name, name))
                if m["pos"] - src["pos"] != 1 or abs(m["slot"] - src["slot"]) != 1:
                    out.append(f"{src_name} -> {name}: a cross-column arrow spans one row and one column")
        if m["reqs"] and not any(missions.get(r, {}).get("slot") == m["slot"] for r in m["reqs"]):
            out.append(f"{name}: needs a parent in its own column, the arrow runs down the parent's column")
    if cross != [("plt_riga_road", "plt_white_rus")]:
        out.append(f"cross-column arrows are {cross}, expected only plt_riga_road -> plt_white_rus")
    return out


def claim_violations(text: str, area_map: dict[str, set[int]] | None = None) -> list[str]:
    out = []
    area_map = area_map or areas()
    masked = _mask_comments_and_strings(text)
    for banned in ("add_permanent_claim", "add_russian_claim"):
        if banned in masked:
            out.append(f"{banned}: the tree grants temporary claims only")
    if re.search(r"\badd_claim\s*=\s*(?!ROOT\b)\w+", masked):
        out.append("add_claim must name ROOT")
    if re.search(r"_region\s*=\s*\{", masked):
        out.append("a region-wide scope would hand out claims in bulk")
    missions = missions_of(parse(text))
    for name, m in missions.items():
        scopes = claim_scopes(m["effect"])
        wanted = EXPECTED_CLAIMS.get(name, set())
        if set(scopes) != wanted:
            out.append(f"{name}: claims on {sorted(scopes)}, expected {sorted(wanted)}")
        trigger = flat(m["trigger"])
        for scope, block in scopes.items():
            guarded = flat(block)
            if "NOT = { is_claim = ROOT }" not in guarded or "NOT = { is_core = ROOT }" not in guarded:
                out.append(f"{name}: the claim on {scope} lacks its is_claim / is_core guard")
            if "limit = {" not in guarded and "limit = {" not in flat(m["effect"]):
                out.append(f"{name}: the claim on {scope} has no limit")
            if scope.endswith("_area"):
                provinces = area_map.get(scope, set())
                if not 0 < len(provinces) <= 4:
                    out.append(f"{name}: {scope} holds {len(provinces)} provinces; one reward hands out at most four")
                if POLOTSK in provinces:
                    out.append(f"{name}: {scope} contains Polotsk itself")
                if f"{scope} = {{ type = all" in trigger:
                    out.append(f"{name}: claims the area it already asks the player to hold")
        # Staging: the area claimed here is the one the next mission asks to hold.
        follower = HELD_BY_NEXT.get(name)
        if follower and follower in missions:
            held = re.findall(r"\b([a-z0-9_]+_area)\s*=\s*\{ type = all", flat(missions[follower]["trigger"]))
            if set(held) != wanted:
                out.append(f"{follower}: asks to hold {held}, but {name} claims {sorted(wanted)}")
        # A claim reward must sit behind something the player did.
        if wanted and name != "plt_old_principality":
            if not re.search(r"country_or_non_sovereign_subject_holds|\bowns\b|\btreasury\s*=", trigger):
                out.append(f"{name}: a claim reward needs a holding or a payment in its trigger")
    first = missions.get("plt_old_principality")
    if first and "owns = 275" not in flat(first["trigger"]):
        out.append("plt_old_principality: the opening claims need Polotsk in hand")
    return out


def reward_violations(text: str) -> list[str]:
    out = []
    missions = missions_of(parse(text))
    for name, m in missions.items():
        trigger, effect = flat(m["trigger"]), flat(m["effect"])
        for cost in re.findall(r"\btreasury = (\d+)", trigger):
            if f"add_treasury = -{cost}" not in effect:
                out.append(f"{name}: charges {cost} in the trigger but does not pay it in the effect")
    # The capstone asks for what the decision to form Belarus asks for.
    allow = flat(child(read(DECISIONS), "country_decisions", "belarus_nation", "allow"))
    wanted = sorted(re.findall(r"owns_core_province = (\d+)", allow))
    if len(wanted) != 7:
        out.append(f"the decision to form Belarus asks for {len(wanted)} core provinces, this test expects 7")
    capstone = missions.get("plt_white_rus")
    if capstone is None:
        return out + ["plt_white_rus is missing"]
    trigger = flat(capstone["trigger"])
    if sorted(re.findall(r"owns_core_province = (\d+)", trigger)) != wanted:
        out.append("plt_white_rus: its core provinces differ from the decision to form Belarus")
    tech = re.search(r"adm_tech = (\d+)", allow)
    if not tech or f"adm_tech = {tech[1]}" not in trigger:
        out.append("plt_white_rus: administrative technology differs from the decision to form Belarus")
    if "is_free_or_tributary_trigger = yes" not in trigger:
        out.append("plt_white_rus: must ask for a free or tributary state, like the decision")
    if sorted(capstone["reqs"]) != ["plt_pripyat_marshes", "plt_riga_road"]:
        out.append("plt_white_rus: needs the last White Ruthenian mission and the Dvina road")
    vilnius = flat(missions["plt_vilnius_terms"]["trigger"]) if "plt_vilnius_terms" in missions else ""
    for needle in ("alliance_with = LIT", "is_subject_of = LIT"):
        if needle not in vilnius:
            out.append(f"plt_vilnius_terms: the terms with Vilnius must accept {needle}")
    return out


def holding_violations(text: str, area_map: dict[str, set[int]] | None = None) -> list[str]:
    """The three holding missions ask for whole areas, held directly or through a subject."""
    out = []
    area_map = area_map or areas()
    missions = missions_of(parse(text))
    for name, area in (("plt_white_ruthenia", "white_ruthenia_area"),
                       ("plt_minsk_lands", "minsk_area"),
                       ("plt_pripyat_marshes", "pripyat_area")):
        if name not in missions:
            out.append(f"{name} is missing")
            continue
        if f"{area} = {{ type = all country_or_non_sovereign_subject_holds = ROOT }}" not in flat(missions[name]["trigger"]):
            out.append(f"{name}: must hold all of {area}")
        if area_map.get(area) != AREAS[area]:
            out.append(f"{area}: {sorted(area_map.get(area, set()))} is not {sorted(AREAS[area])}")
    return out


def world_violations(others: dict[str, str] | None = None) -> list[str]:
    """Nothing else gates PLT; the old tree is silent about it; the decisions swap the missions."""
    out = []
    if others is None:
        others = {path.name: path.read_text(encoding="utf-8-sig", errors="replace")
                  for path in sorted((ROOT / "missions").glob("*.txt")) if path.name != MISSIONS.split("/")[1]}
    for name, body in others.items():
        if re.search(r"\btag\s*=\s*PLT\b", re.sub(r"#[^\n]*", "", body)):
            out.append(f"{name}: another series gates PLT and would stack with this tree")
    for decision, source in (("polotsk_nation", DECISIONS), ("rip_seat_become_plt", "decisions/RIP_CapitalLoss.txt")):
        block = flat(named_block(read(source), decision))
        if "change_tag = PLT" not in block or "swap_non_generic_missions = yes" not in block:
            out.append(f"{decision}: must change the tag to PLT and swap the missions")
    return out


def loc_violations(text: str, english: dict[str, str], fallbacks: dict[str, dict[str, str]],
                   modifier_text: str) -> list[str]:
    out = []
    missions = missions_of(parse(text))
    keys = [f"{name}_{part}" for name in missions for part in ("title", "desc")]
    modifiers = dict(children(modifier_text))
    scopes: dict[str, set[str]] = {}
    for m in missions.values():
        effect = _mask_comments_and_strings(m["effect"])
        for scope, call in (("country", "add_country_modifier"), ("province", "add_province_modifier")):
            for used in re.findall(rf"{call}\s*=\s*\{{\s*name\s*=\s*([A-Za-z0-9_]+)", effect):
                scopes.setdefault(used, set()).add(scope)
    for used, kinds in scopes.items():
        keys += [used, f"desc_{used}"]
        if used not in modifiers:
            out.append(f"modifier {used} is not defined in {MODIFIERS}")
        elif len(kinds) != 1:
            out.append(f"modifier {used} is applied as both a country and a province modifier")
        else:
            fields = re.findall(r"^\s*([a-z_]+)\s*=", modifiers[used], re.M)
            local = [f for f in fields if f.startswith(PROVINCE_SCOPE_KEYS)]
            if kinds == {"country"} and local:
                out.append(f"modifier {used}: province fields {local} in a country modifier")
            if kinds == {"province"} and len(local) != len(fields):
                out.append(f"modifier {used}: country fields in a province modifier")
    for key in keys:
        value = english.get(key, "")
        if not value.strip():
            out.append(f"English text missing: {key}")
        if "!" in value or '"' in value:
            out.append(f"{key}: no exclamation marks or quotation marks in the text")
        for lang, table in fallbacks.items():
            if table.get(key) != english.get(key):
                out.append(f"{lang} replace copy of {key} differs from the English text")
    titles = [english.get(f"{name}_title", "") for name in missions]
    if len(set(titles)) != len(titles):
        out.append("two missions share a title")
    if "alternative-history" not in english.get("plt_city_of_sophia_desc", ""):
        out.append("plt_city_of_sophia: the description must label a sovereign Polotsk an alternative-history path")
    return out


def corpus() -> tuple[dict[str, str], dict[str, dict[str, str]], str]:
    english = entries(ENGLISH)
    fallbacks = {lang: entries(f"localisation/replace/RIP_shared_belarus_content_l_{lang}.yml")
                 for lang in ("french", "german", "spanish")}
    return english, fallbacks, read(MODIFIERS)


def violations(text: str) -> list[str]:
    english, fallbacks, modifiers = corpus()
    return (layout_violations(text) + claim_violations(text) + reward_violations(text)
            + holding_violations(text) + world_violations()
            + loc_violations(text, english, fallbacks, modifiers))


# ---------------------------------------------------------------- planted violations

def planted(text: str) -> list[tuple[str, str, str]]:
    """(label, spoiled text, fragment the violation list must contain)."""
    head, marker, tail = text.partition("\nplt_missions_1 = {")
    assert marker, "the first series was not found"

    def swap(old: str, new: str, count: int = 1) -> str:
        # Only the code below the header comment: the comment quotes add_claim and tag = PLT.
        assert old in tail, old
        return head + marker + tail.replace(old, new, count)

    return [
        ("permanent claim", swap("add_claim = ROOT", "add_permanent_claim = ROOT"), "temporary claims only"),
        ("claim for another owner", swap("add_claim = ROOT", "add_claim = LIT"), "add_claim must name ROOT"),
        ("column 4 filled", swap("slot = 3\n", "slot = 4\n"), "belong to the generic missions"),
        ("generic left on", swap("\tgeneric = no", "\tgeneric = yes"), "generic = no"),
        ("wrong tag", swap("tag = PLT", "tag = VTB"), "tag = PLT"),
        ("shared cell", swap("position = 2\n", "position = 1\n"), "shares cell"),
        ("hole in a column", swap("position = 4\n\n\t\tprovinces_to_highlight = {\n\t\t\tOR = {\n\t\t\t\tprovince_id = 273",
                                  "position = 6\n\n\t\tprovinces_to_highlight = {\n\t\t\tOR = {\n\t\t\t\tprovince_id = 273"),
         "without a hole"),
        ("tree reaches the Diaspora rows", swap("position = 5\n", "position = 24\n"), "Diaspora rows"),
        ("arrow skips a card", swap("required_missions = { plt_dvina_castles }", "required_missions = { plt_city_of_sophia }"),
         "a card sits between"),
        ("capstone loses the Dvina road", swap("required_missions = { plt_pripyat_marshes plt_riga_road }",
                                               "required_missions = { plt_pripyat_marshes }"), "cross-column arrows"),
        ("claim burst across a region", swap("smolensk_area = {", "russia_region = {"), "region-wide"),
        ("unguarded claim", swap("NOT = { is_claim = ROOT }", "NOT = { is_core = ROOT }"), "guard"),
        ("reward claims the wrong area", swap("minsk_area = {\n\t\t\t\tlimit", "pripyat_area = {\n\t\t\t\tlimit"), "claims on"),
        ("free toll", swap("\t\t\tadd_treasury = -150\n", ""), "does not pay"),
        ("capstone drops a province", swap("\t\t\towns_core_province = 4246\n", ""), "core provinces differ"),
        ("capstone weakens the tech gate", swap("adm_tech = 15", "adm_tech = 10"), "technology differs"),
        ("holding mission accepts any province", swap("white_ruthenia_area = {\n\t\t\t\ttype = all",
                                                      "white_ruthenia_area = {\n\t\t\t\ttype = any"), "must hold all"),
        ("Vilnius accepts only an alliance", swap("\t\t\t\tis_subject_of = LIT\n", ""), "is_subject_of"),
        ("modifier called through the wrong API", swap("add_province_modifier = {\n\t\t\t\t\tname = polotsk_sophia_precinct",
                                                       "add_country_modifier = {\n\t\t\t\t\tname = polotsk_sophia_precinct"),
         "province fields"),
        ("unknown modifier", swap("name = dvina_trade_charter", "name = dvina_no_such_charter"), "not defined"),
        ("mission without a text", head + marker + tail.replace("plt_dvina_castles", "plt_dvina_towers"), "English text missing"),
    ]


def run_planted(text: str) -> int:
    caught = 0
    for label, spoiled, fragment in planted(text):
        assert spoiled != text, f"{label}: the planted text equals the original"
        assert any(fragment in found for found in violations(spoiled)), \
            f"planted violation not caught: {label} (expected {fragment!r})"
        caught += 1

    # Contracts that live outside the mission text: a French copy that drifted, a second series
    # gating PLT, a Third Rome tree that lists PLT again.
    english, fallbacks, modifiers = corpus()
    drifted = {**fallbacks, "french": {**fallbacks["french"], "plt_riga_road_desc": "changed"}}
    assert any("differs from the English" in v for v in loc_violations(text, english, drifted, modifiers)), "french drift"
    assert any("another series gates PLT" in v for v in world_violations({"Other.txt": "potential = { tag = PLT }"})), "second series"
    assert not world_violations({"Quiet.txt": "# tag = PLT is only a comment\npotential = { tag = LIT }"}), "comment tripped it"
    assert any("a region-wide" in v for v in claim_violations(text.replace("smolensk_area = {", "balkan_region = {"))), "region"
    assert any("holds 5 provinces" in v for v in claim_violations(text, {**areas(), "smolensk_area": {1, 2, 3, 4, 5}})), "big area"
    assert any("contains Polotsk" in v for v in claim_violations(text, {**areas(), "smolensk_area": {275, 293}})), "own capital"
    return caught + 6


def main() -> int:
    text = read(MISSIONS)
    found = violations(text)
    if found:
        print("PLT MISSIONS FAIL:\n  " + "\n  ".join(found))
        return 1
    caught = run_planted(text)
    series = parse(text)
    heights = {info["slot"]: max(m["pos"] for m in info["missions"].values()) for info in series.values()}
    print(f"PLT MISSIONS PASS: {len(missions_of(series))} missions, columns 1-3 reach rows "
          f"{[heights[slot] for slot in sorted(heights)]}, temporary claims only, four languages, "
          f"{caught} planted violations caught")
    return 0


if __name__ == "__main__":
    sys.exit(main())
