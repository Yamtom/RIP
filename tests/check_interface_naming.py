"""Check the byte-preserving interface migration and custom GUI binding coverage."""
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from audit_diplomacy_history import province_tree
from audit_country_history import read

manifest = json.loads((ROOT / 'docs/data/interface_rename_manifest.json').read_text())
fixed = {'countrygovernmentview.gui', 'countryreligionview.gui', 'provinceview.gui', 'parliament.gui'}
errors = []
for row in manifest:
    old, new = ROOT/'interface'/row['old'], ROOT/'interface'/row['new']
    if old.exists() or not new.exists():
        errors.append('Migration path mismatch: '+row['old'])
    elif hashlib.sha256(new.read_bytes()).hexdigest() != row['sha256']:
        errors.append('Migration changed engine content: '+row['new'])
for path in (ROOT / 'interface').iterdir():
    if path.suffix in ('.gui', '.gfx') and path.name not in fixed:
        # Files overriding lowercase vanilla sprites (e.g. countryview.gfx, provinceview.gfx)
        # require a lowercase `zz_` prefix so EU4's ASCII load order applies them last.
        if not re.fullmatch(r'(?:zz_)?RIP_(?:[A-Z0-9]{3}|shared)_[a-z0-9_]+\.(?:gui|gfx)',path.name):
            errors.append('Noncanonical name: '+path.name)
for name in fixed:
    if not (ROOT/'interface'/name).is_file():
        errors.append('Missing exact-filename vanilla override: '+name)
sprites = defaultdict(list)
for path in (ROOT/'interface').glob('*.gfx'):
    for _, entries in province_tree(read(path)):
        if not isinstance(entries,list): continue
        for _, definition in entries:
            if isinstance(definition,list):
                name=dict(definition).get('name','').strip('"')
                if name: sprites[name].append(path.name)
errors += ['Duplicate sprite: '+key for key,files in sprites.items() if len(files)>1]
bindings=set()
for p in (ROOT/'common/custom_gui').glob('*.txt'):
    bindings.update(re.findall(r'\bname\s*=\s*"?([\w]+)',read(p)))
def inspect(items,path):
    for kind, val in items:
        if not isinstance(val,list):continue
        d=dict(val)
        if d.get('scripted')=='yes':
            name=d.get('name','').strip('"')
            if name not in bindings:errors.append(f'{path.name}: unbound scripted control {name}')
        inspect(val,path)
for p in (ROOT/'interface').glob('*.gui'):inspect(province_tree(read(p)),p)
if errors:raise SystemExit('\n'.join(errors))
print(f'PASS: {len(manifest)} byte-preserving renames, 4 native filenames, {len(sprites)} unique sprites, scripted binding coverage')
