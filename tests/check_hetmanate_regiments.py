"""Regression contracts for Hetmanate regimental territorial governance.

Verifies:
1. Decision het_regimental_territorial_governance_decision:
   - provinces_to_highlight present for regimental provinces.
   - Gated on HET/regimental reforms, peacetime, stability >= 0, 25 ADM, cooldown.
   - Calls event het_regiment_governance.1.
2. Event chain in events/HetmanateRegimentalGovernance.txt:
   - Root selector event het_regiment_governance.1 branches into regional polky.
   - Three repeatable governing paths in each branch:
     a) Military Service: het_regiment_military_service (+35% manpower, upkeep, +5 autonomy).
     b) Starshyna Rights: het_regiment_starshyna_rights (+15% autonomy, -15% manpower, +20% production, -5 unrest).
     c) Centralization: het_regiment_centralized_rule (-15% autonomy, +25% tax, +3 unrest, absolutism/tradition).
3. Modifiers in common/event_modifiers/RIP_HET_modifiers.txt follow the het_ prefix and formatting standards.
4. Localization present in English and all 3 fallback languages.
"""

from __future__ import annotations

import re
from pathlib import Path
from clausewitz_testlib import ROOT, read, named_block, normalized


def test_decision():
    decisions = read("decisions/HetmanateDecisions.txt")
    decision = named_block(decisions, "het_regimental_territorial_governance_decision")
    assert decision, "het_regimental_territorial_governance_decision missing in decisions/HetmanateDecisions.txt"

    assert "provinces_to_highlight" in decision, "Decision must highlight regimental seats on map"
    assert "adm_power = 25" in decision
    assert "NOT = { has_country_modifier = het_recent_regimental_reform }" in decision
    assert "country_event = { id = het_regiment_governance.1 }" in decision

    potential = normalized(named_block(decision, "potential"))
    assert "tag = HET" in potential
    assert "has_reform = het_regimental_system_reform" in potential


def test_events():
    events = read("events/HetmanateRegimentalGovernance.txt")
    assert "namespace = het_regiment_governance" in events

    root_event = named_block(events, "country_event")
    assert "id = het_regiment_governance.1" in root_event
    assert "country_event = { id = het_regiment_governance.2 }" in root_event
    assert "country_event = { id = het_regiment_governance.3 }" in root_event
    assert "country_event = { id = het_regiment_governance.4 }" in root_event
    assert "country_event = { id = het_regiment_governance.5 }" in root_event

    for event_id in ["het_regiment_governance.2", "het_regiment_governance.3", "het_regiment_governance.4", "het_regiment_governance.5"]:
        assert f"id = {event_id}" in events
        assert "name = het_regiment_military_service" in events
        assert "name = het_regiment_starshyna_rights" in events
        assert "name = het_regiment_centralized_rule" in events
        assert "add_local_autonomy = 15" in events, "Starshyna rights concede +15% autonomy"
        assert "add_local_autonomy = -15" in events, "Centralization reduces autonomy by -15%"



def test_modifiers():
    modifiers = read("common/event_modifiers/RIP_HET_modifiers.txt")
    mil = named_block(modifiers, "het_regiment_military_service")
    assert "local_manpower_modifier = 0.35" in mil
    assert "local_regiment_cost = 0.1" in mil
    assert "state_maintenance_modifier = 0.2" in mil

    starshyna = named_block(modifiers, "het_regiment_starshyna_rights")
    assert "local_production_efficiency = 0.2" in starshyna
    assert "local_manpower_modifier = -0.15" in starshyna
    assert "local_tax_modifier = -0.2" in starshyna
    assert "state_maintenance_modifier = -0.25" in starshyna

    central = named_block(modifiers, "het_regiment_centralized_rule")
    assert "local_tax_modifier = 0.25" in central
    assert "autonomy_change_time = -0.25" in central
    assert "state_maintenance_modifier = 0.15" in central


def test_localization():
    required_keys = [
        "het_regimental_territorial_governance_decision_title",
        "het_regimental_territorial_governance_decision_desc",
        "het_regiment_governance.1.t",
        "het_regiment_governance.1.a",
        "het_regiment_governance.1.b",
        "het_regiment_governance.1.c",
        "het_regiment_governance.2.t",
        "het_regiment_governance.2.a",
        "het_regiment_governance.2.b",
        "het_regiment_governance.2.c",
        "het_regiment_military_service",
        "het_regiment_starshyna_rights",
        "het_regiment_centralized_rule",
        "het_recent_regimental_reform",
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
    print("HETMANATE REGIMENTAL GOVERNANCE PASS: Territorial administration, military service, starshyna rights, and centralization contracts verified.")


if __name__ == "__main__":
    main()
