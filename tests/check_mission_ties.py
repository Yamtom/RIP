"""Check DLC variants, prerequisite arrows and near-neighbor placement against EU4 1.37.x mission files."""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "dev_tools"))

import mission_grid as mg  # noqa: E402
from clausewitz_testlib import ROOT, read, vanilla_root  # noqa: E402

# (label, tag, DLC the player lacks, [(mission, column, row, parent)]); parent "" = a root. DLC owned = every DLC but the missing one.
# "adjacent" rows are checked against the tail of the column instead of a fixed number (a root stacks under whatever is there).
CASES = [
    ("Moscow, Domination", "MOS", None, [
        ("rip_rus_kyiv_scribes", 1, 9, "mos_rus_europes_greatest_power"),
        ("rip_rus_copy_ruthenian_books", 1, 10, "rip_rus_kyiv_scribes"),
        ("rip_rus_ruthenian_press", 1, 11, "rip_rus_copy_ruthenian_books")]),
    # Russia stacks the chain below the Sudebnik and the Book of Royal Degrees, so the arrow passes behind those two cards.
    ("Russia, Domination", "RUS", None, [
        ("rip_rus_kyiv_scribes", 1, 12, "mos_rus_europes_greatest_power"),
        ("rip_rus_ruthenian_press", 1, 14, "rip_rus_copy_ruthenian_books")]),
    ("Moscow without Domination", "MOS", "Domination", [
        ("rip_rus_kyiv_scribes_alt", 1, "adjacent", ""),
        ("rip_rus_copy_ruthenian_books_alt", 1, "next", "rip_rus_kyiv_scribes_alt"),
        ("rip_rus_ruthenian_press_alt", 1, "next", "rip_rus_copy_ruthenian_books_alt")]),
    ("Lithuania, Lions of the North", "LIT", None, [
        ("rip_lit_ruthenian_chancery", 1, 6, "lit_jesuit_academy"),
        ("rip_lit_princes_of_rus", 1, 7, "rip_lit_ruthenian_chancery"),
        ("rip_lit_kyiv_succession", 1, 8, "rip_lit_princes_of_rus"),
        ("rip_lit_volok_survey", 3, 5, "lit_build_manufactories")]),
    ("Lithuania without Lions of the North", "LIT", "Lions of the North", [
        ("rip_lit_ruthenian_chancery_classic", 1, 5, "lit_develop_sluck"),
        ("rip_lit_princes_of_rus_classic", 1, 6, "rip_lit_ruthenian_chancery_classic"),
        ("rip_lit_kyiv_succession_classic", 1, 7, "rip_lit_princes_of_rus_classic"),
        ("rip_lit_volok_survey_classic", 3, 1, "")]),
    ("Golden Horde, Winds of Change", "GOL", None, [
        ("rip_tat_ruthenian_yarlyks", 5, 17, "tatars_intercontinental_trade"),
        ("rip_tatar_dnieper_tribute", 5, 18, "rip_tat_ruthenian_yarlyks")]),
    ("Crimea, Winds of Change", "CRI", None, [
        ("rip_tat_ruthenian_yarlyks", 5, 17, "tatars_intercontinental_trade"),
        ("rip_tatar_dnieper_tribute", 5, 18, "rip_tat_ruthenian_yarlyks")]),
    ("Crimea without Winds of Change", "CRI", "Winds of Change", [
        ("rip_tat_ruthenian_yarlyks_classic", 5, 5, "tatar_yoke_mission"),
        ("rip_tatar_dnieper_tribute_classic", 5, 6, "rip_tat_ruthenian_yarlyks_classic")]),
    ("Ottomans, Domination", "TUR", None, [
        ("rip_tur_podillian_eyalet", 4, 14, ""),
        ("rip_record_ladyzhyn", 4, 15, "rip_tur_podillian_eyalet")]),
    ("Ottomans without Domination", "TUR", "Domination", [
        ("rip_tur_podillian_eyalet_classic", 4, 10, ""),
        ("rip_record_ladyzhyn_classic", 4, 11, "rip_tur_podillian_eyalet_classic")]),
    ("Rum", "RUM", None, [
        ("rip_tur_podillian_eyalet_classic", 4, 10, "")]),
    ("Austria, Winds of Change", "HAB", None, [
        ("rip_hab_galician_ruthenians", 5, 8, "hab_galicia")]),
    ("Austria without Winds of Change", "HAB", "Winds of Change", [
        ("rip_hab_galician_ruthenians_classic", 5, 11, "")]),
]

# main series, its twin, the file, the suffix the twin's keys carry
TWINS = [
    ("rip_russian_ruthenian_contacts", "rip_russian_ruthenian_contacts_alt", "zzz_Ruthenian_Contacts.txt", "_alt"),
    ("rip_horde_ruthenian_contacts", "rip_horde_ruthenian_contacts_classic", "zzzz_Ruthenian_Contacts_Horde_Habsburg.txt", "_classic"),
    ("rip_lit_ruthenian_missions", "rip_lit_ruthenian_missions_classic", "zzzzz_Neighbor_Ruthenian_Missions.txt", "_classic"),
    ("rip_lit_volok_missions", "rip_lit_volok_missions_classic", "zzzzz_Neighbor_Ruthenian_Missions.txt", "_classic"),
    ("rip_tur_ruthenian_missions", "rip_tur_ruthenian_missions_classic", "zzzzz_Neighbor_Ruthenian_Missions.txt", "_classic"),
]
LOC_FILES = ("RIP_shared_ruthenian_contacts", "RIP_shared_ruthenian_neighbor_missions", "RIP_LIT_reckoning")


def brace_block(text: str, header: str) -> str:
    match = re.search(rf"(?m)^{re.escape(header)} = \{{", text)
    if not match:
        raise KeyError(header)
    depth = 0
    for index in range(match.end() - 1, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[match.start(): index + 1]
    raise ValueError(header)


def strip_block(text: str, header: str) -> str:
    """Remove a `\\theader = { ... }` block that sits directly in the series (one tab deep)."""
    match = re.search(rf"(?m)^\t{re.escape(header)} = \{{", text)
    if not match:
        return text
    depth = 0
    for index in range(match.end() - 1, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[: match.start()] + text[index + 1:]
    raise ValueError(header)


def normalised(block: str, suffix: str | None) -> str:
    """The series without what a twin may change: keys, rows, the parents, the potential."""
    text = block
    if suffix:
        text = re.sub(rf"\b(rip_\w+?){re.escape(suffix)}\b", r"\1", text)
    text = strip_block(text, "potential")
    text = strip_block(text, "potential_on_load")
    text = re.sub(r"(?m)^\s*mission_completed = (tur_black_sea_dominance|take_kaffa)\s*$", "", text)
    text = re.sub(r"position = \d+", "position = N", text)
    text = re.sub(r"required_missions = \{[^}]*\}", "required_missions = { }", text)
    text = re.sub(r"(?m)^[ \t]*#.*\n", "", text)
    return re.sub(r"\s+", " ", text).strip()


def twin_problems() -> list[str]:
    problems = []
    for main, twin, filename, suffix in TWINS:
        text = read(f"missions/{filename}")
        try:
            main_block, twin_block = brace_block(text, main), brace_block(text, twin)
        except KeyError as missing:
            problems.append(f"{filename}: series {missing} not found")
            continue
        # the twin's own series name carries the suffix; only the series header differs. A main series may name
        # its twin (a reward guard), so the suffix is stripped on both sides.
        main_body = normalised(main_block, suffix).split("{", 1)[1]
        twin_body = normalised(twin_block, suffix).split("{", 1)[1]
        if main_body != twin_body:
            problems.append(f"{twin} has drifted from {main}: the two must differ only in keys, rows, the first parent and the potential")
    return problems


def loc_problems() -> list[str]:
    problems = []
    for main, twin, filename, suffix in TWINS:
        text = read(f"missions/{filename}")
        keys = re.findall(rf"(?m)^\t(rip_\w+{re.escape(suffix)}) = \{{", brace_block(text, twin))
        for language in ("english", "french", "german", "spanish"):
            entries = {}
            for stem in LOC_FILES:
                path = ROOT / f"localisation/{stem}_l_{language}.yml"
                if path.exists():
                    entries.update(re.findall(r'(?m)^ ([A-Za-z0-9_.]+):\d* "(.*)"\s*$', read(f"localisation/{stem}_l_{language}.yml")))
            for key in keys:
                for part in ("title", "desc"):
                    want = f"${key[:-len(suffix)]}_{part}$"
                    if entries.get(f"{key}_{part}") != want:
                        problems.append(f"{language}: {key}_{part} must be {want}, found {entries.get(f'{key}_{part}')!r}")
    return problems


def cell_problems() -> list[str]:
    problems = []
    files = mg.load_files(False)
    all_dlc = set()
    for text in files.values():
        all_dlc.update(re.findall(r'has_dlc = "([^"]+)"', text))
    twin_keys = {m for _, twin, filename, suffix in TWINS
                 for m in re.findall(rf"(?m)^\t(rip_\w+{re.escape(suffix)}) = \{{", brace_block(read(f'missions/{filename}'), twin))}
    for label, tag, lacks, missions in CASES:
        placed = mg.layout(files, mg.Context(tag, all_dlc - ({lacks} if lacks else set())))
        for mission, column, row, parent in missions:
            if mission not in placed:
                problems.append(f"{label}: {mission} is not on screen")
                continue
            slot, actual, required, _, _ = placed[mission]
            if slot != column:
                problems.append(f"{label}: {mission} is in column {slot}, expected {column}")
            if row == "adjacent":
                tail = max([r for s, r, *_ in placed.values() if s == column and r < actual] or [0])
                if actual != tail + 1:
                    problems.append(f"{label}: {mission} is on row {actual}, the column ends on row {tail}: a vacuum")
            elif row == "next":
                before = placed[parent][1]
                if actual != before + 1:
                    problems.append(f"{label}: {mission} is on row {actual}, expected {before + 1}")
            elif actual != row:
                problems.append(f"{label}: {mission} is on row {actual}, expected {row}")
            if required != ([parent] if parent else []):
                problems.append(f"{label}: {mission} requires {required}, expected {[parent] if parent else []}")
            if parent:
                if parent not in placed:
                    problems.append(f"{label}: the parent {parent} of {mission} is not on screen")
                else:
                    p_slot, p_row, *_ = placed[parent]
                    if p_slot != slot or p_row >= actual:
                        problems.append(f"{label}: {parent} is not above {mission} in the same column")
        # one copy per country: a twin and its main mission never share a screen
        shown = {m for m in placed if m.endswith(("_alt", "_classic"))}
        mains = {m[: m.rindex("_")] for m in shown}
        both = mains & set(placed)
        if both:
            problems.append(f"{label}: both {sorted(both)} and their copies are on screen")
        if not (shown & twin_keys) and not any(m in placed for m, *_ in missions):
            problems.append(f"{label}: no copy of the series is on screen")
    return problems


def revised_layout_problems() -> list[str]:
    problems = []
    files = mg.load_files(False)
    vanilla = vanilla_root() / "missions" / "WoC_Austrian_Missions.txt"
    original = vanilla.read_text(encoding="utf-8-sig")
    patched = files[vanilla.name]
    from check_vanilla_mission_sync import parse
    series = brace_block(patched, "WoC_austria_5")
    unpatched = patched.replace(series, strip_block(series, "rip_hab_galician_ruthenians"), 1)
    if parse(unpatched) != parse("\n".join(line.rstrip() for line in original.splitlines())):
        problems.append("Winds of Change Austrian override changed vanilla data")
    dlcs = set(re.findall(r'has_dlc = "([^"]+)"', "".join(files.values())))
    chain = [
        ("rip_pol_carpathian_passes", 1, 11, []),
        ("rip_pol_rusyn_fairs", 2, 12, ["rip_pol_carpathian_passes"]),
        ("rip_pol_lviv_charters", 2, 13, ["rip_pol_rusyn_fairs"]),
        ("rip_pol_ruthenian_palatinates", 2, 14, ["rip_pol_lviv_charters"]),
    ]
    for tag in ("POL", "PLC"):
        for owned in (dlcs, dlcs - {"Lions of the North"}):
            placed = mg.layout(files, mg.Context(tag, owned))
            for name, col, row, parents in chain:
                if placed.get(name, ())[:3] != (col, row, parents):
                    problems.append(f"{tag}: broken regional chain at {name}")
            shown = {name for name, (_, _, _, series, _) in placed.items() if series.startswith("POL_re_missions_")}
            if len(shown) != (11 if tag == "PLC" else 0):
                problems.append(f"{tag}: unexpected Commonwealth mission count {len(shown)}")
            for name in shown:
                col, row, parents, *_ = placed[name]
                for parent in parents:
                    if parent not in placed:
                        problems.append(f"{tag}: {name} has missing prerequisite {parent}")
                        continue
                    pc, pr, *_ = placed[parent]
                    if abs(col - pc) > 1 or row != pr + 1:
                        problems.append(f"{tag}: {name} should be directly below or diagonal to {parent}")
    return problems


def self_test(files_present: bool) -> list[str]:
    """Damaged copies of the checks' inputs that must be caught; returns those that were not."""
    missed = []
    text = read("missions/zzzzz_Neighbor_Ruthenian_Missions.txt")
    main = brace_block(text, "rip_tur_ruthenian_missions")
    twin = brace_block(text, "rip_tur_ruthenian_missions_classic")
    base = normalised(main, None).split("{", 1)[1]
    if normalised(twin, "_classic").split("{", 1)[1] != base:
        missed.append("clean twin differs (self-test setup)")
    drifted = twin.replace("add_prestige = 15", "add_prestige = 16", 1)
    if normalised(drifted, "_classic").split("{", 1)[1] == base:
        missed.append("a changed reward in the twin")
    other = twin.replace("rip_tur_northern_protectorate", "rip_tur_kamianets_citadel", 1)
    if normalised(other, "_classic").split("{", 1)[1] == base:
        missed.append("a swapped modifier in the twin")
    return missed


def main() -> int:
    problems = twin_problems() + loc_problems()
    measured = vanilla_root() is not None
    if measured:
        problems += cell_problems() + revised_layout_problems()
    for label in self_test(measured):
        problems.append(f"self-test: not caught: {label}")
    if problems:
        print("MISSION TIES FAILED:")
        for item in problems:
            print(" ", item)
        return 1
    where = "against the installed vanilla columns" if measured else "twins and loc only (no installed EU4)"
    print(f"MISSION TIES PASS: {len(CASES)} country and DLC cases laid out {where}; "
          f"{len(TWINS)} twin series match their main series; 3 damaged twins caught")
    return 0


if __name__ == "__main__":
    sys.exit(main())
