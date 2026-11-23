"""Layout contract for the Zaporozhie mission tree in every state of the Rada.

EU4 stacks the visible series of one column in file order: a mission lands on
max(previous row + 1, declared position). An arrow runs down its PARENT's column to the gap
above the child's row, then across and into the child. Two things make a tree read badly:
an arrow that runs behind another card (it seems to leave that card) and a card that jumps
to another row when the player's choice hides its siblings.

Six course roots hang off "A Zaporozhian State" but there are only five columns, so the
tree has two tiers: four roots directly under the hub and, one row lower, the Giray pact
straight down the hub's own column and the Cossack Republic beside it. This check simulates
the stacking for the opening state and for each of the six choices and pins:

* declared position == stacked row for every mission (nothing is shifted by the engine);
* every parent is visible, above its child, and no arrow runs behind a card;
* the hub has a row of its own and nothing else shares it;
* each course root keeps the same cell before and after it is chosen;
* the first missions of a chosen path sit exactly one row under their root.

Source-contract check only - it does not launch EU4.
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "tests"))

from clausewitz_testlib import read  # noqa: E402

ZAZ = "missions/Zaporozhie_Missions.txt"
HUB = "ZAZ_finally"
# course root -> (flag it sets, slot, tier): tier 1 sits one row under the hub, tier 2 two rows
ROOTS = {
    "ZAZ_ally_tur": ("zaz_allied_tur", 1, 1),
    "ZAZ_ally_tartar": ("zaz_allied_gol", 2, 1),
    "ZAZ_ally_pol": ("zaz_allied_pol", 4, 1),
    "ZAZ_ally_rus": ("zaz_allied_rus", 5, 1),
    "ZAZ_ally_crimea": ("zaz_allied_cri", 3, 2),
    "ZAZ_only_zaz": ("zaz_only_zaz", 2, 2),
}
PATH_PREFIX = {
    "zaz_allied_tur": "ZAZ_TUR_", "zaz_allied_gol": "ZAZ_GOL_", "zaz_allied_pol": "ZAZ_POL_",
    "zaz_allied_rus": "ZAZ_RUS_", "zaz_allied_cri": "ZAZ_CRI_", "zaz_only_zaz": "ZAZ_UKR_",
}


def parse() -> list[tuple[str, int, str, list[tuple[str, int, list[str]]]]]:
    text = read(ZAZ).replace("\r\n", "\n")
    out = []
    for series in re.finditer(r"(?ms)^([A-Za-z0-9_]+) = \{\n(.*?)^\}\n", text):
        body = series[2]
        slot = int(re.search(r"slot = (\d+)", body)[1])
        potential = re.search(r"(?s)potential = \{(.*?)\n\t\}", body)
        missions = []
        for mission in re.finditer(r"(?ms)^\t(ZAZ_[A-Za-z0-9_]+) = \{\n(.*?)^\t\}\n", body):
            position = int(re.search(r"position = (\d+)", mission[2])[1])
            required = re.search(r"required_missions = \{([^}]*)\}", mission[2])
            missions.append((mission[1], position, required[1].split() if required else []))
        out.append((series[1], slot, potential[1] if potential else "", missions))
    return out


def holds(potential: str, flags: set[str]) -> bool:
    """Evaluate the small potential grammar the ZAZ series use; anything else fails loudly."""
    tokens = re.findall(r"[A-Za-z0-9_]+|=|\{|\}", potential)
    position = 0

    def block() -> list[tuple]:
        nonlocal position
        items = []
        while position < len(tokens) and tokens[position] != "}":
            key = tokens[position]
            assert tokens[position + 1] == "=", key
            position += 2
            if tokens[position] == "{":
                position += 1
                items.append(("block", key, block()))
                position += 1
            else:
                items.append(("pair", key, tokens[position]))
                position += 1
        return items

    def evaluate(items: list[tuple], mode: str = "AND") -> bool:
        results = []
        for kind, key, value in items:
            if kind == "pair":
                if key == "tag":
                    result = value == "ZAZ"
                elif key == "has_country_flag":
                    result = value in flags
                elif key == "zaz_has_legacy_missions":
                    result = True
                elif key == "zaz_rada_course_open":
                    result = not any(f.startswith("zaz_allied") or f == "zaz_only_zaz" for f in flags)
                else:
                    raise AssertionError(f"potential uses {key}: teach this check how to evaluate it")
            elif key == "AND":
                result = evaluate(value, "AND")
            elif key == "OR":
                result = evaluate(value, "OR")
            elif key == "NOT":
                result = not evaluate(value, "OR")
            else:
                raise AssertionError(f"potential uses block {key}")
            results.append(result)
        return any(results) if mode == "OR" else all(results)

    return evaluate(block())


def layout(flags: set[str]) -> tuple[dict[str, tuple[int, int, list[str]]], dict[tuple[int, int], str], list[str]]:
    cursor: dict[int, int] = defaultdict(int)
    placed: dict[str, tuple[int, int, list[str]]] = {}
    grid: dict[tuple[int, int], str] = {}
    shifts = []
    for name, slot, potential, missions in parse():
        if not holds(potential, flags):
            continue
        for mission, declared, required in missions:
            actual = max(cursor[slot] + 1, declared)
            if actual != declared:
                shifts.append(f"{mission} declared {declared} but stacked on {actual}")
            cursor[slot] = actual
            assert (slot, actual) not in grid, (mission, grid[(slot, actual)])
            grid[(slot, actual)] = mission
            placed[mission] = (slot, actual, required)
    return placed, grid, shifts


def arrow_problems(placed, grid) -> list[str]:
    problems = []
    for name, (slot, row, required) in placed.items():
        for parent in required:
            if parent not in placed:
                problems.append(f"{name}: parent {parent} is not on screen")
                continue
            p_slot, p_row, _ = placed[parent]
            if row <= p_row:
                problems.append(f"{name}: parent {parent} is not above it")
                continue
            # the arrow runs down the parent's column to the gap above the child's row
            behind = [grid[(p_slot, y)] for y in range(p_row + 1, row) if (p_slot, y) in grid]
            if behind:
                problems.append(f"{parent} -> {name}: the arrow runs behind {behind}")
    return problems


def states() -> dict[str, set[str]]:
    result = {"opening": set()}
    for root, (flag, _, _) in ROOTS.items():
        result[root] = {flag}
    return result


def check_every_state_stacks_cleanly() -> None:
    for label, flags in states().items():
        placed, grid, shifts = layout(flags)
        assert not shifts, (label, shifts)
        problems = arrow_problems(placed, grid)
        assert not problems, (label, problems)
        assert max(row for _, row in grid) <= 17, label


def check_hub_has_a_row_of_its_own() -> None:
    for label, flags in states().items():
        placed, grid, _ = layout(flags)
        hub_slot, hub_row, _ = placed[HUB]
        others = [name for (slot, row), name in grid.items() if row == hub_row and name != HUB]
        assert not others, (label, others)
        # the spine from "Consolidate the Host" to the hub is free of cards
        assert placed[HUB][2] == ["ZAZ_proper"], placed[HUB]
        assert not [y for y in range(placed["ZAZ_proper"][1] + 1, hub_row) if (hub_slot, y) in grid], label
        # and every other column of the opening ends above the hub
        assert all(row < hub_row for (slot, row), name in grid.items()
                   if name in ("ZAZ_krakow", "ZAZ_saratov", "ZAZ_moskva", "ZAZ_istanbul",
                               "ZAZ_sahaidachnyi_reforms", "ZAZ_heroic_campaigns")), label


def check_course_roots_sit_under_the_hub_in_two_tiers() -> None:
    placed, grid, _ = layout(set())
    hub_slot, hub_row, _ = placed[HUB]
    assert set(ROOTS) <= set(placed), set(ROOTS) - set(placed)
    for root, (_, slot, tier) in ROOTS.items():
        assert placed[root][:2] == (slot, hub_row + tier), (root, placed[root])
        assert placed[root][2] == [HUB], (root, placed[root])
    # the four tier-1 roots leave the hub's own column free, so the trunk to tier 2 is not hidden
    assert (hub_slot, hub_row + 1) not in grid
    # the roots of tier 2 have nothing under the cards of tier 1 except the Republic's neighbour
    assert grid[(2, hub_row + 1)] == "ZAZ_ally_tartar" and grid[(2, hub_row + 2)] == "ZAZ_only_zaz"


def check_a_chosen_root_keeps_its_cell() -> None:
    opening, _, _ = layout(set())
    for root, (flag, _, _) in ROOTS.items():
        chosen, grid, _ = layout({flag})
        assert chosen[root][:2] == opening[root][:2], (root, chosen[root], opening[root])
        # nothing of the other courses is left on screen
        for other in ROOTS:
            if other != root:
                assert other not in chosen, (root, other)
        # the first missions of the path hang one row under their root
        first = [name for name, (s, r, req) in chosen.items() if req == [root]]
        assert first, root
        rows = {chosen[name][1] for name in first}
        assert rows == {chosen[root][1] + 1}, (root, rows)
        assert all(name.startswith(PATH_PREFIX[flag]) or name == "ZAZ_perekop_trade" for name in first), (root, first)


def main() -> int:
    check_every_state_stacks_cleanly()
    check_hub_has_a_row_of_its_own()
    check_course_roots_sit_under_the_hub_in_two_tiers()
    check_a_chosen_root_keeps_its_cell()
    print(
        "ZAZ MISSION LAYOUT PASS: the opening and all six choices stack without a shifted mission or an "
        "arrow behind a card, the hub has a row of its own, the course roots sit under it in two tiers "
        "and keep their cell once chosen, and every path starts one row under its root (static only)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
