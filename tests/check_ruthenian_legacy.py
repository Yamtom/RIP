"""Static dependency and geography checks for the restored 32-mission tree."""
from pathlib import Path
import re
import sys

from clausewitz_testlib import ROOT, vanilla_root, named_block, _mask_comments_and_strings

sys.path.insert(0, str(ROOT / 'tools'))
from build_ruthenian_legacy_localisation import MISSIONS, render

VANILLA = vanilla_root()
assert VANILLA, 'Install EU4 1.37.5 or set EU4_DIR for dependency checks'


def read(path):
    return path.read_text(encoding='utf-8-sig', errors='replace')


def source(directory, suffix):
    return '\n'.join(read(p) for base in (VANILLA, ROOT)
                     for p in (base / directory).glob('*' + suffix))


s = read(ROOT / 'missions/Ruthenian_Missions.txt')
mission_ids = set(re.findall(r'(?m)^\s*(ukr_(?!missions_)\w+)\s*=\s*\{', s))
assert len(mission_ids) == 32 and mission_ids == set(MISSIONS), mission_ids ^ set(MISSIONS)
for dependencies in re.findall(r'required_missions\s*=\s*\{([^}]+)\}', s):
    assert set(dependencies.split()) <= mission_ids, dependencies
pending = {}
for mission in mission_ids:
    body = named_block(s, mission)
    dependencies = re.search(r'required_missions\s*=\s*\{([^}]*)\}', body)
    pending[mission] = set(dependencies[1].split())
resolved = set()
while pending:
    available = {key for key, dependencies in pending.items() if dependencies <= resolved}
    assert available, ('mission dependency cycle', pending)
    resolved.update(available)
    pending = {key: dependencies for key, dependencies in pending.items() if key not in available}

for language in ('english', 'french', 'german', 'spanish'):
    path = ROOT / 'localisation' / f'Legacy_of_Rus_l_{language}.yml'
    assert path.read_bytes() == render(language), path
    new_keys = set(re.findall(r'^ (\S+):', render(language).decode('utf-8'), re.M))
    for other in (ROOT / 'localisation').rglob(f'*_l_{language}.yml'):
        if other != path:
            keys = set(re.findall(r'^\s*(\S+):\d*\s', read(other), re.M))
            assert not new_keys.intersection(keys), (other, new_keys.intersection(keys))

# Legacy rows must not share coordinates with any currently shipped RIP tree.
positions = {int(x) for x in re.findall(r'\bposition\s*=\s*(\d+)', s)}
assert positions == set(range(24, 32))
for path in (ROOT / 'missions').glob('*.txt'):
    if path.name != 'Ruthenian_Missions.txt':
        assert not positions.intersection(map(int, re.findall(r'\bposition\s*=\s*(\d+)', read(path)))), path

gfx = source('interface', '.gfx')
assert 'name = "DIPLOMACY_eventPicture"' in gfx
for icon in set(re.findall(r'\bicon\s*=\s*(\w+)', s)):
    definition = re.search(r'name\s*=\s*"' + re.escape(icon) + r'"\s+texturefile\s*=\s*"([^"]+)"', gfx)
    assert definition, ('missing icon', icon)
    relative = definition[1].replace('\\', '/').replace('//', '/')
    assert any((base / relative).exists() for base in (ROOT, VANILLA)), relative
for icon in ('petro_mohyla', 'mission_ukr_magdeburg_laws'):
    assert (ROOT / 'gfx/interface/missions' / (icon + '.dds')).read_bytes().startswith(b'DDS ')

events = source('events', '.txt')
calls = set(re.findall(r'country_event\s*=\s*\{\s*id\s*=\s*(\S+)', s))
assert calls == {f'flavor_ukr_legacy_of_rus.{n}' for n in range(1, 5)}
for event in calls:
    assert len(re.findall(r'(?m)^\s*id\s*=\s*' + re.escape(event) + r'\s*$', events)) == 1, event
    body = read(ROOT / 'events/RIP_shared_ruthenian_LegacyOfRus.txt')
    assert f'{event}.t' in body and f'{event}.d' in body

modifiers = source('common/event_modifiers', '.txt')
for modifier in re.findall(r'add_(?:country|province)_modifier\s*=\s*\{\s*name\s*=\s*"?(\w+)', s):
    assert re.search(r'(?m)^\s*' + re.escape(modifier) + r'\s*=\s*\{', modifiers), modifier
opinions = source('common/opinion_modifiers', '.txt')
assert re.search(r'(?m)^ruthenian_swedish_alliance\s*=', opinions)

# These are province identities, not random_list weights (10, 40 and 50).
expected = {
    149: 'Edirne', 151: 'Constantinople', 162: 'Zemplen', 260: 'Lublin',
    275: 'Polotsk', 280: 'Kiev', 282: 'Yedisan', 283: 'Zaporozhia',
    284: 'Crimea', 285: 'Kaffa', 286: 'Azow', 287: 'Kouban',
    289: 'Chernigov', 290: 'Poltava', 295: 'Moskva', 310: 'Novgorod',
    1945: 'Novgorod-Seversky', 1952: 'Maramaros', 1974: 'Yedishkul',
    2406: 'Ingil', 2407: 'Pereyaslav', 2410: 'Theodoro', 2411: 'Mansur',
    2412: 'Kyzyl-Yar', 2447: 'Mantrega', 2959: 'Tarnow', 2960: 'Sadecki',
    2962: 'Rowne', 4244: 'Starodub', 4543: 'Rylsk', 4705: 'Gumulcine',
    4706: 'Tolcu', 4779: 'Gallipoli',
}
masked = _mask_comments_and_strings(s)
used = {int(a or b) for a, b in re.findall(r'(?m)^\s*(\d+)\s*=\s*\{|province_id\s*=\s*(\d+)', masked)} - {10, 40, 50}
assert used == set(expected), used ^ set(expected)
for province, name in expected.items():
    assert (VANILLA / 'history/provinces' / f'{province} - {name}.txt').exists(), (province, name)
for suffix, filename in (('_area', 'area.txt'), ('_region', 'region.txt')):
    path = ROOT / 'map' / filename
    geography = read(path if path.exists() else VANILLA / 'map' / filename)
    for key in set(re.findall(r'\b\w+' + suffix + r'\b', s)):
        assert re.search(r'(?m)^\s*' + key + r'\s*=', geography), key

for mission in ('ukr_barocco', 'ukr_second_jerusalem'):
    assert 'has_great_project' not in named_block(s, mission)
assert 'OR = { owned_by = MOS owned_by = RUS }' in named_block(s, 'ukr_defeat_muscowy')
assert 'rename_capital = "Samar"' not in s  # 2411 is Mansur in Crimea, not Samar.
sloboda = named_block(s, 'ukr_sloboda_ukraine')
assert '4543 = {' in sloboda and 'province_id = 4543' in sloboda
assert '2411' not in sloboda  # Mansur is unrelated to the Sloboda frontier.
print(f'PASS: 32 missions, {len(expected)} province IDs, 4 events, icons, rewards and four language files')
