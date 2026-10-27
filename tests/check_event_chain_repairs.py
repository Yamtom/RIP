"""Source contracts for the Ruina, Hetmanate and Cossack incident repairs."""
from pathlib import Path
import re
from clausewitz_testlib import keyed_blocks, named_block, normalized

ROOT = Path(__file__).resolve().parents[1]


def event(filename, event_id):
    text = (ROOT / 'events' / filename).read_text(encoding='utf-8')
    matches = [block for _, block in keyed_blocks(text, 'country_event')
               if re.search(r'^\s*title\s*=', block, re.M)
               and re.search(r'^\s*id\s*=\s*(\S+)', block, re.M).group(1) == event_id]
    assert len(matches) == 1, event_id
    return matches[0]


ruina = event('RIP_HET_Ruina.txt', 'ruina_events.2')
bridge = named_block(named_block(ruina, 'immediate'), 'if')
assert 'tag = CHR' in named_block(bridge, 'limit')
assert 'set_country_flag = chernihiv_ruina_resolved' in bridge
assert 'id = chr_flavor.18' in bridge
choice = event('RIP_CHR_Chernihiv.txt', 'chr_flavor.18')
assert 'NOT = { has_country_flag = chr_ruina_path_selected }' in normalized(named_block(choice, 'trigger'))

count = 0
for filename, event_id, areas in [
    ('RIP_HET_HetmanateFlavor.txt', 'het_flavor.8', ['east_dniepr_area', 'west_dniepr_area']),
    ('RIP_HET_HetmanateEnhanced.txt', 'het_enhanced.3', ['east_dniepr_area', 'west_dniepr_area']),
    ('RIP_HET_HetmanateMoldovanExpansion.txt', 'het_moldova.3', ['moldavia_area']),
]:
    for area in areas:
        for _, block in keyed_blocks(event(filename, event_id), area):
            assert 'owned_by = ROOT' in named_block(block, 'limit'), (event_id, area)
            count += 1
assert count == 6

reckoning = event('RIP_ZAZ_ZaporizhiaFlavor.txt', 'zaz_flavor.18')
trigger = normalized(named_block(reckoning, 'trigger'))
assert 'fire_only_once = yes' in reckoning
assert 'is_year = 1770' in trigger and 'NOT = { is_year = 1780 }' in trigger
assert 'exists = RUS' in trigger
assert 'OR = { war_with = RUS is_subject_of = RUS }' in trigger
assert 'NOT = { has_country_flag = zaz_final_reckoning_resolved }' in trigger
assert 'set_country_flag = zaz_final_reckoning_resolved' in named_block(reckoning, 'immediate')
for bypass in ['has_institution', 'current_age', 'army_tradition', 'controlled_by']:
    assert bypass not in trigger

incident = event('RIP_shared_cossack_CossackRevolts.txt', 'zaz.4')
assert 'declare_war_with_cb' not in incident
guard = normalized(named_block(named_block(incident, 'if'), 'limit'))
for required in ['tag = TUR', 'exists = PLC', 'is_subject = no',
                 'PLC = { is_subject = no }', 'NOT = { war_with = PLC }',
                 'NOT = { truce_with = PLC }', 'NOT = { alliance_with = PLC }',
                 'NOT = { has_casus_belli = { target = PLC type = cb_insult } }']:
    assert required in guard, required
assert 'add_casus_belli = { target = PLC type = cb_insult months = 12 }' in normalized(incident)
print('PASS: Ruina bridge, six owned-area effects, one-shot Russian threat, guarded optional war CB')
