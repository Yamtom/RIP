"""Static mission contracts for Ruthenian additions to Russia, the minors, the Tatars and Austria."""
from __future__ import annotations

import re
import sys
from pathlib import Path

from check_vanilla_mission_sync import dump, parse
from clausewitz_testlib import ROOT, read, vanilla_root

NEW_FILE = "zzzz_Ruthenian_Contacts_Horde_Habsburg.txt"
LATEST_NEW_ROW = 18  # the lowest row the later-loading series must clear (Tatar tribute row 18)
# Vanilla files that fill column 5 for Tatar or Habsburg tags (measured on 1.37.5 with the check below).
KNOWN_COLUMN_FILES = ("zzz_WoC_Shared_Horde_Missions.txt", "WoC_Austrian_Missions.txt", "WoC_Tatar_Missions.txt")
TATAR_TAGS = ("GOL", "CRI", "NOG", "KAZ", "SHY", "GLH", "SIB", "BSH", "AST", "QAS", "KZH", "CHG", "KAS")
TAGS = TATAR_TAGS + ("HAB", "AUH")
TAG_HELPERS = ("is_tatar_nation", "was_tatar_nation", "is_mongol_nation", "is_moghulistan_nation")

MISSION_KEYS = {
    "rip_rus_kyiv_metropolia": ("localisation/RIP_MOS_RUS_realm_l_english.yml", "replace"),
    "tr_rip_ruthenian_charters": ("localisation/RIP_MOS_RUS_realm_l_english.yml", "replace"),
    "rip_tat_ruthenian_yarlyks": ("localisation/RIP_shared_ruthenian_contacts_l_english.yml", "contacts"),
    "rip_hab_galician_ruthenians_classic": ("localisation/RIP_shared_ruthenian_contacts_l_english.yml", "contacts"),
    "rip_hab_galician_ruthenians": ("localisation/RIP_shared_ruthenian_contacts_l_english.yml", "contacts"),
}
MODIFIERS = {
    "rip_rus_kyivan_clergy": "common/event_modifiers/RIP_ruthenian_contacts_modifiers.txt",
    "rip_tat_ruthenian_tribute": "common/event_modifiers/RIP_ruthenian_contacts_modifiers.txt",
    "rip_hab_ruthenian_clergy": "common/event_modifiers/RIP_ruthenian_contacts_modifiers.txt",
    "tr_rip_ruthenian_charters": "common/event_modifiers/RIP_TR_minors_modifiers.txt",
}


def series_list(text: str):
    """[(series, slot, generic, potential_dump, {mission: (position, required, body)})] for one file."""
    result = []
    for name, body in parse(text):
        if not isinstance(body, list):
            continue
        slot = generic = potential = None
        missions = {}
        for key, value in body:
            if key == "slot":
                slot = int(value)
            elif key == "generic":
                generic = value
            elif key == "potential":
                potential = dump(value)
            elif isinstance(value, list) and any(k in ("icon", "position") for k, _ in value):
                position = next((int(v) for k, v in value if k == "position"), None)
                required = next((dump(v) for k, v in value if k == "required_missions"), "")
                missions[key] = (position, required, dump(value))
        result.append((name, slot, generic, potential or "", missions))
    return result


def applies(potential: str) -> bool:
    """Could a Tatar or Habsburg country satisfy this potential? Over-approximates on purpose."""
    return any(re.search(rf"\btag = {tag}\b|\bwas_tag = {tag}\b", potential) for tag in TAGS) or any(
        helper in potential for helper in TAG_HELPERS)


def column_files() -> dict[str, str]:
    """Every mission file that loads: vanilla ones, then the mod's, mod names replacing vanilla names."""
    files: dict[str, str] = {}
    root = vanilla_root()
    if root is not None:
        for path in (root / "missions").glob("*.txt"):
            files[path.name] = path.read_text(encoding="utf-8-sig", errors="replace")
    for path in (ROOT / "missions").glob("*.txt"):
        files[path.name] = path.read_text(encoding="utf-8-sig")
    return files


def load_order_problems(new_name: str, files: dict[str, str], known: tuple[str, ...]) -> list[str]:
    problems = []
    mine = new_name.lower()
    for name in known:
        if name.lower() > mine:
            problems.append(f"{new_name} sorts before {name}, which fills the same column and would be pushed down")
    for name, text in files.items():
        if name == new_name:
            continue
        for series, slot, generic, potential, missions in series_list(text):
            if slot != 5 or generic == "yes" or not missions or not applies(potential):
                continue
            # A series that loads after the new file only stacks below it, which is harmless as long as
            # its declared rows start under the new missions; one that starts higher would sit above them.
            lowest = min((position for position, _, _ in missions.values() if position), default=0)
            classic_tatar = ('NOT = { has_dlc = "Winds of Change" }' in potential
                             and not re.search(r"\b(?:was_)?tag = (HAB|AUH)\b", potential))
            tail = 6 if classic_tatar else LATEST_NEW_ROW
            if name.lower() > mine and lowest <= tail:
                problems.append(f"{name}/{series} fills column 5 for Tatar or Habsburg tags, loads after {new_name} "
                                f"and starts at row {lowest}, not below row {tail}")
    return problems


def tallest_row(files: dict[str, str], new_name: str, tags: tuple[str, ...], helpers: tuple[str, ...]) -> int:
    """Highest declared row of any vanilla or mod column-5 series that a country of this family can see."""
    rows = [0]
    for name, text in files.items():
        if name == new_name or name.lower() > new_name.lower():
            continue  # only series that load before the new file can push it down
        for series, slot, generic, potential, missions in series_list(text):
            if slot != 5 or generic == "yes":
                continue
            hit = any(re.search(rf"\b(?:was_)?tag = {tag}\b", potential) for tag in tags) or any(
                helper in potential for helper in helpers)
            if hit:
                rows += [position for position, _, _ in missions.values() if position]
    return max(rows)


def new_file_problems(text: str, files: dict[str, str], known: tuple[str, ...]) -> list[str]:
    problems = []
    series = {name: (slot, potential, missions) for name, slot, _, potential, missions in series_list(text)}
    # series -> (its missions with their rows, the parent of the first one, tags, helpers, measure against the tallest variant)
    expected = {
        "rip_horde_ruthenian_contacts": ({"rip_tat_ruthenian_yarlyks": 17, "rip_tatar_dnieper_tribute": 18},
                                         "tatars_intercontinental_trade", TATAR_TAGS, TAG_HELPERS, True),
        "rip_horde_ruthenian_contacts_classic": ({"rip_tat_ruthenian_yarlyks_classic": 5, "rip_tatar_dnieper_tribute_classic": 6},
                                                 "tatar_yoke_mission", TATAR_TAGS, TAG_HELPERS, False),
        "rip_austrian_ruthenian_contacts_classic": ({"rip_hab_galician_ruthenians_classic": 11}, "",
                                                    ("HAB",), (), False),
    }
    if set(series) != set(expected):
        problems.append(f"expected series {sorted(expected)}, found {sorted(series)}")
    for name, (rows, parent, tags, helpers, measure) in expected.items():
        if name not in series:
            continue
        slot, potential, missions = series[name]
        if slot != 5:
            problems.append(f"{name}: column {slot}, expected 5")
        if list(missions) != list(rows):
            problems.append(f"{name}: expected exactly the missions {list(rows)}, found {list(missions)}")
            continue
        previous = None
        for mission, row in rows.items():
            position, required, body = missions[mission]
            if position != row:
                problems.append(f"{mission}: row {position}, expected {row}")
            want = parent if previous is None else previous
            if required.strip() != want:
                problems.append(f"{mission}: required_missions {{ {required.strip()} }}, expected {{ {want} }}")
            if "add_country_modifier" not in body and mission.startswith(("rip_tat_ruthenian_yarlyks", "rip_hab")):
                problems.append(f"{mission}: no reward modifier")
            if "rip_diaspora_eligible_culture" not in body:
                problems.append(f"{mission}: no Ruthenian culture gate")
            previous = mission
        if name.startswith("rip_austrian"):
            dlc = 'has_dlc = "Winds of Change"'
            if dlc not in potential or (f"NOT = {{ {dlc} }}" in potential) != name.endswith("_classic"):
                problems.append(f"{name}: DLC eligibility must match its parent")
        if "map_setup = map_setup_random" not in potential:
            problems.append(f"{name}: potential must keep NOT map_setup_random")
        top = tallest_row(files, NEW_FILE, tags, helpers)
        first, row = next(iter(rows.items()))
        if measure and top and row <= top:
            problems.append(f"{first}: row {row} does not clear the tallest vanilla variant (row {top})")
    tatar = series.get("rip_horde_ruthenian_contacts", (0, "", 0))[1]
    if "is_tatar_nation = yes" not in tatar:
        problems.append("Tatar series: potential lost is_tatar_nation")
    if 'has_dlc = "Winds of Change"' not in tatar:
        problems.append("Tatar series: potential must name Winds of Change, the variant whose column it hangs from")
    classic = series.get("rip_horde_ruthenian_contacts_classic", (0, "", 0))[1]
    if 'NOT = { has_dlc = "Winds of Change" }' not in classic or "tag = KAS" not in classic:
        problems.append("Tatar classic series: potential must be the older tree's tag list without Winds of Change")
    austrian = series.get("rip_austrian_ruthenian_contacts_classic", (0, "", 0))[1]
    if not re.search(r"(?<!\w)tag = HAB\b", austrian):
        problems.append("Classic Austrian series must cover HAB")
    _, _, classic_missions = series.get("rip_austrian_ruthenian_contacts_classic", (0, "", {}))
    if "mission_completed = partition_poland" not in classic_missions.get("rip_hab_galician_ruthenians_classic", (0, "", ""))[2]:
        problems.append("Classic Austrian mission must require the conquest of Galicia")
    return problems


def dom_problems(text: str) -> list[str]:
    problems = []
    found = [(s, m) for s, _, _, _, ms in series_list(text) for m in ms if m == "rip_rus_kyiv_metropolia"]
    if found != [("mos_rus_russian_consolidation", "rip_rus_kyiv_metropolia")]:
        return [f"rip_rus_kyiv_metropolia placement: {found}"]
    for series, slot, _, _, missions in series_list(text):
        if series == "mos_rus_russian_consolidation":
            position, required, body = missions["rip_rus_kyiv_metropolia"]
            if slot != 3 or position != 8:
                problems.append(f"Kyiv metropolia sits at column {slot} row {position}, expected 3 / 8")
            if required.strip() != "mos_rus_russian_patriarchate":
                problems.append("Kyiv metropolia must follow mos_rus_russian_patriarchate")
            for needle in ("province_id = 280", "280 = { country_or_non_sovereign_subject_holds = ROOT }",
                           "rip_faith_is_eastern_orthodox = yes", "rip_rus_kyivan_clergy",
                           "rip_diaspora_eligible_culture_province = yes"):
                if needle not in body:
                    problems.append(f"Kyiv metropolia lost: {needle}")
    cells = {}
    for series, slot, _, _, missions in series_list(text):
        if slot == 3 and not series.startswith("rus_"):
            for mission, (position, _, _) in missions.items():
                if cells.setdefault(position, mission) != mission:
                    problems.append(f"column 3 row {position}: {cells[position]} and {mission} collide")
    return problems


def loc_problems() -> list[str]:
    problems = []
    for mission, (english, kind) in MISSION_KEYS.items():
        keys = [f"{mission}_title", f"{mission}_desc"]
        modifier = mission if mission in MODIFIERS else None
        for key in keys:
            if not re.search(rf'(?m)^ {re.escape(key)}:\d* "', read(english)):
                problems.append(f"{english}: missing {key}")
        if kind == "contacts":
            for language in ("french", "german", "spanish"):
                text = read(f"localisation/RIP_shared_ruthenian_contacts_l_{language}.yml")
                for key in keys:
                    if not re.search(rf'(?m)^ {re.escape(key)}:\d* "', text):
                        problems.append(f"contacts {language}: missing {key}")
        else:
            for language in ("french", "german", "spanish"):
                text = read(f"localisation/replace/RIP_MOS_RUS_content_l_{language}.yml")
                for key in keys:
                    if not re.search(rf'(?m)^ {re.escape(key)}:\d* "', text):
                        problems.append(f"MOS_RUS {language}: missing {key}")
    for modifier, path in MODIFIERS.items():
        if not re.search(rf"(?m)^{re.escape(modifier)}\s*=\s*\{{", read(path)):
            problems.append(f"{path}: modifier {modifier} not defined")
        for name in (modifier, f"desc_{modifier}"):
            sources = ["localisation/RIP_MOS_RUS_realm_l_english.yml", "localisation/RIP_shared_ruthenian_contacts_l_english.yml"]
            if not any(re.search(rf'(?m)^ {re.escape(name)}:\d* "', read(s)) for s in sources):
                problems.append(f"modifier text missing: {name}")
    return problems


def self_test(new_text: str, dom_text: str, files: dict[str, str]) -> list[str]:
    """Return the damaged variants that were NOT caught."""
    missed = []

    def expect(label, problems):
        if not problems:
            missed.append(label)

    expect("file renamed to load before the vanilla horde files",
           load_order_problems("zzz_Ruthenian_Contacts_Horde_Habsburg.txt", files, KNOWN_COLUMN_FILES))
    expect("series moved to column 1", new_file_problems(new_text.replace("slot = 5", "slot = 1", 1), files, KNOWN_COLUMN_FILES))
    expect("Tatar mission dropped under the vanilla tree",
           new_file_problems(new_text.replace("position = 17", "position = 3", 1), files, KNOWN_COLUMN_FILES) if len(files) > 40
           else ["not measurable without vanilla"])
    expect("Tatar chain loses its parent", new_file_problems(
        new_text.replace("required_missions = { tatars_intercontinental_trade }", "required_missions = { }", 1), files, KNOWN_COLUMN_FILES))
    expect("Austrian mission loses its parent", new_file_problems(
        new_text.replace("mission_completed = partition_poland", "always = yes", 1), files, KNOWN_COLUMN_FILES))
    expect("culture gate removed", new_file_problems(
        new_text.replace("rip_diaspora_eligible_culture_province = yes", "development = 1"), files, KNOWN_COLUMN_FILES))
    expect("HAB gate lost", new_file_problems(new_text.replace("tag = HAB", "tag = BOH", 1), files, KNOWN_COLUMN_FILES))
    expect("DOM mission moved onto the patriarchate row", dom_problems(dom_text.replace(
        "required_missions = { mos_rus_russian_patriarchate }\r\n\t\tposition = 8",
        "required_missions = { mos_rus_russian_patriarchate }\r\n\t\tposition = 7").replace(
        "required_missions = { mos_rus_russian_patriarchate }\n\t\tposition = 8",
        "required_missions = { mos_rus_russian_patriarchate }\n\t\tposition = 7")))
    expect("DOM mission loses Kyiv gate", dom_problems(dom_text.replace("280 = { country_or_non_sovereign_subject_holds = ROOT }", "always = yes", 1)))
    return missed


def main() -> int:
    new_text = read(f"missions/{NEW_FILE}")
    dom_text = read("missions/DOM_Russia_Missions.txt")
    files = column_files()
    problems = load_order_problems(NEW_FILE, files, KNOWN_COLUMN_FILES)
    problems += new_file_problems(new_text, files, KNOWN_COLUMN_FILES)
    problems += dom_problems(dom_text)
    problems += loc_problems()
    for label in self_test(new_text, dom_text, files):
        problems.append(f"self-test: damaged variant not caught: {label}")
    if problems:
        print("RUTHENIAN MISSION SERIES FAILED:")
        for item in problems:
            print(" ", item)
        return 1
    measured = "with the installed 1.37.x" if vanilla_root() is not None else "from recorded file names only"
    print(f"RUTHENIAN MISSION SERIES PASS: 4 missions in 4 trees, load order proved {measured}, "
          "9 damaged variants caught")
    return 0


if __name__ == "__main__":
    sys.exit(main())
