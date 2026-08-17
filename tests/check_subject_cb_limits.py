"""Regression contract for mission/event-granted subject casus belli.

Run from the mod root: ``python tests/check_subject_cb_limits.py``.
The two Austrian PU grants are an exact vanilla 1.37.5 carry-over and are the
only allowed subject-CB blocks without an explicit duration.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from clausewitz_testlib import ROOT, keyed_blocks, line_number, named_block, read


SUBJECT_CBS = {
    "cb_restore_personal_union": 240,
    "cb_vassalize_mission": 120,
    "cb_force_tributary_mission": 120,
    "cb_force_tributary": 0,
}
VANILLA_PU_FILE = Path("common/scripted_effects/03_scripted_effects_for_mission_rewards.txt")
VANILLA_PU_TARGETS = {"POL", "PLC"}


def value(block: str, key: str) -> str | None:
    match = re.search(rf"\b{re.escape(key)}\s*=\s*([A-Za-z0-9_.-]+)", block)
    return match.group(1) if match else None


def require(failures: list[str], condition: bool, message: str) -> None:
    if not condition:
        failures.append(message)


def event_block(text: str, event_id: str) -> str:
    for _, block in keyed_blocks(text, "country_event"):
        if value(block, "id") == event_id:
            return block
    raise KeyError(f"country_event id {event_id!r} not found")


def scan_all_grants(failures: list[str]) -> None:
    for directory in ("common", "decisions", "events", "missions"):
        for path in sorted((ROOT / directory).rglob("*.txt")):
            relative = path.relative_to(ROOT)
            text = path.read_text(encoding="utf-8-sig", errors="replace")
            for offset, block in keyed_blocks(text, "add_casus_belli"):
                cb_type = value(block, "type")
                if cb_type not in SUBJECT_CBS:
                    continue

                target = value(block, "target")
                months_text = value(block, "months")
                location = f"{relative}:{line_number(text, offset)}"
                vanilla_exception = (
                    relative == VANILLA_PU_FILE
                    and cb_type == "cb_restore_personal_union"
                    and target in VANILLA_PU_TARGETS
                )

                if cb_type == "cb_force_tributary":
                    failures.append(
                        f"{location}: generic cb_force_tributary cannot be granted by an effect"
                    )

                if months_text is None:
                    if not vanilla_exception:
                        failures.append(f"{location}: RIP subject CB needs explicit months")
                    continue

                try:
                    months = int(months_text)
                except ValueError:
                    failures.append(f"{location}: non-numeric months={months_text}")
                    continue

                cap = SUBJECT_CBS[cb_type]
                if cap and months > cap:
                    failures.append(
                        f"{location}: {cb_type} lasts {months} months (cap {cap})"
                    )


def check_kyiv(failures: list[str]) -> None:
    text = read("missions/Kyiv_Missions.txt")
    north = named_block(text, "KIE_northern_expansion")
    require(failures, "valid_for_personal_unions_trigger = yes" in north,
            "KIE_northern_expansion: PU eligibility guard is missing")
    require(failures, "is_neighbor_of = ROOT" in north,
            "KIE_northern_expansion: geographical guard is missing")
    require(failures, "else_if = {" in north,
            "KIE_northern_expansion: republican NOV fallback is not exclusive")
    require(failures, "months = 240" in north and "months = 120" in north,
            "KIE_northern_expansion: expected 240-month PU / 120-month vassal fallback")

    ruler = named_block(text, "KIE_true_ruler")
    require(failures, ruler.count("add_casus_belli = {") == 2,
            "KIE_true_ruler: expected exactly two alternative grants")
    require(failures, "else_if = {" in ruler,
            "KIE_true_ruler: VOL and VLN must be mutually exclusive")
    require(failures, ruler.count("months = 120") == 2 and "months = 300" not in ruler,
            "KIE_true_ruler: both alternatives must be capped at 120 months")
    require(failures, ruler.count("is_free_or_tributary_trigger = yes") >= 2,
            "KIE_true_ruler: free-target eligibility guards are missing")
    require(failures, ruler.count("is_neighbor_of = ROOT") >= 2,
            "KIE_true_ruler: geographical guards are missing")


def check_zaporozhia(failures: list[str]) -> None:
    text = read("missions/Zaporozhie_Missions.txt")
    require(failures, "type = cb_force_tributary\n" not in text,
            "Zaporozhie missions still grant the generic Emperor-of-China CB")

    grants = []
    for _, block in keyed_blocks(text, "add_casus_belli"):
        if value(block, "type") == "cb_force_tributary_mission":
            grants.append(block)
    require(failures, len(grants) == 10,
            f"Zaporozhie missions: expected 10 tributary mission grants, found {len(grants)}")
    require(failures, all(value(block, "months") == "120" for block in grants),
            "Zaporozhie missions: every tributary grant must last 120 months")

    triple = named_block(text, "ZAZ_GOL_crimea_3")
    require(failures, triple.count("else_if = {") >= 2,
            "ZAZ_GOL_crimea_3: IME/AVR/GAZ targets are not mutually exclusive")
    require(failures, triple.count("add_casus_belli = {") == 3,
            "ZAZ_GOL_crimea_3: expected three exclusive target alternatives")
    require(failures, triple.count("add_claim = ROOT") >= 2,
            "ZAZ_GOL_crimea_3: normal-claim route fallback is missing")

    cleanup_calls = len(re.findall(r"rip_clear_[A-Za-z0-9_]*tributary[A-Za-z0-9_]*\s*=\s*yes", text))
    require(failures, cleanup_calls >= 10,
            "Zaporozhie missions: each new tributary reward must clear the old chain CB")
    require(failures, text.count("is_free_or_tributary_trigger = yes") >= 10,
            "Zaporozhie missions: tributary target eligibility guards are incomplete")
    require(failures, text.count("is_neighbor_of = ROOT") >= 10,
            "Zaporozhie missions: tributary geographical guards are incomplete")


def check_recurring_events(failures: list[str]) -> None:
    cases = (
        ("events/HetmanateMoldovanExpansion.txt", "het_moldova.4"),
        ("events/HetmanateSuccession.txt", "het_succession.5"),
        ("events/Ruina.txt", "ruina_events.4"),
    )
    for relative, block_name in cases:
        block = event_block(read(relative), block_name)
        require(failures, "has_casus_belli" in block,
                f"{block_name}: recurring reward can refresh an active subject CB")

    uzh = named_block(read("missions/Zakarpatta_Missions.txt"), "uz_crown_of_saint_stephen")
    require(failures, "valid_for_personal_unions_trigger = yes" in uzh,
            "uz_crown_of_saint_stephen: HUN PU eligibility guard is missing")

    svydrigaylo = event_block(read("events/svydrigaylo_independence.txt"), "svydrigaylo.001")
    require(failures, "months = 120" in svydrigaylo,
            "svydrigaylo.001: vassal CB needs an explicit 120-month duration")


def main() -> int:
    failures: list[str] = []
    scan_all_grants(failures)
    check_kyiv(failures)
    check_zaporozhia(failures)
    check_recurring_events(failures)

    if failures:
        print("Subject-CB contract failures:")
        for failure in failures:
            print(f"  {failure}")
        return 1

    print("Subject-CB durations, eligibility, and target exclusivity are bounded")
    return 0


if __name__ == "__main__":
    sys.exit(main())
