#!/usr/bin/env python3
"""
Test to verify the Cossack Frontier Host Network:
1. Sloboda Host geography: holds_the_sloboda_country and found_the_sloboda_host
   specifically target area = sloboda_ukraine_area, not the entire ruthenia_region.
2. Network coordination: GetHostCountryName recognizes multiple hosts (calc_true_if amount = 2)
   as HOSTLAND_UNITED ("United Cossack Hosts").
3. Localizations are present across all languages.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_sloboda_triggers():
    triggers_file = ROOT / "common" / "scripted_triggers" / "zaz_refuge_triggers.txt"
    content = triggers_file.read_text(encoding="utf-8")

    assert "holds_the_sloboda_country = {" in content
    start = content.index("holds_the_sloboda_country = {")
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
    sloboda_block = content[start:end]

    assert "area = sloboda_ukraine_area" in sloboda_block, (
        "holds_the_sloboda_country must check area = sloboda_ukraine_area"
    )
    assert "region = ruthenia_region" not in sloboda_block, (
        "holds_the_sloboda_country must not check entire ruthenia_region"
    )
    assert "value = 2" in sloboda_block


def test_sloboda_decision():
    decisions_file = ROOT / "decisions" / "CossackHostDecisions.txt"
    content = decisions_file.read_text(encoding="utf-8")

    assert "found_the_sloboda_host = {" in content
    start = content.index("found_the_sloboda_host = {")
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
    sloboda_block = content[start:end]

    assert "area = sloboda_ukraine_area" in sloboda_block
    assert "region = ruthenia_region" not in sloboda_block
    assert "holds_the_sloboda_country = yes" in sloboda_block
    assert "add_permanent_claim = ROOT" in sloboda_block


def test_host_network_dynamic_names():
    dyn_file = ROOT / "customizable_localization" / "RIP_shared_cossack_host_dynamic_names.txt"
    content = dyn_file.read_text(encoding="utf-8")

    # SEAT_SLOBODA must check sloboda_ukraine_area, not all ruthenia_region
    start_seat = content.rfind("defined_text = {", 0, content.index("name = GetHostSeatName"))
    depth = 0
    end_seat = start_seat
    for i, char in enumerate(content[start_seat:], start_seat):
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                end_seat = i + 1
                break
    seat_block = content[start_seat:end_seat]
    assert "area = sloboda_ukraine_area" in seat_block
    assert "SEAT_SLOBODA" in seat_block

    # GetHostCountryName must have HOSTLAND_UNITED for multiple hosts
    start_country = content.rfind("defined_text = {", 0, content.index("name = GetHostCountryName"))
    depth = 0
    end_country = start_country
    for i, char in enumerate(content[start_country:], start_country):
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                end_country = i + 1
                break
    country_block = content[start_country:end_country]

    assert "HOSTLAND_UNITED" in country_block
    assert "calc_true_if" in country_block
    assert "amount = 2" in country_block
    assert "has_country_flag = founded_don_host" in country_block
    assert "has_country_flag = founded_sloboda_host" in country_block
    assert "has_country_flag = founded_danube_sich" in country_block
    assert "has_country_flag = founded_eastern_host" in country_block


def test_localization_keys():
    loc_files = [
        ROOT / "localisation" / "zaz_paths_l_english.yml",
        ROOT / "localisation" / "replace" / "zzz_zaz_paths_l_french.yml",
        ROOT / "localisation" / "replace" / "zzz_zaz_paths_l_german.yml",
        ROOT / "localisation" / "replace" / "zzz_zaz_paths_l_spanish.yml",
    ]

    for loc in loc_files:
        text = loc.read_text(encoding="utf-8-sig")
        assert "HOSTLAND_UNITED" in text, f"HOSTLAND_UNITED missing from {loc.name}"
        assert "HOSTLAND_SLOBODA" in text, f"HOSTLAND_SLOBODA missing from {loc.name}"
        assert "found_the_sloboda_host_title" in text, f"found_the_sloboda_host_title missing from {loc.name}"


if __name__ == "__main__":
    test_sloboda_triggers()
    test_sloboda_decision()
    test_host_network_dynamic_names()
    test_localization_keys()
    print("ALL COSSACK HOST NETWORK TESTS PASSED")
