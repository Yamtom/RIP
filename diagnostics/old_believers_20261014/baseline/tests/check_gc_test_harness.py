"""Contracts for the manual laboratory; does not simulate the EU4 engine."""
import re
from clausewitz_testlib import ROOT, read
from check_religion_settlement import parse

event_path = 'events/RIP_GreekCatholicTest.txt'
effect_path = 'common/scripted_effects/rip_gc_test_effects.txt'
events = [dict(v) for k, v in parse(read(event_path)) if k == 'country_event']
assert len(events) == 10
assert {e['id'] for e in events} == {f'rip_gc_test.{n}' for n in range(1, 11)}
for event in events:
    assert event['is_triggered_only'] == 'yes'
    assert 'mean_time_to_happen' not in event and 'fire_only_once' not in event

# A test fixture must never be invoked by ordinary gameplay.
for directory in ('common', 'events', 'decisions', 'missions', 'interface'):
    for path in (ROOT / directory).rglob('*.txt'):
        if path.relative_to(ROOT).as_posix() in (event_path, effect_path):
            continue
        text = re.sub(r'#[^\n]*', '', path.read_bytes().decode('latin-1'))
        assert not re.search(r'\brip_gc_test[._]', text), str(path)

loc_path = ROOT / 'localisation/rip_gc_test_l_english.yml'
assert loc_path.read_bytes().startswith(b'\xef\xbb\xbf')
loc = loc_path.read_text(encoding='utf-8-sig')
keys = re.findall(r'^\s+(\S+):\d*\s+"', loc, re.M)
assert len(keys) == len(set(keys))
for key in re.findall(r'\b(?:title|desc|name)\s*=\s*(rip_gc_test\.[\w.]+)', read(event_path)):
    assert key in keys, key

raw_events = [v for k, v in parse(read(event_path)) if k == 'country_event']
by_id = {dict(e)['id']: e for e in raw_events}
hc_menu = next(e for e in raw_events if dict(e)['id'] == 'rip_gc_test.2')
hc_options = [v for k, v in hc_menu if k == 'option' and 'trigger' in dict(v)]
assert len(hc_options) == 5
for option, target in zip(hc_options, (0, .19, .2, .4, 1)):
    steps = [float(v) for k, v in option if k == 'add_patriarch_authority']
    assert steps == [-1, target]
    for initial in (0, .17, .6, 1):
        result = initial
        for amount in steps:
            result = max(0, min(1, result + amount))
        assert abs(result - target) < 1e-9

effects = dict(parse(read(effect_path)))
greek = dict(effects['rip_gc_test_greek_fixture'])
assert greek['clr_country_flag'].count('rip_church_gc_holy_see_gift_sent') == 1
for province, faith in (('280', 'greek_catholic'), ('2961', 'orthodox'), ('1952', 'catholic')):
    setup = dict(greek[province])
    assert setup['change_religion'] == faith
    assert all(setup[k] == 'ROOT' for k in ('cede_province', 'change_controller', 'add_core'))

# AI scenarios prepare inputs, leaving activation to the real monthly AI pulse.
ai = str(by_id['rip_gc_test.6']) + str(effects['rip_gc_test_ai_quiet'])
assert 'activate_' not in ai and 'ai_icons_effect' not in ai
assert 'rip_uzh_union_date_window' in str(by_id['rip_gc_test.5'])
assert 'rip_uzh_union_late_window' in str(by_id['rip_gc_test.5'])
assert 'rip_uzh_union_scheduled_fresh' in str(by_id['rip_gc_test.5'])
assert 'rip_uc_can_found_schools' in str(by_id['rip_gc_test.7'])
doc = read('docs/GREEK_CATHOLIC_MANUAL_QA.uk.md')
for number in range(1, 11):
    assert f'`event rip_gc_test.{number}`' in doc
assert '# 1. Інтерфейси' in doc and '# 2. Механіки' in doc
print('PASS: 10 manual-only events, localisation, HC boundaries, fixtures and checklist contracts. Runtime unverified.')
