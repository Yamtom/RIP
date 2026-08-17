"""Static regression contract for Border Principalities and Qasim chains."""

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


def event_block(text: str, event_id: str) -> str:
    candidates = [
        block for _, block in keyed_blocks(text, "country_event")
        if scalar(block, "id") == event_id and re.search(r"(?m)^\s*title\s*=", block)
    ]
    if not candidates:
        raise KeyError(f"country_event id {event_id!r} not found")
    return max(candidates, key=len)


def options(block: str) -> list[str]:
    return [option for _, option in keyed_blocks(block, "option")]


def check_border_events(failures: list[str]) -> None:
    text = read("events/BorderPrincipalities.txt")
    for number in range(1, 13):
        event_block(text, f"border_principalities.{number}")

    for province, name in (("4543", "Rylsk"), ("298", "Kursk"),
                           ("297", "Bryansk"), ("1945", "Novgorod-Seversky"),
                           ("4244", "Starodub")):
        require(failures, province in text,
                f"Border Principalities: corrected {name} id {province} is missing")
    for stale in ("province_id = 295", "province_id = 2408", "province_id = 1960"):
        require(failures, stale not in text,
                f"Border Principalities: stale wrong province reference remains: {stale}")

    forbidden_cbs = (
        "cb_restore_personal_union", "cb_core", "cb_annex", "cb_support_rebels",
    )
    for cb_type in forbidden_cbs:
        require(failures, cb_type not in text,
                f"Border Principalities: invalid/prerequisite-driven CB remains: {cb_type}")
    require(failures, "declare_war_with_cb" not in text,
            "Border Principalities: an event still forces an immediate war")

    rylsk = event_block(text, "border_principalities.4")
    jagoldai = event_block(text, "border_principalities.9")
    severia = event_block(text, "border_principalities.11")
    require(failures, "border_war_preparation" in rylsk
            and "border_war_preparation" in jagoldai
            and "border_war_preparation" in severia,
            "Border refusal paths do not consistently prepare a bounded response")
    require(failures, "army_size = LIT" not in jagoldai
            and "MOS = { army_size = ROOT }" in normalized(jagoldai),
            "border_principalities.9: Muscovite strength is still compared to hard-coded LIT")

    glinski = event_block(text, "border_principalities.6")
    require(failures, "save_event_target_as = glinski_disputed_province" in glinski,
            "border_principalities.6: Glinski province is not fixed before option effects")
    rebellion = event_block(text, "border_principalities.7")
    require(failures, "random_owned_province" in rebellion
            and "glinski_tatar_settlement" in rebellion,
            "border_principalities.7: delayed rebellion relies on a global stale event target")
    require(failures, "event_target:glinski_disputed_province" not in rebellion,
            "border_principalities.7: delayed global event-target collision remains")

    for number in (5, 8, 12):
        reception = event_block(text, f"border_principalities.{number}")
        require(failures, "add_casus_belli" not in reception,
                f"border_principalities.{number}: reception event grants an invalid generic CB")


def check_qasim_events(failures: list[str]) -> None:
    text = read("events/QasimKhanate.txt")
    for number in range(1, 7):
        event_block(text, f"qasim_khanate.{number}")

    foundation = event_block(text, "qasim_khanate.1")
    require(failures, foundation.find("release = QAS") < foundation.find("create_subject = {")
            and foundation.find("release = QAS") >= 0,
            "qasim_khanate.1: QAS must be released before it is made a subject")

    intervention = event_block(text, "qasim_khanate.2")
    require(failures, "fire_only_once = yes" in intervention
            and "qasim_kazan_intervention_resolved" in intervention,
            "qasim_khanate.2: recurring intervention is not consumed")
    require(failures, "cb_restore_personal_union" not in intervention
            and "declare_war_with_cb" not in intervention,
            "qasim_khanate.2: invalid Kazan PU war remains")
    require(failures, "type = cb_vassalize_mission" in intervention
            and "months = 120" in intervention and "has_casus_belli" in intervention,
            "qasim_khanate.2: bounded guarded Kazan intervention CB is missing")
    require(failures, "kazan_area" in intervention and "add_claim = QAS" in intervention,
            "qasim_khanate.2: Qasim lacks exact conquest claims in Kazan")
    require(failures, all("set_country_flag = qasim_kazan_intervention_resolved" in option
                          for option in options(intervention)),
            "qasim_khanate.2: one or more choices can refresh the event")

    fate = event_block(text, "qasim_khanate.3")
    require(failures, "fire_only_once = yes" in fate
            and "qasim_kazan_fate_resolved" in fate,
            "qasim_khanate.3: Kazan fate is not a one-shot decision")
    require(failures, "kazan_area = {" in fate and "add_core = QAS" in fate,
            "qasim_khanate.3: installed Qasim ruler does not receive the Kazan area")
    require(failures, "release = QAS" not in fate and "create_subject = {" not in fate,
            "qasim_khanate.3: existing QAS is redundantly released/re-vassalized")
    require(failures, all("set_country_flag = qasim_kazan_fate_resolved" in option
                          for option in options(fate)),
            "qasim_khanate.3: one or more outcomes can repeat")

    loyalty = event_block(text, "qasim_khanate.6")
    require(failures, "fire_only_once = yes" in loyalty
            and "NOT = { has_country_flag = lipka_loyalty_settled }" in loyalty,
            "qasim_khanate.6: Lipka loyalty event can recur")
    require(failures, all("set_country_flag = lipka_loyalty_settled" in option
                          for option in options(loyalty)),
            "qasim_khanate.6: one or more outcomes do not consume the event")


def check_modifiers_and_integration(failures: list[str]) -> None:
    modifiers = read("common/event_modifiers/border_principalities_modifiers.txt")
    lipka = named_block(modifiers, "lipka_tatar_settlement")
    require(failures, "local_hostile_attrition" in lipka,
            "Lipka settlement lacks the documented raid-defense effect")
    require(failures, "border_war_preparation = {" in modifiers,
            "Border war preparation modifier was removed instead of wired")
    for orphan in ("lipka_tatar_garrison", "severian_princes_defection",
                   "muscovite_expansion_momentum"):
        require(failures, f"{orphan} = {{" not in modifiers,
                f"dead Border modifier remains defined: {orphan}")

    raids = read("events/SteppeRaiding.txt")
    target = event_block(raids, "steppe_raid.2")
    for modifier in ("glinski_tatar_settlement", "jagoldai_horde_settlement",
                     "lipka_tatar_settlement"):
        require(failures, target.count(modifier) >= 2,
                f"Steppe raid targeting/damage does not honor {modifier}")


def check_localisation_and_docs(failures: list[str]) -> None:
    border_loc = read("localisation/border_principalities_l_english.yml")
    qasim_loc = read("localisation/qasim_khanate_l_english.yml")
    for number in range(1, 13):
        for suffix in ("t", "d"):
            require(failures, f"border_principalities.{number}.{suffix}:" in border_loc,
                    f"missing Border localisation border_principalities.{number}.{suffix}")
    for number in range(1, 7):
        for suffix in ("t", "d"):
            require(failures, f"qasim_khanate.{number}.{suffix}:" in qasim_loc,
                    f"missing Qasim localisation qasim_khanate.{number}.{suffix}")

    doc = read("docs/BORDER_PRINCIPALITIES_SYSTEM.md")
    require(failures, "tests/check_border_principalities.py" in doc,
            "BORDER_PRINCIPALITIES_SYSTEM: dedicated regression test is undocumented")
    require(failures, "restoration PU war" not in doc and "annexation war" not in doc,
            "BORDER_PRINCIPALITIES_SYSTEM: stale invalid war semantics remain")
    require(failures, "core CB" not in doc and "support rebels CB" not in doc,
            "BORDER_PRINCIPALITIES_SYSTEM: stale prerequisite-driven CB claims remain")
    require(failures, "defined, never applied" not in doc,
            "BORDER_PRINCIPALITIES_SYSTEM: removed orphan modifiers remain documented")
    require(failures, "no direct Cossack-estate effects" in doc,
            "BORDER_PRINCIPALITIES_SYSTEM: indirect Cossack integration is still overclaimed")


def main() -> int:
    failures: list[str] = []
    check_border_events(failures)
    check_qasim_events(failures)
    check_modifiers_and_integration(failures)
    check_localisation_and_docs(failures)

    if failures:
        print("Border/Qasim contract failures:")
        for failure in failures:
            print(f"  {failure}")
        return 1

    print("Border Principalities and Qasim event contracts hold")
    return 0


if __name__ == "__main__":
    sys.exit(main())
