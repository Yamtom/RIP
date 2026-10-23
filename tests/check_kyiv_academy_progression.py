#!/usr/bin/env python3
"""
Test to verify the Kyiv Academy historical progression:
1. het_expand_academy cannot appear in the 15th-16th century merely from embracing Renaissance.
2. The early alternative before 1632 is the Kyiv Brotherhood Collegium (het_found_brotherhood_collegium).
3. The historical route / elevation to Kyiv-Mohyla Academy requires is_year = 1632 or the mature collegium progression.
4. Elevating to the Academy replaces the Brotherhood Collegium with Kyiv-Mohyla Academy.
5. All required modifiers and localizations exist.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_modifiers():
    mod_file = ROOT / "common" / "event_modifiers" / "kyiv_dnieper_modifiers.txt"
    content = mod_file.read_text(encoding="utf-8")
    assert "kyiv_brotherhood_collegium = {" in content
    assert "kyiv_mohyla_academy = {" in content


def test_decisions():
    dec_file = ROOT / "decisions" / "HetmanateDecisions.txt"
    content = dec_file.read_text(encoding="utf-8")

    # Early brotherhood collegium decision
    assert "het_found_brotherhood_collegium = {" in content
    start_bc = content.index("het_found_brotherhood_collegium = {")
    depth = 0
    end_bc = start_bc
    for i, char in enumerate(content[start_bc:], start_bc):
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                end_bc = i + 1
                break
    bc_block = content[start_bc:end_bc]
    assert "NOT = { is_year = 1632 }" in bc_block, "Early collegium must be restricted to before 1632"
    assert "kyiv_brotherhood_collegium" in bc_block
    assert "kyiv_brotherhood_collegium_founded" in bc_block
    assert "kyiv_mohyla_academy" not in bc_block or "NOT = { 280 = { has_province_modifier = kyiv_mohyla_academy } }" in bc_block

    # Historical / elevated academy decision
    assert "het_expand_academy = {" in content
    start_ea = content.index("het_expand_academy = {")
    depth = 0
    end_ea = start_ea
    for i, char in enumerate(content[start_ea:], start_ea):
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                end_ea = i + 1
                break
    ea_block = content[start_ea:end_ea]

    # Must NOT allow bare renaissance to unlock Kyiv-Mohyla Academy in 1480
    assert "has_institution = renaissance" not in ea_block, (
        "het_expand_academy must not allow bare renaissance without proper temporal/collegium gates"
    )
    assert "is_year = 1632" in ea_block, "het_expand_academy must check 1632 historical foundation"
    assert "set_country_flag = academy_expanded" in ea_block
    assert "add_government_reform = het_academy_enlightenment_reform" in ea_block
    assert "remove_province_modifier = kyiv_brotherhood_collegium" in ea_block
    assert "name = kyiv_mohyla_academy" in ea_block


def test_flavor_event():
    event_file = ROOT / "events" / "HetmanateFlavor.txt"
    content = event_file.read_text(encoding="utf-8")
    assert "id = het_flavor.2" in content
    assert "kyiv_brotherhood_collegium" in content


def test_localization():
    loc_files = [
        ROOT / "localisation" / "RIP_l_english.yml",
        ROOT / "localisation" / "replace" / "zzz_RIP_untranslated_l_french.yml",
        ROOT / "localisation" / "replace" / "zzz_RIP_untranslated_l_german.yml",
        ROOT / "localisation" / "replace" / "zzz_RIP_untranslated_l_spanish.yml",
    ]

    for loc in loc_files:
        text = loc.read_text(encoding="utf-8-sig")
        assert "het_found_brotherhood_collegium_title" in text, f"Missing title in {loc.name}"
        assert "het_found_brotherhood_collegium_desc" in text, f"Missing desc in {loc.name}"
        assert "het_expand_academy_title" in text, f"Missing academy title in {loc.name}"
        assert "kyiv_brotherhood_collegium" in text, f"Missing modifier in {loc.name}"


if __name__ == "__main__":
    test_modifiers()
    test_decisions()
    test_flavor_event()
    test_localization()
    print("ALL KYIV ACADEMY PROGRESSION TESTS PASSED")
