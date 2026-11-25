"""Verify national ownership, dates, DLC twin ties, grid placement and event links for the historical record."""
from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "dev_tools"))

import mission_grid as mg  # noqa: E402
from check_donor_mission_ports import parse_series_in_file  # noqa: E402
from clausewitz_testlib import keyed_blocks, named_block, read, vanilla_root  # noqa: E402

path = "missions/zzzzzz_Historical_Record.txt"
missions = read(path)
events = read("events/RIP_shared_ruthenian_HistoricalRecord.txt")
expected = {
    "RUS": {"baturyn": 1708, "chortomlyk": 1709, "presses": 1720,
            "ladoga": 1721, "polubotok": 1723, "new_sich": 1775,
            "solovki": 1776, "serfdom": 1783},
    "PLC": {"solonytsia": 1596, "kodnia": 1768},
    "CRI": {"kyiv_captives": 1482},
    "TUR": {"ladyzhyn": 1674},
    "LIT": {"volhynian_expulsion": 1495},
}
expected_ties = {
    "rip_record_kyiv_captives": (5, 19, ["rip_tatar_dnieper_tribute"]),
    "rip_record_kyiv_captives_classic": (5, 7, ["rip_tatar_dnieper_tribute_classic"]),
    "rip_record_ladyzhyn": (4, 15, ["rip_tur_podillian_eyalet"]),
    "rip_record_ladyzhyn_classic": (4, 11, ["rip_tur_podillian_eyalet_classic"]),
    "rip_record_volhynian_expulsion": (1, 9, ["rip_lit_kyiv_succession"]),
    "rip_record_volhynian_expulsion_classic": (1, 8, ["rip_lit_kyiv_succession_classic"]),
}

event_blocks = dict((re.search(r"id = (rip_historical_record\.\d+)", block)[1], block)
                    for _, block in keyed_blocks(events, "country_event"))
calls = Counter()
seen = {tag: {} for tag in expected}
seen_classic = {tag: {} for tag in expected}
placed_entries = {}
keys = set()
classic_bases = {}

for _, slot, potential, entries in parse_series_in_file(path):
    (tag,) = re.findall(r"\btag = (\w+)", potential)
    for name, row, parents in entries:
        placed_entries[name] = (slot, row, parents)
        if name in expected_ties:
            assert (slot, row, parents) == expected_ties[name], (name, (slot, row, parents))
        trigger = named_block(named_block(missions, name), "trigger")
        effect = named_block(named_block(missions, name), "effect")
        year = int(re.search(r"is_year = (\d+)", trigger)[1])
        event = re.search(r"id = (rip_historical_record\.\d+)", effect)[1]
        if name.endswith("_classic"):
            base_name = name.removesuffix("_classic")
            key = base_name.removeprefix("rip_record_")
            assert key not in seen_classic[tag], name
            seen_classic[tag][key] = (year, event)
            classic_bases[name] = base_name
            assert f"mission_completed = {base_name}" in effect, name
            keys.update((name + "_title", name + "_desc"))
            continue
        key = name.removeprefix("rip_record_")
        assert key not in seen[tag], name
        seen[tag][key] = year
        calls[event] += 1
        body = event_blocks[event]
        assert "is_triggered_only = yes" in body
        redress, refusal = [opt for _, opt in keyed_blocks(body, "option")]
        currency, cost = re.search(r"add_(treasury|adm_power|dip_power|mil_power) = -(\d+)", redress).groups()
        assert f"{currency} = {cost}" in trigger and "trigger =" not in refusal
        for option in (redress, refusal):
            for province in re.findall(r"(?m)^\s*(\d+) = \{\s*$", option):
                assert f"limit = {{ {province} = {{ country_or_non_sovereign_subject_holds = ROOT }} }}" in option
        keys.update((name + "_title", name + "_desc", event + ".t", event + ".d", event + ".a", event + ".b"))

assert seen == expected and calls == Counter({key: 1 for key in event_blocks})
for tag, twins in seen_classic.items():
    for key, (year, event) in twins.items():
        assert seen[tag][key] == year, (tag, key, year)
        base_effect = named_block(named_block(missions, f"rip_record_{key}"), "effect")
        assert re.search(r"id = (rip_historical_record\.\d+)", base_effect)[1] == event, (tag, key, event)
        assert f"mission_completed = rip_record_{key}_classic" in base_effect, (tag, key)

for lang in ("english", "french", "german", "spanish"):
    loc = read(f"localisation/RIP_shared_ruthenian_historical_record_l_{lang}.yml")
    entries_loc = re.findall(r'^ (\S+):0 "([^"\n]+)"$', loc, re.M)
    entry_map = dict(entries_loc)
    assert len(entries_loc) == len(entry_map)
    assert keys | {"rip_record_unredressed", "desc_rip_record_unredressed"} == set(entry_map)
    for cname, bname in classic_bases.items():
        assert entry_map[f"{cname}_title"] == f"${bname}_title$", (lang, cname)
        assert entry_map[f"{cname}_desc"] == f"${bname}_desc$", (lang, cname)

if vanilla_root() is not None:
    files = mg.load_files(False)
    all_dlc = set()
    for txt in files.values():
        all_dlc.update(re.findall(r'has_dlc = "([^"]+)"', txt))
    grid_cases = (
        ("CRI (Winds of Change)", "CRI", None, "rip_record_kyiv_captives", "rip_record_kyiv_captives_classic"),
        ("CRI (classic)", "CRI", "Winds of Change", "rip_record_kyiv_captives_classic", "rip_record_kyiv_captives"),
        ("LIT (Lions of the North)", "LIT", None, "rip_record_volhynian_expulsion", "rip_record_volhynian_expulsion_classic"),
        ("LIT (classic)", "LIT", "Lions of the North", "rip_record_volhynian_expulsion_classic", "rip_record_volhynian_expulsion"),
    )
    for label, tag, lacks, active_m, inactive_m in grid_cases:
        placed = mg.layout(files, mg.Context(tag, all_dlc - ({lacks} if lacks else set())))
        assert active_m in placed, f"{label}: {active_m} not placed"
        assert inactive_m not in placed, f"{label}: {inactive_m} should not share screen with {active_m}"
        want_slot, want_row, want_parents = expected_ties[active_m]
        slot, row, req, _, _ = placed[active_m]
        assert (slot, row, req) == (want_slot, want_row, want_parents), (label, active_m, (slot, row, req))
        parent = want_parents[0]
        assert parent in placed, f"{label}: missing parent {parent}"
        p_slot, p_row, *_ = placed[parent]
        assert p_slot == slot and p_row == row - 1, (label, parent, (p_slot, p_row), (slot, row))

print(
    f"PASS: 13 dated, tag-specific missions (+{len(classic_bases)} DLC twins), "
    "13 distinct events, 26 options, grid ties and four catalogues"
)
