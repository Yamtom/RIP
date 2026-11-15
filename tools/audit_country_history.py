"""Read-only country-history comparison; --output writes a review snapshot.

Use the installed game explicitly. Differences are not automatically defects.
The parser preserves repeated dated blocks and repeated keys.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import datetime
import difflib
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
TOKEN = re.compile(r'#[^\n]*|"(?:\\.|[^"\\])*"|[{}=]|[^\s{}=#"]+')
DATE = re.compile(r'\d+\.\d+\.\d+$')


def read(path):
    raw = path.read_bytes()
    try:
        return raw.decode('utf-8-sig')
    except UnicodeDecodeError:
        return raw.decode('cp1252')


def parse(text):
    tokens = [t for t in TOKEN.findall(text) if not t.startswith('#')]
    pos = 0

    def block(nested=False):
        nonlocal pos
        result = []
        while pos < len(tokens):
            if tokens[pos] == '}':
                if not nested:
                    raise ValueError('unexpected closing brace')
                pos += 1
                return result
            key = tokens[pos]
            pos += 1
            if pos >= len(tokens) or tokens[pos] != '=':
                raise ValueError(f'expected assignment after {key}')
            pos += 1
            value = tokens[pos]
            pos += 1
            if value == '{':
                value = block(True)
            result.append((key, value))
        if nested:
            raise ValueError('unclosed block')
        return result

    return block()


def merged(vanilla, folder):
    files = {p.name: p for p in (vanilla / folder).glob('*.txt')}
    files.update({p.name: p for p in (ROOT / folder).glob('*.txt')})
    return files.values()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--vanilla', required=True, type=Path)
    ap.add_argument('--output', type=Path)
    args = ap.parse_args()
    v = args.vanilla.resolve()
    if not (v / 'history/countries').is_dir():
        ap.error('missing vanilla history/countries')
    version = json.loads((v / 'launcher-settings.json').read_text(encoding='utf-8-sig'))['version']
    provinces = {}
    for p in merged(v, 'history/provinces'):
        m = re.match(r'(\d+)\s*-\s*(.*)', p.stem)
        if m:
            provinces[m[1]] = m[2]
    tags = set()
    for p in merged(v, 'common/country_tags'):
        tags.update(re.findall(r'^\s*([A-Z0-9]{3})\s*=', read(p), re.M))
    definitions = {}
    for folder in ['government_reforms', 'cultures', 'religions', 'event_modifiers', 'estate_privileges']:
        definitions[folder] = set()
        for p in merged(v, 'common/' + folder):
            definitions[folder].update(re.findall(r'\b([\w]+)\s*=\s*\{', read(p)))
    refs = {'add_government_reform': 'government_reforms', 'primary_culture': 'cultures',
            'add_accepted_culture': 'cultures', 'culture': 'cultures', 'religion': 'religions',
            'set_estate_privilege': 'estate_privileges'}
    findings, rows, details = [], [], []
    counts = Counter()
    for p in sorted((ROOT / 'history/countries').glob('*.txt')):
        tag = p.name[:3]
        text = read(p)
        tree = parse(text)
        b = v / 'history/countries' / p.name
        peers = list((v / 'history/countries').glob(tag + '*.txt'))
        if peers and not b.exists():
            findings.append(f'{tag}: different filename for vanilla tag: {[x.name for x in peers]}')
        original = read(b) if b.exists() else ''
        status = 'identical' if b.exists() and tree == parse(original) else ('override' if b.exists() else 'addition')
        counts[status] += 1
        if tag not in tags:
            findings.append(f'{tag}: undefined tag')
        dates = defaultdict(Counter)

        def walk(items, context='root'):
            for key, val in items:
                if DATE.fullmatch(key):
                    datetime.date(*map(int, key.split('.')))
                    if isinstance(val, list):
                        dates[key].update(k for k, _ in val if k in ('monarch', 'heir'))
                if isinstance(val, list):
                    if key == 'add_country_modifier':
                        name = dict(val).get('name', '').strip('"')
                        if name not in definitions['event_modifiers']:
                            findings.append(f'{tag}: unresolved modifier {name}')
                    walk(val, key)
                else:
                    value = val.strip('"')
                    if key in refs and value not in definitions[refs[key]]:
                        findings.append(f'{tag}: unresolved {key} = {value}')
                    if key in ('capital', 'fixed_capital') and value not in provinces:
                        findings.append(f'{tag}: unresolved province {value}')
                    if key in ('historical_friend', 'historical_rival') and value not in tags:
                        findings.append(f'{tag}: unresolved diplomatic tag {value}')
        walk(tree)
        for date, types in dates.items():
            for kind, count in types.items():
                if count > 1:
                    findings.append(f'{tag}: {date}: {count} competing {kind} records')
        header = {k: val for k, val in tree if not isinstance(val, list)}
        capital = header.get('capital', '?')
        rows.append(f'| {tag} | {status} | {capital}: {provinces.get(capital, "?")} | {header.get("government", "?")} / {header.get("add_government_reform", "?")} | {len(dates)} |')
        details += [f'### {p.name}', '', f'RIP SHA256: `{hashlib.sha256(p.read_bytes()).hexdigest()}`', '']
        if b.exists():
            details += [f'Vanilla SHA256: `{hashlib.sha256(b.read_bytes()).hexdigest()}`', '', '```diff',
                        ''.join(difflib.unified_diff(original.splitlines(True), text.splitlines(True), fromfile='vanilla/' + p.name, tofile='RIP/' + p.name)).rstrip(), '```', '']
        else:
            details += ['No vanilla counterpart; historical validation needs external sources.', '']
    out = ['# Country history comparison', '', f'Installed baseline: **{version}**', '', f'Path: `{v}`', '',
           f'Counts: {dict(counts)}', '', f'Only the {sum(counts.values())} RIP country histories are reviewed; inherited vanilla countries are not a global historical audit.',
           'Definition checks establish identifier presence, not reform eligibility or runtime behavior. Province labels are file names, not geographic proof.', '',
           '| Tag | Comparison | Capital (effective province file) | Government / reform | Distinct dated blocks |',
           '|---|---|---|---|---|', *rows, '', '## Review findings', '',
           *(['- ' + f for f in findings] or ['No structural findings.']), '', '## Complete override diffs', '', *details]
    result = '\n'.join(out) + '\n'
    if args.output:
        args.output.write_text(result, encoding='utf-8')
    else:
        print(result)
    print(f'Reviewed {sum(counts.values())} files: {dict(counts)}; {len(findings)} review findings.')
    for finding in findings:
        print(finding)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
