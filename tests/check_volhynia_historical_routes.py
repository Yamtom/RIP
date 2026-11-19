"""Static contracts for Volhynia's Chumak trade, Ostroh education, and Halych partnership routes."""

from __future__ import annotations

import re

from clausewitz_testlib import keyed_blocks, named_block, normalized, read


def check_chumak_route() -> None:
    common = read("missions/Volhynia_Common_Missions.txt")
    mission = named_block(common, "VOL_conquer_moldavia")
    trigger = normalized(named_block(mission, "trigger"))
    effect = normalized(named_block(mission, "effect"))

    # Preserves Moldavia conquest while adding a commercial/diplomatic/security route.
    assert "moldavia_area = { type = all country_or_non_sovereign_subject_holds = ROOT }" in trigger
    assert "1322 = { has_merchant = ROOT trade_share = { country = ROOT share = 15 } }" in trigger
    assert "alliance_with = MOL" in trigger and "1756 = {" in trigger and "2405 = {" in trigger
    assert "podolia_volhynia_area = { type = all country_or_non_sovereign_subject_holds = ROOT NOT = { devastation = 1 } NOT = { unrest = 1 } }" in trigger
    assert "num_of_cavalry = 6" in trigger
    assert "name = vol_chumak_convoy_charters" in effect
    assert "NOT = { alliance_with = ROOT }" in effect


def check_ostroh_education() -> None:
    vol = read("missions/Volhynia_Missions.txt")
    academy = named_block(vol, "VOL_university_expansion")
    academy_trigger = normalized(named_block(academy, "trigger"))
    academy_effect = normalized(named_block(academy, "effect"))

    assert "owns_core_province = 2962" in academy_trigger
    assert "is_year = 1576" in academy_trigger and "has_institution = printing_press" in academy_trigger
    assert "treasury = 100" in academy_trigger and "add_treasury = -100" in academy_effect
    assert "add_building = university" in academy_effect
    assert "country_event = { id = vol_path_events.8 }" in academy_effect

    press = named_block(vol, "VOL_renaissance_court")
    press_trigger = normalized(named_block(press, "trigger"))
    press_effect = normalized(named_block(press, "effect"))
    assert "value = 3 has_building = university" not in press_trigger
    assert "owns_core_province = 2962" in press_trigger
    assert "has_institution = printing_press" in press_trigger
    assert "is_year = 1581" in press_trigger and "advisor = theologian" in press_trigger
    assert "name = vol_ostroh_printing_house" in press_effect
    assert "name = vol_ostroh_bible_legacy" in press_effect
    assert "country_event = { id = vol_path_events.9 }" in press_effect

    events = read("events/RIP_VOL_VOL_path_events.txt")
    ev_blocks = {
        re.search(r"\bid\s*=\s*(vol_path_events\.\d+)", b).group(1): normalized(b)
        for _, b in keyed_blocks(events, "country_event")
    }
    for eid, pic in (("vol_path_events.8", "UNIVERSITY_eventPicture"), ("vol_path_events.9", "BIG_BOOK_eventPicture")):
        assert eid in ev_blocks, f"missing {eid}"
        assert "is_triggered_only = yes" in ev_blocks[eid]
        assert "fire_only_once = yes" in ev_blocks[eid]
        assert f"picture = {pic}" in ev_blocks[eid]
    assert "2962 = { owned_by = ROOT has_building = university }" in ev_blocks["vol_path_events.4"]


def check_galician_partnership() -> None:
    legacy = read("missions/VOL_VLN_Legacy_Transition.txt")

    alliance = named_block(legacy, "VLN_galician_alliance")
    alliance_trigger = normalized(named_block(alliance, "trigger"))
    alliance_effect = normalized(named_block(alliance, "effect"))
    assert "dip_power = 50" in alliance_trigger and "add_dip_power = -50" in alliance_effect
    assert "add_claim = HLC" in alliance_effect
    assert "add_favors = { who = HLC amount = 10 }" in alliance_effect
    assert "add_favors = { who = ROOT amount = 10 }" in alliance_effect
    # Allied path must not grant ROOT claims on Red Ruthenia before the else branch.
    else_pos = alliance_effect.index("else = {")
    assert "add_claim = ROOT" not in alliance_effect[:else_pos]
    assert "NOT = { rip_vol_partner_holds_province = yes }" in alliance_effect[else_pos:]

    unite = named_block(legacy, "VLN_unite_galicia")
    unite_trigger = normalized(named_block(unite, "trigger"))
    for area in ("podolia_volhynia_area", "red_ruthenia_area", "volhynia_area"):
        assert f"{area} = {{ type = all rip_vol_partner_holds_province = yes }}" in unite_trigger, (
            f"VLN_unite_galicia must allow joint partner control of {area}"
        )

    fed = named_block(legacy, "VLN_carpathian_federation_eastern")
    fed_trigger = normalized(named_block(fed, "trigger"))
    fed_effect = normalized(named_block(fed, "effect"))
    assert "trust = { who = HLC value = 65 }" in fed_trigger
    assert "dip_power = 75" in fed_trigger and "treasury = 100" in fed_trigger
    assert "add_dip_power = -75" in fed_effect and "add_treasury = -100" in fed_effect
    assert fed_effect.count("name = rip_vol_carpathian_compact") == 2
    assert "add_favors = { who = HLC amount = 15 }" in fed_effect
    assert "add_favors = { who = ROOT amount = 15 }" in fed_effect

    alt_events = read("events/RIP_VOL_Volhynia_Alt_History.txt")
    ev9 = next(
        normalized(b)
        for _, b in keyed_blocks(alt_events, "country_event")
        if "title = rip_vol_alt_history.9.t" in b
    )
    assert ev9.count("remove_country_modifier = rip_vol_carpathian_compact") == 2
    assert ev9.count("add_dip_power = -50") == 2
    assert "add_favors = { who = FROM amount = 15 }" in ev9
    assert "add_favors = { who = ROOT amount = 15 }" in ev9


def main() -> int:
    check_chumak_route()
    check_ostroh_education()
    check_galician_partnership()
    print(
        "VOLHYNIA HISTORICAL ROUTES PASS: Chumak market/security route, "
        "Ostroh Academy (1576) & Bible (1581), and mutual Halych partnership verified."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
