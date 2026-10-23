"""Regression test for targeted princely re-grant and territorial concessions.

Verifies:
1. Targeted princely udil re-grant diplomatic action (rip_regrant_the_udil).
   - Category, no acceptance, visible to Kyivan reforms over princedom/senior_udil.
   - Balanced pricing: 65 DIP, 10 prestige, removes rip_tenure_lapsed, reduces LD by 30.
   - Cooldown modifier KIE_udil_recently_confirmed on subject.
   - Dynamic ripple effect: +5 LD for other disloyal appanages (LD >= 50).
2. Volhynian targeted territorial concessions (vln_magnate_territorial_concession_decision,
   rip_vln_concessions.1, and vln_magnate_senate_mechanic integration).
   - Highlights eligible provinces on the map.
   - Event offers distinct magnate house options (Ostrozky 2962, Chartoryisky 4539, Sanguszko 4538/277).
   - Balanced pricing: 0.75 income, 30 ADM, +20 local autonomy, vln_magnate_fief_concession (-15% tax/manpower).
   - Mechanic button triggers event for human players.
3. Localization presence across English and all 3 fallback files.
"""

from __future__ import annotations

import re
from pathlib import Path
from clausewitz_testlib import ROOT, read, named_block, normalized


def test_kyivan_targeted_regrant():
    text = read("common/new_diplomatic_actions/RIP_KIE_diplomatic_actions.txt")
    action = named_block(text, "rip_regrant_the_udil")
    assert action, "rip_regrant_the_udil action missing in RIP_KIE_diplomatic_actions.txt"

    assert "category = influence" in action
    assert "require_acceptance = no" in action

    visible = normalized(named_block(action, "is_visible"))
    assert "overlord_of = FROM" in visible
    assert "has_reform = kyivan_rus_reform" in visible
    assert "is_subject_of_type = princedom" in visible
    assert "is_subject_of_type = senior_udil" in visible

    allowed = normalized(named_block(action, "is_allowed"))
    assert "dip_power = 65" in allowed, "Priced higher than random button (65 DIP)"
    assert "prestige = 10" in allowed
    assert "has_country_modifier = rip_tenure_lapsed" in allowed
    assert "NOT = { has_country_modifier = KIE_udil_recently_confirmed }" in allowed

    accept = normalized(named_block(action, "on_accept"))
    assert "add_dip_power = -65" in accept
    assert "add_prestige = -10" in accept
    assert "remove_country_modifier = rip_tenure_lapsed" in accept
    assert "add_liberty_desire = -30" in accept
    assert "name = KIE_udil_recently_confirmed" in accept
    assert "add_liberty_desire = 5" in accept, "Jealousy ripple effect for other disloyal princes"


def test_volhynian_territorial_concessions():
    # Decision check
    decisions = read("decisions/VLNRepublicPaths.txt")
    decision = named_block(decisions, "vln_magnate_territorial_concession_decision")
    assert decision, "vln_magnate_territorial_concession_decision missing in decisions/VLNRepublicPaths.txt"
    assert "provinces_to_highlight" in decision
    assert "years_of_income = 0.75" in decision
    assert "adm_power = 30" in decision
    assert "country_event = { id = rip_vln_concessions.1 }" in decision

    # Event check
    events = read("events/VolhynianConcessions.txt")
    event = named_block(events, "country_event")
    assert "id = rip_vln_concessions.1" in event
    assert "owns = 2962" in event, "Ostrozky Rivne/Ostroh option"
    assert "owns = 4539" in event, "Chartoryisky Kremenets option"
    assert "owns = 4538" in event and "owns = 277" in event, "Sanguszko Chelm/Brest option"
    assert "add_local_autonomy = 20" in event, "Concession increases autonomy by 20%"
    assert "name = vln_magnate_fief_concession" in event

    # Mechanic button check
    mechanic = read("common/government_mechanics/rip_vln_magnate_senate.txt")
    buyoff = named_block(named_block(named_block(mechanic, "vln_magnate_senate_mechanic"), "interactions"), "vln_buy_off_a_magnate_house")
    assert "country_event = { id = rip_vln_concessions.1 }" in buyoff, "Human player receives targeted event"


def test_localization():
    required_keys = [
        "rip_regrant_the_udil",
        "rip_regrant_the_udil_desc",
        "KIE_udil_recently_confirmed",
        "vln_magnate_territorial_concession_decision_title",
        "rip_vln_concessions.1.t",
        "rip_vln_concessions.1.a",
        "rip_vln_concessions.1.b",
        "rip_vln_concessions.1.c",
        "rip_vln_concessions.1.e",
        "rip_vln_concessions.1.f",
        "vln_magnate_fief_concession",
        "vln_magnate_concession_cooldown",
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
    test_kyivan_targeted_regrant()
    test_volhynian_territorial_concessions()
    test_localization()
    print("TARGETED SELECTION PASS: Kyivan princely re-grant and Volhynian territorial concessions contracts verified.")


if __name__ == "__main__":
    main()
