"""Local Uzhhorod foundation and independent UZH institutional sequel."""
import re
from clausewitz_testlib import read, named_block, keyed_blocks, normalized

t = normalized(read('common/scripted_triggers/rip_uzh_union_triggers.txt'))
for guard in ('province_id = 1952', 'is_year = 1646', 'controlled_by = owner',
              'NOT = { has_missionary = yes }', 'religion = orthodox',
              'overlord = { religion = catholic }',
              'any_known_country = { religion = catholic alliance_with = PREV }'):
    assert guard in t, guard
assert 'tag = UZH' not in t and 'is_core' not in t
event = read('events/RIP_UzhLocalUnion.txt')
assert 'immediate = { set_province_flag = rip_uzh_union_answered }' in event
assert 'NOT = { has_province_flag = rip_uzh_union_answered }' in event
options = [b for _, b in keyed_blocks(event, 'option')]
assert len(options) == 2
assert 'trigger = { rip_uzh_local_union_possible = yes }' in options[0]
assert 'limit = { rip_uzh_local_union_possible = yes }' in options[0]
assert 'enable_religion = greek_catholic' in options[0]
assert 'set_province_flag = rip_uzh_union_accepted' in options[0]
assert 'set_country_flag = rip_church_supports_union' in options[0]
assert 'change_religion = greek_catholic' in options[0]
assert 'change_religion' not in named_block(options[0], 'owner')
assert 'trigger =' not in options[1] and 'change_religion' not in options[1]
assert 'add_government_reform' not in event and 'add_country_modifier' not in event
sequel = next(b for _, b in keyed_blocks(read('events/Uzh.txt'), 'country_event')
              if re.search(r'id\s*=\s*uzh\.51\b', b))
gate = normalized(named_block(sequel, 'trigger'))
for guard in ('tag = UZH', 'is_subject = no', 'owns = 1952',
              'controlled_by = ROOT', 'has_province_flag = rip_uzh_union_accepted'):
    assert guard in gate, guard
assert 'add_government_reform = uzh_union_synod_reform' in sequel
loc = read('localisation/rip_uzh_local_union_l_english.yml')
for suffix in ('t', 'd', 'a', 'b'):
    assert f' rip_uzh_union.1.{suffix}:0 ' in loc
assert '63 priests' in loc and '24 April 1646' in loc
assert 'capital = 1952' in read('history/countries/UZH - Huszt.txt')
print('PASS: territory, patronage, one-shot outcomes, province-only conversion, independent UZH sequel and historical localisation')
