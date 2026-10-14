"""Native cultural choices, source preservation and rejection of a donor map."""
from pathlib import Path
import json
import sys
import tempfile

from clausewitz_testlib import ROOT, named_block, vanilla_root
sys.path.insert(0, str(ROOT / 'tools'))
import build_colonial_names as builder

data = builder.load_data()
assert len(data['regions']) * len(data['cultures']) == 44
fixture = ''.join(
    f'{region} = {{\n\tprovinces = {{ 1 2 3 }}\n\t# brace in a string: "}}"\n'
    '\tnames = { name = "COLONIAL_REGION_New_Root_GetName" }\n}\n'
    for region in data['regions'])
# Native cp1252 bytes and CRLF must survive, as must RNW and generic entries.
fixture = ('# Nouvelle-\xc9cosse\n' + fixture).replace('\n', '\r\n').encode('latin-1')
rendered = builder.render(fixture, data)
assert builder.strip_insertions(rendered.decode('latin-1')).encode('latin-1') == fixture
assert rendered.count(b'name = "RIP_COLONIAL_') == 44
assert builder.localization(data).startswith(b'\xef\xbb\xbf')
for region in data['regions']:
    block = named_block(rendered.decode('latin-1'), region)
    for culture, variants in data['cultures'].items():
        assert f'name = "{builder.key(region, culture)}"' in block
        for variant in variants:
            assert f'primary_culture = {variant}' in block

for damaged in (fixture.replace(b'colonial_alaska =', b'colonial_missing ='),
                fixture.replace(b'COLONIAL_REGION_New_Root_GetName', b'missing_fallback'),
                rendered):
    try:
        builder.render(damaged, data)
    except ValueError:
        pass
    else:
        raise AssertionError('Missing/duplicate/incompatible native input was accepted')

with tempfile.TemporaryDirectory(prefix='rip_colonial_contract_') as temporary:
    base = Path(temporary)
    (base / 'launcher-settings.json').write_text(json.dumps({'rawVersion': '1.30.3'}))
    output = base / 'output'
    try:
        builder.install(base, output)
    except ValueError:
        pass
    else:
        raise AssertionError('Donor 1.30 map accepted')
    assert not output.exists(), 'Rejected source must not change output files'

assert (ROOT / builder.LOC).read_bytes() == builder.localization(data)
assert (ROOT / builder.RELATIVE).exists(), 'Names are prepared but not connected'
vanilla = vanilla_root()
if vanilla:
    builder.install(vanilla, check=True)
else:
    print('SKIP: live native source comparison unavailable')
manifest = json.loads((ROOT / builder.MANIFEST).read_text(encoding='utf-8'))
assert manifest['game_version'] in ('1.37.5', '1.37.5.0')
assert manifest['choices'] == 44 and manifest['native_bytes_preserved'] is True
print('COLONIAL NAMES PASS: 44 choices, 9 culture keys, all 11 American regions; source and rejection checks.')
