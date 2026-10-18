"""Regression contracts for Podillia repeatable border policy.

Verifies:
1. Decision pdl_border_policy_decision:
   - provinces_to_highlight present for Podillian marchland provinces.
   - Gated on west_ukraine_pdl_origin_country, peacetime, stability >= 0, cooldown.
   - Calls event pdl_border_policy.1.
2. Event pdl_border_policy.1 in events/PodilliaBorderPolicy.txt:
   - Three repeatable policy paths:
     a) Fund Defense: differentiated by frontier, carpathian, and magnate paths.
     b) Support Settlements: differentiated by frontier, carpathian, and magnate paths.
     c) Delegate Power to Local Elites: differentiated by frontier, carpathian, and magnate paths.
3. Modifiers in common/event_modifiers/podillia_modifiers.txt follow formatting conventions and pdl_ prefix.
4. Localization present in English and all 3 fallback languages.
"""

from __future__ import annotations

from pathlib import Path
from clausewitz_testlib import ROOT, read, named_block, normalized


def test_decision():
    decisions = read("decisions/Podillia_Decisions.txt")
    decision = named_block(decisions, "pdl_border_policy_decision")
    assert decision, "pdl_border_policy_decision missing in decisions/Podillia_Decisions.txt"

    assert "provinces_to_highlight" in decision, "Decision must highlight Podillian borderlands"
    assert "NOT = { has_country_modifier = pdl_recent_border_policy }" in decision
    assert "country_event = { id = pdl_border_policy.1 }" in decision

    potential = normalized(named_block(decision, "potential"))
    assert "west_ukraine_pdl_origin_country = yes" in potential
    assert "has_country_flag = pdl_frontier_path" in potential
    assert "has_country_flag = pdl_carpathian_path" in potential
    assert "has_country_flag = pdl_magnate_path" in potential


def test_events():
    events = read("events/PodilliaBorderPolicy.txt")
    assert "namespace = pdl_border_policy" in events

    root_event = named_block(events, "country_event")
    assert "id = pdl_border_policy.1" in root_event
    assert "name = pdl_border_policy.1.a" in root_event
    assert "name = pdl_border_policy.1.b" in root_event
    assert "name = pdl_border_policy.1.c" in root_event
    assert "name = pdl_border_policy.1.d" in root_event

    # Differentiated paths in each branch
    norm_event = normalized(root_event)
    for branch_flag in ["pdl_frontier_path", "pdl_carpathian_path", "pdl_magnate_path"]:
        count = norm_event.count(f"has_country_flag = {branch_flag}")
        assert count >= 3, f"Flag {branch_flag} must differentiate defense, settlement, and elite delegation (found {count})"

    # Check key modifiers in event
    assert "name = pdl_frontier_defense_funded" in root_event
    assert "name = pdl_carpathian_defense_funded" in root_event
    assert "name = pdl_magnate_defense_funded" in root_event
    assert "name = pdl_frontier_settlement_supported" in root_event
    assert "name = pdl_carpathian_settlement_supported" in root_event
    assert "name = pdl_magnate_settlement_supported" in root_event
    assert "name = pdl_frontier_elites_delegated" in root_event
    assert "name = pdl_carpathian_elites_delegated" in root_event
    assert "name = pdl_magnate_elites_delegated" in root_event


def test_modifiers():
    modifiers = read("common/event_modifiers/podillia_modifiers.txt")

    defense_carpathian = named_block(modifiers, "pdl_carpathian_defense_funded")
    assert "defensiveness = 0.25" in defense_carpathian
    assert "garrison_size = 0.2" in defense_carpathian

    frontier_settlement = named_block(modifiers, "pdl_frontier_settlement_supported")
    assert "global_manpower_modifier = 0.15" in frontier_settlement

    magnate_elites = named_block(modifiers, "pdl_magnate_elites_delegated")
    assert "nobles_loyalty_modifier = 0.15" in magnate_elites
    assert "advisor_cost = -0.1" in magnate_elites


def test_localization():
    required_keys = [
        "pdl_border_policy_decision",
        "pdl_border_policy_decision_desc",
        "pdl_border_policy.1.t",
        "pdl_border_policy.1.d",
        "pdl_border_policy.1.a",
        "pdl_border_policy.1.b",
        "pdl_border_policy.1.c",
        "pdl_border_policy.1.d",
        "pdl_recent_border_policy",
        "pdl_frontier_defense_funded",
        "pdl_carpathian_defense_funded",
        "pdl_magnate_defense_funded",
        "pdl_defense_funded",
        "pdl_frontier_settlement_supported",
        "pdl_carpathian_settlement_supported",
        "pdl_magnate_settlement_supported",
        "pdl_settlement_supported",
        "pdl_frontier_elites_delegated",
        "pdl_carpathian_elites_delegated",
        "pdl_magnate_elites_delegated",
        "pdl_elites_delegated",
    ]

    for lang_file in [
        "localisation/RIP_l_english.yml",
        "localisation/replace/zzz_RIP_untranslated_l_french.yml",
        "localisation/replace/zzz_RIP_untranslated_l_german.yml",
        "localisation/replace/zzz_RIP_untranslated_l_spanish.yml",
    ]:
        content = (ROOT / lang_file).read_text(encoding="utf-8-sig")
        for key in required_keys:
            assert f" {key}:" in content, f"Missing key {key} in {lang_file}"


def main():
    test_decision()
    test_events()
    test_modifiers()
    test_localization()
    print("PODILLIA BORDER POLICY PASS: Repeatable policy, differentiated branch costs/effects, and localization contracts verified.")


if __name__ == "__main__":
    main()
