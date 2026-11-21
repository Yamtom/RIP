#!/usr/bin/env python3
"""Focused regression gate for cossack_carry_the_host.

Verifies the syncretic overhaul of carrying the Host into exile:
1. Shared refuge guards forbid stealing capitals, occupied provinces, or
   hostile countries' land, and honour a 10-year refusal cooldown.
2. Crisis/displacement triggers keep an intact 1444-1449 Zaporozhia (3 cities
   holding 283) from fleeing and enforce timed 25-year cooldown + size caps.
3. Decision wiring checks crisis and refuge-holder triggers and uses valid
   multiplicative ai_will_do gating without old broken conditions.
4. Effect splits AI vs human holders (consent via zaz_paths.6), resolves scope
   via event_target:host_carrying_country (not ROOT), moves capital before
   vacating old lands, cleans zaporozhian_sich_capital, and preserves cores.
5. Human consent event zaz_paths.6 exists once, is triggered-only, revalidates
   locally with FROM, and refunds ADM/MIL on refusal or lapsed preconditions.
6. English + EFIGS replace localisation and docs reflect the live behavior.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tests"))

from clausewitz_testlib import keyed_blocks, named_block, normalized, read


def test_refuge_triggers() -> None:
    text = read("common/scripted_triggers/zaz_refuge_triggers.txt")

    prov = named_block(text, "is_valid_host_refuge_province")
    assert "is_host_refuge = yes" in prov
    assert "NOT = { owned_by = ROOT }" in prov
    assert "is_capital = no" in prov
    assert "controlled_by = owner" in prov

    holder = named_block(text, "is_valid_host_refuge_holder")
    assert "NOT = { tag = ROOT }" in holder
    assert "NOT = { war_with = ROOT }" in holder
    assert "zaz_refused_host_refuge" in holder
    assert "days = 3650" in holder
    assert "alliance_with = ROOT" in holder
    assert "is_subject_of = ROOT" in holder
    assert "has_opinion = { who = ROOT value = 100 }" in holder
    assert "is_valid_host_refuge_province = yes" in holder


def test_path_triggers() -> None:
    text = read("common/scripted_triggers/zaz_path_triggers.txt")

    can_carry = named_block(text, "can_carry_the_host")
    assert "is_cossack_polity = yes" in can_carry
    assert "NOT = { num_of_cities = 5 }" in can_carry
    assert "NOT = { has_country_modifier = zaz_host_in_exile }" in can_carry
    assert "had_country_flag = { flag = host_recently_moved days = 9125 }" in can_carry
    assert "had_country_flag = { flag = host_refuge_request_pending days = 90 }" in can_carry

    forced = named_block(text, "zaz_host_forced_to_flee")
    assert "NOT = { num_of_cities = 5 }" in forced
    assert "zaz_lineage_country = yes" in forced
    assert "NOT = { owns = 283 }" in forced
    assert "NOT = { num_of_cities = 3 }" in forced
    assert "has_disaster = zaporozhian_sich_crisis" in forced
    assert "revanchism = 25" in forced


def test_decision_contract() -> None:
    text = read("decisions/ZaporizhiaDecisions.txt")
    dec = named_block(text, "cossack_carry_the_host")

    potential = named_block(dec, "potential")
    assert "can_carry_the_host = yes" in potential
    assert "is_valid_host_refuge_province = yes" in potential

    highlight = named_block(dec, "provinces_to_highlight")
    assert "is_valid_host_refuge_province = yes" in highlight

    allow = named_block(dec, "allow")
    assert "is_at_war = no" in allow
    assert "stability = 0" in allow
    assert "adm_power = 100" in allow
    assert "mil_power = 100" in allow
    assert "zaz_host_forced_to_flee = yes" in allow
    assert "is_valid_host_refuge_holder = yes" in allow

    effect = named_block(dec, "effect")
    assert "cossack_carry_the_host_effect = yes" in effect
    assert "cossack_carry_the_host_leave_old_tt" in effect

    ai = named_block(dec, "ai_will_do")
    assert re.search(r"^\s*factor\s*=\s*1\b", ai, re.M), "EU4 ai_will_do top factor must be 1"
    assert "factor = 0" in ai
    assert "NOT = { owns = 283 }" in ai
    assert "NOT = { num_of_cities = 3 }" in ai
    assert "NOT = { num_of_cities = 2 }" in ai
    assert "revanchism = 25" in ai
    assert "has_disaster = zaporozhian_sich_crisis" in ai
    assert "war_with = ROOT" not in normalized(ai), "old broken war_with = ROOT inside ai_will_do must stay removed"
    assert not re.search(r"(?<!NOT = \{ )num_of_cities = 2\b", normalized(ai))


def test_effect_contract() -> None:
    text = read("common/scripted_effects/zaz_path_effects.txt")

    entry = named_block(text, "cossack_carry_the_host_effect")
    assert "save_event_target_as = host_carrying_country" in entry
    assert "ai = yes" in entry
    assert "ai = no" in entry
    assert "is_valid_host_refuge_holder = yes" in entry
    assert "is_valid_host_refuge_province = yes" in entry
    assert "zaz_complete_carry_the_host_effect = yes" in entry
    assert "set_country_flag = host_refuge_request_pending" in entry
    assert "country_event = { id = zaz_paths.6 }" in entry

    complete = named_block(text, "zaz_complete_carry_the_host_effect")
    assert "ROOT" not in normalized(complete), (
        "zaz_complete_carry_the_host_effect may be called from FROM = { ... } inside zaz_paths.6; "
        "use event_target:host_carrying_country instead of ROOT"
    )
    assert "has_saved_event_target = host_new_seat" in complete
    assert "has_saved_event_target = host_refuge_holder" in complete
    assert "has_saved_event_target = host_carrying_country" in complete
    assert "remove_core" not in complete, "abandoned provinces must keep cores for reconquest"
    assert complete.index("set_capital = event_target:host_new_seat") < complete.index("every_owned_province"), (
        "capital must move before vacating old provinces"
    )
    assert "remove_province_modifier = zaporozhian_sich_capital" in complete
    assert "any_core_country" in complete
    assert "random_core_country" in complete
    assert "any_neighbor_province" in complete
    assert "random_neighbor_province" in complete
    assert "zaz_gave_the_host_refuge" in complete
    assert "zaz_host_in_exile" in complete
    assert "set_country_flag = host_recently_moved" in complete
    assert "country_event = { id = zaz_paths.5 days = 5 }" in complete


def test_consent_event_contract() -> None:
    text = read("events/RIP_ZAZ_ZaporizhiaPaths.txt")
    events = [blk for _, blk in keyed_blocks(text, "country_event") if re.search(r"\bid\s*=\s*zaz_paths\.6\b", blk)]
    assert len(events) == 1, f"expected exactly 1 zaz_paths.6 definition, found {len(events)}"
    ev = events[0]
    assert "is_triggered_only = yes" in ev
    assert "is_valid_host_refuge_province" not in ev, (
        "ROOT inside zaz_paths.6 is the refuge holder, not FROM; use explicit FROM checks"
    )
    assert "is_host_refuge = yes" in ev
    assert "NOT = { owned_by = FROM }" in ev
    assert "is_capital = no" in ev
    assert "controlled_by = owner" in ev
    assert "zaz_complete_carry_the_host_effect = yes" in ev
    assert "set_country_flag = zaz_refused_host_refuge" in ev
    assert "clr_country_flag = host_refuge_request_pending" in ev
    assert "add_adm_power = 100" in ev
    assert "add_mil_power = 100" in ev


def test_localisation_and_docs() -> None:
    keys = (
        "cossack_carry_the_host_tt",
        "cossack_carry_the_host_crisis_tt",
        "cossack_carry_the_host_leave_old_tt",
        "zaz_paths.6.t",
        "zaz_paths.6.d",
        "zaz_paths.6.a",
        "zaz_paths.6.b",
    )
    files = (
        "localisation/RIP_ZAZ_realm_l_english.yml",
        "localisation/replace/RIP_ZAZ_content_l_french.yml",
        "localisation/replace/RIP_ZAZ_content_l_german.yml",
        "localisation/replace/RIP_ZAZ_content_l_spanish.yml",
    )
    for rel in files:
        txt = read(rel)
        for key in keys:
            assert re.search(rf"^\s*{re.escape(key)}:\d*\s+\".+\"", txt, re.M), f"{key} missing in {rel}"

    doc = read("docs/ZAPORIZHIA_PATHS.md")
    assert "zaz_paths.6" in doc
    assert "zaz_host_forced_to_flee" in doc
    assert "is_valid_host_refuge_province" in doc
    assert "silistria_area" in doc
    assert "sloboda_ukraine_area" in doc


def main() -> int:
    test_refuge_triggers()
    test_path_triggers()
    test_decision_contract()
    test_effect_contract()
    test_consent_event_contract()
    test_localisation_and_docs()
    print("ALL CARRY THE HOST REGRESSION CHECKS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
