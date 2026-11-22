"""Check the Zaporozhian Rada, raid destinations and diplomatic successors."""

import re

from clausewitz_testlib import keyed_blocks, named_block, normalized, read


missions = read("missions/Zaporozhie_Missions.txt")
events = {
    re.search(r"id = ([\w.]+)", block)[1]: block
    for _, block in keyed_blocks(read("events/RIP_ZAZ_ZAZmission.txt"), "country_event")
    if "title = " in block
}


def field(mission, name):
    return normalized(named_block(named_block(missions, mission), name))


for mission, event, city in (
    ("ZAZ_saratov", "zaz_flavor_m_3.2", "303"),
    ("ZAZ_istanbul", "zaz_flavor_m_3.3", "151"),
):
    assert f"{city} = {{" in field(mission, "trigger")
    assert event in field(mission, "effect")
    options = list(keyed_blocks(events[event], "option"))
    assert len(options) == 3
    for _, option in options:
        # an ambush occupies a province only while its owner is at war with ROOT
        assert re.findall(r"(\d+) = \{\s*if = \{\s*limit = \{\s*owner = \{\s*war_with = ROOT\s*\}\s*\}\s*change_controller", option) == [city]
        assert option.count("change_controller") == 1

assert field("ZAZ_finally", "required_missions") == "required_missions = { ZAZ_proper }"
assert "zaz_flavor_m_3.1" in field("ZAZ_finally", "effect")
assert "change_controller" not in events["zaz_flavor_m_3.1"]

for mission, primary, successor in (
    ("ZAZ_ally_tur", "TUR", "RUM"),
    ("ZAZ_ally_tartar", "GOL", "GLH"),
    ("ZAZ_ally_pol", "PLC", "POL"),
    ("ZAZ_ally_rus", "RUS", "MOS"),
):
    trigger = field(mission, "trigger")
    effect = field(mission, "effect")
    for tag in (primary, successor):
        assert f"zaz_rada_partner = {{ partner = {tag} }}" in trigger
    assert f"limit = {{ zaz_rada_partner = {{ partner = {primary} }} }} create_alliance = {primary}" in effect
    assert f"else = {{ create_alliance = {successor} }}" in effect

assert "partner = CRI" in field("ZAZ_ally_crimea", "trigger")
assert "create_alliance = CRI" in field("ZAZ_ally_crimea", "effect")
assert "alliance_with = CRI" in field("ZAZ_perekop_trade", "trigger")
for mission in ("ZAZ_POL_politics", "ZAZ_POL_politics_2"):
    assert "OR = { alliance_with = PLC alliance_with = POL }" in field(mission, "trigger")
assert field("ZAZ_POL_cri", "effect").count("owned_by = CRI") == 3
independent = field("ZAZ_only_zaz", "trigger")
assert "is_subject = no" in independent and "army_size_percentage" in independent
assert all(term not in independent for term in ("exists", "opinion", "alliance_with"))
print("ZAZ Rada, raids, alliances and Sejm contracts passed.")
