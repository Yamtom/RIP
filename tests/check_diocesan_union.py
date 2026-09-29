"""Source contracts for the Catholic patron's bounded provincial union path."""
import re
from clausewitz_testlib import read, named_block, keyed_blocks, normalized, ROOT

triggers = read('common/scripted_triggers/rip_diocesan_union_triggers.txt')
decisions = read('decisions/RIP_DiocesanUnion.txt')
events = read('events/RIP_DiocesanUnion.txt')

patron = normalized(named_block(triggers, 'rip_du_catholic_patron'))
assert 'religion = catholic' in patron
assert 'has_country_flag = rip_church_supports_union' in patron
assert 'any_owned_province = { religion = greek_catholic }' in patron
candidate = normalized(named_block(triggers, 'rip_du_eligible_diocese'))
for guard in ('religion = orthodox', 'is_core = owner', 'controlled_by = owner',
              'NOT = { has_missionary = yes }',
              'NOT = { has_province_modifier = resistance_to_greek_catholic_spread }',
              'had_province_flag = { flag = rip_du_approached days = 3650 }'):
    assert guard in candidate, guard
assert 'rip_du_historical_seat = yes' in candidate
seat = normalized(named_block(triggers, 'rip_du_historical_seat'))
for pid, year in (('277', '1596'), ('278', '1596'), ('279', '1596'), ('4538', '1596'),
                  ('2424', '1691'), ('2961', '1700')):
    assert f'province_id = {pid}' in seat and f'is_year = {year}' in seat, pid
assert 'province_id = 1952' not in seat  # Mukachevo keeps its own 1646 chain
for pid in ('277', '278', '279', '4538', '2424', '2961'):
    assert f'province_id = {pid}' in normalized(events), pid
assert 'ROOT' not in candidate  # Must work in both country and province ROOT.
can = normalized(named_block(triggers, 'rip_du_can_negotiate'))
assert 'had_country_flag = { flag = rip_du_negotiated days = 1825 }' in can
assert 'any_owned_province = { rip_du_eligible_diocese = yes }' in can
selection = named_block(decisions, 'random_owned_province')
assert normalized(named_block(selection, 'limit')) == 'limit = { rip_du_eligible_diocese = yes }'
assert decisions.index('set_country_flag = rip_du_negotiated') < decisions.index('random_owned_province')
assert 'id = rip_diocesan_union.1' in selection

definitions = {re.search(r'id\s*=\s*(\S+)', b)[1]: b
               for _, b in keyed_blocks(events, 'province_event') if 'title =' in b}
assert set(definitions) == {f'rip_diocesan_union.{i}' for i in (1, 2, 3)}
assert all('is_triggered_only = yes' in b for b in definitions.values())
offer = definitions['rip_diocesan_union.1']
options = [b for _, b in keyed_blocks(offer, 'option')]
assert len(options) == 2
guard = normalized(named_block(options[0], 'trigger')).split('= ', 1)[1]
execution_guard = normalized(named_block(options[0], 'limit')).split('= ', 1)[1]
assert guard == execution_guard
assert 'owned_by = FROM' in guard and 'rip_du_catholic_patron = yes' in guard
assert 'dip_power = 50 years_of_income = 0.25' in guard
assert 'trigger =' not in options[1]  # Always possible to dismiss a stale offer.
assert 'add_dip_power = -50 add_years_of_income = -0.25' in options[0]
assert options[0].index('add_dip_power') < options[0].index('random_list')
accepted = named_block(options[0], '60')
refused = named_block(options[0], '40')
assert 'change_religion = greek_catholic' in accepted
assert 'add_local_autonomy = 10' in accepted and 'duration = 7300' in accepted
assert 'change_religion' not in refused and 'duration = 3650' in refused
assert events.count('change_religion =') == 1
assert 'country_event' not in events and 'save_event_target_as' not in events
assert 'create_center_of_reformation' not in events
for outcome in (2, 3):
    assert f'id = rip_diocesan_union.{outcome}' in options[0]
    assert 'change_religion' not in definitions[f'rip_diocesan_union.{outcome}']
loc_path = ROOT / 'localisation/rip_diocesan_union_l_english.yml'
assert loc_path.read_bytes().startswith(b'\xef\xbb\xbf')
loc = loc_path.read_text(encoding='utf-8-sig')
for key in re.findall(r'(?:title|desc|name)\s*=\s*(rip_diocesan_union\.\d+\.[a-z])', events):
    assert f' {key}:0 ' in loc, key
assert 'local_missionary_strength = -1' in read('common/event_modifiers/rip_diocesan_union_modifiers.txt')
print('PASS: Catholic patron, symmetric targeting, cooldowns, stale-owner/resource guards, paid acceptance/refusal and localisation')
