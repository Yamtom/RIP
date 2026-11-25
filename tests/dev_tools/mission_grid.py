"""Print the mission grid of one country: which mission lands on which row of which column.

A development aid for the mission trees, not a gate. EU4 stacks the series of one column in file order
(the load order is the case-insensitive file name; a file of the mod replaces a vanilla file of the same
name) and a mission lands on max(previous row + 1, declared position), so a series that sorts after the
vanilla ones sits BELOW them, and a first mission without a prerequisite floats there without an arrow.
This tool answers "which vanilla mission is the last one in this column?" so that a new series can be
hung under it: required_missions = { that mission }, position = its row + 1.

    python tests/dev_tools/mission_grid.py --tag TUR --dlc "Domination,Winds of Change"
    python tests/dev_tools/mission_grid.py --tag LIT --dlc "Lions of the North" --tails

--dlc lists the DLC the player owns (default: all the DLC names that any mission file mentions).
--tails prints only the last mission of every column and the series that put it there.
--vanilla-only drops the mod's files that are not replacements of vanilla ones (the "before" picture).

Potentials are evaluated for the triggers the mission files really use (tag, was_tag, has_dlc, NOT/OR/AND,
the *_nation helpers, map_setup). Anything else counts as FALSE (a culture or government test that a series needs is not met by a bare tag)
and is listed under "assumed false", so read that list: a trigger that would show a series for the country
you are looking at would change its rows.
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "tests"))

from check_vanilla_mission_sync import parse  # noqa: E402
from clausewitz_testlib import vanilla_root  # noqa: E402

TATAR = {"GOL", "CRI", "NOG", "KAZ", "SHY", "GLH", "SIB", "BSH", "AST", "QAS", "KZH", "CHG", "KAS"}
KNOWN_FALSE = {"map_setup", "has_country_flag", "has_global_flag", "is_random_new_world", "ai"}


def load_files(vanilla_only: bool) -> dict[str, str]:
    files: dict[str, str] = {}
    root = vanilla_root()
    if root is not None:
        for path in (root / "missions").glob("*.txt"):
            files[path.name] = path.read_text(encoding="utf-8-sig", errors="replace")
    mod_dir = ROOT / "missions"
    for path in mod_dir.glob("*.txt"):
        if vanilla_only and path.name not in files:
            continue
        files[path.name] = path.read_text(encoding="utf-8-sig", errors="replace")
    return files


class Context:
    def __init__(self, tag: str, dlcs: set[str]):
        self.tag = tag
        self.dlcs = dlcs
        self.assumed: set[str] = set()

    def leaf(self, key: str, value: str) -> bool:
        value = value.strip('"')
        if key == "tag":
            return value == self.tag
        if key == "was_tag":
            return value == self.tag
        if key == "has_dlc":
            return value in self.dlcs
        if key in ("is_tatar_nation", "was_tatar_nation"):
            return (self.tag in TATAR) == (value == "yes")
        if key in ("is_mongol_nation", "was_mongol_nation", "is_moghulistan_nation", "was_moghulistan_nation"):
            return value != "yes"
        if key in KNOWN_FALSE:
            return False
        self.assumed.add(f"{key} = {value}")
        return False

    def evaluate(self, items, mode: str = "AND") -> bool:
        results = []
        taken = False  # an if / else_if branch of the current chain already ran
        for key, value in items:
            if key is None:
                continue
            if key in ("if", "else_if", "else") and isinstance(value, list):
                if key == "if":
                    taken = False
                if taken:
                    continue
                limit = next((v for k, v in value if k == "limit" and isinstance(v, list)), None)
                if limit is None or self.evaluate(limit, "AND"):
                    taken = True
                    results.append(self.evaluate([(k, v) for k, v in value if k != "limit"], "AND"))
                continue
            if isinstance(value, list):
                if key == "OR":
                    results.append(self.evaluate(value, "OR"))
                elif key == "AND":
                    results.append(self.evaluate(value, "AND"))
                elif key == "NOT":
                    results.append(not self.evaluate(value, "OR"))
                else:
                    self.assumed.add(f"{key} = {{ ... }}")
                    results.append(False)
            else:
                results.append(self.leaf(key, value))
        if not results:
            return True
        return any(results) if mode == "OR" else all(results)


def series_of(text: str):
    """[(series, slot, generic, potential_items, [(mission, position, [required])])]"""
    out = []
    for name, body in parse(text):
        if not isinstance(body, list):
            continue
        slot, generic, potential, missions = None, "no", [], []
        for key, value in body:
            if key == "slot":
                slot = int(value)
            elif key == "generic":
                generic = value
            elif key == "potential" and isinstance(value, list):
                potential = value
            elif isinstance(value, list) and any(k in ("icon", "position") for k, _ in value):
                position = next((int(v) for k, v in value if k == "position"), 0)
                required = next((v for k, v in value if k == "required_missions" and isinstance(v, list)), [])
                missions.append((key, position, [v for _, v in required]))
        if slot is not None:
            out.append((name, slot, generic, potential, missions))
    return out


def layout(files: dict[str, str], ctx: Context):
    cursor: dict[int, int] = defaultdict(int)
    placed: dict[str, tuple[int, int, list[str], str, str]] = {}
    active = []
    for fname in sorted(files, key=str.lower):
        for series, slot, generic, potential, missions in series_of(files[fname]):
            if ctx.evaluate(potential):
                active.append((fname, series, slot, generic, missions))
    for slot in {a[2] for a in active}:
        if any(a[3] != "yes" for a in active if a[2] == slot):
            active = [a for a in active if not (a[2] == slot and a[3] == "yes")]
    for fname, series, slot, generic, missions in active:
        for mission, position, required in missions:
            row = max(cursor[slot] + 1, position)
            cursor[slot] = row
            placed[mission] = (slot, row, required, series, fname)
    return placed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--dlc", default=None)
    parser.add_argument("--tails", action="store_true")
    parser.add_argument("--vanilla-only", action="store_true")
    args = parser.parse_args()

    files = load_files(args.vanilla_only)
    if args.dlc is None:
        names = set()
        for text in files.values():
            names.update(re.findall(r'has_dlc = "([^"]+)"', text))
        dlcs = names
    else:
        dlcs = {d.strip() for d in args.dlc.split(",") if d.strip()}
    ctx = Context(args.tag, dlcs)
    placed = layout(files, ctx)

    by_slot: dict[int, list] = defaultdict(list)
    for mission, (slot, row, required, series, fname) in placed.items():
        by_slot[slot].append((row, mission, required, series, fname))

    print(f"tag {args.tag}; DLC: {', '.join(sorted(dlcs)) or 'none'}; {len(placed)} missions placed")
    for slot in sorted(by_slot):
        rows = sorted(by_slot[slot])
        if args.tails:
            row, mission, required, series, fname = rows[-1]
            print(f"column {slot}: last row {row}  {mission}  (series {series}, {fname})")
            continue
        print(f"--- column {slot}")
        for row, mission, required, series, fname in rows:
            parent = ",".join(required) if required else "-"
            print(f"  row {row:2d}  {mission:44s} <- {parent:34s} [{series}; {fname}]")
    if ctx.assumed:
        print("assumed false (unevaluated triggers): " + "; ".join(sorted(ctx.assumed)[:30]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
