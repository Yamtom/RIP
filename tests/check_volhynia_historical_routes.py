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
    legacy = read("missions/zzz_VOL_VLN_Legacy_Transition.txt")

    alliance = named_block(legacy, "VLN_galician_alliance")
    alliance_trigger = normalized(named_block(alliance, "trigger"))
    alliance_effect = normalized(named_block(alliance, "effect"))
    # An independent HLC must not first conquer allied Volhynia to choose a path.
    assert "hlc_has_any_path" not in alliance_trigger
    assert "VOL_unite_galicia" not in alliance_trigger
    assert "is_subject = no" in alliance_trigger
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
    assert "hlc_has_any_path" not in fed_trigger
    assert "trust = { who = HLC value = 65 }" in fed_trigger
    assert "dip_power = 75" in fed_trigger and "treasury = 100" in fed_trigger
    assert "add_dip_power = -75" in fed_effect and "add_treasury = -100" in fed_effect
    assert fed_effect.count("name = rip_vol_carpathian_compact") == 2
    assert "add_favors = { who = HLC amount = 15 }" in fed_effect
    assert "add_favors = { who = ROOT amount = 15 }" in fed_effect

    alt_events = read("events/RIP_VOL_Volhynia_Alt_History.txt")
    for dead_id in ("rip_vol_alt_history.5", "rip_vol_alt_history.6", "rip_vol_alt_history.7", "rip_vol_alt_history.8"):
        assert dead_id not in alt_events, f"dead decorative stub {dead_id} must stay removed"

    ev_by_title = {
        re.search(r"\btitle\s*=\s*(rip_vol_alt_history\.\d+\.t)", b).group(1): normalized(b)
        for _, b in keyed_blocks(alt_events, "country_event")
        if "title = rip_vol_alt_history." in b
    }
    ev9 = ev_by_title["rip_vol_alt_history.9.t"]
    assert ev9.count("remove_country_modifier = rip_vol_carpathian_compact") >= 2
    assert ev9.count("add_dip_power = -50") == 2
    assert "add_historical_friend = FROM" in ev9 and "add_historical_friend = ROOT" in ev9
    assert "name = rip_vol_federal_compact duration = -1" in ev9
    assert "name = rip_vol_sovereign_alliance_modifier" in ev9
    assert "add_favors = { who = FROM amount = 15 }" in ev9
    assert "add_favors = { who = ROOT amount = 15 }" in ev9

    ev2 = ev_by_title["rip_vol_alt_history.2.t"]
    assert "name = rip_vol_grand_ruthenia_doctrine duration = -1" in ev2
    assert "name = rip_vol_baltic_hegemon_doctrine duration = -1" in ev2
    assert "add_dip_power" not in ev2 and "add_mil_power" not in ev2

    ev3 = ev_by_title["rip_vol_alt_history.3.t"]
    assert "name = rip_vol_synod_orthodox_settlement duration = -1" in ev3
    assert "name = rip_vol_synod_uniate_settlement duration = -1" in ev3
    assert "name = rip_vol_synod_pluralist_settlement duration = -1" in ev3

    ev4 = ev_by_title["rip_vol_alt_history.4.t"]
    assert ev4.count("change_estate_land_share") == 3
    assert "add_adm_power" not in ev4 and "add_dip_power" not in ev4 and "add_mil_power" not in ev4

    vol_on_actions = normalized(read("common/on_actions/RIP_VOL_on_actions.txt"))
    assert "on_alliance_broken = {" in vol_on_actions
    assert "remove_historical_friend = FROM" in vol_on_actions
    assert "remove_country_modifier = rip_vol_federal_compact" in vol_on_actions
    assert "remove_country_modifier = rip_vol_sovereign_alliance_modifier" in vol_on_actions


def check_conquest_hegemony_triggers() -> None:
    conquest = read("missions/Volhynia_Conquest_Missions.txt")
    reward = normalized(named_block(named_block(conquest, "VOL_conquer_bilorus"), "effect"))
    assert "add_adm_power = 50" in reward and "add_dip_power = 75" in reward
    assert "add_accepted_culture" not in reward and "add_claim" not in reward
    north = named_block(read("missions/Volhynia_Common_Missions.txt"), "VOL_integrate_north")
    white_reward = named_block(named_block(north, "effect"), "white_ruthenia_area")
    assert "add_permanent_claim" not in white_reward and "add_claim" not in white_reward
    ascendancy = named_block(read("common/event_modifiers/VOL_mission_modifiers.txt"), "vol_diplomatic_ascendancy")
    assert "karma" not in ascendancy
    for mission_name in ("VOL_demolish_poland", "VOL_demolish_lithuania", "VOL_demolish_MOS"):
        trigger = normalized(named_block(named_block(conquest, mission_name), "trigger"))
        assert "NOT = { any_owned_province = { region = ruthenia_region } }" in trigger, (
            f"{mission_name}: must allow completion via regional expulsion instead of total annexation"
        )
        assert "NOT = { is_great_power = yes }" in trigger, (
            f"{mission_name}: must check loss of Great Power hegemony"
        )
        assert "NOT = { army_strength = { who = ROOT" in trigger, (
            f"{mission_name}: must check loss of military parity"
        )
    vln_legacy = read("missions/zzz_VOL_VLN_Legacy_Transition.txt")
    baltic_trig = normalized(named_block(named_block(vln_legacy, "VLN_baltic_aspirations"), "trigger"))
    assert "NOT = { any_owned_province = { region = ruthenia_region } }" in baltic_trig
    crimea_trig = normalized(named_block(named_block(vln_legacy, "VLN_conquer_crimea"), "trigger"))
    assert "NOT = { any_owned_province = { region = crimea_region } }" in crimea_trig


def main() -> int:
    check_chumak_route()
    check_ostroh_education()
    check_galician_partnership()
    check_conquest_hegemony_triggers()
    print(
        "VOLHYNIA HISTORICAL ROUTES PASS: Chumak market/security route, "
        "Ostroh Academy (1576) & Bible (1581), substantive political settlements, "
        "non-annihilation conquest triggers, and mutual Halych partnership verified."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
