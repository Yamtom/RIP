"""1771 Mukachevo bull, 1774 Greek Catholic name and the un-chained Zamosc synod."""
import re
from clausewitz_testlib import read, named_block, keyed_blocks, normalized

events = read('events/RIP_HabsburgGreekCatholic.txt')
blocks = {re.search(r'id\s*=\s*(rip_hgc\.\d+)', b).group(1): b for _, b in keyed_blocks(events, 'country_event')}
assert set(blocks) == {'rip_hgc.1', 'rip_hgc.2'}, sorted(blocks)

bull = normalized(named_block(blocks['rip_hgc.1'], 'trigger'))
for guard in ('is_year = 1771', 'NOT = { tag = UZH }', 'owns = 1952',
              '1952 = { religion = greek_catholic }',
              'NOT = { has_country_flag = rip_hgc_mukachevo_bull }'):
    assert guard in bull, guard
name = normalized(named_block(blocks['rip_hgc.2'], 'trigger'))
for guard in ('is_year = 1774', 'tag = AUS', 'has_country_flag = rip_hgc_mukachevo_bull',
              'any_owned_province = { religion = greek_catholic }',
              'NOT = { has_country_flag = rip_hgc_greek_catholic_name }'):
    assert guard in name, guard
for eid, block in blocks.items():
    assert 'is_triggered_only' not in block and 'mean_time_to_happen' in block, eid
    assert len(list(keyed_blocks(block, 'option'))) == 2, eid
    assert 'change_religion' not in block, eid   # no faith is changed by either event
# The bull must not touch the UZH road: no reform, no government change.
assert 'add_government_reform' not in events and 'change_government' not in events

loc = read('localisation/rip_habsburg_greek_catholic_l_english.yml')
for eid in blocks:
    for suffix in ('t', 'd', 'a', 'b'):
        assert f' {eid}.{suffix}:0 ' in loc, (eid, suffix)
assert '19 September 1771' in loc and 'Eximia regalium' in loc and '1774' in loc and 'Barbareum' in loc

# Zamosc is reachable for every Greek Catholic state, not only via the Brest chain.
zamosc = next(b for _, b in keyed_blocks(read('events/UniateChurch.txt'), 'country_event')
              if re.search(r'id\s*=\s*uniate_church\.5\b', b))
gate = normalized(named_block(zamosc, 'trigger'))
assert 'has_country_flag = pursuing_uniate_union' in gate and 'religion = greek_catholic' in gate
assert 'is_year = 1710' in gate and 'NOT = { is_year = 1750 }' in gate
print('PASS: 1771 bull, 1774 name and seminary, one-shot flags, no faith change, Zamosc reachable for every Greek Catholic state')
