"""Regression contracts for Hetmanate historical process-driven decision windows.

Verifies:
1. het_pereiaslav_treaty:
   - No closed arbitrary calendar windows (no NOT = { is_year = 1670 }).
   - Institutions/ages do not disable early alternative access (no inverted NOT = { OR = { ... } }).
   - Early path gates on severe crisis (WE >= 6) and readiness threshold (200 DIP), while base deduction is 100 DIP.
   - Preserves Russian/Muscovite patron peace filters.
2. het_mazepa_independence:
   - No closed arbitrary calendar windows (no NOT = { is_year = 1720 }).
   - Institutions do not disable early alternative access.
   - Early path gates on high LD (75+), army (35+), and readiness threshold (300 MIL), while base deduction is 150 MIL.
   - Preserves great power ally requirement and AI non-zero weighting.
"""

from __future__ import annotations

import sys
from clausewitz_testlib import named_block, read


def require(failures: list[str], condition: bool, message: str) -> None:
    if not condition:
        failures.append(message)


def check_pereiaslav_window(failures: list[str]) -> None:
    text = read("decisions/HetmanateDecisions.txt")
    pereiaslav = named_block(text, "het_pereiaslav_treaty")
    potential = named_block(pereiaslav, "potential")
    allow = named_block(pereiaslav, "allow")
    effect = named_block(pereiaslav, "effect")

    # 1. Potential: no artificial cutoff at 1670
    require(failures, "is_year = 1670" not in potential,
            "het_pereiaslav_treaty: artificial 1670 cutoff remains in potential")
    require(failures, "new_world_i" not in potential,
            "het_pereiaslav_treaty: institution check incorrectly blocks early potential")

    # 2. Allow: mature vs early crisis routes
    require(failures, "war_exhaustion = 3" in allow,
            "het_pereiaslav_treaty: missing standard war exhaustion requirement")
    require(failures, "war_exhaustion = 6" in allow and "dip_power = 200" in allow,
            "het_pereiaslav_treaty: missing early crisis thresholds (WE 6, DIP 200)")

    # 3. Effect: base deduction only (threshold, not double charge)
    require(failures, "add_dip_power = -100" in effect,
            "het_pereiaslav_treaty: base DIP power deduction is missing")
    require(failures, "add_dip_power = -200" not in effect,
            "het_pereiaslav_treaty: threshold mistakenly converted to double charge")
    require(failures, "het_pereiaslav_treaty_effect = yes" in effect,
            "het_pereiaslav_treaty: missing scripted treaty effect")


def check_mazepa_window(failures: list[str]) -> None:
    text = read("decisions/HetmanateDecisions.txt")
    mazepa = named_block(text, "het_mazepa_independence")
    potential = named_block(mazepa, "potential")
    allow = named_block(mazepa, "allow")
    effect = named_block(mazepa, "effect")

    # 1. Potential: no artificial cutoff at 1720
    require(failures, "is_year = 1720" not in potential,
            "het_mazepa_independence: artificial 1720 cutoff remains in potential")
    require(failures, "global_trade" not in potential,
            "het_mazepa_independence: institution check incorrectly blocks early potential")

    # 2. Allow: mature vs early preparedness routes
    require(failures, "liberty_desire = 50" in allow and "army_size = 20" in allow,
            "het_mazepa_independence: missing mature era thresholds")
    require(failures, "liberty_desire = 75" in allow and "army_size = 35" in allow and "mil_power = 300" in allow,
            "het_mazepa_independence: missing early preparedness thresholds (LD 75, Army 35, MIL 300)")

    # 3. Effect: base deduction only
    require(failures, "add_mil_power = -150" in effect,
            "het_mazepa_independence: base MIL power deduction is missing")
    require(failures, "add_mil_power = -300" not in effect,
            "het_mazepa_independence: threshold mistakenly converted to double charge")
    require(failures, "het_break_with_overlord_effect = yes" in effect,
            "het_mazepa_independence: missing scripted break effect")


def main() -> int:
    failures: list[str] = []
    check_pereiaslav_window(failures)
    check_mazepa_window(failures)

    if failures:
        print("Hetmanate historical decision window contract failures:")
        for failure in failures:
            print(f"  {failure}")
        return 1

    print("Hetmanate Pereiaslav and Mazepa process-driven window contracts hold")
    return 0


if __name__ == "__main__":
    sys.exit(main())
