"""One-shot, token-verified migration from the pre-country event layout.

Run only on the old layout. Normal generation uses event_layout.layout instead.
"""
from pathlib import Path
import json
from event_layout import ROOT, layout
from audit_event_links import inventory, read, vanilla_root


def main():
    assert (ROOT / 'events/RIP.txt').exists(), 'Already migrated; use audit_event_links.py'
    vanilla = vanilla_root()
    assert vanilla
    original = inventory(ROOT)
    outputs, files = {}, {}
    for source in sorted((ROOT / 'events').glob('*.txt')):
        rel = source.relative_to(ROOT).as_posix()
        result = layout(rel, read(source))
        assert not set(result) & set(outputs), f'Destination collision: {source}'
        outputs.update(result)
        files[rel] = list(result)
    manifest = {'vanilla_filename_overrides': sorted(p.name for p in (ROOT / 'events').glob('*.txt')
                                                    if (vanilla / 'events' / p.name).exists()),
                'events': {eid: {k: v for k, v in row.items() if k != 'body'} for eid, row in original.items()},
                'files': files}
    (ROOT / 'tools/data/event_layout_manifest.json').write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    for path, text in outputs.items():
        (ROOT / path).write_text(text, encoding='utf-8', newline='\n')
    for source in files:
        if source not in outputs:
            (ROOT / source).unlink()
    current = inventory(ROOT)
    assert set(original) == set(current)
    assert all(original[e]['sha256_tokens'] == current[e]['sha256_tokens'] for e in original)
    # Active consumers: update exact event paths, preserving encoding and line endings.
    generators = {'build_regional_governments.py', 'build_church_support.py',
                  'build_hetman_authority.py', 'build_eparchy_timeline.py'}
    changed = []
    for directory in ('tests', 'tools', 'docs'):
        for path in (ROOT / directory).rglob('*'):
            if path.suffix not in ('.py', '.md', '.ps1', '.json') or not path.is_file():
                continue
            if path.name in generators | {'event_layout.py', 'migrate_event_files.py', 'event_layout_manifest.json'}:
                continue
            raw = path.read_bytes()
            updated = raw
            for old, destinations in files.items():
                if len(destinations) == 1:
                    updated = updated.replace(old.encode(), destinations[0].encode())
                    if directory == 'tests':
                        old_name = Path(old).name.encode()
                        new_name = Path(destinations[0]).name.encode()
                        for quote in (b'"', b"'"):
                            updated = updated.replace(quote + old_name + quote, quote + new_name + quote)
            if updated != raw:
                path.write_bytes(updated)
                changed.append(path.relative_to(ROOT).as_posix())
    print(f'Migrated {len(files)} -> {len(outputs)} files, preserved {len(current)} events; updated {len(changed)} consumers.')


if __name__ == '__main__':
    main()
