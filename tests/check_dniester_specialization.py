"""Regression contract for Dniester Estuary economic specializations.

Verifies:
1. Decisions establish_dniester_fishing, establish_dniester_wine_trade, and
   establish_dniester_salt_works are mutually exclusive:
   - All three require NOT = { has_country_flag = dniester_estuary_specialized }
   - All three verify province 1756 has none of the other specialization modifiers
   - All three set set_country_flag = dniester_estuary_specialized
   - Each decision explicitly cleanses alternative specialization modifiers and
     unconditionally sets the corresponding trade good (fish, wine, salt).
2. Prevents stacking of dniester_fishing_industry (+15%), dniester_wine_merchants (+20%),
   and dniester_salt_production (+15%) on province 1756.
"""

from __future__ import annotations

import sys
from clausewitz_testlib import named_block, read


def require(failures: list[str], condition: bool, message: str) -> None:
    if not condition:
        failures.append(message)


def check_specialization_contract(failures: list[str]) -> None:
    text = read("decisions/DniesterEstuaryDecisions.txt")

    decisions = {
        "establish_dniester_fishing": {
            "good": "fish",
            "mod": "dniester_fishing_industry",
            "other_mods": ["dniester_wine_merchants", "dniester_salt_production"],
        },
        "establish_dniester_wine_trade": {
            "good": "wine",
            "mod": "dniester_wine_merchants",
            "other_mods": ["dniester_fishing_industry", "dniester_salt_production"],
        },
        "establish_dniester_salt_works": {
            "good": "salt",
            "mod": "dniester_salt_production",
            "other_mods": ["dniester_fishing_industry", "dniester_wine_merchants"],
        },
    }

    for decision_id, data in decisions.items():
        block = named_block(text, decision_id)
        potential = named_block(block, "potential")
        allow = named_block(block, "allow")
        effect = named_block(block, "effect")

        # Must have shared mutual exclusion flag in potential and effect
        require(
            failures,
            "NOT = { has_country_flag = dniester_estuary_specialized }" in potential,
            f"{decision_id}: missing shared exclusion flag in potential",
        )
        require(
            failures,
            "set_country_flag = dniester_estuary_specialized" in effect,
            f"{decision_id}: missing shared exclusion flag in effect",
        )

        # Must check that 1756 does not have other specialization modifiers
        for other_mod in data["other_mods"]:
            require(
                failures,
                f"NOT = {{ has_province_modifier = {other_mod} }}" in potential,
                f"{decision_id}: potential does not check absence of {other_mod}",
            )
            require(
                failures,
                f"NOT = {{ has_province_modifier = {other_mod} }}" in allow,
                f"{decision_id}: allow does not check absence of {other_mod}",
            )
            require(
                failures,
                f"remove_province_modifier = {other_mod}" in effect,
                f"{decision_id}: effect does not clean up conflicting {other_mod}",
            )

        # Must add own modifier and change trade goods
        require(
            failures,
            f"name = {data['mod']}" in effect,
            f"{decision_id}: missing modifier {data['mod']} in effect",
        )
        require(
            failures,
            f"change_trade_goods = {data['good']}" in effect,
            f"{decision_id}: missing trade good assignment to {data['good']}",
        )


def check_localisation_notes(failures: list[str]) -> None:
    loc = read("localisation/uniate_and_raid_l_english.yml")
    for key in (
        "establish_dniester_fishing_desc:",
        "establish_dniester_wine_trade_desc:",
        "establish_dniester_salt_works_desc:",
    ):
        require(failures, key in loc, f"missing English localisation {key}")
        require(
            failures,
            "mutually exclusive with other estuary specializations" in loc,
            f"English localisation {key} does not indicate mutual exclusivity",
        )


def main() -> int:
    failures: list[str] = []
    check_specialization_contract(failures)
    check_localisation_notes(failures)

    if failures:
        print("Dniester Estuary specialization contract failures:")
        for failure in failures:
            print(f"  {failure}")
        return 1

    print("Dniester Estuary mutual exclusion specialization contracts hold")
    return 0


if __name__ == "__main__":
    sys.exit(main())
