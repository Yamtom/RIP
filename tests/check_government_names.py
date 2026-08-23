"""Static regression contract for RIP government-name priority and titles."""

from __future__ import annotations

import re
import sys

from clausewitz_testlib import named_block, normalized, read


NAMES_PATH = "common/government_names/000_RIP_names.txt"


def require(failures: list[str], condition: bool, message: str) -> None:
    if not condition:
        failures.append(message)


def positions(text: str) -> dict[str, int]:
    entries = re.findall(r"(?m)^([A-Za-z0-9_]+)\s*=\s*\{", text)
    return {name: index for index, name in enumerate(entries)}


def require_order(
    failures: list[str], order: dict[str, int], earlier: str, later: str
) -> None:
    require(failures, earlier in order, f"missing government-name block {earlier}")
    require(failures, later in order, f"missing government-name block {later}")
    if earlier in order and later in order:
        require(
            failures,
            order[earlier] < order[later],
            f"{earlier} must precede {later} under first-valid semantics",
        )


def check_priority(failures: list[str], text: str) -> None:
    entries = re.findall(r"(?m)^([A-Za-z0-9_]+)\s*=\s*\{", text)
    order = positions(text)
    require(failures, len(entries) == 60, f"expected 60 blocks, found {len(entries)}")
    require(
        failures,
        len(order) == len(entries),
        "government-name file contains a duplicate top-level block key",
    )

    require_order(
        failures, order, "chr_grain_directorate_reform", "siversk_veche_reform"
    )
    require_order(
        failures, order, "representation_monarchy_reform", "ruthenian_principality_reform"
    )
    require_order(
        failures, order, "representation_monarchy_reform", "kyivan_rus_reform"
    )

    roads = (
        "zaz_cossack_cantons_reform",
        "zaz_host_and_state_reform",
        "zaz_sacred_host_order_reform",
        "zaz_sacred_horde_reform",
    )
    zaz_legacy = (
        "zaz_last_sich_reform",
        "zaz_free_host_reform",
        "zaz_kosh_elections_reform",
        "zaz_sich_brotherhood_reform",
    )
    het_legacy = (
        "het_collegium_control_reform",
        "het_mazepist_autocracy_reform",
        "het_academy_enlightenment_reform",
        "het_hetman_for_life_reform",
        "het_starshyna_oligarchy_reform",
    )
    for earlier, later in zip(zaz_legacy, zaz_legacy[1:]):
        require_order(failures, order, earlier, later)
    for earlier, later in zip(het_legacy, het_legacy[1:]):
        require_order(failures, order, earlier, later)
    for road in roads:
        for legacy in (*zaz_legacy, *het_legacy):
            require_order(failures, order, road, legacy)
        require_order(failures, order, road, "rip_cossacks_reform")
    for legacy in (*zaz_legacy, *het_legacy):
        require_order(failures, order, legacy, "rip_cossacks_reform")

    vln = (
        "vln_grand_ruthenia_reform",
        "vln_ruthenia_reform",
        "vln_ruthenian_renaissance_reform",
        "vln_voivode_council",
        "vln_magdeburg_rights",
        "vln_black_voivode_legion",
        "vln_confessional_reform",
        "vln_confessional_academy",
        "vln_cossack_host_reform",
        "vln_voivodeship_reform",
    )
    for earlier, later in zip(vln, vln[1:]):
        require_order(failures, order, earlier, later)

    pdl = (
        "pdl_grand_podillia",
        "pdl_absolute_dominion",
        "pdl_magnate_republic",
        "pdl_magnate_dominion",
        "pdl_enlightened_voivodeship",
        "pdl_revolutionary_republic",
        "pdl_carpathian_bastion",
        "pdl_frontier_republic",
        "pdl_palatine_court",
        "pdl_aristocratic_assembly",
        "pdl_clan_assembly",
        "pdl_steppe_principality",
        "pdl_voivodeship_kingdom",
        "pdl_frontier_voivodeship",
    )
    for earlier, later in zip(pdl, pdl[1:]):
        require_order(failures, order, earlier, later)


def check_triggers_and_mappings(failures: list[str], text: str) -> None:
    for name in (
        "zaz_last_sich_reform",
        "zaz_free_host_reform",
        "zaz_kosh_elections_reform",
        "zaz_sich_brotherhood_reform",
    ):
        require(
            failures,
            "tag = ZAZ" in normalized(named_block(text, name)),
            f"{name} lacks a ZAZ tag gate",
        )
    for name in (
        "het_collegium_control_reform",
        "het_mazepist_autocracy_reform",
        "het_academy_enlightenment_reform",
        "het_hetman_for_life_reform",
        "het_starshyna_oligarchy_reform",
    ):
        require(
            failures,
            "tag = HET" in normalized(named_block(text, name)),
            f"{name} lacks an HET tag gate",
        )

    frontier = normalized(named_block(text, "pdl_frontier_republic"))
    require(
        failures,
        "has_country_flag = pdl_frontier_path" in frontier,
        "PDL frontier title does not use the exclusive path flag",
    )
    require(
        failures,
        "pdl_cossack_recruited" not in frontier,
        "PDL frontier title still uses the general Cossack mission flag",
    )
    grand = normalized(named_block(text, "pdl_grand_podillia"))
    require(
        failures,
        "has_country_flag = pdl_grand_podillia" in grand
        and "has_reform = pdl_grand_podillia_reform" in grand,
        "Grand Podillia title must accept the terminal mission or reform",
    )

    grain = normalized(named_block(text, "chr_grain_directorate_reform"))
    require(
        failures,
        "ruler_female = { 1 = GRANARY_ATAMANKA" in grain,
        "Grain Directorate rank-1 female ruler does not use GRANARY_ATAMANKA",
    )
    factional = normalized(named_block(text, "ruthenian_factional_empire_reform"))
    require(
        failures,
        "ruler_male = { 1 = RUTHENIAN_PRINCE 2 = RUTHENIAN_KING" in factional
        and "ruler_female = { 1 = RUTHENIAN_PRINCESS 2 = RUTHENIAN_QUEEN"
        in factional,
        "Factional Kingdom still uses prince/princess titles at rank 2",
    )

    ruthenian = normalized(named_block(text, "ruthenian_principality_reform"))
    require(
        failures,
        "NOT = { tag = VLN }" in ruthenian and "NOT = { tag = PDL }" in ruthenian,
        "generic Ruthenian Principality still shadows VLN or PDL country names",
    )
    pdl_monarchic_names = " ".join(
        normalized(named_block(text, name))
        for name in (
            "pdl_magnate_republic",
            "pdl_aristocratic_assembly",
            "pdl_revolutionary_republic",
        )
    )
    magnate_compact = normalized(named_block(text, "pdl_magnate_republic"))
    require(
        failures,
        "ruler_male = { 1 = MAGNATE_DUKE" in magnate_compact
        and "ruler_female = { 1 = MAGNATE_DUCHESS" in magnate_compact,
        "Magnate Compact rank-1 state and ruler titles do not agree",
    )
    for stale_key in (
        "OLIGARCHY",
        "MERCHANT_REPUBLIC",
        "ARISTOCRATIC_REPUBLIC",
        "DEMOCRATIC_REPUBLIC",
        "PREMIER",
    ):
        require(
            failures,
            stale_key not in pdl_monarchic_names,
            f"monarchic PDL name still selects republican key {stale_key}",
        )


def check_rank_reachability(failures: list[str]) -> None:
    reforms = read("common/government_reforms/RIP_government_reforms.txt")
    for name in ("rip_cossacks_reform", "vln_voivodeship_reform"):
        block = normalized(named_block(reforms, name))
        require(
            failures,
            "fixed_rank = 1" not in block,
            f"{name} still makes its rank-2/3 titles and rank rewards unreachable",
        )

    legion_raw = named_block(reforms, "vln_black_voivode_legion")
    legion = normalized(legion_raw)
    require(
        failures,
        'has_dlc = "Cradle of Civilization"' in legion_raw
        and "army_professionalism = 0.4" in legion
        and "else = { army_tradition = 60" in legion,
        "Black Voivode Legion lacks the vanilla-style no-DLC army-tradition fallback",
    )
    require(
        failures,
        'has_dlc = "Rights of Man"' in legion_raw
        and "discipline = 0.025" in legion
        and "land_morale = 0.10" in legion
        and "infantry_cost" not in legion
        and "infantry_fire" not in legion,
        "Black Voivode Legion no longer matches its DLC and vanilla-tier balance contract",
    )

    require(
        failures,
        "land_forcelimit = 0.10" not in reforms
        and "land_forcelimit = 0.15" not in reforms,
        "a percentage force-limit bonus still uses the near-zero flat modifier",
    )


def check_reform_balance_and_lifecycle(failures: list[str]) -> None:
    reforms = read("common/government_reforms/RIP_government_reforms.txt")
    grain = normalized(named_block(reforms, "chr_grain_directorate_reform"))
    require(
        failures,
        "global_trade_goods_size_modifier = 0.05" in grain
        and "production_efficiency = 0.05" in grain
        and "burghers_loyalty_modifier = 0.05" in grain
        and "extra_trade_goods_from_grain" not in grain
        and "chinampa_farms_mechanic" not in grain,
        "Grain Directorate still stacks borrowed mechanics or exceeds its balance contract",
    )

    confessional = normalized(named_block(reforms, "vln_confessional_reform"))
    require(
        failures,
        "tolerance_heretic = 3" in confessional
        and "religious_unity = 0.10" in confessional
        and "tolerance_heathen" not in confessional
        and "stability_cost_modifier" not in confessional,
        "Volhynian Confessional State exceeds its focused tolerance contract",
    )
    ruthenia = normalized(named_block(reforms, "vln_ruthenia_reform"))
    require(
        failures,
        "max_absolutism = 10" in ruthenia
        and "legitimacy = 0.5" in ruthenia
        and "administrative_efficiency" not in ruthenia
        and "reform_progress_growth" not in ruthenia,
        "Crown of Ruthenia exceeds its base reform contract",
    )
    academy = normalized(named_block(reforms, "vln_confessional_academy"))
    require(
        failures,
        "technology_cost = -0.05" in academy
        and "religious_unity = 0.10" in academy
        and "advisor_pool = 1" in academy
        and "idea_cost" not in academy,
        "Confessional Academy exceeds its vanilla-tier balance contract",
    )

    chr_modifiers = read("common/event_modifiers/RIP_CHR_modifiers.txt")
    grain_province = normalized(
        named_block(chr_modifiers, "chr_grain_directorate_province")
    )
    require(
        failures,
        "trade_goods_size_modifier = 0.1" in grain_province
        and "local_production_efficiency = 0.1" in grain_province,
        "Left-Bank Grain Combine does not match its displayed +10%/+10% effects",
    )

    vln_modifiers = read("common/event_modifiers/VLN_government_modifiers.txt")
    diet = normalized(named_block(vln_modifiers, "vln_confessional_diet"))
    statutes = normalized(named_block(vln_modifiers, "vln_crown_statutes"))
    require(
        failures,
        "tolerance_own = 1" in diet
        and "global_unrest = -1" in diet
        and "tolerance_heretic" not in diet
        and "stability_cost_modifier" not in diet,
        "Confessional Diet hidden modifier duplicates the base reform",
    )
    require(
        failures,
        "administrative_efficiency = 0.025" in statutes
        and "nobles_loyalty_modifier = 0.05" in statutes
        and "global_autonomy" not in statutes
        and "legitimacy" not in statutes,
        "Crown Statutes hidden modifier exceeds its balance contract",
    )

    on_actions = read("common/scripted_effects/01_scripted_effects_for_on_actions.txt")
    owner_change = normalized(
        named_block(on_actions, "on_province_owner_change_government_effect")
    )
    trade_good_change = normalized(
        named_block(on_actions, "on_trade_good_changed_government_effect")
    )
    require(
        failures,
        owner_change.count("chr_grain_directorate_province") >= 4
        and owner_change.count("chr_grain_directorate_reform") >= 2,
        "Grain Combine is not added and removed when province ownership changes",
    )
    require(
        failures,
        trade_good_change.count("chr_grain_directorate_province") >= 3
        and "chr_grain_directorate_reform" in trade_good_change,
        "Grain Combine is not maintained when a province trade good changes",
    )

    chr_effects = normalized(
        named_block(
            read("common/scripted_effects/chr_effects.txt"),
            "chr_refresh_grain_directorate_effect",
        )
    )
    chr_on_actions = read("common/on_actions/chr_pantheon_on_actions.txt")
    startup = normalized(named_block(chr_on_actions, "on_startup"))
    yearly = normalized(named_block(chr_on_actions, "on_yearly_pulse"))
    require(
        failures,
        chr_effects.count("chr_grain_directorate_province") >= 5
        and "has_reform = chr_grain_directorate_reform" in chr_effects
        and "NOT = { trade_goods = grain }" in chr_effects
        and "chr_refresh_grain_directorate_effect = yes" in startup
        and "chr_refresh_grain_directorate_effect = yes" in yearly,
        "Grain Directorate lacks its old-save reconciliation path",
    )


def check_visible_language(failures: list[str]) -> None:
    english = "\n".join(
        read(path)
        for path in (
            "localisation/RIP_l_english.yml",
            "localisation/volhynia_government_l_english.yml",
            "localisation/zaz_paths_l_english.yml",
            "localisation/podillia_events_l_english.yml",
            "localisation/replace/zzz_RIP_l_english.yml",
            "localisation/replace/zzz_RIP_untranslated_l_french.yml",
            "localisation/replace/zzz_RIP_untranslated_l_german.yml",
            "localisation/replace/zzz_RIP_untranslated_l_spanish.yml",
            "localisation/replace/zzz_zaz_paths_l_french.yml",
            "localisation/replace/zzz_zaz_paths_l_german.yml",
            "localisation/replace/zzz_zaz_paths_l_spanish.yml",
        )
    )
    for stale in (
        "Agro Hypercorporation",
        "Agro Hypercorp",
        'REFORMED_KINGDOM:0 "Reformed Kingdom"',
        'VOIVODE_PALATINATE:0 "Voivode Palatinate"',
        'PALATINE_VOIVODE:0 "Palatine Voivode"',
        'FORT_CAPTAINESS:0 "Fort Captainess"',
        'LIBERTY_GUARDIANESS:0 "Guardianess of Liberty"',
        'pdl_revolutionary_republic_reform:0 "Revolutionary Republic"',
        'PEOPLES_REPUBLIC:0 "Citizens\' Republic"',
        'SUPREME_COMMISSAR:0 "Consul of the Republic"',
        "+15% local production efficiency",
        "Magnate Republic",
        "Frontier Republic",
        "Podillian Consulate",
        "First Consul",
        "Mazovian",
        "Grand Podillia Kingdom",
        "Grand Podillia Voivodeship",
        "Voivodeship Kingdom",
        "Left-Bank Grain Combine",
        "Harbor Consuless",
        "Directoress-General",
        "before Russian pressure forces submission",
        "The Hetmanate is abolished",
        "Under Hetman Ivan Mazepa's patronage",
        "Volyn's Orthodox",
        "across Volyn.",
        "Noble autonomy and trade power define this path",
    ):
        require(failures, stale not in english, f"anachronistic or synthetic title remains: {stale}")


def main() -> int:
    failures: list[str] = []
    text = read(NAMES_PATH)
    check_priority(failures, text)
    check_triggers_and_mappings(failures, text)
    check_rank_reachability(failures)
    check_reform_balance_and_lifecycle(failures)
    check_visible_language(failures)

    if failures:
        print("GOVERNMENT NAME CHECK: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print(
        "GOVERNMENT NAME CHECK: PASS "
        "(60 blocks; priority, reachability, lifecycle, and title contracts hold)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
