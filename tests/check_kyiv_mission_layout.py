"""Static KIE, KRU and UKR mission-screen layout gate.

Models EU4 per-slot stacking and arrow routing (vertical run in the parent
column down to the gap above the child row, inferred from in-game screenshots
on 2026-11-21). Static inspection only - does not launch EU4 or prove runtime.
"""
from __future__ import annotations

from collections import defaultdict
import re

from check_donor_mission_ports import parse_series_in_file

MISSION_FILES = (
    "Kyiv_Missions.txt",
    "Kyiv_Shared_Missions.txt",
    "Kyiv_Successors_Missions.txt",
)
ALLOWED_ROOTS = {"KIE_true_ruler", "KIE_mohyla_academy"}
# UKR_ruthenia opens the successor column; every other successor mission has a parent.
SUCCESSOR_ROOTS = ALLOWED_ROOTS | {"UKR_ruthenia"}
# The one arrow that still runs behind a card: Serbia sits in the cell under the
# port, because Serbia must hang directly under Bulgaria (column 3, row 9).
KNOWN_OCCLUSIONS = {("UKR_port", "UKR_fleet")}
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
SUCCESSOR_CELLS = {
    "UKR_breadbasket_of_europe": (1, 4),
    "UKR_ruthenia": (1, 5),
    "UKR_baltic_dominion": (2, 12),
    "UKR_ruthenian_empire": (3, 12),
    "UKR_dniepr": (4, 6),
    "UKR_crimea": (4, 7),
    "UKR_port": (4, 9),
    "UKR_serbia": (4, 10),
    "UKR_fleet": (4, 11),
    "UKR_sloboda_frontier": (5, 7),
    "UKR_tatar": (5, 8),
    "UKR_demand_tribute": (5, 9),
    "UKR_horde": (5, 10),
    "UKR_kazan": (5, 11),
    "UKR_perm": (5, 12),
    "UKR_siberia": (5, 13),
}


def collect_grid(tag: str) -> tuple[
    dict[str, tuple[int, int, list[str]]],
    dict[tuple[int, int], str],
    list[str],
]:
    """Simulate EU4 slot-by-slot mission placement for one tag."""
    series = []
    for filename in sorted(MISSION_FILES, key=str.lower):
        for sname, slot, pot, missions in parse_series_in_file(f"missions/{filename}"):
            if re.search(rf"\btag\s*=\s*{tag}\b", pot):
                series.append((sname, slot, missions))

    cursors: dict[int, int] = defaultdict(int)
    placed: dict[str, tuple[int, int, list[str]]] = {}
    grid: dict[tuple[int, int], str] = {}
    failures: list[str] = []

    for sname, slot, missions in series:
        if not 1 <= slot <= 5:
            failures.append(f"{sname}: slot {slot} outside 1..5")
        for mname, pos, reqs in missions:
            row = max(cursors[slot] + 1, pos)
            if (slot, row) in grid:
                failures.append(
                    f"cell collision at ({slot}, {row}): {grid[(slot, row)]} vs {mname}"
                )
            cursors[slot] = row
            grid[(slot, row)] = mname
            placed[mname] = (slot, row, reqs)

    return placed, grid, failures


def check_layout(tag: str = "KIE") -> list[str]:
    """Validate roots, arrow visibility, and expected coordinates for one tag."""
    placed, grid, failures = collect_grid(tag)
    roots = ALLOWED_ROOTS if tag == "KIE" else SUCCESSOR_ROOTS
    known = set() if tag == "KIE" else KNOWN_OCCLUSIONS

    for mname, (slot, row, reqs) in placed.items():
        if not reqs and mname not in roots:
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
            if occluders and (dep, mname) not in known:
                failures.append(
                    f"occluded arrow {dep} ({dep_slot}, {dep_row}) -> {mname} ({slot}, {row}) behind {occluders}"
                )

    for mname, expected in (EXPECTED_CELLS if tag == "KIE" else SUCCESSOR_CELLS).items():
        if mname not in placed:
            failures.append(f"expected mission {mname} missing from {tag} grid")
            continue
        actual = (placed[mname][0], placed[mname][1])
        if actual != expected:
            failures.append(f"{mname}: expected {expected}, got {actual}")

    if tag == "KIE" and "KIE_dynasty" in placed and "KIE_byzantine_relations" not in placed["KIE_dynasty"][2]:
        failures.append("KIE_dynasty must require KIE_byzantine_relations")
    if tag == "KIE" and "KIE_magdeburg_law" in placed and "KIE_stability" not in placed["KIE_magdeburg_law"][2]:
        failures.append("KIE_magdeburg_law must require KIE_stability")

    dependents: dict[str, list[str]] = defaultdict(list)
    for mname, (_, _, reqs) in placed.items():
        for dep in reqs:
            dependents[dep].append(mname)
    for mname, (slot, row, _) in placed.items():
        if row <= 2 and not dependents[mname]:
            failures.append(f"early mission {mname} at ({slot}, {row}) has no dependent mission")

    return failures


def main() -> int:
    failed = False
    for tag in ("KIE", "KRU", "UKR"):
        failures = check_layout(tag)
        if failures:
            failed = True
            print(f"FAIL: {tag} mission layout")
            for failure in failures:
                print(f"  {failure}")
    if failed:
        return 1
    counts = {tag: len(collect_grid(tag)[0]) for tag in ("KIE", "KRU", "UKR")}
    print(f"PASS: KIE/KRU/UKR mission layout ({counts}; 0 collisions, 0 unexpected roots, "
          f"0 non-downward arrows; {len(KNOWN_OCCLUSIONS)} known occluded arrow; static only)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
