"""Static VFS, reachability, tier, and narrative contracts for RIP reforms."""

from __future__ import annotations

import hashlib
import re
from collections import Counter
from pathlib import Path

from clausewitz_testlib import ROOT, keyed_blocks, named_block, normalized, read


REFORMS_DIR = ROOT / "common/government_reforms"
EXPECTED_REFORM_COUNT = 109
EXPECTED_REFORM_ID_SHA256 = "8b247b233d0713166e00593ab045eeb7dd9c0a6dc1ad75f56589c9b6f48cdcee"


def require(failures: list[str], condition: bool, message: str) -> None:
    if not condition:
        failures.append(message)


def reform_sources() -> tuple[str, dict[str, Path]]:
    chunks: list[str] = []
    owners: dict[str, Path] = {}
    for path in sorted(REFORMS_DIR.glob("*.txt")):
        text = path.read_text(encoding="utf-8-sig")
        chunks.append(text)
        for reform in re.findall(r"(?m)^([A-Za-z0-9_]+)\s*=\s*\{", text):
            if reform in owners:
                raise ValueError(
                    f"duplicate reform {reform}: {owners[reform].name}, {path.name}"
                )
            owners[reform] = path
    return "\n".join(chunks), owners


def check_vfs_and_schema(failures: list[str], reforms: str, owners: dict[str, Path]) -> None:
    require(
        failures,
        not (REFORMS_DIR / "RIP_government_reforms.txt").exists(),
        "obsolete monolithic reform file still exists",
    )
    require(
        failures,
        len(owners) == EXPECTED_REFORM_COUNT,
        f"expected {EXPECTED_REFORM_COUNT} unique reforms, found {len(owners)}",
    )
    reform_id_hash = hashlib.sha256("\n".join(sorted(owners)).encode("utf-8")).hexdigest()
    require(
        failures,
        reform_id_hash == EXPECTED_REFORM_ID_SHA256,
        "government reform ID set changed (possible deleted/renamed save key)",
    )
    reform_map = read("docs/GOVERNMENT_REFORMS_MAP.uk.md")
    for reform in owners:
        require(
            failures,
            f"`{reform}`" in reform_map,
            f"government reform is missing from the visual map: {reform}",
        )
    require(
        failures,
        f"{EXPECTED_REFORM_COUNT} унікальних definition-ID" in reform_map,
        "visual map reports a stale government reform count",
    )
    for path in sorted(REFORMS_DIR.glob("*.txt")):
        require(failures, not path.read_bytes().startswith(b"\xef\xbb\xbf"), f"BOM: {path.name}")

    for stale in (
        "max_states",
        "monarch_mil_power",
        "prussian_republic_legacy",
        "monastic_order_legacy",
        'icon = "merchant_republic"',
        'icon = "monastic_order"',
    ):
        require(failures, stale not in reforms, f"stale or invalid reform token remains: {stale}")


def check_registration(failures: list[str], owners: dict[str, Path]) -> None:
    governments = read("common/governments/00_governments.txt")
    registered_chunks: list[str] = []
    for government_type in ("monarchy", "republic", "tribal", "native", "theocracy"):
        government = named_block(governments, government_type)
        basic_match = re.search(r"(?m)^\s*basic_reform\s*=\s*([A-Za-z0-9_]+)", government)
        if basic_match:
            registered_chunks.append(basic_match.group(1))
        reform_levels = named_block(government, "reform_levels")
        registered_chunks.extend(block for _, block in keyed_blocks(reform_levels, "reforms"))
    registered = normalized("\n".join(registered_chunks))
    for reform in owners:
        require(
            failures,
            re.search(rf"\b{re.escape(reform)}\b", registered) is not None,
            f"unregistered reform: {reform}",
        )

    m4 = normalized(named_block(governments, "state_and_religion"))
    m6 = normalized(named_block(governments, "deliberative_assembly"))
    m7 = normalized(named_block(governments, "growth_of_administration"))
    m8 = normalized(named_block(governments, "economical_matters"))
    m11 = normalized(named_block(governments, "separation_of_power"))
    r8 = normalized(named_block(governments, "economical_matters_republic"))
    require(failures, "assembly_houses_reform" in m6, "Assembly Houses is not registered at M6")
    for reform in (
        "sacred_regulation_reform",
        "patriarch_engagement_reform",
        "uzh_union_synod_reform",
    ):
        require(failures, reform in m4, f"religious reform is not registered at M4: {reform}")
    for reform in ("vln_magdeburg_rights", "chr_grain_directorate_reform"):
        require(failures, reform in m8, f"economic reform is not registered at M8: {reform}")
    for reform in ("chr_grain_directorate_reform", "zaz_chaiky_trade_reform"):
        require(failures, reform in r8, f"economic reform is not registered at R8: {reform}")
    republic_levels = normalized(
        named_block(named_block(governments, "republic"), "reform_levels")
    )
    for reform in (
        "pdl_enlightened_voivodeship_reform",
        "pdl_revolutionary_republic_reform",
    ):
        require(
            failures,
            reform in m11 and reform not in m7 and reform not in republic_levels,
            f"late Podillian monarchical settlement is not aligned with vanilla M11: {reform}",
        )

    m1 = normalized(named_block(governments, "feudalism_vs_autocracy"))
    m2 = normalized(named_block(governments, "hereditary_vs_nobility"))
    m10 = normalized(named_block(governments, "absolute_rule_vs_constitutional"))
    for pair, tier in (
        (("hlc_magnate_assembly_reform", "hlc_centralized_voivodeship_reform"), m2),
        (("hlc_galician_sejm_reform", "hlc_austrian_bureaucracy_reform"), m6),
        (("hlc_crown_authority_reform", "hlc_crown_and_sejm_reform"), m10),
    ):
        require(failures, all(item in tier for item in pair), f"HLC alternatives do not share a tier: {pair}")

    r1 = normalized(named_block(governments, "oligarchy_merchant_class_noble_elite"))
    r10 = normalized(named_block(governments, "guiding_principle_of_administration"))
    require(
        failures,
        "uzh_palanok_captaincy_reform" in m1
        and "uzh_palanok_captaincy_reform" in r1,
        "UZH Palanok Captaincy lacks its M1/R1 start tiers",
    )
    require(
        failures,
        "uzh_komitat_system_reform" in m1
        and "uzh_komitat_system_reform" not in r1
        and "uzh_republican_komitat_system_reform" in r1
        and "uzh_republican_komitat_system_reform" not in m1,
        "UZH Komitat variants are not separated into M1 and R1",
    )
    for reform in (
        "uzh_palatial_ruthenian_reform",
        "uzh_palatial_rusyn_reform",
    ):
        require(failures, reform in m10 and reform in r10, f"UZH Palatial reform lacks an M10/R10 tier: {reform}")
    require(
        failures,
        "uzh_palatial_uhro_reform" in m10
        and "uzh_palatial_uhro_reform" not in r10
        and "uzh_palatial_uhro_republic_reform" in r10
        and "uzh_palatial_uhro_republic_reform" not in m10,
        "UZH Ugro-Rusyn Palatial variants are not separated into M10 and R10",
    )


def check_localisation(failures: list[str], owners: dict[str, Path]) -> None:
    keys: Counter[str] = Counter()
    for path in (ROOT / "localisation").rglob("*_l_english.yml"):
        text = path.read_text(encoding="utf-8-sig")
        keys.update(re.findall(r'(?m)^\s*([A-Za-z0-9_.-]+):\d+\s+"', text))

    for reform in owners:
        for key in (reform, f"{reform}_desc"):
            if reform == "grand_duchy_reform":
                require(
                    failures,
                    keys[key] <= 1,
                    f"duplicate mod localisation for vanilla-resolved key: {key}",
                )
            else:
                require(
                    failures,
                    keys[key] == 1,
                    f"government reform localisation count is {keys[key]}, expected 1: {key}",
                )


def check_reachability_and_scope(failures: list[str], reforms: str) -> None:
    odesa = normalized(named_block(reforms, "odesa_trade_republic_reform"))
    require(
        failures,
        "trade_city_reform = trading_city" in odesa
        and "trading_city_legacy" not in odesa,
        "ODS modern reform still creates a legacy-system trading city",
    )

    principality = normalized(named_block(reforms, "ruthenian_principality_reform"))
    require(
        failures,
        re.search(r"\bmin_autonomy\s*=", principality) is None
        and "liberty_desire_from_subject_development = -0.15" in principality,
        "Ruthenian Principality remains an early autonomy trap instead of a subject polity",
    )
    assemblies = normalized(named_block(reforms, "elected_assemblies_reform"))
    for stale_bonus in (
        "diplomats",
        "diplomatic_reputation",
        "envoy_travel_time",
        "inflation_reduction",
    ):
        require(
            failures,
            re.search(rf"\b{stale_bonus}\s*=", assemblies) is None,
            f"Veche Assemblies still carries an unrelated stacked bonus: {stale_bonus}",
        )
    require(
        failures,
        "max_absolutism = -10" in assemblies,
        "Veche Assemblies lacks its decentralization trade-off",
    )

    patriarchal_faiths = ("orthodox", "russian_orthodox", "greek_catholic")
    for reform_id in ("patriarch_engagement_reform", "prl_episcopal_authority_reform"):
        reform = normalized(named_block(reforms, reform_id))
        require(
            failures,
            all(f"religion = {faith}" in reform for faith in patriarchal_faiths),
            f"patriarch-authority reform is selectable outside its three Eastern-rite faiths: {reform_id}",
        )

    volhynian_host = normalized(named_block(reforms, "vln_cossack_host_reform"))
    for foreign_mechanic in (
        "militarization_mechanic",
        "monthly_militarized_society",
        "mil_tech_cost_modifier",
    ):
        require(
            failures,
            foreign_mechanic not in volhynian_host,
            f"Volhynian Host still stacks a foreign/extra military mechanic: {foreign_mechanic}",
        )
    require(
        failures,
        "cossacks_mechanic" in volhynian_host and "max_absolutism = -10" in volhynian_host,
        "Volhynian Host lost its coherent Cossack mechanic or privilege trade-off",
    )

    last_sich = normalized(named_block(reforms, "zaz_last_sich_reform"))
    require(
        failures,
        "zaz_lineage_country = yes" in last_sich and "is_subject = yes" in last_sich,
        "Last Sich lacks the bounded ZAZ-lineage subject path",
    )
    for borrowed in ("jacobins_influence", "royalists_influence", "girondists_influence"):
        require(failures, borrowed not in last_sich, f"Last Sich still borrows French faction: {borrowed}")

    shared = read("common/government_reforms/RIP_shared_ruthenian_government_reforms.txt")
    volhynian = read("common/government_reforms/RIP_VLN_government_reforms.txt")
    for regional in ("vln_magdeburg_rights", "vln_ruthenian_renaissance_reform"):
        require(failures, regional in shared and regional not in volhynian, f"regional reform is still country-locked: {regional}")

    kie = read("common/government_reforms/RIP_KIE_KRU_government_reforms.txt")
    require(failures, "cossacks_mechanic" not in kie, "medieval KIE/KRU forms still expose Cossack UI")

    uzh = read("common/government_reforms/RIP_UZH_government_reforms.txt")
    for foreign_attribute in ("has_dutch_election", "english_parliament"):
        require(
            failures,
            foreign_attribute not in uzh,
            f"UZH still leaks a foreign country-specific mechanic: {foreign_attribute}",
        )
    komitat = normalized(named_block(uzh, "uzh_komitat_system_reform"))
    palanok = normalized(named_block(uzh, "uzh_palanok_captaincy_reform"))
    require(
        failures,
        "republican_tradition" not in palanok
        and "land_morale = -0.05" in palanok
        and "global_unrest = 1" in palanok,
        "UZH Palanok parties still contain authority modifiers that are no-ops in one government type",
    )
    republican_komitat = normalized(
        named_block(uzh, "uzh_republican_komitat_system_reform")
    )
    require(
        failures,
        all(token in komitat for token in ("queen = yes", "heir = yes", "royal_marriage = yes"))
        and all(
            token not in republican_komitat
            for token in ("queen = yes", "heir = yes", "royal_marriage = yes")
        ),
        "UZH republican Komitat still receives the monarchical dynastic layer",
    )
    uhro_palatial = normalized(named_block(uzh, "uzh_palatial_uhro_reform"))
    uhro_republic = normalized(
        named_block(uzh, "uzh_palatial_uhro_republic_reform")
    )
    require(
        failures,
        "legitimacy = 0.5" in uhro_palatial
        and "republican_tradition = 0.25" not in uhro_palatial
        and "republican_tradition = 0.25" in uhro_republic
        and "legitimacy = 0.5" not in uhro_republic
        and "allow = { government =" not in normalized(uzh),
        "UZH Ugro-Rusyn Palatial reform does not use government-appropriate authority",
    )
    synod = normalized(named_block(uzh, "uzh_union_synod_reform"))
    require(
        failures,
        "is_year = 1646 has_country_flag = uzh_union_synod_established" in synod
        and "potential = { OR = { has_reform = uzh_union_synod_reform tag = UZH has_country_flag = uzh_union_synod_established"
        in synod
        and "tag = UZH is_year = 1646" not in synod
        and "has_country_modifier = uz_greek_catholic_concord" not in synod,
        "UZH Union Synod is still gated by an expiring modifier instead of its permanent outcome",
    )
    republic_government = named_block(
        read("common/governments/00_governments.txt"), "republic"
    )
    republic_exclusions = normalized(
        "\n".join(
            block
            for _, block in keyed_blocks(republic_government, "exclusive_reforms")
        )
    )
    require(
        failures,
        "uzh_union_synod_reform" not in republic_exclusions,
        "UZH Union Synod is mutually exclusive with the parliament needed by its Palatial branch",
    )
    uzh_missions_raw = read("missions/Zakarpatta_Missions.txt")
    uzh_missions = normalized(uzh_missions_raw)
    require(
        failures,
        "has_government_attribute = has_dutch_election" not in uzh_missions,
        "UZH mission still tests the removed Dutch election attribute",
    )
    require(
        failures,
        'has_dlc = "Res Publica"'
        in named_block(uzh_missions_raw, "uzh_komitat_system")
        and "has_reform = uzh_palanok_captaincy_reform" in uzh_missions
        and "statists_vs_orangists = 0.7" in uzh_missions,
        "UZH Komitat mission does not enforce Captains' Party support for the Palanok mechanic",
    )
    komitat_mission = normalized(named_block(uzh_missions_raw, "uzh_komitat_system"))
    require(
        failures,
        "government = monarchy" in komitat_mission
        and "add_government_reform = uzh_komitat_system_reform" in komitat_mission
        and "government = republic" in komitat_mission
        and "add_government_reform = uzh_republican_komitat_system_reform"
        in komitat_mission,
        "UZH Komitat mission does not grant the government-specific M1/R1 reform",
    )
    uzh_slot = normalized(named_block(read("missions/Zakarpatta_Missions.txt"), "UZH_missions_4"))
    require(
        failures,
        "government = monarchy" in uzh_slot
        and "government = republic" in uzh_slot
        and "government = theocracy" not in uzh_slot,
        "UZH constitutional missions can force M/R-only reforms into an unsupported government type",
    )
    palatial_mission = named_block(read("missions/Zakarpatta_Missions.txt"), "uzh_palatial_reform")
    palatial_requirements = normalized(named_block(palatial_mission, "required_missions"))
    require(
        failures,
        "uzh_rusin_nobility" in palatial_requirements
        and "uz_identity_question" in palatial_requirements,
        "UZH Palatial mission can resolve before an identity path exists",
    )
    identity_question = normalized(
        named_block(uzh_missions_raw, "uz_identity_question")
    )
    pre_identity_culture = normalized(
        named_block(
            read("common/scripted_triggers/uzh_triggers.txt"),
            "uzh_pre_identity_candidate_culture",
        )
    )
    require(
        failures,
        "uzh_pre_identity_candidate_culture = yes" in identity_question
        and "uzh_identity_core_culture = yes" not in identity_question
        and all(
            f"culture = {culture}" in pre_identity_culture
            and f"primary_culture = {culture}" in identity_question
            for culture in (
                "rusyn",
                "rusyn_new",
                "ruthenian",
                "ruthenian_new",
                "rusyn_new_new",
            )
        ),
        "UZH identity selector still depends on its not-yet-selected identity",
    )
    backa_settlements = normalized(
        named_block(uzh_missions_raw, "uzh_backa_settlements")
    )
    banat_colonization = normalized(
        named_block(uzh_missions_raw, "uzh_banat_colonization")
    )
    require(
        failures,
        "uzh_set_identity_culture = yes" in backa_settlements
        and "uzh_set_identity_culture = yes" in banat_colonization
        and "change_culture = rusyn" not in backa_settlements
        and "change_culture = rusyn" not in banat_colonization,
        "UZH Alföld/Banat settlement still overwrites the selected identity culture",
    )
    palatial_effect = normalized(palatial_mission)
    require(
        failures,
        "government = monarchy } add_government_reform = uzh_palatial_uhro_reform"
        in palatial_effect
        and "government = republic } add_government_reform = uzh_palatial_uhro_republic_reform"
        in palatial_effect,
        "UZH Palatial mission does not grant the government-specific Ugro-Rusyn reform",
    )
    require(
        failures,
        "num_of_owned_provinces_with = { region = carpathia_region has_seat_in_parliament = yes value = 5"
        in palatial_effect
        and "calc_true_if" not in palatial_effect,
        "UZH Palatial mission uses calc_true_if as a province counter and is unreachable",
    )
    rusyn_autonomy = normalized(named_block(uzh_missions_raw, "uz_rusyn_autonomy"))
    carpathian_federation = normalized(
        named_block(uzh_missions_raw, "uz_carpathian_federation")
    )
    carpathian_commonwealth = normalized(
        named_block(uzh_missions_raw, "uz_carpathian_commonwealth")
    )
    require(
        failures,
        "government = republic" not in rusyn_autonomy
        and "government = republic" not in carpathian_federation
        and "add_legitimacy_equivalent = { amount = 20 republican_tradition = 10"
        in rusyn_autonomy
        and "add_legitimacy_equivalent = { amount = 30 republican_tradition = 15"
        in carpathian_federation
        and "add_legitimacy_equivalent = { amount = 15 republican_tradition = 8"
        in carpathian_commonwealth,
        "UZH Rusyn identity branch is still republic-locked or gives authority no-ops",
    )
    zakarpattia_realm = normalized(
        named_block(uzh_missions_raw, "uz_zakarpattia_realm")
    )
    require(
        failures,
        "add_legitimacy_equivalent = { amount = 15 republican_tradition = 8"
        in zakarpattia_realm
        and "add_legitimacy = 15" not in zakarpattia_realm
        and "add_republican_tradition = 8" not in zakarpattia_realm,
        "UZH early realm mission still gives government-specific authority no-ops",
    )
    pressburg = normalized(named_block(uzh_missions_raw, "uz_pressburg_compact"))
    saint_stephen = normalized(
        named_block(uzh_missions_raw, "uz_crown_of_saint_stephen")
    )
    require(
        failures,
        "legitimacy_equivalent = 70" in pressburg
        and "legitimacy = 70" not in pressburg
        and "add_legitimacy_equivalent = { amount = 10 republican_tradition = 5"
        in pressburg
        and "add_legitimacy_equivalent = { amount = 15 republican_tradition = 7"
        in saint_stephen,
        "UZH Ugro-Rusyn branch still blocks republics or gives authority no-ops",
    )
    require(
        failures,
        "owns_or_subject_of = 1772" in pressburg
        and "region = carpathia_region value = 8" in pressburg,
        "UZH Pressburg Compact has no regional-sovereignty route if Hungary disappears",
    )
    uhro_integration = normalized(
        named_block(uzh_missions_raw, "uz_uhro_rusyn_integration")
    )
    danubian_ascendancy = normalized(
        named_block(uzh_missions_raw, "uz_danubian_monarchy")
    )
    require(
        failures,
        "owns_or_subject_of = 1772" in uhro_integration
        and "region = carpathia_region value = 8" in uhro_integration
        and "owns_or_subject_of = 153" in danubian_ascendancy
        and "owns_or_subject_of = 1772" in danubian_ascendancy
        and "region = carpathia_region value = 15" in danubian_ascendancy,
        "UZH Ugro-Rusyn branch still becomes unreachable after Hungary is conquered or inherited",
    )
    revival = normalized(named_block(uzh_missions_raw, "uz_national_revival"))
    require(
        failures,
        "has_reform = uzh_komitat_system_reform" in revival
        and "has_reform = uzh_republican_komitat_system_reform" in revival,
        "UZH revival mission does not recognize both Komitat variants",
    )
    rusyn_state_mission = normalized(
        named_block(uzh_missions_raw, "uz_rusin_state")
    )
    require(
        failures,
        "is_subject = no" in rusyn_state_mission
        and "total_development = 200" in rusyn_state_mission
        and "has_country_flag = uzh_revival_complete" in rusyn_state_mission,
        "UZH can proclaim its sovereign Rusyn State capstone while still a subject",
    )
    srem = normalized(named_block(uzh_missions_raw, "uzh_srem_metropolis"))
    require(
        failures,
        "4173" in srem
        and "2960" not in srem
        and "religion = ROOT" in srem
        and "limit = { religion = catholic } add_papal_influence = 15" in srem
        and "else = { add_patriarch_authority = 0.15" in srem,
        "UZH Srem Metropolis has the wrong province or gives a faith-currency no-op",
    )
    security_congress = normalized(
        named_block(uzh_missions_raw, "uz_resist_habsburgs")
    )
    require(
        failures,
        "government = monarchy num_of_royal_marriages = 1" in security_congress
        and "government = republic OR = { diplomatic_reputation = 2 republican_tradition = 70"
        in security_congress
        and "add_legitimacy_equivalent = { amount = 10 republican_tradition = 5"
        in security_congress
        and "uzh_select_dynasty_patron_unlocked" not in security_congress,
        "UZH Palanok security mission remains monarchy-locked or advertises a missing decision",
    )
    union_mission = normalized(
        named_block(read("missions/Zakarpatta_Missions.txt"), "uz_union_dilemma")
    )
    preserve_faith = normalized(
        named_block(read("missions/Zakarpatta_Missions.txt"), "uz_preserve_orthodox_faith")
    )
    require(
        failures,
        "set_country_flag = uzh_union_synod_established" in union_mission
        and "is_year = 1646" in union_mission
        and "government = monarchy government = republic" in union_mission
        and "add_government_reform = uzh_union_synod_reform" in union_mission
        and "set_country_flag = uzh_union_old_rite_confirmed" in union_mission,
        "UZH religious mission outcomes do not persist or grant their supported Synod reform",
    )
    require(
        failures,
        "religion = greek_catholic" in preserve_faith
        and "religion = greek_catholic" in union_mission
        and "limit = { religion = catholic } add_papal_influence = 25" in union_mission
        and "limit = { religion = greek_catholic } add_patriarch_authority = 0.15"
        in union_mission,
        "UZH mission tree excludes its own Greek Catholic religious path",
    )
    rite_settlement = normalized(
        named_block(uzh_missions_raw, "uz_orthodox_unity")
    )
    require(
        failures,
        "religion = orthodox religion = greek_catholic" in rite_settlement
        and "religion = catholic papal_influence = 50" in rite_settlement
        and "religion = ROOT uzh_identity_core_culture = yes value = 8"
        in rite_settlement
        and "limit = { religion = catholic } add_papal_influence = 25"
        in rite_settlement
        and "else = { add_patriarch_authority = 0.25" in rite_settlement,
        "UZH Ruthenian identity branch still requires Orthodox-only currency or provinces",
    )
    uzh_modifiers_raw = read("common/event_modifiers/RIP_UZH_modifiers.txt")
    uzh_modifiers = normalized(named_block(uzh_modifiers_raw, "orthodox_zeal"))
    require(
        failures,
        "papal_influence" not in uzh_modifiers,
        "Ruthenian rite settlement still penalizes the Catholic path it now supports",
    )
    for modifier_id in (
        "uz_pannonian_autonomy",
        "uz_pannonian_league",
        "uz_slavo_rusyn_identity",
        "uz_carpathian_commonwealth",
        "uz_sovereign_rusin_state",
        "uz_pressburg_compact",
        "uz_crown_of_saint_stephen",
        "uz_rusyn_autonomy",
        "uz_kyivan_legacy",
        "uz_rusyn_self_governance",
    ):
        modifier = normalized(named_block(uzh_modifiers_raw, modifier_id))
        require(
            failures,
            "legitimacy =" not in modifier
            and "republican_tradition =" not in modifier,
            f"cross-government UZH modifier has an authority no-op: {modifier_id}",
        )
    constitutional_modifier = normalized(
        named_block(uzh_modifiers_raw, "uz_constitutional_system")
    )
    require(
        failures,
        "legitimacy = 0.5" in constitutional_modifier
        and "republican_tradition =" not in constitutional_modifier,
        "monarchy-only UZH constitutional modifier lost its coherent authority reward",
    )
    basilian_modifier = normalized(
        named_block(uzh_modifiers_raw, "uz_basilian_monasteries")
    )
    karloca_modifier = normalized(
        named_block(uzh_modifiers_raw, "uz_karloca_synod_blessing")
    )
    require(
        failures,
        "papal_influence" not in basilian_modifier
        and "tolerance_own = 1" in basilian_modifier
        and "yearly_patriarch_authority" not in karloca_modifier
        and "church_loyalty_modifier = 0.1" in karloca_modifier,
        "UZH permanent rite modifiers still give a supported faith a dead currency",
    )
    tisza_customs = normalized(
        named_block(read("missions/Zakarpatta_Missions.txt"), "uzh_tisza_customs_convention")
    )
    require(
        failures,
        "134 = { is_strongest_trade_power = ROOT" in tisza_customs
        and "137 = { is_strongest_trade_power = ROOT" in tisza_customs
        and not re.search(r"\b(?:118|120|121|122|123|124)\b", tisza_customs),
        "UZH Tisza Customs checks provinces outside the stated Wien/Ragusa trade nodes",
    )
    federative_statutes = normalized(
        named_block(read("missions/Zakarpatta_Missions.txt"), "uzh_federative_statutes")
    )
    require(
        failures,
        "num_of_subjects = 2" in federative_statutes
        and "NOT = { any_subject_country = { liberty_desire = 50" in federative_statutes
        and "calc_true_if" not in federative_statutes,
        "UZH Federative Statutes uses calc_true_if as a subject counter and is unreachable",
    )
    federalization = named_block(uzh_missions_raw, "uzh_federalization")
    federal_requirements = normalized(named_block(federalization, "required_missions"))
    federal_trigger = normalized(named_block(federalization, "trigger"))
    require(
        failures,
        "uzh_pannonian_republic" in federal_requirements
        and "uzh_constitutional_monarchy" not in federal_requirements
        and "has_country_flag = uzh_constitutional_framework" in federal_trigger
        and "has_country_flag = uzh_pannonian_compact_signed" in federal_trigger
        and "add_legitimacy_equivalent = { amount = 15 republican_tradition = 8"
        in normalized(federalization)
        and "add_legitimacy = 10" not in normalized(federalization)
        and "add_republican_tradition = 15" not in normalized(federalization),
        "UZH Federalization still requires mutually exclusive monarchy and republic missions",
    )
    uzh_events = read("events/Uzh.txt")
    rite_event = normalized(
        next(
            block
            for _, block in keyed_blocks(uzh_events, "country_event")
            if re.search(r"\bid = uzh\.1\b", normalized(block))
        )
    )
    karloca_event = normalized(
        next(
            block
            for _, block in keyed_blocks(uzh_events, "country_event")
            if "id = uzh.201" in normalized(block)
        )
    )
    security_event = normalized(
        next(
            block
            for _, block in keyed_blocks(uzh_events, "country_event")
            if re.search(r"\bid = uzh\.5\b", normalized(block))
        )
    )
    rusyn_state_event = normalized(
        next(
            block
            for _, block in keyed_blocks(uzh_events, "country_event")
            if re.search(r"\bid = uzh\.8\b", normalized(block))
        )
    )
    constitutional_event = normalized(
        next(
            block
            for _, block in keyed_blocks(uzh_events, "country_event")
            if re.search(r"\bid = uzh\.52\b", normalized(block))
        )
    )
    rusyn_identity_event = normalized(
        next(
            block
            for _, block in keyed_blocks(uzh_events, "country_event")
            if "id = uzh_identity.3" in normalized(block)
        )
    )
    require(
        failures,
        "limit = { religion = catholic } add_papal_influence = 10" in rite_event
        and "else = { add_patriarch_authority = 0.1" in rite_event
        and "limit = { religion = catholic } add_papal_influence = 10"
        in karloca_event
        and "else = { add_patriarch_authority = 0.05" in karloca_event,
        "UZH Carpathian rite events still give Catholics Patriarch Authority no-ops",
    )
    require(
        failures,
        "add_legitimacy_equivalent = { amount = 10 republican_tradition = 5"
        in security_event
        and "add_legitimacy = 10" not in security_event
        and "add_republican_tradition = 5" not in security_event,
        "UZH security congress follow-up still gives government-specific authority no-ops",
    )
    require(
        failures,
        all(f"add_{power}_power = 150" in rusyn_state_event for power in ("adm", "dip", "mil"))
        and "add_adm_power = 400" not in rusyn_state_event
        and "limit = { NOT = { government_rank = 2 } } set_government_rank = 2"
        in rusyn_state_event,
        "UZH Rusyn State capstone remains over-rewarded or can downgrade an empire",
    )
    require(
        failures,
        "add_legitimacy_equivalent = { amount = 10 republican_tradition = 5"
        in constitutional_event
        and "add_legitimacy = 10" not in constitutional_event
        and "add_republican_tradition = 5" not in constitutional_event
        and "add_legitimacy_equivalent = { amount = 30 republican_tradition = 15"
        in rusyn_identity_event
        and "add_republican_tradition = 15" not in rusyn_identity_event,
        "UZH constitutional/identity events still give government-specific authority no-ops",
    )
    identity_choice_event = normalized(
        next(
            block
            for _, block in keyed_blocks(uzh_events, "country_event")
            if "id = uzh_identity.1" in normalized(block)
        )
    )
    require(
        failures,
        "add_legitimacy_equivalent = { amount = 10 republican_tradition = 5"
        in identity_choice_event
        and "add_legitimacy_equivalent = { amount = 20 republican_tradition = 10"
        in identity_choice_event
        and "add_legitimacy = 10" not in identity_choice_event
        and "add_republican_tradition = 10" not in identity_choice_event,
        "UZH identity choices still give monarchy- or republic-only authority no-ops",
    )
    synod_event_raw = next(
        block
        for _, block in keyed_blocks(uzh_events, "country_event")
        if re.search(r"\bid = uzh\.51\b", normalized(block))
    )
    synod_event = normalized(synod_event_raw)
    require(
        failures,
        "set_country_flag = uzh_union_synod_established" in synod_event
        and "government = monarchy government = republic" in synod_event
        and "add_government_reform = uzh_union_synod_reform" in synod_event
        and "set_country_flag = uzh_union_old_rite_confirmed" in synod_event,
        "UZH 1646 union event outcomes do not persist or grant their supported Synod reform",
    )
    synod_event_trigger = normalized(named_block(synod_event_raw, "trigger"))
    require(
        failures,
        "religion = orthodox" in synod_event_trigger
        and "religion = catholic" in synod_event_trigger
        and "religion = greek_catholic" in synod_event_trigger
        and "religion_group = christian" not in synod_event_trigger,
        "UZH Union of Uzhhorod event is available to narratively incompatible Christian faiths",
    )
    ruthenian_identity_event = normalized(
        next(
            block
            for _, block in keyed_blocks(uzh_events, "country_event")
            if "id = uzh_identity.2" in normalized(block)
        )
    )
    require(
        failures,
        "limit = { religion = catholic } add_papal_influence = 15"
        in ruthenian_identity_event
        and "else = { add_patriarch_authority = 0.1" in ruthenian_identity_event
        and "religion = ROOT uzh_identity_core_culture = yes"
        in ruthenian_identity_event,
        "UZH Ruthenian identity consequence still gives Catholics a Patriarch Authority no-op",
    )
    synod_migration_raw = next(
        block
        for _, block in keyed_blocks(uzh_events, "country_event")
        if re.search(r"\bid = uzh\.204\b", normalized(block))
    )
    synod_migration = normalized(synod_migration_raw)
    require(
        failures,
        "hidden = yes" in synod_migration
        and "mean_time_to_happen = { days = 1 }" in synod_migration
        and "has_country_modifier = uz_greek_catholic_concord" in synod_migration
        and "set_country_flag = uzh_union_synod_established" in synod_migration
        and "has_country_modifier = uz_old_rite_resilience" in synod_migration
        and "set_country_flag = uzh_union_old_rite_confirmed" in synod_migration,
        "UZH old saves with active union outcomes are not migrated to permanent flags",
    )
    migration_trigger = normalized(named_block(synod_migration_raw, "trigger"))
    require(
        failures,
        migration_trigger.startswith("trigger = { OR = {")
        and "tag = UZH" not in synod_migration
        and "government = republic has_reform = uzh_komitat_system_reform"
        in migration_trigger
        and "government = republic has_reform = uzh_palatial_uhro_reform"
        in migration_trigger
        and "remove_government_reform = uzh_komitat_system_reform"
        in synod_migration
        and "add_government_reform = uzh_republican_komitat_system_reform"
        in synod_migration
        and "remove_government_reform = uzh_palatial_uhro_reform"
        in synod_migration
        and "add_government_reform = uzh_palatial_uhro_republic_reform"
        in synod_migration,
        "UZH descendant republic saves do not migrate the old shared reform IDs",
    )
    uzh_name = normalized(
        named_block(read("common/government_names/000_RIP_names.txt"), "uzh_komitat_system_reform")
    )
    require(
        failures,
        "has_reform = uzh_komitat_system_reform" in uzh_name
        and "has_reform = uzh_republican_komitat_system_reform" in uzh_name,
        "UZH Komitat government name does not recognize the republican reform ID",
    )
    for path in (
        "localisation/RIP_l_english.yml",
        "localisation/replace/zzz_RIP_untranslated_l_french.yml",
        "localisation/replace/zzz_RIP_untranslated_l_german.yml",
        "localisation/replace/zzz_RIP_untranslated_l_spanish.yml",
    ):
        locale = read(path)
        require(
            failures,
            re.search(
                r"(?m)^\s*(?:statists|orangists)(?:_influence|_FACTION_DESC)?:\d+\s+",
                locale,
            )
            is None,
            f"UZH still globally renames the vanilla Dutch factions in {path}",
        )
    english = read("localisation/RIP_l_english.yml")
    fallback_paths = (
        "localisation/replace/zzz_RIP_untranslated_l_french.yml",
        "localisation/replace/zzz_RIP_untranslated_l_german.yml",
        "localisation/replace/zzz_RIP_untranslated_l_spanish.yml",
    )
    for key in (
        "uzh_palanok_captaincy_reform_desc",
        "uzh_komitat_system_reform_desc",
        "uzh_republican_komitat_system_reform",
        "uzh_republican_komitat_system_reform_desc",
        "uzh_palatial_ruthenian_reform",
        "uzh_palatial_ruthenian_reform_desc",
        "uzh_palatial_uhro_reform_desc",
        "uzh_palatial_uhro_republic_reform",
        "uzh_palatial_uhro_republic_reform_desc",
        "boyar_elite_reform_desc",
        "uz_danubian_monarchy_title",
        "uz_danubian_monarchy_desc",
        "danubian_monarchy_influence",
        "desc_danubian_monarchy_influence",
        "UZH_orthodox_unity_culture_tt",
        "uz_orthodox_unity_title",
        "uz_orthodox_unity_desc",
        "orthodox_zeal",
        "desc_orthodox_zeal",
        "uz_orthodox_metropolis",
        "desc_uz_orthodox_metropolis",
        "uz_orthodox_revival",
        "desc_uz_orthodox_revival",
        "uzh_identity.2.a",
        "uzh_identity.2.d",
        "uz_pressburg_compact_desc",
        "desc_uz_pressburg_compact",
        "uz_preserve_orthodox_faith_title",
        "uz_preserve_orthodox_faith_desc",
        "uzh.1.t",
        "uzh.1.d",
        "uzh.1.a",
        "uzh_srem_metropolis_desc",
        "desc_uz_ruthenian_awakening",
        "UZH_resist_habsburgs_base_tt",
        "UZH_resist_habsburgs_habsburg_tt",
        "uz_resist_habsburgs_title",
        "uz_resist_habsburgs_desc",
        "uz_border_dynasty_network",
        "desc_uz_border_dynasty_network",
        "opinion_uz_border_dynasty",
        "uzh.5.t",
        "uzh.5.d",
        "uzh.5.a",
        "uzh.5.b",
        "partia_soymu_MECHANIC_TOOLTIP",
        "partia_kapitaniv_MECHANIC_TOOLTIP",
        "UZH_federalization_authority_tt",
        "uz_rusin_state_title",
        "uz_rusin_state_desc",
        "uz_crown_of_saint_stephen",
        "uz_crown_of_saint_stephen_title",
        "uz_crown_of_saint_stephen_desc",
        "uzh.8.d",
        "uzh_identity.3.d",
        "uzh_identity.3.a",
        "desc_uz_crown_of_saint_stephen",
        "desc_uz_slavo_rusyn_identity",
        "desc_uz_pannonian_autonomy",
        "desc_uz_pannonian_league",
        "desc_uz_kyivan_legacy",
        "desc_uz_carpathian_federation",
        "desc_uz_karloca_synod_blessing",
    ):
        match = re.search(rf'(?m)^\s*{key}:\d+\s+"([^"]*)"', english)
        require(failures, match is not None, f"missing English narrative key: {key}")
        if match is None:
            continue
        for path in fallback_paths:
            fallback = read(path)
            fallback_match = re.search(rf'(?m)^\s*{key}:\d+\s+"([^"]*)"', fallback)
            require(
                failures,
                fallback_match is not None and fallback_match.group(1) == match.group(1),
                f"fallback copy does not match English for {key}: {path}",
            )
    require(
        failures,
        "hereditary Palanok captaincy" not in english
        and "Palatinate of Three Nations" not in english
        and "kings cannot rule alone, and needs" not in english
        and "our chosen identity" not in english
        and 'uz_danubian_monarchy_title:0 "Danubian Monarchy"' not in english
        and 'uz_crown_of_saint_stephen_title:0 "Crown of Saint Stephen"' not in english
        and "As an independent nation" not in english
        and "multicultural republic" not in english
        and "republican institutions" not in english
        and "Patriarchal favor warms our altars" not in english,
        "UZH/Ruthenian reform localisation retains the audited narrative or grammar defect",
    )

    podillia = read("decisions/Podillia_Decisions.txt")
    require(failures, "change_tag = RUS" not in podillia, "unsafe duplicate PDL-to-Russia formable remains")
    galician_union = normalized(named_block(podillia, "pdl_unite_with_galicia_diplo"))
    require(
        failures,
        "inherit = HLC" in galician_union and "change_tag = HLC" not in galician_union,
        "Podillian diplomatic union still discards its reform path by changing into HLC",
    )

    ruthenia = normalized(read("decisions/RuthenianNation.txt"))
    ukr_change = ruthenia.find("change_tag = UKR")
    ukr_swap = ruthenia.find("swap_non_generic_missions = yes", ukr_change)
    ukr_change_effect = ruthenia.find("on_change_tag_effect = yes", ukr_change)
    require(
        failures,
        ukr_change < ukr_swap < ukr_change_effect,
        "UKR formation does not call the vanilla tag-change effect after swapping missions",
    )
    for source_tag, origin_flag in (
        ("HLC", "rip_vol_origin_hlc"),
        ("VLN", "rip_vol_origin_vln"),
        ("PDL", "rip_vol_origin_pdl"),
    ):
        origin = ruthenia.find(
            f"limit = {{ tag = {source_tag} }} set_country_flag = {origin_flag}"
        )
        require(
            failures,
            origin >= 0 and ukr_change >= 0 and origin < ukr_change,
            f"direct {source_tag}-to-UKR formation loses its reform lineage",
        )
    hlc_path_recovery = ruthenia.find(
        "has_country_flag = rip_vol_origin_hlc "
        "NOT = { hlc_has_any_path = yes } } "
        "country_event = { id = rip_galicia.1 days = 1 }"
    )
    require(
        failures,
        hlc_path_recovery > ukr_change,
        "HLC-origin UKR can lose the only event that selects its foundational reform path",
    )

    hetmanate_nation = named_block(read("decisions/HetmanateNation.txt"), "hetmanate_nation")
    hetmanate_potential = normalized(named_block(hetmanate_nation, "potential"))
    require(
        failures,
        "tag = PRL" in hetmanate_potential
        and "tag = ZAZ government = republic" in hetmanate_potential,
        "a sacred-order or sacred-horde ZAZ can still enter the republican HET tree",
    )
    hetmanate_decisions = read("decisions/HetmanateDecisions.txt")
    for decision_id in (
        "het_establish_regiments",
        "het_expand_academy",
        "het_reform_elections",
    ):
        decision = named_block(hetmanate_decisions, decision_id)
        potential = normalized(named_block(decision, "potential"))
        require(
            failures,
            "tag = HET" in potential and "government = republic" in potential,
            f"republic-only HET mechanics leak into another government: {decision_id}",
        )

    for path, target_tag in (
        ("decisions/KyivTriggers.txt", "KRU"),
        ("decisions/VHKNation.txt", "VOL"),
        ("decisions/HetmanateNation.txt", "HET"),
        ("decisions/KuyabaNation.txt", "KUY"),
        ("decisions/PolesianBelarusianNations.txt", "RPS"),
        ("decisions/PolesianBelarusianNations.txt", "PLT"),
        ("decisions/PolesianBelarusianNations.txt", "BLR"),
    ):
        transition = normalized(read(path))
        change = transition.find(f"change_tag = {target_tag}")
        swap = transition.find("swap_non_generic_missions = yes", change)
        on_change = transition.find("on_change_tag_effect = yes", swap)
        require(
            failures,
            change >= 0 and change < swap < on_change,
            f"{target_tag} formation does not finish the vanilla mission/tag-change lifecycle",
        )
    lineage_gates = read("common/scripted_triggers/rip_path_state_triggers.txt")
    for gate in (
        "west_ukraine_hlc_origin_country",
        "west_ukraine_vln_origin_country",
        "west_ukraine_pdl_origin_country",
    ):
        require(
            failures,
            "tag = UKR" in normalized(named_block(lineage_gates, gate)),
            f"UKR cannot continue its inherited western reform lineage: {gate}",
        )

    pdl_reforms = read("common/government_reforms/RIP_PDL_government_reforms.txt")
    pdl_absolute = normalized(named_block(pdl_reforms, "pdl_absolute_dominion_reform"))
    pdl_enlightened = normalized(
        named_block(pdl_reforms, "pdl_enlightened_voivodeship_reform")
    )
    pdl_popular = normalized(named_block(pdl_reforms, "pdl_revolutionary_republic_reform"))
    require(
        failures,
        "pdl_magnate_reforms_visible = yes" in pdl_absolute
        and "pdl_frontier_reform_visible = yes" not in pdl_absolute,
        "PDL Absolute Dominion is not confined to the magnate path",
    )
    require(
        failures,
        "pdl_frontier_reform_visible = yes" in pdl_popular
        and "current_age = age_of_revolutions" in pdl_popular,
        "PDL Popular Sovereignty lacks its frontier path or late-era gate",
    )
    require(
        failures,
        "pdl_carpathian_reform_visible = yes" in pdl_enlightened
        and "has_institution = enlightenment" in pdl_enlightened,
        "PDL Enlightened Voivodeship lacks its Dniester path or Enlightenment gate",
    )
    pdl_gates = read("common/scripted_triggers/pdl_reform_triggers.txt")
    pdl_magnate_gate = normalized(named_block(pdl_gates, "pdl_magnate_reforms_visible"))
    require(
        failures,
        "has_reform = pdl_absolute_dominion_reform" in pdl_magnate_gate
        and "has_reform = pdl_palatine_court_reform" not in pdl_magnate_gate,
        "PDL magnate self-gate leaks into the Dniester path",
    )

    pdl_history = normalized(read("history/countries/PDL - Podillia.txt"))
    vln_history = normalized(read("history/countries/VLN - Voln.txt"))
    require(
        failures,
        "add_government_reform = pdl_frontier_voivodeship_reform" in pdl_history
        and "add_government_reform = feudalism_reform" not in pdl_history,
        "PDL still starts without its unique fallback reform",
    )
    require(
        failures,
        "add_government_reform = vln_voivodeship_reform" in vln_history
        and "add_government_reform = feudalism_reform" not in vln_history,
        "VLN still starts without its unique voivodeship reform",
    )
    for base_reform in (
        "pdl_clan_assembly_reform",
        "pdl_steppe_principality_reform",
        "pdl_voivodeship_kingdom_reform",
        "pdl_frontier_voivodeship_reform",
    ):
        require(
            failures,
            "lock_level_when_selected = yes"
            in normalized(named_block(pdl_reforms, base_reform)),
            f"PDL path base does not lock its first tier: {base_reform}",
        )

    pdl_decisions = read("decisions/Podillia_Decisions.txt")
    for decision, flag, reform in (
        ("pdl_adopt_carpathian_doctrine", "pdl_carpathian_path", "pdl_steppe_principality_reform"),
        ("pdl_adopt_cossack_traditions", "pdl_frontier_path", "pdl_clan_assembly_reform"),
        ("pdl_adopt_magnate_governance", "pdl_magnate_path", "pdl_voivodeship_kingdom_reform"),
    ):
        block = named_block(pdl_decisions, decision)
        potential = normalized(named_block(block, "potential"))
        ai_will_do = normalized(named_block(block, "ai_will_do"))
        normalized_block = normalized(block)
        flag_pos = normalized_block.find(f"set_country_flag = {flag}")
        reform_pos = normalized_block.find(f"add_government_reform = {reform}")
        require(
            failures,
            flag_pos >= 0 and reform_pos >= 0 and flag_pos < reform_pos,
            f"PDL path does not set its gate before replacing the base reform: {decision}",
        )
        require(
            failures,
            "west_ukraine_pdl_origin_country = yes" in potential
            and "tag = PDL" not in potential
            and all(
                f"NOT = {{ has_country_flag = {path_flag} }}" in potential
                for path_flag in (
                    "pdl_carpathian_path",
                    "pdl_frontier_path",
                    "pdl_magnate_path",
                )
            ),
            f"PDL-origin VOL/UKR cannot make one exclusive path choice: {decision}",
        )
        require(
            failures,
            re.search(r"\bfactor\s*=\s*[1-9]", ai_will_do) is not None,
            f"PDL path selector has no positive AI weight: {decision}",
        )

    migration = read("common/scripted_effects/west_ukraine_government_effects.txt")
    normalized_migration = normalized(migration)
    startup = normalized(read("common/on_actions/west_ukraine_on_actions.txt"))
    for effect in ("pdl_reconcile_base_reform_effect", "vln_reconcile_base_reform_effect"):
        require(
            failures,
            effect in normalized_migration and f"{effect} = yes" in startup,
            f"old-save base-reform reconciliation is not wired: {effect}",
        )
    legacy_union = normalized(named_block(migration, "pdl_migrate_legacy_galician_union_effect"))
    require(
        failures,
        "tag = HLC" in legacy_union
        and "has_country_flag = pdl_united_with_galicia" in legacy_union
        and "NOT = { exists = PDL }" in legacy_union
        and "change_tag = PDL" in legacy_union
        and "add_government_reform = hlc_galician_voivodeship_reform" in legacy_union
        and "country_event = { id = rip_galicia.1 days = 1 }" in legacy_union
        and "tag = VOL tag = UKR" in legacy_union
        and "clr_country_flag = rip_vol_origin_hlc" in legacy_union
        and "clr_country_flag = rip_vol_origin_vln" in legacy_union
        and "set_country_flag = rip_vol_origin_pdl" in legacy_union
        and "pdl_migrate_legacy_galician_union_effect = yes" in startup,
        "old saves from the broken PDL-to-HLC union are not migrated safely",
    )
    galicia_event = normalized(named_block(read("events/RIP_Galicia_AltHistory.txt"), "country_event"))
    require(
        failures,
        "id = rip_galicia.1" in galicia_event
        and "NOT = { hlc_has_any_path = yes }" in galicia_event
        and "fire_only_once = yes" not in galicia_event,
        "HLC foundational path selector remains globally one-shot or can repeat after selection",
    )

    odesa = normalized(named_block(read("decisions/OdesaGovernmentDecisions.txt"), "establish_hajibey_free_port"))
    for token in (
        "has_institution = global_trade",
        "change_tag = ODS",
        "change_government = republic",
        "add_government_reform = odesa_trade_republic_reform",
    ):
        require(failures, token in odesa, f"Odesa alternative path lacks {token}")
    require(
        failures,
        odesa.find("swap_non_generic_missions = yes")
        < odesa.find("on_change_tag_effect = yes"),
        "Odesa formation calls the vanilla tag-change effect before swapping missions",
    )

    rank_two_gate = "limit = { NOT = { government_rank = 2 } } set_government_rank = 2"
    cossack_host = normalized(
        named_block(read("decisions/CossackHostDecisions.txt"), "form_cossack_host")
    )
    great_chernihiv = normalized(
        named_block(
            read("common/scripted_effects/chr_path_effects.txt"),
            "chr_proclaim_great_chernihiv_effect",
        )
    )
    prl_missions = read("missions/Pereiaslav_Missions.txt")
    prl_vassal_management = normalized(
        named_block(prl_missions, "prl_vassal_management")
    )
    prl_regional_hegemony = normalized(
        named_block(prl_missions, "prl_regional_hegemony")
    )
    require(
        failures,
        rank_two_gate in cossack_host
        and "government_rank = 1" not in cossack_host
        and rank_two_gate in great_chernihiv
        and "government_rank = 1" not in great_chernihiv
        and rank_two_gate in prl_regional_hegemony,
        "a Cossack/CHR/PRL rank-two reward can downgrade an empire",
    )
    chernihiv_events = normalized(read("events/Chernihiv.txt"))
    chernihiv_independence = normalized(
        named_block(read("missions/Chernihiv_Missions.txt"), "chr_independence")
    )
    require(
        failures,
        "add_legitimacy =" not in chernihiv_events
        and chernihiv_events.count("add_legitimacy_equivalent =") >= 4
        and "add_legitimacy_equivalent = { amount = 30 republican_tradition = 30"
        in chernihiv_independence
        and "add_legitimacy = 30" not in chernihiv_independence
        and "add_republican_tradition = 30" not in chernihiv_independence,
        "CHR missions/events give the reachable republic path legitimacy no-ops",
    )
    require(
        failures,
        "add_legitimacy_equivalent = { amount = 20 republican_tradition = 10"
        in prl_vassal_management
        and "add_legitimacy = 20" not in prl_vassal_management,
        "PRL vassal-management mission gives its republican path a legitimacy no-op",
    )
    prl_events = read("events/PereiaslavFlavor.txt")
    prl_council_event = normalized(
        named_block(prl_events, "country_event", occurrence=1)
    )
    prl_statute_event = normalized(
        named_block(prl_events, "country_event", occurrence=2)
    )
    require(
        failures,
        "add_legitimacy_equivalent = { amount = 10 republican_tradition = 5"
        in prl_council_event
        and "add_legitimacy = 10" not in prl_council_event
        and "add_legitimacy_equivalent = { amount = 10 republican_tradition = 5"
        in prl_statute_event
        and "add_legitimacy = 10" not in prl_statute_event,
        "PRL flavor events give the Regimental Republic a legitimacy no-op",
    )


def check_linked_lifecycle(failures: list[str]) -> None:
    het = normalized(read("decisions/HetmanateDecisions.txt"))
    regimental_flag = het.find("set_country_flag = regiments_established")
    regimental_reform = het.find("add_government_reform = het_regimental_system_reform")
    require(
        failures,
        regimental_flag >= 0
        and regimental_reform >= 0
        and regimental_flag < regimental_reform,
        "HET regimental unlock flag is set after the reform is granted",
    )
    academy_flag = het.find("set_country_flag = academy_expanded")
    academy_reform = het.find("add_government_reform = het_academy_enlightenment_reform")
    require(
        failures,
        academy_flag >= 0
        and academy_reform >= 0
        and academy_flag < academy_reform,
        "HET academy unlock flag is set after the reform is granted",
    )

    het_reforms = read("common/government_reforms/RIP_HET_government_reforms.txt")
    owner_change = read("common/scripted_effects/01_scripted_effects_for_on_actions.txt")
    het_migration = read("common/scripted_effects/het_government_effects.txt")
    het_startup = read("common/on_actions/het_on_actions.txt")
    require(
        failures,
        "het_regimental_province_administration" in het_reforms
        and "het_regimental_province_administration" in owner_change
        and "name = the_provincial_system" not in het_reforms,
        "HET regimental provinces still collide with the vanilla Ottoman pasha modifier",
    )
    require(
        failures,
        "has_reform = het_regimental_system_reform" in het_migration
        and "remove_province_modifier = the_provincial_system" in het_migration
        and "name = het_regimental_province_administration" in het_migration
        and "het_reconcile_regimental_province_modifiers_effect = yes" in het_startup,
        "old HET saves do not migrate the borrowed Ottoman province modifier",
    )
    sacred_migration = normalized(
        named_block(het_migration, "het_migrate_legacy_sacred_origin_effect")
    )
    sacred_change = sacred_migration.find("change_tag = ZAZ")
    sacred_swap = sacred_migration.find("swap_non_generic_missions = yes", sacred_change)
    sacred_on_change = sacred_migration.find("on_change_tag_effect = yes", sacred_swap)
    require(
        failures,
        "tag = HET" in sacred_migration
        and "has_country_flag = rip_hetmanate_origin_zaz" in sacred_migration
        and "has_reform = zaz_sacred_host_order_reform" in sacred_migration
        and "has_reform = zaz_sacred_horde_reform" in sacred_migration
        and "NOT = { exists = ZAZ }" in sacred_migration
        and sacred_change >= 0
        and sacred_change < sacred_swap < sacred_on_change
        and "remove_government_reform = zaz_sacred_host_order_reform" in sacred_migration
        and "remove_government_reform = zaz_sacred_horde_reform" in sacred_migration
        and "change_government = republic" in sacred_migration
        and "add_government_reform = rip_cossacks_reform" in sacred_migration
        and "het_migrate_legacy_sacred_origin_effect = yes" in het_startup,
        "old sacred-route HET saves are not migrated to a coherent government tree",
    )

    danube = normalized(
        named_block(read("missions/zzz_Hetmanate_Missions.txt"), "het_danube_frontier")
    )
    require(
        failures,
        "province_id = 159" in danube
        and "159 = { country_or_non_sovereign_subject_holds = ROOT" in danube
        and "province_id = 153" not in danube
        and "153 = {" not in danube,
        "HET Danube Frontier does not consistently target Silistria/Dobruja (159)",
    )
    ottoman_threat_raw = named_block(read("missions/Podillia_Missions.txt"), "PDL_withstand_ottoman_threat")
    ottoman_highlight = normalized(named_block(ottoman_threat_raw, "provinces_to_highlight"))
    require(
        failures,
        "area = podolia_volhynia_area" in ottoman_highlight
        and "NOT = { owned_by = ROOT" in ottoman_highlight
        and not re.search(r"\b47(?:4[9]|[5-9][0-9])\b", ottoman_highlight),
        "PDL Ottoman Threat highlights unrelated placeholder provinces",
    )
    zaz_het_triggers = read("common/scripted_triggers/zaz_het_triggers.txt")
    wild_fields = normalized(named_block(zaz_het_triggers, "is_wild_fields"))
    sloboda = normalized(named_block(zaz_het_triggers, "can_establish_sloboda"))
    require(
        failures,
        "province_id = 2410" not in wild_fields
        and "province_id = 2411" not in wild_fields
        and "area = sloboda_ukraine_area" in sloboda
        and "province_id = 2408" not in sloboda,
        "ZAZ/HET regional triggers still depend on mislabeled redundant province IDs",
    )

    union = normalized(named_block(read("events/UnionDispute.txt"), "country_event"))
    require(
        failures,
        "set_country_flag = lit_union_path_open" in union
        and "set_country_flag = lit_separate_path_open" in union,
        "LIT deferral option can still close both constitutional endpoints",
    )

    collegium_raw = named_block(read("events/HetmanateFlavor.txt"), "country_event", occurrence=12)
    collegium = normalized(collegium_raw)
    collegium_resistance = normalized(named_block(collegium_raw, "option", occurrence=2))
    require(
        failures,
        "id = het_flavor.12" in collegium
        and "government = republic" in collegium
        and "NOT = { is_year = 1728" in collegium
        and "mean_time_to_happen = { months = 24" in collegium
        and "add_republican_tradition = -10" in collegium
        and "name = het_autonomy_guaranteed" in collegium_resistance
        and "name = centralization_modifier" not in collegium_resistance,
        "Little Russian Collegium is not confined to the republican HET path or its choices contradict the narrative",
    )


def main() -> int:
    failures: list[str] = []
    try:
        reforms, owners = reform_sources()
    except ValueError as exc:
        print(f"GOVERNMENT REFORM CHECK: FAIL\n  - {exc}")
        return 1

    check_vfs_and_schema(failures, reforms, owners)
    check_registration(failures, owners)
    check_localisation(failures, owners)
    check_reachability_and_scope(failures, reforms)
    check_linked_lifecycle(failures)

    if failures:
        print("GOVERNMENT REFORM CHECK: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print(
        "GOVERNMENT REFORM CHECK: PASS "
        f"({EXPECTED_REFORM_COUNT} definitions; VFS, tiers, gates, and lifecycle hold)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
