"""Static regression contract for the Steppe raiding expansion package.

The checks are intentionally narrow: they validate reachability, target scope,
bounded cooldown/CB behavior, Kaffa policy wiring, and the documented province
IDs without trying to emulate the EU4 engine.
"""

from __future__ import annotations

import re
import sys

from clausewitz_testlib import keyed_blocks, named_block, normalized, read


def require(failures: list[str], condition: bool, message: str) -> None:
    if not condition:
        failures.append(message)


def scalar(block: str, key: str) -> str | None:
    match = re.search(rf"\b{re.escape(key)}\s*=\s*([A-Za-z0-9_.-]+)", block)
    return match.group(1) if match else None


def event_block(text: str, event_id: str, kind: str = "country_event") -> str:
    candidates = [
        block for _, block in keyed_blocks(text, kind)
        if scalar(block, "id") == event_id and re.search(r"(?m)^\s*title\s*=", block)
    ]
    if candidates:
        return max(candidates, key=len)
    raise KeyError(f"{kind} id {event_id!r} not found")


def check_core_cycle(failures: list[str]) -> None:
    text = read("events/SteppeRaiding.txt")
    organize = event_block(text, "steppe_raid.1")
    for eligibility in (
        "tag = CRI", "tag = NOG", "tag = KAZ", "tag = AST", "tag = GOL",
        "has_reform = steppe_horde", "has_reform = great_mongol_state_reform",
    ):
        require(failures, eligibility in organize,
                f"steppe_raid.1: missing explicit raider eligibility {eligibility}")
    require(failures, "government_rank" not in organize,
            "steppe_raid.1: government rank must not make every OPM a horde raider")

    target = event_block(text, "steppe_raid.2")
    for protection in (
        "glinski_tatar_settlement", "jagoldai_horde_settlement",
        "lipka_tatar_settlement", "zasechnaya_cherta_province",
    ):
        require(failures, protection in target,
                f"steppe_raid.2: {protection} is not integrated into raid protection")

    success = event_block(text, "steppe_raid.4")
    require(failures, "rip_feed_kaffa_market_effect = yes" in success,
            "steppe_raid.4: successful yasyr sale does not feed the Kaffa market")

    revenge = event_block(text, "steppe_raid.6")
    require(failures, "reverse_has_opinion_modifier" in revenge,
            "steppe_raid.6: retaliation checks the yasyr opinion in the wrong direction")
    require(failures, revenge.count("reverse_has_opinion_modifier") >= 2,
            "steppe_raid.6: trigger and target filter must use the same opinion direction")

    nogai = event_block(text, "steppe_raid.8")
    for province in ("owns = 282", "owns = 1756", "owns = 287"):
        require(failures, province in nogai,
                f"steppe_raid.8: correct migration target {province} is missing")
    for wrong in ("2410", "2447", "2416"):
        require(failures, wrong not in nogai,
                f"steppe_raid.8: stale wrong province id {wrong} remains")

    kalmyk = event_block(text, "steppe_raid.9")
    require(failures, "owns = 464" in kalmyk and "owns = 474" in kalmyk,
            "steppe_raid.9: Astrakhan/Yaik ownership contract is incomplete")
    require(failures, "1082" not in kalmyk,
            "steppe_raid.9: Kazan is still misidentified as Lower Yayik")


def check_new_chains(failures: list[str]) -> None:
    text = read("events/SteppeRaiding.txt")

    don = event_block(text, "steppe_raid.11")
    for marker in (
        "lower_don_area", "azov_area", "cossacks_reform",
        "cossack_raid_cooldown", "id = steppe_raid.12",
        "rip_request_ottoman_crimean_reaction_effect = yes",
    ):
        require(failures, marker in don, f"steppe_raid.11: missing {marker}")
    require(failures, "is_at_war = no" in don and "truce_with = ROOT" in don,
            "steppe_raid.11: Don raid peace/truce guards are incomplete")

    don_target = event_block(text, "steppe_raid.12")
    require(failures, "is_triggered_only = yes" in don_target,
            "steppe_raid.12: target response must not fire autonomously")
    require(failures, "rip_disrupt_kaffa_market_effect = yes" in don_target,
            "steppe_raid.12: a successful Don raid cannot disrupt Kaffa")
    for protection in (
        "glinski_tatar_settlement", "jagoldai_horde_settlement",
        "lipka_tatar_settlement", "zasechnaya_cherta_province",
    ):
        require(failures, don_target.count(protection) >= 2,
                f"steppe_raid.12: {protection} is not used in selection and damage")

    ottoman = event_block(text, "steppe_raid.13")
    require(failures, "tag = TUR" in ottoman and "is_subject_of = ROOT" in ottoman,
            "steppe_raid.13: Ottoman/Crimean subject scope is not enforced")
    require(failures, "FROM = {" in ottoman and "alliance_with = ROOT" in ottoman,
            "steppe_raid.13: raider validity/alliance guard is missing")
    require(failures, "ottoman_crimean_reaction_cooldown" in ottoman,
            "steppe_raid.13: reaction cooldown is missing")
    require(failures, "type = cb_insult" in ottoman and "months = 60" in ottoman,
            "steppe_raid.13: retaliation CB must be bounded to 60 months")
    require(failures, "has_casus_belli" in ottoman and "truce_with = FROM" in ottoman,
            "steppe_raid.13: duplicate-CB/truce guards are missing")
    require(failures, "declare_war_with_cb" not in ottoman,
            "steppe_raid.13: Ottoman reaction must not force an immediate war")
    require(failures, "ottoman_vassal_support" in ottoman,
            "steppe_raid.13: support-the-vassal alternative is missing")

    circassian = event_block(text, "steppe_raid.14")
    require(failures, "tag = CRI" in circassian and "circassia_area" in circassian,
            "steppe_raid.14: Crimean/Circassian geography is not enforced")
    require(failures, "steppe_raid_cooldown" in circassian
            and "id = steppe_raid.15" in circassian,
            "steppe_raid.14: cooldown or target response is missing")

    circassian_target = event_block(text, "steppe_raid.15")
    require(failures, "is_triggered_only = yes" in circassian_target
            and "FROM = { tag = CRI }" in circassian_target,
            "steppe_raid.15: only a Crimean raid may invoke the target response")
    require(failures, "circassia_area" in circassian_target
            and "rip_feed_kaffa_market_effect = yes" in circassian_target,
            "steppe_raid.15: Circassian damage/yasyr-to-Kaffa route is incomplete")

    kaffa = event_block(text, "steppe_raid.16", "province_event")
    require(failures, "province_id = 285" in kaffa,
            "steppe_raid.16: Kaffa must be province 285")
    for modifier in ("crimean_yasyr_market", "trade_route_disrupted", "kaffa_ransom_exchange"):
        require(failures, modifier in kaffa,
                f"steppe_raid.16: Kaffa policy is missing {modifier}")
    market = next((block for _, block in keyed_blocks(kaffa, "option")
                   if "crimean_yasyr_market" in block), "")
    require(failures, bool(market) and "trigger = {" in market,
            "steppe_raid.16: slave-market option is available to every owner")
    require(failures, any(tag in market for tag in ("tag = GEN", "tag = CRI", "tag = TUR"))
            and "religion_group = muslim" in market,
            "steppe_raid.16: market-compatible owners are not explicitly bounded")


def check_helpers_and_callers(failures: list[str]) -> None:
    effects = read("common/scripted_effects/steppe_raid_effects.txt")
    feed = named_block(effects, "rip_feed_kaffa_market_effect")
    disrupt = named_block(effects, "rip_disrupt_kaffa_market_effect")
    reaction = named_block(effects, "rip_request_ottoman_crimean_reaction_effect")
    require(failures, "285 = {" in feed and "slave_trade_income" in feed,
            "Kaffa feed helper does not resolve province 285 and its owner")
    require(failures, "285 = {" in disrupt and "province_id = 285" not in disrupt,
            "Kaffa disruption helper is not callable from country scope")
    require(failures, "remove_province_modifier = crimean_yasyr_market" in disrupt
            and "name = trade_route_disrupted" in disrupt,
            "Kaffa disruption helper does not replace the market with disruption")
    require(failures, "is_subject_of = TUR" in reaction
            and "id = steppe_raid.13" in reaction,
            "Ottoman reaction helper is not gated by a Crimean subject")

    raid_mechanics = read("events/RaidMechanics.txt")
    seasonal = event_block(raid_mechanics, "raid_mechanics.1")
    seasonal_norm = normalized(seasonal)
    require(failures, re.search(r"OR = \{ is_month = 3 is_month = 5 \}", seasonal_norm) is not None,
            "raid_mechanics.1: March/May are still an impossible AND")
    require(failures, "id = raid_mechanics.2" in seasonal,
            "raid_mechanics.2: no caller remains in the seasonal chain")
    chaiky = event_block(raid_mechanics, "raid_mechanics.42")
    require(failures, "any_known_country" in chaiky and "random_known_country" in chaiky,
            "raid_mechanics.42: maritime raids are incorrectly limited to land neighbors")
    require(failures, "is_chaiky_raid_target = yes" in chaiky
            and "rip_request_ottoman_crimean_reaction_effect = yes" in chaiky,
            "raid_mechanics.42: valid target/reaction wiring is incomplete")

    zaz_effects = read("common/scripted_effects/zaz_het_effects.txt")
    chaiky_effect = named_block(zaz_effects, "zaz_chaiky_raid_effect")
    require(failures, "rip_request_ottoman_crimean_reaction_effect = yes" in chaiky_effect,
            "Zaporozhian chaiky success does not request an Ottoman reaction")
    require(failures, "rip_disrupt_kaffa_market_effect" not in chaiky_effect,
            "A raid on Constantinople incorrectly disrupts Kaffa unconditionally")

    het = read("events/HetmanateCossackRaids.txt")
    require(failures, het.count("rip_request_ottoman_crimean_reaction_effect = yes") >= 2,
            "Hetmanate Ottoman/Crimean raid paths are not wired to the reaction")
    require(failures, het.count("limit = { owns = 285 }") >= 2,
            "Hetmanate Kaffa disruption is not guarded by actual target ownership")


def check_policy_and_cooldowns(failures: list[str]) -> None:
    missions = read("missions/Zaporozhie_Missions.txt")
    slave_trade = named_block(missions, "ZAZ_TUR_slave_trade")
    require(failures, "province_id = 285" in slave_trade and "286 = {" not in slave_trade,
            "ZAZ_TUR_slave_trade: mission still targets Azov instead of Kaffa")
    effect = named_block(slave_trade, "effect")
    require(failures, "remove_province_modifier = crimean_yasyr_market" in effect
            and "name = kaffa_ransom_exchange" in effect,
            "ZAZ_TUR_slave_trade: anti-slave policy does not replace the Kaffa market")

    decisions = read("decisions/ZaporizhiaDecisions.txt")
    for decision, flag, days in (
        ("zaz_great_raid", "great_raid_recent", "1825"),
        ("zaz_chaiky_raid", "chaiky_raid_recent", "1825"),
        ("zaz_liberate_slaves", "liberated_slaves_recent", "3650"),
    ):
        block = named_block(decisions, decision)
        require(failures, f"NOT = {{ has_country_flag = {flag} }}" in block
                and "had_country_flag = {" in block and f"days = {days}" in block,
                f"{decision}: reusable flag cooldown is not age-gated correctly")

    het = named_block(
        read("decisions/HetmanateCossackRaids.txt"), "het_deep_penetration_raid"
    )
    require(failures, "NOT = { has_country_flag = het_deep_raid_cooldown }" in het
            and "had_country_flag = {" in het and "days = 1825" in het,
            "het_deep_raid: reusable flag cooldown is not age-gated correctly")


def check_localisation_and_docs(failures: list[str]) -> None:
    loc = read("localisation/zzz_steppe_raiding_l_english.yml")
    for event_id, options in ((11, "ab"), (12, "ab"), (13, "abc"),
                              (14, "ab"), (15, "ab"), (16, "ab")):
        for suffix in ("t", "d", *options):
            key = f"steppe_raid.{event_id}.{suffix}:"
            require(failures, key in loc, f"missing English localisation {key}")
    for key in (
        "ottoman_crimean_reaction_cooldown:", "kaffa_ransom_exchange:",
        "desc_kaffa_ransom_exchange:",
    ):
        require(failures, key in loc, f"missing English localisation {key}")

    doc = read("docs/STEPPE_RAIDING_SYSTEM.md")
    future_match = re.search(r"(?is)## Ідеї майбутніх розширень(.*)", doc)
    future = future_match.group(1) if future_match else ""
    require(failures, bool(future_match), "STEPPE_RAIDING_SYSTEM: Future section is missing")
    for completed in ("ринок Кафи", "донськ", "черкес", "османська відповідь"):
        require(failures, completed.lower() not in future.lower(),
                f"STEPPE_RAIDING_SYSTEM: completed feature remains FUTURE: {completed}")
    require(failures, "localisation/zzz_steppe_raiding_l_english.yml" in doc,
            "STEPPE_RAIDING_SYSTEM: localisation path is stale")
    require(failures, "Єдисан (`282`)" in doc and "Яїк (`474`)" in doc,
            "STEPPE_RAIDING_SYSTEM: corrected migration IDs are not documented")


def main() -> int:
    failures: list[str] = []
    check_core_cycle(failures)
    check_new_chains(failures)
    check_helpers_and_callers(failures)
    check_policy_and_cooldowns(failures)
    check_localisation_and_docs(failures)

    if failures:
        print("Steppe expansion contract failures:")
        for failure in failures:
            print(f"  {failure}")
        return 1

    print("Don/Circassian raids, Ottoman reaction, and Kaffa market contracts hold")
    return 0


if __name__ == "__main__":
    sys.exit(main())
