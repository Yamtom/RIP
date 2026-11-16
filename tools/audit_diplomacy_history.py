"""Compare every RIP diplomacy record with vanilla and inspect merged overlaps.

Read-only unless --output is supplied; never edits engine files.
Intervals use [start, end) for analysis; touching dates are not conflicts.
"""
import argparse
from collections import Counter
import datetime as dt
import hashlib
import json
from pathlib import Path
import re

from audit_country_history import ROOT, DATE, TOKEN, merged, parse, read

SUBJECTS = {'vassal', 'march', 'union', 'dependency'}


def province_tree(text):
    """Read assignments and bare list entries (e.g. latent_trade_goods)."""
    tokens = iter(t for t in TOKEN.findall(text) if not t.startswith('#'))
    sequence = list(tokens)
    pos = 0

    def block(nested=False):
        nonlocal pos
        result = []
        while pos < len(sequence):
            key = sequence[pos]
            pos += 1
            if key == '}':
                if not nested:
                    raise ValueError('unexpected brace')
                return result
            if pos < len(sequence) and sequence[pos] == '=':
                pos += 1
                val = sequence[pos]
                pos += 1
                result.append((key, block(True) if val == '{' else val))
            else:
                result.append((key, None))
        if nested:
            raise ValueError('unclosed province block')
        return result
    return block()


def date(value):
    return dt.date(*map(int, value.split('.')))


def records(path, mod=False):
    result = []
    for i, (kind, fields) in enumerate(parse(read(path)), 1):
        data = dict(fields)
        if len(data) != len(fields):
            raise ValueError(f'{path}:{i}: duplicate field')
        result.append(dict(kind=kind, fields=data, source=f'{path.name}#{i}', mod=mod))
    return result


def signature(r):
    return r['kind'], tuple(sorted(r['fields'].items()))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--vanilla', type=Path, required=True)
    ap.add_argument('--output', type=Path)
    args = ap.parse_args()
    v = args.vanilla.resolve()
    if re.search(r'replace_path\s*=\s*"history(?:/diplomacy)?"', read(ROOT / 'descriptor.mod')):
        ap.error('replace_path changes file merging; update the auditor before using it')
    if not (v / 'history/diplomacy').is_dir():
        ap.error('missing vanilla history/diplomacy')
    version = json.loads(read(v / 'launcher-settings.json'))['version']
    local = sorted((ROOT / 'history/diplomacy').glob('*.txt'))
    local_names = {p.name for p in local}
    vanilla_signatures = {signature(r) for p in (v / 'history/diplomacy').glob('*.txt') for r in records(p)}
    all_records = []
    for p in merged(v, 'history/diplomacy'):
        all_records.extend(records(p, p.name in local_names))
    tags = set()
    for p in merged(v, 'common/country_tags'):
        tags.update(k for k, _ in parse(read(p)))
    # Province ownership is only a static existence screen, not a runtime model.
    ownership = []
    for p in merged(v, 'history/provinces'):
        tree = province_tree(read(p))
        owner = next((x for k, x in tree if k == 'owner'), None)
        changes = []
        for k, val in tree:
            if DATE.fullmatch(k) and isinstance(val, list):
                changes.extend((date(k), x) for field, x in val if field == 'owner')
        ownership.append((owner, sorted(changes)))
    cache = {}

    def existing(when):
        if when not in cache:
            owners = set()
            for owner, changes in ownership:
                for changed, new in changes:
                    if changed > when:
                        break
                    owner = new
                if owner:
                    owners.add(owner)
            cache[when] = owners
        return cache[when]

    findings, conflicts, summaries, rows, changes = [], [], [], [], []
    for p in local:
        ours = records(p, True)
        base = v / 'history/diplomacy' / p.name
        before = records(base) if base.exists() else []
        a, b = Counter(map(signature, before)), Counter(map(signature, ours))
        summaries.append(f'| {p.name} | {len(ours)} | {"override" if base.exists() else "addition"} | {sum((a-b).values())} | {sum((b-a).values())} |')
        changes += [f'### {p.name}', '', f'RIP SHA256: `{hashlib.sha256(p.read_bytes()).hexdigest()}`', '']
        if base.exists():
            changes += [f'Vanilla SHA256: `{hashlib.sha256(base.read_bytes()).hexdigest()}`', '']
            for label, delta in [('Removed', a-b), ('Added', b-a)]:
                changes += [f'- {label} ({count}): `{kind} {dict(fields)}`' for (kind, fields), count in delta.items()]
        for r in ours:
            f = r['fields']
            start, end = date(f['start_date']), date(f['end_date'])
            if start >= end:
                findings.append(f'{r["source"]}: invalid date interval')
            for side in ('first', 'second'):
                if f[side] not in tags:
                    findings.append(f'{r["source"]}: undefined {side} {f[side]}')
            absent = [f[side] for side in ('first', 'second') if f[side] not in existing(start)]
            rows.append(f'| {r["source"]} | {r["kind"]} | {f["first"]} → {f["second"]} | {f["start_date"]}–{f["end_date"]} | {"same" if signature(r) in a else "RIP"} | {", ".join(absent) or "—"} |')
    for i, a in enumerate(all_records):
        for b in all_records[i+1:]:
            if not (a['mod'] or b['mod']):
                continue
            x, y = a['fields'], b['fields']
            if not all(k in x and k in y for k in ('start_date', 'end_date', 'first', 'second')):
                continue
            start = max(date(x['start_date']), date(y['start_date']))
            end = min(date(x['end_date']), date(y['end_date']))
            if start >= end:
                continue
            kind = None
            if a['kind'] in SUBJECTS and b['kind'] in SUBJECTS and x['second'] == y['second']:
                kind = 'multiple overlords' if x['first'] != y['first'] else 'overlapping subject records'
            elif a['kind'] == b['kind'] and (
                (x['first'], x['second']) == (y['first'], y['second']) or
                (a['kind'] in {'alliance', 'royal_marriage'} and
                 (x['first'], x['second']) == (y['second'], y['first']))):
                kind = 'overlapping relation'
            if kind:
                provenance = ' [inherited vanilla pair]' if signature(a) in vanilla_signatures and signature(b) in vanilla_signatures else ''
                conflicts.append(f'- {kind}{provenance}: {a["source"]} / {b["source"]}; {start}–{end}')
    report = ['# Diplomacy comparison', '', f'Installed baseline: **{version}**', '',
              'Semantic comparison ignores comments and field order, preserves record multiplicity.',
              'Merged files use exact-name overrides; different filenames add records. No replace_path is assumed.',
              'Ownership screen evaluates province history on the relation start date only. It does not prove later existence, event releases or engine behavior.', '',
              '| File | Records | Mode | Removed vanilla records | Added RIP records |', '|---|---|---|---|---|',
              *summaries, '', '## Every local record', '',
              '| File / record index | Type | Direction | Interval | Vanilla match | No province owner at start |',
              '|---|---|---|---|---|---|', *rows, '', '## Merged overlap findings', '',
              *conflicts, '', '## Reference/date findings', '', *findings, '', '## Override changes and hashes', '', *changes]
    if args.output:
        args.output.write_text('\n'.join(report)+'\n', encoding='utf-8')
    else:
        print('\n'.join(report))
    print(f'{len(local)} local files; {len(rows)} local records; {len(conflicts)} overlap pairs; {len(findings)} reference/date errors')
    print('\n'.join(conflicts))


if __name__ == '__main__':
    main()
