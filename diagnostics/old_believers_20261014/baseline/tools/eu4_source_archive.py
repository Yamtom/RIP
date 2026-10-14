"""Preserve read-only EU4 text donors and compare them with a target installation.

No executable, user settings, saves, credentials or binary game assets are copied.
Source files are never modified. An existing archive is verified, not overwritten.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tests'))
from clausewitz_testlib import vanilla_version

DATA_DIRS = ('common', 'events', 'decisions', 'missions', 'history',
             'localisation', 'customizable_localization', 'map', 'interface')
TEXT_SUFFIXES = {'.txt', '.lua', '.csv', '.yml', '.json', '.gui', '.gfx', '.map'}
ROOT_FILES = ('launcher-settings.json', 'checksum_manifest.txt')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sources(root):
    for name in ROOT_FILES:
        if (root / name).is_file():
            yield root / name
    for folder in DATA_DIRS:
        base = root / folder
        if base.is_dir():
            for path in sorted(base.rglob('*')):
                if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
                    yield path


def verify(archive):
    data = json.loads((archive / 'manifest.json').read_text(encoding='utf-8'))
    failures = [item['path'] for item in data['files']
                if not (archive / item['path']).is_file()
                or digest(archive / item['path']) != item['sha256']]
    if failures:
        raise ValueError('Archive verification failed: ' + ', '.join(failures[:10]))
    return data


def capture(source, output, expected):
    source, output = source.resolve(), output.resolve()
    if output == source or source in output.parents:
        raise ValueError('Archive must be outside the source installation')
    version = vanilla_version(source)
    if version != expected:
        raise ValueError(f'Expected {expected}, found {version!r}; source not copied')
    if output.exists():
        data = verify(output)
        if data['game_version'] != expected:
            raise ValueError('Existing archive belongs to a different version')
        print(f"VERIFIED existing archive: {len(data['files'])} files, {expected}")
        return
    output.mkdir(parents=True)
    files = []
    for path in sources(source):
        relative = path.relative_to(source)
        dest = output / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        before = digest(path)
        shutil.copy2(path, dest)
        if digest(dest) != before or digest(path) != before:
            raise ValueError(f'Source changed while copying: {relative}')
        files.append({'path': relative.as_posix(), 'sha256': before, 'bytes': dest.stat().st_size})
    data = {
        'schema': 1, 'created_utc': datetime.now(timezone.utc).isoformat(),
        'source': str(source), 'game_version': version,
        'provenance': 'Installed game; launcher version recorded, not a Steam depot attestation',
        'dependency_families': list(DATA_DIRS),
        'excluded': ['executables', 'binary assets', 'DLC archives', 'settings', 'logs', 'saves'],
        'files': files,
    }
    (output / 'manifest.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    verify(output)
    print(f"CAPTURED AND VERIFIED {len(files)} files, {sum(f['bytes'] for f in files):,} bytes, EU4 {version}")
    print(output / 'manifest.json')


def compare(donor, target, output):
    old = verify(donor)
    version = vanilla_version(target)
    if version not in ('1.37.5', '1.37.5.0'):
        raise ValueError(f'Comparison target must be 1.37.5, found {version!r}')
    changes = []
    for item in old['files']:
        relative = item['path']
        current = target / relative
        status = 'absent_at_same_path' if not current.exists() else (
            'identical' if digest(current) == item['sha256'] else 'changed')
        changes.append({'path': relative, 'status': status})
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({
        'donor_version': old['game_version'], 'target_version': version,
        'note': 'A missing filename does not prove its events were removed; compare IDs and callers.',
        'files': changes,
    }, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('COMPARISON:', output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    cap = sub.add_parser('capture')
    cap.add_argument('--source', type=Path, required=True)
    cap.add_argument('--output', type=Path, required=True)
    cap.add_argument('--expect-version', required=True)
    check = sub.add_parser('verify')
    check.add_argument('archive', type=Path)
    cmp = sub.add_parser('compare')
    cmp.add_argument('--donor', type=Path, required=True)
    cmp.add_argument('--target', type=Path, required=True)
    cmp.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.command == 'capture':
        capture(args.source, args.output, args.expect_version)
    elif args.command == 'verify':
        data = verify(args.archive)
        print(f"VERIFIED: {len(data['files'])} files, EU4 {data['game_version']}")
    else:
        compare(args.donor, args.target, args.output)


if __name__ == '__main__':
    main()
