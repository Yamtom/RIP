"""Static chronology and regional-name regression checks; no runtime claim."""
import re

from clausewitz_testlib import ROOT, keyed_blocks, named_block, read
from check_uzh_local_union import get, parse, walk, window_true


def body(text, name):
    return parse(named_block(text, name))[0][1]


def dates(items):
    result = []
    for key, value in items:
        if key == 'is_year':
            result.append((key, value))
        elif key in ('NOT', 'OR', 'AND'):
            nested = dates(value)
            if nested:
                result.append((key, nested))
    return result


def check_window(trigger, first, last=1821):
    for year in range(1444, 1822):
        assert window_true(dates(trigger), year, 0) == (first <= year <= last), year


missions = read('missions/Zakarpatta_Missions.txt')
events = read('events/RIP_UZH_Uzh.txt')
check_window(get(body(missions, 'uz_union_dilemma'), 'trigger')[0], 1646)

chain = [
    ('uzh_srem_metropolis', 3, 1713, 'uzh_pannonian_frontier', 'uzh_frontier_prepared'),
    ('uzh_banat_colonization', 4, 1718, 'uzh_srem_metropolis', 'uzh_srem_metropolis_consecrated'),
    ('uzh_backa_settlements', 5, 1751, 'uzh_banat_colonization', 'uzh_banat_settled'),
]
for name, position, year, predecessor, flag in chain:
    mission = body(missions, name)
    assert get(mission, 'position') == [str(position)]
    assert re.search(r'required_missions\s*=\s*\{\s*' + predecessor + r'\s*\}', named_block(missions, name))
    trigger = get(mission, 'trigger')[0]
    check_window(trigger, year)
    assert [v for k, v in walk(trigger) if k == 'has_country_flag'] == [flag], name
    assert f'set_country_flag = {flag}' in named_block(missions, predecessor)
assert re.search(r'required_missions\s*=\s*\{\s*uzh_backa_settlements\s*\}', named_block(missions, 'uzh_pannonian_expansion'))

for eid, first, last in [('uzh.52', 1703, 1711), ('uzh.53', 1770, 1821)]:
    candidates = [parse(block)[0][1] for _, block in keyed_blocks(events, 'country_event')]
    definitions = [b for b in candidates if get(b, 'id') == [eid] and get(b, 'title')]
    assert len(definitions) == 1
    event = definitions[0]
    trigger = get(event, 'trigger')[0]
    check_window(trigger, first, last)
    assert get(event, 'fire_only_once') == ['yes']
    if eid == 'uzh.52':
        assert get(trigger, 'exists') == ['HAB']
        assert int(get(get(event, 'mean_time_to_happen')[0], 'months')[0]) <= 36
    else:
        assert get(trigger, 'has_institution') == ['enlightenment']

def entries(path):
    return dict(re.findall(r'^ ([\w.]+):\d+ "(.*)"$', path.read_text(encoding='utf-8-sig'), re.M))

english = entries(ROOT / 'localisation/RIP_UZH_realm_l_english.yml')
assert english['UZH_Zakarpattia_Name'] == "Carpathian Rus'"
assert 'Dukhnovych' not in ' '.join(english[k] for k in ('uzh.53.t', 'uzh.53.d', 'uz_duchnovych_awakening'))
for key in ('uz_huszt_rename_desc', 'uz_mukachevo_autonomy_desc', 'uz_national_revival_desc', 'uz_union_dilemma_desc'):
    assert all(city in english[key] for city in ('Khust', 'Mukachevo', 'Uzhhorod')), key
keys = ['UZH_Zakarpattia_Name', 'UZH_laws', 'UZH_roads', 'uzh.53.t', 'uzh.53.d',
        'uz_duchnovych_awakening', 'uz_zakarpattia_realm_title', 'uz_union_dilemma_desc',
        'uzh_srem_metropolis_desc', 'uzh_banat_colonization_desc', 'uzh_backa_settlements_desc']
for path in (ROOT / 'localisation/replace').glob('RIP_UZH_content_l_*.yml'):
    fallback = entries(path)
    assert all(fallback[k] == english[k] for k in keys), path
print('PASS: UZH date boundaries 1444-1821, mission dependencies/flags, event windows, regional names and fallbacks')
