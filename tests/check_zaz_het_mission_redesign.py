"""Focused regression checks for Zaporozhie branch victory conditions and Hetmanate missions/events."""

from __future__ import annotations

import re
import sys

from clausewitz_testlib import keyed_blocks, named_block, normalized, read


def require(failures: list[str], condition: bool, message: str) -> None:
    if not condition:
        failures.append(message)


def event_block(text: str, event_id: str) -> str:
    candidates = [
        block for _, block in keyed_blocks(text, "country_event")
        if re.search(rf"\bid\s*=\s*{re.escape(event_id)}\b", block)
        and re.search(r"(?m)^\s*title\s*=", block)
    ]
    if candidates:
        return max(candidates, key=len)
    raise KeyError(f"country_event {event_id!r} not found")


def check_preserved_zaz_strengths(failures: list[str], zaz_missions: str, zaz_events: str) -> None:
    sich = named_block(zaz_missions, "ZAZ_establish_sich")
    require(failures, "283 = {" in sich and "has_building = fort_15th" in sich,
            "ZAZ_establish_sich must preserve Lower Dnieper fort requirement on 283")

    kaffa = named_block(zaz_missions, "ZAZ_TUR_slave_trade")
    require(
        failures,
        "province_id = 285" in kaffa
        and "remove_province_modifier = crimean_yasyr_market" in kaffa
        and "name = kaffa_ransom_exchange" in kaffa
        and "center_of_trade = 1" in kaffa,
        "ZAZ_TUR_slave_trade must preserve Kaffa ransom exchange and CoT development",
    )

    rel_ev = event_block(zaz_events, "zaz_flavor_m_5.1")
    require(failures, "change_religion" not in rel_ev and "sunni" not in rel_ev
            and "zaz_ottoman_berat" in rel_ev and "zaz_ortho" in rel_ev,
            "zaz_flavor_m_5.1 is the Sultan's berat: an accept option that changes no faith, and the Orthodox option")


def check_zaz_branch_victory_and_russia_finale(failures: list[str], zaz_missions: str) -> None:
    # 1. Distinct path victory conditions (no mandatory full Ruthenia direct conquest)
    pol_end = named_block(zaz_missions, "ZAZ_POL_ruthenia")
    pol_trig = named_block(pol_end, "trigger")
    pol_eff = named_block(pol_end, "effect")
    require(failures, "ruthenia_region" not in pol_end and "add_permanent_claim" not in pol_eff,
            "ZAZ_POL_ruthenia must not require full Ruthenia conquest or grant Russia permanent claims")
    require(
        failures,
        "rip_hadiach_ratified" in pol_trig
        and "rip_register_confirmed" in pol_trig
        and "name = zaz_pol_host_charter" in pol_eff,
        "ZAZ_POL_ruthenia must reward recognized rights of the Host",
    )

    cri_end = named_block(zaz_missions, "ZAZ_cri_crossings_compact")
    cri_trig = named_block(cri_end, "trigger")
    cri_eff = named_block(cri_end, "effect")
    require(
        failures,
        "alliance_with = CRI" in cri_trig
        and "owns = 283" in cri_trig
        and "kaffa_ransom_exchange" in cri_trig
        and "name = zaz_cri_crossings_compact_mod" in cri_eff,
        "ZAZ_cri_crossings_compact must validate Crimean crossings/captives accord",
    )

    gol_end = named_block(zaz_missions, "ZAZ_GOL_ruthenia")
    gol_trig = named_block(gol_end, "trigger")
    gol_eff = named_block(gol_end, "effect")
    require(failures, "ruthenia_region" not in gol_end and "add_permanent_claim" not in gol_eff,
            "ZAZ_GOL_ruthenia must not require full Ruthenia conquest or grant Russia permanent claims")
    require(
        failures,
        "alliance_with = GOL" in gol_trig
        and "owns = 283" in gol_trig
        and "kaffa_ransom_exchange" in gol_trig
        and "name = zaz_gol_steppe_compact" in gol_eff,
        "ZAZ_GOL_ruthenia must reward Horde crossings and captive accord",
    )

    ukr_settle = named_block(zaz_missions, "ZAZ_UKR_settle_north_1")
    require(
        failures,
        "development_in_provinces = {" in ukr_settle and "development = 650" not in ukr_settle,
        "ZAZ_UKR_settle_north_1 must use development_in_provinces instead of single-province 650 dev",
    )

    ukr_end = named_block(zaz_missions, "ZAZ_UKR_ruthenia")
    ukr_trig = named_block(ukr_end, "trigger")
    ukr_eff = named_block(ukr_end, "effect")
    require(failures, "ruthenia_region" not in ukr_end and "add_permanent_claim" not in ukr_eff,
            "ZAZ_UKR_ruthenia must not require full Ruthenia conquest or grant Russia permanent claims")
    require(
        failures,
        "is_subject = no" in ukr_trig
        and "owns_core_province = 283" in ukr_trig
        and "calc_true_if" in ukr_trig
        and "amount = 3" in ukr_trig
        and "name = zaz_ukr_unbroken_liberties" in ukr_eff,
        "ZAZ_UKR_ruthenia must require preserving liberties and enduring multi-neighbor pressure",
    )

    # 2. Optional grand-war Russian finale across all three branches
    for prefix in ("ZAZ_POL", "ZAZ_GOL", "ZAZ_UKR"):
        m1 = named_block(zaz_missions, f"{prefix}_russia")
        m2 = named_block(zaz_missions, f"{prefix}_russia_2")
        m3 = named_block(zaz_missions, f"{prefix}_russia_3")
        require(failures, "add_permanent_claim" not in m1 and "add_claim = ROOT" in m1,
                f"{prefix}_russia must grant normal claims only")
        require(
            failures,
            "295 = { country_or_non_sovereign_subject_holds = ROOT }" in normalized(m2)
            and "value = 23" in m2
            and "add_permanent_claim" not in m2
            and "add_claim = ROOT" in m2,
            f"{prefix}_russia_2 must gate full Russia claims behind Moskva (295) + 23 provinces",
        )
        require(failures, "russia_region = {" in m3 and "name = zaz_russia_buff" in m3,
                f"{prefix}_russia_3 must reward completing the optional Russia finale")


def check_hetmanate_missions_and_events(
    failures: list[str], het_missions: str, het_events: str, het_loc: str
) -> None:
    khm = named_block(het_missions, "het_khmelnytsky_uprising")
    khm_trig = named_block(khm, "trigger")
    khm_eff = named_block(khm, "effect")
    require(failures, "has_institution = renaissance" not in khm_trig,
            "het_khmelnytsky_uprising must not unlock on bare Renaissance without military/political trigger")
    require(failures, "ruthenia_region = {" not in khm_eff and "west_dniepr_area = {" in khm_eff,
            "het_khmelnytsky_uprising must scope claims to core Hetmanate areas rather than all Ruthenia")
    require(failures, 'het_khmelnytsky_uprising_title:0 "Uprising of the Host"' in het_loc,
            "het_khmelnytsky_uprising must use general title 'Uprising of the Host'")

    ortho = named_block(het_missions, "het_orthodox_defender")
    ortho_trig = named_block(ortho, "trigger")
    ortho_eff = named_block(ortho, "effect")
    require(failures, "poland_region" not in ortho_eff,
            "het_orthodox_defender must not grant permanent claims on Catholic Poland")
    require(
        failures,
        "het_orthodox_metropolis_pillar_tt" in ortho_trig
        and "het_orthodox_brotherhood_pillar_tt" in ortho_trig
        and "het_orthodox_register_pillar_tt" in ortho_trig
        and "country_event = { id = het_enhanced.9 }" in normalized(ortho_eff),
        "het_orthodox_defender must gate on Metropolis/Brotherhood/Register and fire het_enhanced.9",
    )

    ev9 = event_block(het_events, "het_enhanced.9")
    require(
        failures,
        "is_triggered_only = yes" in ev9
        and "kyiv_orthodox_metropolitanate" in ev9
        and "orthodox_brotherhoods" in ev9
        and "het_registered_cossacks_integrated" in ev9,
        "het_enhanced.9 must offer Metropolis, Brotherhoods, and Register settlement options",
    )

    maz_ren = named_block(het_missions, "het_mazepa_renaissance")
    maz_trig = named_block(maz_ren, "trigger")
    maz_eff = named_block(maz_ren, "effect")
    require(
        failures,
        ("has_building = university" in maz_trig or "has_building = cathedral" in maz_trig)
        and "country_event = { id = het_enhanced.10 }" in normalized(maz_eff),
        "het_mazepa_renaissance must require collegium/temple patronage and fire het_enhanced.10",
    )

    ev10 = event_block(het_events, "het_enhanced.10")
    require(
        failures,
        "is_triggered_only = yes" in ev10
        and "add_treasury = -200" in ev10
        and "kyiv_mohyla_academy" in ev10
        and "het_kyiv_mazepa_golden_age" in ev10
        and "het_cultural_center" in ev10,
        "het_enhanced.10 must allow tangible funding of collegium or Baroque cathedral",
    )

    ev5 = event_block(het_events, "het_enhanced.5")
    require(
        failures,
        "set_country_flag = mazepa_allied_sweden" in ev5
        and "set_country_flag = mazepa_remained_loyal" in ev5
        and 'name = "het_loyal_hetmanate_charter"' in ev5,
        "het_enhanced.5 must set both mazepa_allied_sweden and mazepa_remained_loyal with charter reward",
    )

    swe = named_block(het_missions, "het_swedish_alliance")
    swe_trig = named_block(swe, "trigger")
    swe_eff = named_block(swe, "effect")
    require(
        failures,
        "global_trade" not in swe_trig
        and "is_year = 1708" not in swe_trig
        and "age_of_absolutism" not in swe_trig
        and "army_tradition = 80" not in swe_trig,
        "het_swedish_alliance must not allow completing without Swedish or loyalist commitment",
    )
    require(
        failures,
        "has_country_flag = mazepa_allied_sweden" in swe_trig
        and "alliance_with = SWE" in swe_trig
        and "has_country_flag = mazepa_remained_loyal" in swe_trig
        and "het_independence_struggle" in swe_eff
        and "het_loyal_autonomy_accord" in swe_eff,
        "het_swedish_alliance must accept mazepa_allied_sweden/alliance OR loyal course with distinct rewards",
    )


def main() -> int:
    failures: list[str] = []
    zaz_missions = read("missions/Zaporozhie_Missions.txt")
    zaz_events = read("events/RIP_ZAZ_ZAZmission.txt")
    het_missions = read("missions/zzz_Hetmanate_Missions.txt")
    het_events = read("events/RIP_HET_HetmanateEnhanced.txt")
    het_loc = read("localisation/RIP_HET_realm_l_english.yml")

    check_preserved_zaz_strengths(failures, zaz_missions, zaz_events)
    check_zaz_branch_victory_and_russia_finale(failures, zaz_missions)
    check_hetmanate_missions_and_events(failures, het_missions, het_events, het_loc)

    if failures:
        print("ZAZ/HET mission redesign contract failures:")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print("ZAZ/HET mission redesign contracts hold")
    return 0


if __name__ == "__main__":
    sys.exit(main())
