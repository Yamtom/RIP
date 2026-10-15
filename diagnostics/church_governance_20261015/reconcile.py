"""Reinstall the user's explicitly confirmed separate-confession model."""
import hashlib
import json
from pathlib import Path

here = Path(__file__).resolve().parent
manifest = json.loads((here / 'deployment_manifest.json').read_text(encoding='utf-8'))
source = Path(manifest['source']).resolve()
target = Path(manifest['target']).resolve()
backup = here / 'backup' / 'before_confirmed_reinstall'
results = []
for row in manifest['files']:
    src = (source / row['path']).resolve()
    dst = (target / row['path']).resolve()
    assert src.is_relative_to(source) and dst.is_relative_to(target)
    payload = src.read_bytes()
    old = dst.read_bytes() if dst.exists() else None
    if old != payload:
        saved = backup / row['path']
        assert not saved.exists(), saved
        saved.parent.mkdir(parents=True, exist_ok=True)
        if old is not None:
            saved.write_bytes(old)
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(payload)
    assert dst.read_bytes() == payload, dst
    results.append({'path': row['path'], 'sha256': hashlib.sha256(payload).hexdigest()})
(here / 'confirmed_install.json').write_text(json.dumps(results, indent=2) + '\n', encoding='utf-8')
print(f'PASS: {len(results)} installed files verified; replaced files backed up.')
