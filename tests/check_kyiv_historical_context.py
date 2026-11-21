"""Guard dynasty preservation and synchronized Kyiv historical context."""
import re
from clausewitz_testlib import read, named_block

event = read('events/RIP_KIE_KIEmission.txt')
assert 'set_dynasty' not in event
assert event.count('name = M_UKR_Events.1.') == 7

def entries(path):
    return dict(re.findall(r'^ ([\w.]+):\d+ "(.*)"$', read(path), re.M))

english = entries('localisation/RIP_KIE_realm_l_english.yml')
anchors = {
    'M_UKR_Events.1.d': ('Gediminids', 'preserves the ruling dynasty'),
    'KIE_integrate_novgorod_desc': ('Mykhailo Olelkovych', '1470-1471', 'alternative-history'),
    'KIE_byzantine_relations_desc': ('Isidore', '1439', 'Florence'),
    'KIE_cossack_desc': ('1492', 'Dashkevych', '1533', 'alternative-history'),
    'kyiv_succession_history.4.d': ('1471', 'voivodeship'),
}
for key, words in anchors.items():
    assert all(word in english[key] for word in words), key
keys = set(anchors) | {k for k in english if k.startswith(('M_UKR_Events.1.', 'desc_UKR_', 'UKR_rurikovich', 'UKR_gedyminovich', 'UKR_jagiellon', 'KIE_dynasty', 'KIE_cossack', 'KIE_byzantine_relations', 'KIE_integrate_novgorod', 'kyiv_succession_history.4.'))}
for language in ('french', 'german', 'spanish'):
    fallback = entries(f'localisation/replace/RIP_KIE_content_l_{language}.yml')
    for key in keys:
        assert fallback[key] == english[key], (language, key)
for text in english.values():
    assert 'as do all Eastern European rulers' not in text
print('PASS: Kyiv historical context and dynasty preservation (static only)')

byz = named_block(read('missions/Kyiv_Missions.txt'), 'KIE_byzantine_relations')
trigger = named_block(byz, 'trigger')
alive = named_block(trigger, 'if')
assert 'exists = BYZ' in alive and 'alliance_with = BYZ' in alive
assert 'is_rival = root' in alive and 'modifier = insulted' in alive
dead = named_block(trigger, 'else')
assert 'advisor = theologian' in dead
kyiv = named_block(dead, '280')
assert 'owned_by = ROOT' in kyiv
assert 'has_building = temple' in kyiv and 'has_building = cathedral' in kyiv
assert '1453' not in trigger

diaspora = read('missions/zzzz_RuthenianDiaspora_Missions.txt')
from pathlib import Path

cells = set()
for group in re.findall(r'(?m)^(RIP_diaspora_missions_\d+) =', diaspora):
    series = named_block(diaspora, group)
    slot = int(re.search(r'\bslot = (\d+)', series)[1])
    for row in re.findall(r'\bposition = (\d+)', series):
        cell = (slot, int(row))
        assert cell not in cells, ('diaspora overlap', cell)
        cells.add(cell)
assert len(cells) == 15
for path in (Path(__file__).resolve().parents[1] / 'missions').glob('*.txt'):
    script = re.sub(r'#[^\n]*', '', path.read_text(encoding='utf-8-sig'))
    for key, value in re.findall(r'\b(slot|position)\s*=\s*(-?\d+)\b', script):
        assert int(value) >= 1 and (key != 'slot' or int(value) <= 5), (path, key, value)
print('PASS: Byzantine fallback, mission coordinates and diaspora layout')
