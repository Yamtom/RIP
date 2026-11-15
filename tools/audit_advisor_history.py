"""Compare RIP advisor overrides with an explicitly selected vanilla installation.

Read-only by default. --output writes a Markdown snapshot, never engine files.
Historical accuracy is reviewed separately in docs/ADVISOR_HISTORY_AUDIT.uk.md.
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
TOKEN = re.compile(r'#[^\n]*|"(?:\\.|[^"\\])*"|[{}=]|[^\s{}=#"]+')


def read(path: Path, vanilla: bool = False) -> str:
    raw = path.read_bytes()
    try:
        return raw.decode('utf-8-sig')
    except UnicodeDecodeError:
        if not vanilla:
            raise
        return raw.decode('cp1252')


def advisors(path: Path, vanilla: bool = False) -> list[dict[str, str]]:
    tokens = [x for x in TOKEN.findall(read(path, vanilla)) if not x.startswith('#')]
    result = []
    pos = 0
    while pos < len(tokens):
        if tokens[pos:pos + 3] != ['advisor', '=', '{']:
            raise ValueError(f'{path}: unsupported root syntax near {tokens[pos:pos+3]}')
        pos += 3
        fields = {}
        while tokens[pos] != '}':
            key, eq, value = tokens[pos:pos + 3]
            if eq != '=' or value in '{}=' or key in fields:
                raise ValueError(f'{path}: nested/duplicate/invalid advisor field {key}')
            fields[key] = value.strip('"')
            pos += 3
        pos += 1
        result.append(fields)
    return result


def merged_files(vanilla: Path, relative: str) -> dict[str, Path]:
    result = {p.name: p for p in (vanilla / relative).glob('*.txt')}
    result.update({p.name: p for p in (ROOT / relative).glob('*.txt')})
    return result


def date(value: str) -> dt.date:
    return dt.date(*map(int, value.split('.')))


def cell(value: str) -> str:
    return value.replace('|', '\\|').replace('\n', ' ')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--vanilla', required=True, type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    vanilla = args.vanilla.resolve()
    if not (vanilla / 'history/advisors').is_dir():
        parser.error('Vanilla history/advisors directory does not exist')
    overrides = sorted((ROOT / 'history/advisors').glob('*.txt'))
    errors, warnings, rows, diffs, hashes = [], [], [], [], []
    province_names = {}
    for p in merged_files(vanilla, 'history/provinces').values():
        match = re.match(r'(\d+)\s*-\s*(.+)', p.stem)
        if match:
            province_names[match[1]] = match[2]
    definitions = {}
    for folder in ['advisortypes', 'cultures', 'religions']:
        definitions[folder] = set()
        for p in merged_files(vanilla, 'common/' + folder).values():
            definitions[folder].update(re.findall(r'\b(\w+)\s*=\s*\{', read(p, p.is_relative_to(vanilla))))
    effective_ids = collections.defaultdict(list)
    for p in merged_files(vanilla, 'history/advisors').values():
        for record in advisors(p, p.is_relative_to(vanilla)):
            effective_ids[record.get('advisor_id', '<missing>')].append(p.name)
    for key, files in effective_ids.items():
        if len(files) > 1:
            errors.append(f'Duplicate advisor_id {key}: {files}')
    for p in overrides:
        base = vanilla / 'history/advisors' / p.name
        original = {r['advisor_id']: r for r in advisors(base, True)} if base.exists() else {}
        current = advisors(p)
        if base.exists():
            hashes.append(f'- `{p.name}`: `{hashlib.sha256(base.read_bytes()).hexdigest()}`')
        missing = set(original) - {r['advisor_id'] for r in current}
        if missing:
            warnings.append(f'{p.name}: absent vanilla IDs: {sorted(missing, key=int)}')
        for record in current:
            key = record.get('advisor_id', '<missing>')
            for field in ['advisor_id', 'name', 'location', 'skill', 'type', 'date', 'death_date']:
                if field not in record:
                    errors.append(f'{key}: missing {field}')
            if record.get('location') not in province_names:
                errors.append(f'{key}: unknown province {record.get("location")}')
            for field, folder in [('type', 'advisortypes'), ('culture', 'cultures'), ('religion', 'religions')]:
                if field in record and record[field] not in definitions[folder]:
                    errors.append(f'{key}: unknown {field} {record[field]}')
            try:
                assert int(key) > 0 and 1 <= int(record['skill']) <= 3
                assert date(record['date']) < date(record['death_date'])
            except (ValueError, KeyError, AssertionError):
                errors.append(f'{key}: invalid ID, skill or date interval')
            if '?' in record.get('name', ''):
                warnings.append(f'{key}: damaged name {record["name"]}')
            before = original.get(key)
            delta = [] if before is None else [f'{f}: {before.get(f, "—")} → {record.get(f, "—")}' for f in sorted(before.keys() | record.keys()) if before.get(f) != record.get(f)]
            status = 'RIP addition' if before is None else ('RIP changed' if delta else 'vanilla identical')
            if delta:
                diffs.append(f'| {key} | {cell(record["name"])} | {cell("; ".join(delta))} |')
            rows.append((int(key), record, status))
    version_file = vanilla / 'launcher-settings.json'
    version = json.loads(read(version_file, True)).get('version', 'unknown') if version_file.exists() else 'unknown'
    counts = collections.Counter(status for _, _, status in rows)
    out = ['# Advisor comparison snapshot', '', f'Vanilla: `{vanilla}`', '', f'Installed version: **{version}**', '',
           f'RIP records: **{len(rows)}**; {dict(counts)}.', '',
           'Comparison ignores comments, whitespace and field order. Vanilla decoding: UTF-8, falling back to Windows-1252. RIP: UTF-8 only.', '',
           'This is a structural comparison, not a historical certificate or a runtime test. Definition lookup checks identifier existence, not engine semantics.', '',
           '## Vanilla SHA-256', '', *hashes, '', '## Structural errors', '', *(errors or ['None.']), '',
           '## Review warnings', '', *(warnings or ['None.']), '',
           '## Changed vanilla fields', '', '| ID | Name | Vanilla → RIP |', '|---|---|---|', *diffs, '',
           '## Complete RIP inventory', '', '| ID | Name | Role / skill | Province ID: current map name | Availability fields | Culture / religion | Comparison |',
           '|---|---|---|---|---|---|---|']
    for key, r, status in sorted(rows):
        out.append('| ' + ' | '.join(map(cell, [str(key), r.get('name', ''), f'{r.get("type")} / {r.get("skill")}',
            f'{r.get("location")}: {province_names.get(r.get("location"), "UNKNOWN")}',
            f'{r.get("date")} — {r.get("death_date")}', f'{r.get("culture", "inherited")} / {r.get("religion", "inherited")}', status])) + ' |')
    report = '\n'.join(out) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding='utf-8')
        print(f'{len(rows)} records; {len(errors)} errors; {len(warnings)} warnings; {dict(counts)}')
        print(f'Report: {args.output}')
    else:
        print(report)
    return bool(errors)


if __name__ == '__main__':
    raise SystemExit(main())
