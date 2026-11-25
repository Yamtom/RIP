"""Polish/Commonwealth mission rework: load order, genericity, Hadiach triggers.

What is held (static only, nothing here runs the game):

* The rework file loads AFTER the vanilla Polish_Missions.txt and SCA_Polish_Missions.txt.
  EU4 loads missions/ alphabetically and stacks the series of a column one under
  another, so a file that sorts first with positions 11-18 pushes the vanilla tree
  below row 18.
* Its series are generic = no and keep out of map_setup_random, like the vanilla ones.
* No calc_true_if can be unsatisfiable by arithmetic (amount larger than the number
  of triggers written directly inside it): one any_owned_province is one trigger.
* The Hadiach missions state each condition once, inside one custom_trigger_tooltip,
  not twice (a hidden copy plus an open copy doubled the player's tooltip lines).
* The Compact of Three Nations does not make assimilation cheaper.
* The Russian patriarchate reward also reaches russian_orthodox.
"""

from __future__ import annotations

import re
import sys

from clausewitz_testlib import ROOT, _mask_comments_and_strings, keyed_blocks, named_block, normalized, read

REWORK = "zzz_Poland_Commonwealth_Rework.txt"
# Files of the installed game that define the Polish series, by name; the
# comparison is case-insensitive, as the engine's is.
VANILLA_POLISH = ("Polish_Missions.txt", "SCA_Polish_Missions.txt")
HADIACH_MISSIONS = ("pol_hadiach_commission", "pol_codify_hadiach_privileges", "pol_triatomic_commonwealth")


def require(failures: list[str], condition: bool, message: str) -> None:
    if not condition:
        failures.append(message)


def statements(body: str) -> list[str]:
    """Top-level statements of a block body, one entry per `key = value` or `key = { ... }`."""
    tokens = re.findall(r"[{}=]|[^\s{}=]+", _mask_comments_and_strings(body))
    result: list[str] = []
    index = 0
    while index < len(tokens):
        key = tokens[index]
        if key in "{}=":
            index += 1
            continue
        if index + 2 < len(tokens) + 0 and tokens[index + 1] == "=":
            if tokens[index + 2] == "{":
                depth, cursor = 0, index + 2
                while cursor < len(tokens):
                    depth += tokens[cursor] == "{"
                    depth -= tokens[cursor] == "}"
                    cursor += 1
                    if depth == 0:
                        break
                result.append(" ".join(tokens[index:cursor]))
                index = cursor
            else:
                result.append(" ".join(tokens[index:index + 3]))
                index += 3
        else:
            index += 1
    return result


def unsatisfiable_calc_true_if(text: str) -> list[str]:
    """calc_true_if blocks that count fewer triggers than `amount` and have no all_* iterator.

    calc_true_if adds up the triggers written directly inside it. An all_* scope
    iterator (all_owned_province, all_country...) counts every scope that passes, so it
    can reach any amount; an any_* iterator is one trigger and adds at most 1.
    A custom_trigger_tooltip wrapper and the vanilla `desc =` form (a scripted iterator
    such as european_trade_node_scope) are left alone: either may carry its own iterator.
    """
    problems = []
    for offset, block in keyed_blocks(text, "calc_true_if"):
        opening = block.index("{")
        body = block[opening + 1: block.rindex("}")]
        masked = _mask_comments_and_strings(body)
        amount_match = re.search(r"\bamount\s*=\s*(\d+)", masked)
        if (not amount_match or re.search(r"\ball_\w+\s*=\s*\{", masked)
                or "custom_trigger_tooltip" in masked or re.search(r"\bdesc\s*=", masked)):
            continue
        amount = int(amount_match.group(1))
        children = [s for s in statements(body) if not re.match(r"amount\s*=", s)]
        if len(children) < amount:
            problems.append(f"line {text.count(chr(10), 0, offset) + 1}: amount = {amount}, "
                            f"{len(children)} trigger(s) inside")
    return problems


def check_load_order(failures: list[str]) -> None:
    names = sorted(path.name for path in (ROOT / "missions").glob("*.txt"))
    require(failures, REWORK in names,
            f"missions/{REWORK} is missing (the Polish rework must load after the vanilla Polish files)")
    require(failures, "Poland_Commonwealth_Rework.txt" not in names,
            "missions/Poland_Commonwealth_Rework.txt sorts before Polish_Missions.txt: rename it with zzz_")
    for vanilla in VANILLA_POLISH:
        require(failures, REWORK.lower() > vanilla.lower(),
                f"{REWORK} must sort after the vanilla {vanilla}")


def check_series(failures: list[str]) -> None:
    text = read(f"missions/{REWORK}")
    series = [named_block(text, f"POL_re_missions_{slot}") for slot in range(1, 5)]
    opening = named_block(text, "rip_pol_carpathian_passes")
    for parent in ("pol_moldavia", "annex_mazovia"):
        require(failures, f"mission_completed = {parent}" in opening, f"Missing native opening {parent}")
    for key, parent in (("pol_restore_sejm_discipline", "rip_pol_carpathian_passes"),
                        ("pol_secure_grain_trade", "rip_pol_lviv_charters")):
        require(failures, parent in named_block(named_block(text, key), "required_missions"),
                f"{key} must follow {parent}")
    for block in series:
        name = re.search(r"POL_re_missions_\d", block).group(0)
        require(failures, re.search(r"(?m)^\tgeneric = no\s*$", block) is not None,
                f"{name}: must be generic = no (a generic series gives way to the vanilla non-generic ones)")
        require(failures, "NOT = { map_setup = map_setup_random }" in normalized(named_block(block, "potential")),
                f"{name}: potential must exclude map_setup_random, like the vanilla series")


def check_hadiach(failures: list[str]) -> None:
    text = read(f"missions/{REWORK}")
    for problem in unsatisfiable_calc_true_if(text):
        failures.append(f"{REWORK}: calc_true_if can never be true ({problem})")

    codify = named_block(text, "pol_codify_hadiach_privileges")
    trigger = named_block(codify, "trigger")
    require(failures, "calc_true_if" not in _mask_comments_and_strings(trigger),
            "pol_codify_hadiach_privileges: count the seated provinces with num_of_owned_provinces_with")
    counted = [block for _, block in keyed_blocks(trigger, "num_of_owned_provinces_with")]
    require(failures, any(
        "value = 3" in block and "region = ruthenia_region" in block
        and "has_seat_in_parliament = yes" in block for block in counted),
        "pol_codify_hadiach_privileges: needs num_of_owned_provinces_with = 3 Ruthenian provinces with a seat")

    for mission in HADIACH_MISSIONS:
        trigger = named_block(named_block(text, mission), "trigger")
        require(failures, "hidden_trigger" not in trigger,
                f"{mission}: a hidden copy of a visible condition doubles the tooltip")
        tooltips = re.findall(r"tooltip\s*=\s*(POL_\w+)", _mask_comments_and_strings(trigger))
        require(failures, bool(tooltips) and len(tooltips) == len(set(tooltips)),
                f"{mission}: each custom tooltip must appear exactly once")
        for _, tooltip_block in keyed_blocks(trigger, "custom_trigger_tooltip"):
            body = tooltip_block[tooltip_block.index("{") + 1: tooltip_block.rindex("}")]
            real = [s for s in statements(body) if not re.match(r"tooltip\s*=", s)]
            require(failures, len(real) >= 1,
                    f"{mission}: a custom tooltip has no real trigger inside it, so it would show a line and check nothing")
        # What stands inside a tooltip must not be written a second time outside it.
        outside = trigger
        for _, tooltip_block in keyed_blocks(trigger, "custom_trigger_tooltip"):
            outside = outside.replace(tooltip_block, "")
        require(failures, "any_subject_country" not in outside
                and "num_of_owned_provinces_with" not in outside
                and "any_owned_province" not in outside,
                f"{mission}: a condition shown in a custom tooltip is repeated outside it")


def check_modifier(failures: list[str]) -> None:
    block = named_block(read("common/event_modifiers/RIP_POL_modifiers.txt"), "pol_triatomic_compact")
    require(failures, "culture_conversion_cost" not in block,
            "pol_triatomic_compact: an equal federation must not make assimilation cheaper")
    require(failures, "promote_culture_cost = -0.25" in block,
            "pol_triatomic_compact: expected promote_culture_cost = -0.25")


def check_patriarchate(failures: list[str]) -> None:
    block = named_block(read("missions/DOM_Russia_Missions.txt"), "mos_rus_russian_patriarchate")
    effect = named_block(block, "effect")
    first_limit = re.search(r"limit\s*=\s*\{([^}]*)\}", effect)
    require(failures, first_limit is not None
            and "rip_faith_is_eastern_orthodox = yes" in first_limit.group(1)
            and "religion = orthodox" not in first_limit.group(1),
            "mos_rus_russian_patriarchate: the patriarchate reward must reach russian_orthodox too")


def check_repository_calc_true_if(failures: list[str]) -> None:
    """The same arithmetic mistake anywhere else in the scripted layer."""
    for folder in ("missions", "decisions", "events", "common"):
        for path in sorted((ROOT / folder).rglob("*.txt")):
            # Some script files are cp1252 (vanilla style), so decode leniently.
            text = path.read_text(encoding="utf-8-sig", errors="replace")
            if "calc_true_if" not in text:
                continue
            for problem in unsatisfiable_calc_true_if(text):
                failures.append(f"{path.relative_to(ROOT).as_posix()}: calc_true_if can never be true ({problem})")


def self_test(failures: list[str]) -> None:
    broken = "x = {\n\tcalc_true_if = {\n\t\tamount = 3\n\t\tany_owned_province = {\n\t\t\tregion = a\n\t\t}\n\t}\n}\n"
    fine = ("x = {\n\tcalc_true_if = {\n\t\tamount = 2\n\t\tany_owned_province = { a = b }\n"
            "\t\tnum_accepted_cultures = 4\n\t\tNOT = { b = c }\n\t}\n}\n")
    require(failures, len(unsatisfiable_calc_true_if(broken)) == 1,
            "self-test: one any_owned_province with amount = 3 must be flagged")
    require(failures, not unsatisfiable_calc_true_if(fine),
            "self-test: three direct triggers with amount = 2 must pass")


def main() -> int:
    failures: list[str] = []
    self_test(failures)
    check_load_order(failures)
    check_series(failures)
    check_hadiach(failures)
    check_modifier(failures)
    check_patriarchate(failures)
    check_repository_calc_true_if(failures)
    if failures:
        print("Polish Commonwealth mission contract failures:")
        for failure in failures:
            print(f"  {failure}")
        return 1
    print("POLISH COMMONWEALTH MISSIONS PASS: loads after the vanilla Polish files, generic = no, "
          "Hadiach seat count satisfiable, one tooltip line per condition, Compact keeps assimilation "
          "price, patriarchate reaches russian_orthodox, no unsatisfiable calc_true_if in the scripts. "
          "Static only.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
