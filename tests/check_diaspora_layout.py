"""Static contracts for the two copies of the Ruthenian Diaspora mission tree.

Columns stack one series under another and the national trees differ in height, so
the tree exists twice: the original at rows 24-32 for every country, and a copy
with the suffix _kyiv at rows 15-23 for the tags of rip_diaspora_short_tree. This
test keeps the copies identical apart from ids and rows, checks that the short
tags really end above row 15 and that no tree reaches the tall rows, and that the
copy's texts and the decisions follow the originals.

Static only: it models EU4's per-slot stacking and does not run the game. Series
that gate on no literal tag (VOL_missions_*, ZAZ_missions_*, prl_missions_*) cannot
be measured here; they sit in the tall class, which is the safe one.
"""
import re
from collections import defaultdict

from check_donor_mission_ports import parse_series_in_file
from clausewitz_testlib import ROOT, named_block, read

DIASPORA = "missions/zzzz_RuthenianDiaspora_Missions.txt"
SHIFT = 9
SUFFIX = "_kyiv"
TALL_ROOT_ROW = 24
SHORT_ROOT_ROW = TALL_ROOT_ROW - SHIFT
DIASPORA_SLOTS = (2, 3, 4)


def mission_files():
    names = sorted((p.name for p in (ROOT / "missions").glob("*.txt")), key=str.lower)
    return [name for name in names if name != "zzzz_RuthenianDiaspora_Missions.txt"]


def balanced(text, start):
    depth = 0
    for index in range(start, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[start:index + 1]
    raise ValueError("unbalanced braces")


def series_with_tags(name):
    """(slot, potential, [position, ...]) per series; tolerant of files the donor parser rejects."""
    text = re.sub(r"#[^\n]*", "", read(f"missions/{name}"))
    found = []
    for match in re.finditer(r"(?m)^\w+ = \{", text):
        body = balanced(text, match.end() - 1)
        slot = re.search(r"\bslot = (\d+)", body)
        potential = re.search(r"potential = \{", body)
        if not slot or not potential:
            continue
        positions = []
        for mission in re.finditer(r"(?m)^\t(\w+) = \{", body):
            if mission.group(1) in ("potential", "potential_on_load", "ai_weight"):
                continue
            position = re.search(r"\bposition = (\d+)", balanced(body, mission.end() - 1))
            if position:
                positions.append(int(position.group(1)))
        found.append((int(slot.group(1)), balanced(body, potential.end() - 1), positions))
    return found


def heights(tag):
    """Highest occupied row per slot for one tag, counting every series that names it."""
    cursors = defaultdict(int)
    matched = 0
    for name in mission_files():
        for slot, potential, positions in series_with_tags(name):
            if re.search(rf"\btag\s*=\s*{tag}\b", potential):
                matched += 1
                for position in positions:
                    cursors[slot] = max(cursors[slot] + 1, position)
    return matched, dict(cursors)


def short_tags():
    trigger = named_block(read("common/scripted_triggers/rip_diaspora_triggers.txt"), "rip_diaspora_short_tree")
    return re.findall(r"\btag = (\w+)", trigger)


def check_short_tags(tags):
    failures = []
    for tag in tags:
        matched, cursors = heights(tag)
        if not matched:
            failures.append(f"{tag}: gates no mission series by a literal tag, so its height cannot be measured")
            continue
        tallest = max((cursors.get(slot, 0) for slot in DIASPORA_SLOTS), default=0)
        if tallest >= SHORT_ROOT_ROW:
            failures.append(f"{tag}: tree reaches row {tallest} in columns 2-4; the short copy starts at row {SHORT_ROOT_ROW}")
    return failures


def all_literal_tags():
    tags = set()
    for name in mission_files():
        for _, potential, _ in series_with_tags(name):
            tags |= set(re.findall(r"\btag\s*=\s*(\w+)", potential))
    return tags


def check_tall_rows():
    failures = []
    for tag in sorted(all_literal_tags()):
        _, cursors = heights(tag)
        tallest = max((cursors.get(slot, 0) for slot in DIASPORA_SLOTS), default=0)
        if tallest >= TALL_ROOT_ROW:
            failures.append(f"{tag}: tree reaches row {tallest} in columns 2-4, into the tall Diaspora rows")
    return failures


def normalised(block, suffixed):
    block = re.sub(r"\bposition = \d+", "position = N", block)
    if suffixed:
        block = block.replace(SUFFIX, "")
    return re.sub(r"\s+", " ", block).strip()


def main():
    text = read(DIASPORA)
    series = {name: (slot, potential, missions) for name, slot, potential, missions in parse_series_in_file(DIASPORA)}
    tall = [f"RIP_diaspora_missions_{n}" for n in (1, 2, 3)]
    short = [f"RIP_diaspora_kyiv_missions_{n}" for n in (1, 2, 3)]
    assert set(series) == set(tall + short), sorted(series)

    ids = []
    cells = {"tall": set(), "short": set()}
    for tall_name, short_name in zip(tall, short):
        t_slot, t_potential, t_missions = series[tall_name]
        s_slot, s_potential, s_missions = series[short_name]
        assert t_slot == s_slot, (tall_name, t_slot, s_slot)
        assert "NOT = { rip_diaspora_short_tree = yes }" in t_potential, tall_name
        assert "rip_diaspora_short_tree = yes" in s_potential and "NOT = { rip_diaspora_short_tree" not in s_potential, short_name
        assert len(t_missions) == len(s_missions)
        for (t_id, t_pos, t_reqs), (s_id, s_pos, s_reqs) in zip(t_missions, s_missions):
            assert s_id == t_id + SUFFIX, (t_id, s_id)
            assert s_pos == t_pos - SHIFT, (t_id, t_pos, s_pos)
            assert s_reqs == [r + SUFFIX for r in t_reqs], (t_id, t_reqs, s_reqs)
            assert t_pos >= TALL_ROOT_ROW and SHORT_ROOT_ROW <= s_pos < TALL_ROOT_ROW, (t_id, t_pos, s_pos)
            assert (t_slot, t_pos) not in cells["tall"] and (s_slot, s_pos) not in cells["short"], (t_id, "cell reused")
            cells["tall"].add((t_slot, t_pos))
            cells["short"].add((s_slot, s_pos))
            assert normalised(named_block(text, t_id), False) == normalised(named_block(text, s_id), True), \
                f"{s_id} differs from {t_id} beyond its id and row"
            ids.append(t_id)
    assert len(ids) == 15 and len(cells["tall"]) == len(cells["short"]) == 15
    assert not cells["tall"] & cells["short"]

    failures = check_short_tags(short_tags()) + check_tall_rows()
    assert not failures, "\n".join(failures)
    assert set(short_tags()) == {"KIE", "KRU", "UKR"}, short_tags()

    # Texts of the copy are references to the originals, in all four languages.
    english = dict(re.findall(r'^ ([\w.]+):\d+ "(.*)"$', read("localisation/RIP_shared_ruthenian_expeditions_l_english.yml"), re.M))
    for ident in ids:
        for part in ("title", "desc"):
            key = f"{ident}{SUFFIX}_{part}"
            assert english[key] == f"${ident}_{part}$", key
            assert english[f"{ident}_{part}"].strip(), f"{ident}_{part}"
    for lang in ("french", "german", "spanish"):
        fallback = dict(re.findall(r'^ ([\w.]+):\d+ "(.*)"$', read(f"localisation/replace/RIP_shared_ruthenian_content_l_{lang}.yml"), re.M))
        for ident in ids:
            for part in ("title", "desc"):
                assert fallback[f"{ident}{SUFFIX}_{part}"] == english[f"{ident}{SUFFIX}_{part}"], (lang, ident, part)

    # The decisions read flags, which both copies set; the empire decision reads the final mission.
    assert "mission_completed = rip_diaspora_of_rus_kyiv" in read("decisions/RIP_StateSymbolsDecisions.txt")
    assert "mission_id" not in read("decisions/RIP_RuthenianDiaspora.txt")

    # Planted violations: a tall tree in the short class, and a tree reaching the tall rows.
    assert check_short_tags(["CHR"]), "a 22-row tree was accepted for the short copy"
    assert check_short_tags(["XXX"]), "a tag with no series was accepted"
    original = heights

    def tall_heights(tag):
        return 1, {2: TALL_ROOT_ROW}

    globals()["heights"] = tall_heights
    try:
        assert check_tall_rows(), "a tree reaching row 24 was accepted"
    finally:
        globals()["heights"] = original

    print(f"PASS: Diaspora tree in two copies (rows {TALL_ROOT_ROW}-32 and {SHORT_ROOT_ROW}-{TALL_ROOT_ROW - 1}); "
          f"short tags {short_tags()} end by row {max(max(heights(t)[1].get(s, 0) for s in DIASPORA_SLOTS) for t in short_tags())}; static only")


if __name__ == "__main__":
    main()
