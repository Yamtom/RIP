"""Verify national ownership, dates and event links for the historical record."""
import re
from collections import Counter

from check_donor_mission_ports import parse_series_in_file
from clausewitz_testlib import keyed_blocks, named_block, read

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
event_blocks = dict((re.search(r"id = (rip_historical_record\.\d+)", block)[1], block)
                    for _, block in keyed_blocks(events, "country_event"))
calls = Counter()
seen = {tag: {} for tag in expected}
keys = set()
for _, slot, potential, entries in parse_series_in_file(path):
    (tag,) = re.findall(r"\btag = (\w+)", potential)
    for name, row, parents in entries:
        if tag == "CRI" and slot == 1:
            # Winds of Change uses column one through row 16 for its branching missions.
            assert row > 16, name
        trigger = named_block(named_block(missions, name), "trigger")
        key = name.removeprefix("rip_record_")
        assert key not in seen[tag], name
        seen[tag][key] = int(re.search(r"is_year = (\d+)", trigger)[1])
        effect = named_block(named_block(missions, name), "effect")
        event = re.search(r"id = (rip_historical_record\.\d+)", effect)[1]
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
for lang in ("english", "french", "german", "spanish"):
    loc = read(f"localisation/RIP_shared_ruthenian_historical_record_l_{lang}.yml")
    entries = re.findall(r'^ (\S+):0 "[^"\n]+"$', loc, re.M)
    assert len(entries) == len(set(entries))
    assert keys | {"rip_record_unredressed", "desc_rip_record_unredressed"} == set(entries)
print("PASS: 13 dated, tag-specific missions, 13 distinct events, 26 options and four catalogues")
