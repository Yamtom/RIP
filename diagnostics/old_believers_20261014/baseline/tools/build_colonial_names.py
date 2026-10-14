"""Add RIP names to the exact EU4 1.37.5 native colonial-region file.

This never substitutes a 1.30 map. Native definitions outside marked name
insertions are preserved byte for byte, including generic choices and RNW data.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tests'))
from clausewitz_testlib import _mask_comments_and_strings, matching_brace, vanilla_version

DATA = ROOT / 'tools/data/rip_colonial_names.json'
RELATIVE = 'common/colonial_regions/00_colonial_regions.txt'
LOC = 'localisation/rip_colonial_names_l_english.yml'
MANIFEST = 'docs/data/colonial_names_source.json'
BEGIN = '\t# RIP CULTURAL NAMES BEGIN\n'
END = '\t# RIP CULTURAL NAMES END\n'
REGIONS = {'colonial_alaska', 'colonial_canada', 'colonial_eastern_america',
           'colonial_louisiana', 'colonial_california', 'colonial_mexico',
           'colonial_the_carribean', 'colonial_colombia', 'colonial_peru',
           'colonial_la_plata', 'colonial_brazil'}


def load_data(path=DATA):
    data = json.loads(path.read_text(encoding='utf-8'))
    assert data['target_version'] == '1.37.5'
    assert set(data['regions']) == REGIONS
    assert set(data['cultures']) == {'ruthenian', 'byelorussian', 'ryazanian', 'rusyn'}
    aliases = [a for group in data['cultures'].values() for a in group]
    assert len(aliases) == len(set(aliases))
    for region, names in data['regions'].items():
        assert set(names) == set(data['cultures']), region
        for name, adjective in names.values():
            assert name and adjective and all('"' not in s and '\n' not in s for s in (name, adjective))
    return data


def key(region, culture):
    return 'RIP_' + region.upper() + '_' + culture.upper()


def name_insert(region, data, newline='\n'):
    lines = [BEGIN.rstrip('\n')]
    for culture, variants in data['cultures'].items():
        lines += ['\tnames = {', '\t\ttrigger = {', '\t\t\tOR = {']
        lines += [f'\t\t\t\tprimary_culture = {variant}' for variant in variants]
        lines += ['\t\t\t}', '\t\t}', f'\t\tname = "{key(region, culture)}"', '\t}']
    lines.append(END.rstrip('\n'))
    return newline.join(lines) + newline


def strip_insertions(text):
    return re.sub(r'\t# RIP CULTURAL NAMES BEGIN\r?\n.*?\t# RIP CULTURAL NAMES END\r?\n',
                  '', text, flags=re.S)


def render(base, data):
    # Latin-1 is a reversible byte mapping; vanilla cp1252 strings stay intact.
    text = base.decode('latin-1')
    if 'RIP CULTURAL NAMES BEGIN' in text:
        raise ValueError('Source already contains RIP insertions')
    newline = '\r\n' if '\r\n' in text else '\n'
    edits = []
    masked = _mask_comments_and_strings(text)
    for region in data['regions']:
        matches = list(re.finditer(rf'(?m)^{re.escape(region)}\s*=\s*\{{', masked))
        if len(matches) != 1:
            raise ValueError(f'Expected one native definition: {region}')
        opening = text.index('{', matches[0].start())
        closing = matching_brace(text, opening)
        body = text[opening + 1:closing]
        # Insert just before the first native names block; leave every old choice.
        first = re.search(r'(?m)^\t(?=names\s*=\s*\{)', body)
        if not first or 'COLONIAL_REGION_New_Root_GetName' not in body:
            raise ValueError(f'Missing expected native names/fallback in {region}')
        edits.append((opening + 1 + first.start(), name_insert(region, data, newline)))
    for offset, addition in sorted(edits, reverse=True):
        text = text[:offset] + addition + text[offset:]
    if strip_insertions(text).encode('latin-1') != base:
        raise AssertionError('Native colonial data changed outside insertions')
    return text.encode('latin-1')


def localization(data):
    lines = ['l_english:', ' # Counterfactual colonies: geographic and homeland references.']
    for region, cultures in data['regions'].items():
        for culture, (name, adjective) in cultures.items():
            loc_key = key(region, culture)
            lines += [f' {loc_key}:0 "{name}"', f' {loc_key}_ADJ:0 "{adjective}"']
    return ('\ufeff' + '\n'.join(lines) + '\n').encode('utf-8')


def prepare(output=ROOT):
    data = load_data()
    loc = output / LOC
    loc.parent.mkdir(parents=True, exist_ok=True)
    loc.write_bytes(localization(data))
    print('PREPARED 44 names and 44 adjectives; native hook requires install with EU4 1.37.5.')


def install(source, output=ROOT, check=False):
    version = vanilla_version(source)
    if version not in ('1.37.5', '1.37.5.0'):
        raise ValueError(f'EU4 1.37.5 is required; found {version!r}. No files changed.')
    data = load_data()
    original = (source / RELATIVE).read_bytes()
    result = render(original, data)
    destination = output / RELATIVE
    if destination.exists() and strip_insertions(destination.read_bytes().decode('latin-1')).encode('latin-1') != original:
        raise ValueError('Existing mod colonial file differs from this vanilla source; review it before replacing.')
    if check:
        if not destination.exists() or destination.read_bytes() != result:
            raise ValueError('Native colonial file missing or out of date')
        if (output / LOC).read_bytes() != localization(data):
            raise ValueError('Colonial localization out of date')
        print('VERIFIED 44 native choices; all other source bytes preserved.')
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(result)
    prepare(output)
    manifest = output / MANIFEST
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps({
        'game_version': version, 'source_file': RELATIVE,
        'source_sha256': hashlib.sha256(original).hexdigest(),
        'output_sha256': hashlib.sha256(result).hexdigest(),
        'choices': 44, 'classification': data['classification'],
        'native_bytes_preserved': True,
        'runtime_verified': False,
    }, indent=2) + '\n', encoding='utf-8')
    print('INSTALLED native names for 11 regions and 4 culture families.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('prepare')
    for verb in ('install', 'check'):
        command = sub.add_parser(verb)
        command.add_argument('--source', type=Path, required=True)
    args = parser.parse_args()
    if args.command == 'prepare':
        prepare()
    else:
        install(args.source, check=args.command == 'check')


if __name__ == '__main__':
    main()
