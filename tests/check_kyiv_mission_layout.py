"""Static KIE/KRU/UKR mission-screen layout and 2-line title gate.

Models EU4 per-slot stacking and arrow routing (vertical run in the parent
column down to the gap above the child row, inferred from in-game screenshots
on 2026-11-21) and checks mission banner wrapping against vic_18.fnt.
Static inspection only - does not launch EU4 or prove runtime.
"""
from __future__ import annotations

from collections import defaultdict
import re

from check_donor_mission_ports import parse_series_in_file
from clausewitz_testlib import read, vanilla_root

MISSION_FILES = (
    "Kyiv_Missions.txt",
    "Kyiv_Shared_Missions.txt",
    "Kyiv_Successors_Missions.txt",
)
TITLE_FILES = (
    "Kyiv_Missions.txt",
    "Kyiv_Shared_Missions.txt",
    "Kyiv_Successors_Missions.txt",
    "zzzz_RuthenianDiaspora_Missions.txt",
)
ALLOWED_ROOTS = {"KIE_true_ruler", "KIE_mohyla_academy"}
ALLOWED_SUCCESSOR_ROOTS = {
    "KIE_true_ruler",
    "UKR_ruthenia",
    "KIE_mohyla_academy",
}
EXPECTED_CELLS = {
    "KIE_stability": (5, 2),
    "KIE_byzantine_relations": (4, 2),
    "KIE_dynasty": (4, 4),
    "KIE_dniestr_trade_route": (4, 6),
    "KIE_trade_houses": (4, 7),
    "KIE_free_trade_cities": (4, 8),
    "KIE_cossack": (5, 5),
    "KIE_dnieper_settlement": (5, 6),
}
EXPECTED_SUCCESSOR_CELLS = {
    "UKR_baltic": (2, 4),
    "UKR_merchant_commonwealth": (2, 5),
    "UKR_princely_compact": (4, 5),
    "UKR_dniepr": (4, 6),
    "UKR_crimea": (4, 7),
    "UKR_small_discrepancies": (4, 8),
    "UKR_port": (4, 9),
    "UKR_fleet": (4, 10),
    "UKR_serbia": (4, 11),
    "UKR_kazan": (4, 12),
    "UKR_sloboda_frontier": (5, 7),
    "UKR_tatar": (5, 8),
    "UKR_demand_tribute": (5, 9),
    "UKR_horde": (5, 10),
    "UKR_breadbasket_of_europe": (5, 11),
    "UKR_perm": (5, 12),
    "UKR_siberia": (5, 13),
}


def collect_tag_grid(tag: str) -> tuple[
    dict[str, tuple[int, int, list[str]]],
    dict[tuple[int, int], str],
    dict[str, tuple[str, int, int]],
    list[str],
]:
    """Simulate EU4 slot-by-slot mission placement for a given tag."""
    series = []
    for filename in sorted(MISSION_FILES, key=str.lower):
        for sname, slot, pot, missions in parse_series_in_file(f"missions/{filename}"):
            if re.search(rf"\btag\s*=\s*{tag}\b", pot):
                series.append((sname, slot, missions))

    cursors: dict[int, int] = defaultdict(int)
    placed: dict[str, tuple[int, int, list[str]]] = {}
    grid: dict[tuple[int, int], str] = {}
    shifted: dict[str, tuple[str, int, int]] = {}
    failures: list[str] = []

    for sname, slot, missions in series:
        if not 1 <= slot <= 5:
            failures.append(f"{tag}:{sname}: slot {slot} outside 1..5")
        for mname, pos, reqs in missions:
            row = max(cursors[slot] + 1, pos)
            if row != pos:
                shifted[mname] = (sname, pos, row)
            if (slot, row) in grid:
                failures.append(
                    f"{tag}: cell collision at ({slot}, {row}): {grid[(slot, row)]} vs {mname}"
                )
            cursors[slot] = row
            grid[(slot, row)] = mname
            placed[mname] = (slot, row, reqs)

    return placed, grid, shifted, failures


def check_kie_layout() -> list[str]:
    """Validate KIE roots, arrow visibility, and expected coordinates."""
    placed, grid, shifted, failures = collect_tag_grid("KIE")
    if shifted:
        failures.append(f"KIE: unexpected cursor shifts {shifted}")

    for mname, (slot, row, reqs) in placed.items():
        if not reqs and mname not in ALLOWED_ROOTS:
            failures.append(
                f"{mname} at ({slot}, {row}) has no required_missions (unexpected root)"
            )
        for dep in reqs:
            if dep not in placed:
                failures.append(f"{mname}: missing prerequisite {dep}")
                continue
            dep_slot, dep_row, _ = placed[dep]
            if dep_row >= row:
                failures.append(
                    f"non-downward arrow {dep} ({dep_slot}, {dep_row}) -> {mname} ({slot}, {row})"
                )
                continue
            occluders = [
                grid[(dep_slot, y)]
                for y in range(dep_row + 1, row)
                if (dep_slot, y) in grid
            ]
            if occluders:
                failures.append(
                    f"occluded arrow {dep} ({dep_slot}, {dep_row}) -> {mname} ({slot}, {row}) behind {occluders}"
                )

    for mname, expected in EXPECTED_CELLS.items():
        if mname not in placed:
            failures.append(f"expected mission {mname} missing from KIE grid")
            continue
        actual = (placed[mname][0], placed[mname][1])
        if actual != expected:
            failures.append(f"{mname}: expected {expected}, got {actual}")

    if "KIE_dynasty" in placed and "KIE_byzantine_relations" not in placed["KIE_dynasty"][2]:
        failures.append("KIE_dynasty must require KIE_byzantine_relations")
    if "KIE_magdeburg_law" in placed and "KIE_stability" not in placed["KIE_magdeburg_law"][2]:
        failures.append("KIE_magdeburg_law must require KIE_stability")

    dependents: dict[str, list[str]] = defaultdict(list)
    for mname, (_, _, reqs) in placed.items():
        for dep in reqs:
            dependents[dep].append(mname)
    for mname, (slot, row, _) in placed.items():
        if row <= 2 and not dependents[mname]:
            failures.append(f"early mission {mname} at ({slot}, {row}) has no dependent mission")

    return failures


def check_successor_layout(tag: str) -> list[str]:
    """Validate KRU/UKR roots, unshifted UKR series, and 1-row arrow routing."""
    placed, grid, shifted, failures = collect_tag_grid(tag)
    for mname, (sname, pos, row) in shifted.items():
        if sname != "KIE_missions_1_culture":
            failures.append(f"{tag}: {sname}::{mname} declared pos={pos} shifted to row={row}")

    for mname, (slot, row, reqs) in placed.items():
        if not reqs and mname not in ALLOWED_SUCCESSOR_ROOTS:
            failures.append(f"{tag}: unexpected root {mname} at ({slot}, {row})")
        for dep in reqs:
            if dep not in placed:
                failures.append(f"{tag}: {mname} missing prerequisite {dep}")
                continue
            dep_slot, dep_row, _ = placed[dep]
            if row - dep_row != 1:
                failures.append(
                    f"{tag}: non-adjacent-row arrow {dep} ({dep_slot}, {dep_row}) -> {mname} ({slot}, {row})"
                )

    for mname, expected in EXPECTED_SUCCESSOR_CELLS.items():
        if mname not in placed:
            failures.append(f"{tag}: expected mission {mname} missing")
            continue
        actual = (placed[mname][0], placed[mname][1])
        if actual != expected:
            failures.append(f"{tag}: {mname} expected {expected}, got {actual}")

    if "UKR_breadbasket_of_europe" in placed:
        reqs = set(placed["UKR_breadbasket_of_europe"][2])
        if reqs != {"UKR_fleet", "UKR_horde"}:
            failures.append(f"{tag}: UKR_breadbasket_of_europe expected {{UKR_fleet, UKR_horde}}, got {reqs}")
    # Kazan and Perm used to float free; both hang one row under the Granary, and
    # Siberia follows both.
    for mname in ("UKR_kazan", "UKR_perm"):
        if mname in placed and set(placed[mname][2]) != {"UKR_breadbasket_of_europe"}:
            failures.append(f"{tag}: {mname} expected {{UKR_breadbasket_of_europe}}, got {set(placed[mname][2])}")
    if "UKR_siberia" in placed and set(placed["UKR_siberia"][2]) != {"UKR_kazan", "UKR_perm"}:
        failures.append(f"{tag}: UKR_siberia expected {{UKR_kazan, UKR_perm}}, got {set(placed['UKR_siberia'][2])}")

    return failures


def check_two_line_titles() -> list[str]:
    """Validate that Kyiv, successor and diaspora mission titles fit EU4's 2-line banner."""
    vanilla = vanilla_root()
    if not vanilla or not (vanilla / "gfx/fonts/vic_18.fnt").is_file():
        return []

    fnt = (vanilla / "gfx/fonts/vic_18.fnt").read_text(encoding="latin-1")
    adv = {int(m.group(1)): int(m.group(2)) for m in re.finditer(r"char\s+id=(\d+).*?xadvance=(-?\d+)", fnt)}
    sp = adv.get(32, 4)

    def wrap_metrics(title: str, max_w: int) -> tuple[int, int]:
        lines_w: list[int] = []
        cur_w = 0
        for word in title.split(" "):
            ww = sum(adv.get(ord(ch), 7) for ch in word)
            if cur_w == 0:
                cur_w = ww
            elif cur_w + sp + ww <= max_w:
                cur_w += sp + ww
            else:
                lines_w.append(cur_w)
                cur_w = ww
        if cur_w:
            lines_w.append(cur_w)
        return len(lines_w), max(lines_w or [0])

    en_titles: dict[str, str] = {}
    for loc_file in (
        "RIP_KIE_realm_l_english.yml",
        "RIP_KRU_realm_l_english.yml",
        "RIP_shared_ruthenian_expeditions_l_english.yml",
    ):
        for k, v in re.findall(r'^ ([A-Za-z0-9_.\-]+_title):\d+\s+"(.*)"\s*$', read(f"localisation/{loc_file}"), re.M):
            en_titles[k] = v
    # The short copy of the Diaspora tree reads the originals' titles as $key$ references.
    for k, v in list(en_titles.items()):
        seen = set()
        while re.fullmatch(r"\$[A-Za-z0-9_.\-]+\$", v) and v not in seen:
            seen.add(v)
            v = en_titles.get(v[1:-1], v)
        en_titles[k] = v

    failures: list[str] = []
    for filename in TITLE_FILES:
        for _, _, _, missions in parse_series_in_file(f"missions/{filename}"):
            for mname, _, _ in missions:
                key = f"{mname}_title"
                if key not in en_titles:
                    failures.append(f"{filename}::{mname}: missing title {key}")
                    continue
                title = en_titles[key]
                n84, w84 = wrap_metrics(title, 84)
                n90, w90 = wrap_metrics(title, 90)
                if n84 > 2 or n90 > 2 or w84 > 84 or w90 > 90:
                    failures.append(
                        f"{filename}::{mname}: title {title!r} wraps >2 lines or overflows "
                        f"(n84={n84}, w84={w84}, n90={n90}, w90={w90})"
                    )
    return failures


def check_layout() -> list[str]:
    """Run all Kyiv, successor, and 2-line title layout checks."""
    return (
        check_kie_layout()
        + check_successor_layout("KRU")
        + check_successor_layout("UKR")
        + check_two_line_titles()
    )


def main() -> int:
    failures = check_layout()
    if failures:
        print("FAIL: KIE/KRU/UKR mission layout")
        for failure in failures:
            print(f"  {failure}")
        return 1
    kie_placed, _, _, _ = collect_tag_grid("KIE")
    ukr_placed, _, _, _ = collect_tag_grid("UKR")
    print(
        f"PASS: KIE ({len(kie_placed)} missions) and KRU/UKR ({len(ukr_placed)} missions) layout, "
        f"0 collisions, 0 hidden/non-downward arrows, 2-line vic_18 titles (static only)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
