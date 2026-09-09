"""Inventory donor event definitions, gates, dependencies and native pulse callers.

Compare event IDs throughout the target events directory, not just filenames.
The report separates machine observations from editorial restoration decisions.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tests'))
from clausewitz_testlib import _mask_comments_and_strings, vanilla_version
from eu4_source_archive import verify

TOPICS = {
    'principalities': 'RussianPrincipalities.txt',
    'orthodox': 'Orthodox.txt',
    'muscovy_russia': 'FlavorRUS.txt',
    'polish_lithuanian': 'flavorPOL.txt',
    'cossack_estate': 'estate_cossacks.txt',
    'tsardom': 'RussianTsardom.txt',
}


def read_game(path):
    raw = path.read_bytes()
    try:
        return raw.decode('utf-8-sig')
    except UnicodeDecodeError:
        return raw.decode('cp1252', errors='replace')


def top_blocks(text):
    masked = _mask_comments_and_strings(text)
    depth, start = 0, None
    for match in re.finditer(r'[{}]', masked):
        if match[0] == '{':
            if depth == 0:
                prefix = re.search(r'([A-Za-z_][A-Za-z_0-9]*)\s*=\s*$', masked[:match.start()])
                start = (prefix[1], prefix.start()) if prefix else None
            depth += 1
        else:
            depth -= 1
            if depth < 0:
                raise ValueError('Unmatched closing brace')
            if depth == 0 and start:
                yield start[0], start[1], text[start[1]:match.end()]
    if depth:
        raise ValueError('Unmatched opening brace')


def definitions(path):
    text = read_game(path)
    for kind, offset, body in top_blocks(text):
        if kind not in ('country_event', 'province_event'):
            continue
        match = re.search(r'(?m)^\s*id\s*=\s*([\w.]+)', body)
        if match:
            yield match[1], text.count('\n', 0, offset) + 1, body


def values(body, field):
    # Comments are masked, while quoted DLC and modifier names are retained.
    clean = re.sub(r'(?m)#.*$', '', body)
    return sorted(set(a or b for a, b in re.findall(
        rf'\b{re.escape(field)}\s*=\s*(?:"([^"]+)"|([\w.]+))', clean)))


def pulse_index(root, ids):
    answer = {event_id: [] for event_id in ids}
    pattern = re.compile(r'(?<![\w.])(' + '|'.join(re.escape(e) for e in ids) + r')(?![\w.])')
    for path in sorted((root / 'common/on_actions').glob('*.txt')):
        text = re.sub(r'(?m)#.*$', '', read_game(path))
        for match in pattern.finditer(text):
            answer[match[0]].append(f'{path.relative_to(root).as_posix()}:{text.count(chr(10), 0, match.start()) + 1}')
    return answer


def inventory(donor, target=None):
    archive = verify(donor)
    records = []
    for topic, filename in TOPICS.items():
        path = donor / 'events' / filename
        if not path.exists():
            raise ValueError(f'Missing selected donor file: {filename}')
        file_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        for event_id, line, body in definitions(path):
            records.append({
                'topic': topic, 'id': event_id, 'source': 'events/' + filename,
                'line': line, 'source_sha256': file_hash,
                'title_keys': values(body, 'title'),
                'dlc_dependencies': values(body, 'has_dlc'),
                'reform_dependencies': values(body, 'has_reform'),
                'religion_dependencies': values(body, 'religion'),
                'culture_dependencies': values(body, 'primary_culture'),
                'name_dependencies': values(body, 'name'),
                'event_dependencies': sorted(set(values(body, 'id')) - {event_id}),
                'picture_dependencies': values(body, 'picture'),
                'uses_authority': 'uses_patriarch_authority' in _mask_comments_and_strings(body),
                'comparison': 'pending_target_1.37.5',
                'restoration_decision': 'pending_comparison_and_scope_review',
            })
    callers = pulse_index(donor, [r['id'] for r in records])
    for record in records:
        record['donor_pulse_callers'] = callers[record['id']]
    target_version = None
    if target:
        target_version = vanilla_version(target)
        if target_version not in ('1.37.5', '1.37.5.0'):
            raise ValueError(f'Target must be 1.37.5, found {target_version!r}')
        indexed = {}
        for path in sorted((target / 'events').glob('*.txt')):
            for event_id, line, body in definitions(path):
                indexed.setdefault(event_id, []).append((path, line, body))
        target_callers = pulse_index(target, [r['id'] for r in records])
        for record in records:
            definitions_now = indexed.get(record['id'], [])
            record['target_definitions'] = [f'{p.relative_to(target).as_posix()}:{line}' for p, line, _ in definitions_now]
            record['target_pulse_callers'] = target_callers[record['id']]
            if not definitions_now:
                record['comparison'] = 'id_absent_review_replacement'
            elif len(definitions_now) != 1:
                record['comparison'] = 'duplicate_target_id_review'
            else:
                path, _, body = definitions_now[0]
                record['comparison'] = 'id_present'
                record['target_reform_dependencies'] = values(body, 'has_reform')
                record['target_religion_dependencies'] = values(body, 'religion')
                record['target_tag_dependencies'] = values(body, 'tag')
                record['target_estate_dependencies'] = values(body, 'has_estate')
                if record['topic'] in ('principalities', 'tsardom') and record['target_reform_dependencies']:
                    record['candidate_class'] = 'retained_but_gated_to_native_reforms'
                    record['restoration_decision'] = 'adapt_selected_institutional_choices_no_whole_file_override'
                else:
                    record['candidate_class'] = 'already_inherited_under_native_conditions'
                    record['restoration_decision'] = 'keep_native_conditions_do_not_duplicate'
                if record['topic'] == 'orthodox' and 'uses_patriarch_authority' in _mask_comments_and_strings(body) and target_callers[record['id']]:
                    record['restoration_decision'] = 'inherited_authority_flavor_do_not_duplicate'
    return {
        'donor_version': archive['game_version'], 'target_version': target_version,
        'dependency_scope': 'Selected event files, declared gates, effects, graphics and direct on-action callers. Indirect event/estate chains require scope review.',
        'note': 'ID presence is evidence, not an automatic balance verdict. An absent ID can have a replacement under another name.',
        'counts': dict(Counter(r['topic'] for r in records)), 'events': records,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--donor', type=Path, required=True)
    parser.add_argument('--target', type=Path)
    parser.add_argument('--output', type=Path, default=ROOT / 'docs/data/flavor_130_inventory.json')
    args = parser.parse_args()
    report = inventory(args.donor, args.target)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'events': len(report['events']), 'topics': report['counts'],
                      'target_version': report['target_version']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
