"""Targeted regression checks for KIE/KRU, Russia, and distant claims."""

from __future__ import annotations

import sys
import re

from clausewitz_testlib import keyed_blocks, named_block, normalized, read


def require(failures: list[str], condition: bool, message: str) -> None:
    if not condition:
        failures.append(message)


def quoted_value(block: str, key: str) -> str:
    """Return a multiline scripted-effect argument stored as a quoted string."""
    match = re.search(rf'(?ms)^\s*{re.escape(key)}\s*=\s*"(.*?)"', block)
    return match.group(1) if match else ""


def has_control_gate(block: str, region: str, value: int) -> bool:
    """Require the region/value pair inside a control trigger in allow."""
    allow = named_block(block, "allow")
    gates = keyed_blocks(
        allow, "num_of_provinces_owned_or_owned_by_non_sovereign_subjects_with"
    )
    return any(
        f"region = {region}" in gate and f"value = {value}" in gate
        for _, gate in gates
    )


def has_normal_claim_scope(block: str, scope: str, recipient: str = "ROOT") -> bool:
    """Check that a named province/area/region scope grants only normal claims."""
    try:
        claim_scope = named_block(block, scope)
    except (KeyError, ValueError):
        return False
    return (
        f"add_claim = {recipient}" in claim_scope
        and "add_permanent_claim" not in claim_scope
        and "add_russian_claim" not in claim_scope
    )


def check_kyiv_formations(failures: list[str]) -> None:
    text = read("decisions/KyivTriggers.txt")
    for decision in ("rus_nation", "like_rus_nation", "kyiv_factional_ruthenia"):
        block = named_block(text, decision)
        require(
            failures,
            has_control_gate(block, "ruthenia_region", 20),
            f"{decision}: permanent Ruthenia reward needs the 20-province control gate",
        )

    rus_potential = named_block(named_block(text, "rus_nation"), "potential")
    require(failures, "NOT = { exists = RUS }" in rus_potential,
            "rus_nation: KRU formation must be exclusive with the RUS fallback")
    require(failures, "has_institution = renaissance" not in rus_potential,
            "rus_nation: ADM 10 path must not be made unreachable by a pre-Renaissance gate")
    like = named_block(text, "like_rus_nation")
    like_potential = named_block(like, "potential")
    like_normalized = normalized(like_potential)
    rival_tags = ("RUS", "UKR", "HET", "KUY", "KRU")
    rival_ors = [block for _, block in keyed_blocks(like_potential, "OR")]
    require(
        failures,
        any(all(f"exists = {tag}" in rival_or for tag in rival_tags)
            for rival_or in rival_ors),
        "like_rus_nation: fallback must require the RUS/UKR/HET/KUY/KRU rival-tag OR",
    )
    for tag in rival_tags:
        require(
            failures,
            f"NOT = {{ exists = {tag} }}" not in like_normalized,
            f"like_rus_nation: {tag} must be a positive existence trigger",
        )
    require(failures, "has_institution = renaissance" not in like_potential,
            "like_rus_nation: rival-tag fallback must not depend on Renaissance timing")

    ruthenia = named_block(read("decisions/RuthenianNation.txt"), "ruthenian_nation")
    require(
        failures,
        has_control_gate(ruthenia, "ruthenia_region", 20),
        "ruthenian_nation: permanent Ruthenia reward needs the 20-province control gate",
    )


def check_kyiv_missions(failures: list[str]) -> None:
    text = read("missions/Kyiv_Missions.txt")
    muscovy = named_block(text, "UKR_muscovy")
    muscovy_effect = named_block(muscovy, "effect")
    require(failures, "russia_region = {" not in muscovy_effect,
            "UKR_muscovy: early reward still grants the whole Russia region")
    for area in (
        "tver_area", "yaroslavl_area", "suzdal_area", "vladimir_area",
        "novgorod_area", "beloozero_area",
    ):
        require(failures, has_normal_claim_scope(muscovy_effect, area),
                f"UKR_muscovy: staged northern route is missing {area}")

    novgorod = named_block(text, "UKR_novgorod")
    novgorod_effect = named_block(novgorod, "effect")
    require(failures, has_normal_claim_scope(novgorod_effect, "baltic_region"),
            "UKR_novgorod: temporary Baltic route is missing")
    require(failures, "scandinavia_region = {" not in novgorod_effect,
            "UKR_novgorod: Baltic and Scandinavia must not burst from one reward")

    princes = named_block(text, "UKR_princes")
    princes_trigger = named_block(princes, "trigger")
    princes_effect = named_block(princes, "effect")
    require(failures, "region = russia_region" in princes_trigger
            and "value = 23" in princes_trigger,
            "UKR_princes: full Russia reward needs the 40% control gate")
    require(failures, has_normal_claim_scope(princes_effect, "russia_region"),
            "UKR_princes: post-gate remainder must use temporary claims")

    subjugate = named_block(text, "KIE_subjugate_moscow")
    subjugate_trigger = named_block(subjugate, "trigger")
    require(failures, "region = russia_region" in subjugate_trigger
            and "value = 23" in subjugate_trigger,
            "KIE_subjugate_moscow: full Russia reward needs the 40% control gate")

    baltic = named_block(text, "UKR_baltic")
    baltic_effect = named_block(baltic, "effect")
    require(failures, "add_permanent_claim = ROOT" not in baltic_effect,
            "UKR_baltic: distant Polish claims must remain temporary")
    for area in (
        "finland_area", "bothnia_area", "laponia_area", "norrland_area",
        "svealand_area", "ostra_svealand_area", "vastra_gotaland_area",
    ):
        require(failures, has_normal_claim_scope(baltic_effect, area),
                f"UKR_baltic: staged Scandinavian route is missing {area}")
    require(failures, has_normal_claim_scope(baltic_effect, "poland_region"),
            "UKR_baltic: distant Polish route must use temporary claims")


def check_russian_formation(failures: list[str]) -> None:
    block = named_block(read("decisions/RussianNation.txt"), "russian_nation")
    effect = named_block(block, "effect")
    require(failures, has_normal_claim_scope(effect, "russia_region", "RUS"),
            "russian_nation: home-region formation claims must be temporary")
    require(failures, "add_permanent_claim = RUS" not in effect,
            "russian_nation: formation still grants permanent regional claims")
    require(failures, "crimea_region = {" not in effect and "ural_region = {" not in effect,
            "russian_nation: Crimea/Ural claims must be earned through missions")


def check_domination_russia(failures: list[str]) -> None:
    text = read("missions/DOM_Russia_Missions.txt")
    distant_blocks = (
        "mos_rus_conquer_novgorod",
        "nov_rus_conquer_muscovy",
        "mos_rus_window_on_the_west",
        "nov_rus_window_on_the_west",
        "mos_rus_conquer_finland",
        "nov_rus_conquer_finland",
        "nov_rus_take_danzig",
        "nov_rus_involve_in_asian_trade",
        "mos_rus_conquer_kazan",
        "mos_rus_expand_eastwards",
        "mos_rus_colonize_west_siberia",
        "mos_rus_colonize_central_siberia",
        "mos_rus_colonize_eastern_siberia",
    )
    for mission in distant_blocks:
        block = named_block(text, mission)
        require(failures, "add_russian_claim = yes" not in block,
                f"{mission}: distant reward still resolves to permanent Russian claims")
        require(failures, "add_permanent_claim" not in block,
                f"{mission}: distant reward contains a direct permanent claim")
        has_temporary_claim = (
            "add_claim = ROOT" in block
            or "rip_add_temporary_claim_to_root = yes" in block
        )
        require(failures, has_temporary_claim,
                f"{mission}: temporary claim reward is missing")

    for mission in ("mos_rus_conquer_finland", "nov_rus_conquer_finland"):
        block = named_block(text, mission)
        require(failures, "scandinavia_region = {" not in block,
                f"{mission}: whole-Scandinavia claim burst remains")
        require(failures, "add_claim = ROOT" in block,
                f"{mission}: focused temporary Scandinavian route is missing")
        for area in (
            "norrland_area", "svealand_area", "ostra_svealand_area",
            "vastra_gotaland_area",
        ):
            require(failures, has_normal_claim_scope(block, area),
                    f"{mission}: staged route cannot reach the 25-province follow-up ({area})")

    asian = named_block(text, "nov_rus_involve_in_asian_trade")
    route_blocks = list(keyed_blocks(
        asian, "simple_dynamic_effect_without_alternative"
    ))
    require(failures, len(route_blocks) == 1,
            "nov_rus_involve_in_asian_trade: supported dynamic route helper is missing")
    if route_blocks:
        route = route_blocks[0][1]
        first_limit = quoted_value(route, "first_limit")
        first_effect = quoted_value(route, "first_effect")
        second_limit = quoted_value(route, "second_limit")
        second_effect = quoted_value(route, "second_effect")
        for argument, value in (
            ("first_limit", first_limit),
            ("first_effect", first_effect),
            ("second_limit", second_limit),
            ("second_effect", second_effect),
        ):
            require(
                failures,
                0 < len(value.encode("utf-8")) <= 512,
                "nov_rus_involve_in_asian_trade: "
                f"{argument} exceeds Clausewitz's 512-byte quoted-string limit",
            )
        require(
            failures,
            "707 = {" in first_limit
            and "shanshan_area = {" in first_effect
            and "tarim_basin_area = {" in first_effect
            and "lahore_area" not in first_effect
            and "mongolia_region" not in asian
            and first_effect.count("rip_add_temporary_claim_to_root = yes") == 2
            and "507 = {" in second_limit
            and re.search(r"NOT\s*=\s*\{\s*707\s*=\s*\{", second_limit) is not None
            and "lahore_area = {" in second_effect
            and "shanshan_area" not in second_effect
            and "tarim_basin_area" not in second_effect
            and "hindusthan_region" not in asian
            and second_effect.count("rip_add_temporary_claim_to_root = yes") == 1
            and "add_claim = ROOT" not in route
            and "add_russian_claim" not in route
            and "add_permanent_claim" not in route,
            "nov_rus_involve_in_asian_trade: Central Asian/Lahore routes are not exclusive focused temporary rewards",
        )

    temporary_claim_effect = named_block(
        read("common/scripted_effects/rip_claim_effects.txt"),
        "rip_add_temporary_claim_to_root",
    )
    require(
        failures,
        "add_claim = ROOT" in temporary_claim_effect
        and "add_permanent_claim" not in temporary_claim_effect
        and "add_russian_claim" not in temporary_claim_effect,
        "rip_add_temporary_claim_to_root must resolve to one normal claim",
    )

    gated_blocks = {
        "mos_rus_conquer_ruthenia": 20,
        "mos_rus_partition_poland": 15,
        "mos_rus_carpathian_conquest": 15,
        "mos_rus_protect_south_slavs": 25,
        "nov_rus_handle_ruthenia": 20,
        "mos_rus_conquer_crimea": 10,
        "mos_rus_conquer_the_caucasus": 15,
    }
    for mission, threshold in gated_blocks.items():
        block = named_block(text, mission)
        require(failures, "add_russian_claim = yes" in block,
                f"{mission}: completion-gated Russian claim policy was not preserved")
        trigger = named_block(block, "trigger")
        require(failures, f"value = {threshold}" in trigger,
                f"{mission}: control threshold for the regional reward changed")

    require(failures, "flavor_rus.100" not in text,
            "DOM Russia opener still invokes vanilla's oversized permanent-claim event")
    require(failures, "country_event = { id = rip_russia_balance.1 }" in text,
            "DOM Russia opener is not wired to a namespaced balanced replacement")


def check_russia_balance_event(failures: list[str]) -> None:
    text = read("events/RIP_RussiaBalance.txt")
    require(failures, "namespace = rip_russia_balance" in text,
            "RIP Russia balance event must use its own namespace")
    matching_events = [
        block for _, block in keyed_blocks(text, "country_event")
        if "id = rip_russia_balance.1" in block
    ]
    require(failures, len(matching_events) == 1,
            "RIP Russia balance event definition is missing or duplicated")
    event = matching_events[0] if matching_events else ""
    require(failures, "is_triggered_only = yes" in event,
            "RIP Russia balance event must only fire from the mission")

    options = [block for _, block in keyed_blocks(event, "option")]
    require(failures, len(options) == 2,
            "RIP Russia balance event must retain both administrative choices")
    claim_scopes = (
        "russia_region", "kama_area", "bashkiria_area", "volga_area",
        "kazan_area", "samara_area", "saratov_area", "lower_don_area",
        "astrakhan_area",
    )
    for index, option in enumerate(options, start=1):
        require(failures, "add_permanent_claim" not in option,
                f"RIP Russia balance option {index}: immediate claims must be temporary")
        require(failures, option.count("add_claim_province = {") == 3,
                f"RIP Russia balance option {index}: focused province claims changed")
        ai_chance = named_block(option, "ai_chance")
        require(failures, "factor = 1" in ai_chance,
                f"RIP Russia balance option {index}: AI choice is disabled")
        for scope in claim_scopes:
            require(failures, has_normal_claim_scope(option, scope),
                    f"RIP Russia balance option {index}: {scope} is not a normal-claim reward")

    if len(options) == 2:
        require(failures, "rus_expanded_administrative_offices" not in options[0],
                "RIP Russia balance option A must retain completion-gated permanent claims")
        require(failures, "rus_expanded_administrative_offices" in options[1],
                "RIP Russia balance option B must activate normal scripted claims")


def main() -> int:
    failures: list[str] = []
    check_kyiv_formations(failures)
    check_kyiv_missions(failures)
    check_russian_formation(failures)
    check_domination_russia(failures)
    check_russia_balance_event(failures)

    if failures:
        print("Claim-pacing contract failures:")
        for failure in failures:
            print(f"  {failure}")
        return 1

    print("KIE/KRU, Russia, and long-range claim pacing contracts hold")
    return 0


if __name__ == "__main__":
    sys.exit(main())
