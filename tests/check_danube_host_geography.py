#!/usr/bin/env python3
"""
Test to verify that the Danube Host (found_the_danube_sich) correctly requires
actual Danube littoral / riverbank territory and does not accept arbitrary inland
provinces (like northern Moldavia), does not inappropriately assign exile penalties
to an autonomous sovereign host, and uses the correct host nomenclature.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_refuge_triggers():
    triggers_file = ROOT / "common" / "scripted_triggers" / "zaz_refuge_triggers.txt"
    content = triggers_file.read_text(encoding="utf-8")

    assert "holds_the_danube_bank = {" in content, "holds_the_danube_bank missing"

    # Extract holds_the_danube_bank block
    start = content.index("holds_the_danube_bank = {")
    # Find matching brace
    depth = 0
    end = start
    for i, char in enumerate(content[start:], start):
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    danube_block = content[start:end]

    # Must require genuine Danubian bank/littoral
    assert "area = silistria_area" in danube_block, "Danube bank must check silistria_area (Dobruja/Silistria)"
    assert "province_id = 1756" in danube_block, "Danube bank must check 1756 (Kiliia/Budjak Danube mouth)"
    # Must NOT simply allow any moldavia_area province (e.g. Suceava/Iasi)
    assert "area = moldavia_area" not in danube_block, "Inland moldavia_area must not satisfy Danube bank"

    # is_host_refuge must include silistria_area (the historical Danube Sich refuge)
    start_refuge = content.index("is_host_refuge = {")
    depth = 0
    end_refuge = start_refuge
    for i, char in enumerate(content[start_refuge:], start_refuge):
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                end_refuge = i + 1
                break
    refuge_block = content[start_refuge:end_refuge]
    assert "area = silistria_area" in refuge_block, "is_host_refuge should include silistria_area"


def test_cossack_host_decision():
    decisions_file = ROOT / "decisions" / "CossackHostDecisions.txt"
    content = decisions_file.read_text(encoding="utf-8")

    assert "found_the_danube_sich = {" in content, "found_the_danube_sich decision missing"
    start = content.index("found_the_danube_sich = {")
    depth = 0
    end = start
    for i, char in enumerate(content[start:], start):
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    dec_block = content[start:end]

    # Check geography
    assert "area = silistria_area" in dec_block, "Decision must highlight/check silistria_area"
    assert "province_id = 1756" in dec_block, "Decision must highlight/check 1756"
    assert "area = moldavia_area" not in dec_block, "Inland moldavia_area must not be in potential/highlight"

    # Check allow and effect
    assert "holds_the_danube_bank = yes" in dec_block
    assert "found_cossack_host_effect = yes" in dec_block
    assert "zaz_host_in_exile" not in dec_block, (
        "Free Danube Host formation must not inflict zaz_host_in_exile penalties; "
        "exile is reserved for actual flight (cossack_carry_the_host_effect)."
    )


def test_dynamic_names():
    dyn_file = ROOT / "customizable_localization" / "RIP_shared_cossack_host_dynamic_names.txt"
    content = dyn_file.read_text(encoding="utf-8")

    # GetHostSeatName for Danube must include silistria_area and 1756
    assert "area = silistria_area" in content
    assert "localisation_key = SEAT_DANUBE" in content
    assert "localisation_key = HOSTLAND_DANUBE" in content


def test_localization():
    loc_files = [
        ROOT / "localisation" / "zaz_paths_l_english.yml",
        ROOT / "localisation" / "replace" / "zzz_zaz_paths_l_french.yml",
        ROOT / "localisation" / "replace" / "zzz_zaz_paths_l_german.yml",
        ROOT / "localisation" / "replace" / "zzz_zaz_paths_l_spanish.yml",
    ]

    for loc in loc_files:
        text = loc.read_text(encoding="utf-8-sig")
        assert "HOSTLAND_DANUBE" in text
        assert "found_the_danube_sich_title" in text
        assert "Danube Sich" not in text, f"Danube Sich found in {loc.name}, should be Host"


if __name__ == "__main__":
    test_refuge_triggers()
    test_cossack_host_decision()
    test_dynamic_names()
    test_localization()
    print("ALL DANUBE HOST GEOGRAPHY TESTS PASSED")
