"""Compare every RIP war record with vanilla and check RIP map alignment.

Read-only unless --output is supplied; never edits engine files.
Evaluates merged province ownership across every war date event.
"""
from __future__ import annotations

import argparse
from collections import Counter
import difflib
import hashlib
import json
from pathlib import Path
import re
import sys

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))
TESTS_DIR = TOOLS_DIR.parent / 'tests'
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

from audit_country_history import DATE, ROOT, TOKEN, merged, parse, read
from audit_diplomacy_history import date, province_tree
from clausewitz_testlib import vanilla_root

EE_TAGS = frozenset({
    'POL', 'LIT', 'PLC', 'MOS', 'RUS', 'CRI', 'TUR', 'MOL', 'WAL',
    'ZAZ', 'PDL', 'HET', 'CHR', 'KIE', 'HLC', 'VLN', 'UZH', 'PLT', 'SMK', 'OKA',
})

RUTHENIAN_OVERLAP_TAGS = ('ZAZ', 'PDL', 'HET', 'CHR', 'KIE', 'HLC', 'VLN', 'OKA', 'CRI')


def load_ownership(vanilla):
    """Build sorted province owner timelines and province names for merged files."""
    timelines = {}
    names = {}
    for p in merged(vanilla, 'history/provinces'):
        m = re.match(r'^(\d+)\s*-\s*(.*)', p.stem)
        if not m:
            continue
        pid = int(m[1])
        tree = province_tree(read(p))
        base = next((val for k, val in tree if k == 'owner' and isinstance(val, str)), None)
        changes = []
        for k, val in tree:
            if DATE.fullmatch(k) and isinstance(val, list):
                for field, new_owner in val:
                    if field == 'owner' and isinstance(new_owner, str):
                        changes.append((date(k), new_owner))
        changes.sort(key=lambda item: item[0])
        timelines[pid] = (base, changes)
        names[pid] = m[2].strip()
    return timelines, names


def owner_on(timelines, pid, when):
    base, changes = timelines.get(pid, (None, ()))
    current = base
    for changed, new_owner in changes:
        if changed > when:
            break
        current = new_owner
    return current


def tag_provinces_on(timelines, tag, when):
    return [pid for pid in timelines if owner_on(timelines, pid, when) == tag]


def parse_war(text):
    """Parse one history/wars/*.txt file into metadata, war_goal, and dated events."""
    tree = parse(text)
    name = next((val.strip('"') for k, val in tree if k == 'name' and isinstance(val, str)), '')
    wg = {}
    for k, val in tree:
        if k == 'war_goal' and isinstance(val, list):
            wg = {fk: fv.strip('"') for fk, fv in val if isinstance(fv, str)}
            break
    events = []
    for k, val in tree:
        if DATE.fullmatch(k) and isinstance(val, list):
            events.append((k, date(k), val))
    return name, wg, events


def analyze_war_text(text, *, filename='<memory>', tags=None, cbs=None,
                     wargoal_types=None, timelines=None, prov_names=None,
                     require_ascii=False):
    """Validate structure, references, encoding safety, and map state of one war."""
    findings = []
    if require_ascii and any(ord(ch) >= 128 for ch in text):
        findings.append(f'{filename}: non-ASCII character detected (use clean ASCII)')
    try:
        name, wg, events = parse_war(text)
    except ValueError as exc:
        return dict(
            name='', war_goal={}, events=[], tags=set(), intervals=[],
            findings=[f'{filename}: parse error: {exc}'],
        )
    if not name:
        findings.append(f'{filename}: missing war name')
    if not wg:
        findings.append(f'{filename}: missing war_goal block')
    if not events:
        findings.append(f'{filename}: no dated events')
        return dict(name=name, war_goal=wg, events=events, tags=set(), intervals=[], findings=findings)

    if cbs is not None and 'casus_belli' in wg and wg['casus_belli'] not in cbs:
        findings.append(f'{filename}: undefined casus_belli {wg["casus_belli"]}')
    if wargoal_types is not None and 'type' in wg and wg['type'] not in wargoal_types:
        findings.append(f'{filename}: undefined war_goal type {wg["type"]}')
    if tags is not None and 'tag' in wg and wg['tag'] not in tags:
        findings.append(f'{filename}: undefined war_goal tag {wg["tag"]}')
    if timelines is not None and 'province' in wg:
        pid = int(wg['province'])
        if pid not in timelines:
            findings.append(f'{filename}: unknown war_goal province {pid}')

    prev_when = None
    att, dfn = set(), set()
    active_since = {}
    intervals = []
    tags_seen = set()
    start_att, start_dfn = set(), set()

    for idx, (ds, when, body) in enumerate(events):
        if prev_when is not None and when < prev_when:
            findings.append(f'{filename}: {ds}: out-of-order date after {prev_when.isoformat()}')
        prev_when = when
        for fk, fv in body:
            if fk in ('add_attacker', 'add_defender', 'rem_attacker', 'rem_defender'):
                if not isinstance(fv, str):
                    findings.append(f'{filename}: {ds}: non-scalar {fk}')
                    continue
                tags_seen.add(fv)
                if tags is not None and fv not in tags:
                    findings.append(f'{filename}: {ds}: undefined tag {fv}')
                if fk in ('add_attacker', 'add_defender') and timelines is not None:
                    if not tag_provinces_on(timelines, fv, when):
                        side_code = 'ATT' if fk == 'add_attacker' else 'DFN'
                        findings.append(f'{filename}: {ds}: LANDLESS_{side_code}:{fv}')
                if fk == 'add_attacker':
                    if fv in att:
                        findings.append(f'{filename}: {ds}: DUP_ATT:{fv}')
                    att.add(fv)
                    active_since[(fv, 'att')] = ds
                    if idx == 0:
                        start_att.add(fv)
                elif fk == 'add_defender':
                    if fv in dfn:
                        findings.append(f'{filename}: {ds}: DUP_DFN:{fv}')
                    dfn.add(fv)
                    active_since[(fv, 'dfn')] = ds
                    if idx == 0:
                        start_dfn.add(fv)
                elif fk == 'rem_attacker':
                    if fv not in att:
                        findings.append(f'{filename}: {ds}: REM_MISSING_ATT:{fv}')
                    else:
                        st = active_since.pop((fv, 'att'))
                        intervals.append((fv, 'att', st, ds, filename))
                    att.discard(fv)
                elif fk == 'rem_defender':
                    if fv not in dfn:
                        findings.append(f'{filename}: {ds}: REM_MISSING_DFN:{fv}')
                    else:
                        st = active_since.pop((fv, 'dfn'))
                        intervals.append((fv, 'dfn', st, ds, filename))
                    dfn.discard(fv)
                if att & dfn:
                    findings.append(f'{filename}: {ds}: BOTH_SIDES:{sorted(att & dfn)}')
            elif fk == 'battle' and isinstance(fv, list):
                bname = next((bv.strip('"') for bk, bv in fv if bk == 'name' and isinstance(bv, str)), '?')
                bloc = next((bv for bk, bv in fv if bk == 'location' and isinstance(bv, str)), None)
                if bloc is None or not bloc.isdigit():
                    findings.append(f'{filename}: {ds}: battle {bname} missing numeric location')
                elif timelines is not None and int(bloc) not in timelines:
                    findings.append(f'{filename}: {ds}: battle {bname} invalid location {bloc}')
                for bside in ('attacker', 'defender'):
                    sblock = next((bv for bk, bv in fv if bk == bside and isinstance(bv, list)), None)
                    if sblock:
                        country = next((sv for sk, sv in sblock if sk == 'country' and isinstance(sv, str)), None)
                        if country and tags is not None and country not in tags:
                            findings.append(f'{filename}: {ds}: battle {bname} undefined country {country}')

    if att or dfn:
        findings.append(f'{filename}: UNCLOSED:att={sorted(att)},dfn={sorted(dfn)}')

    wg_type = wg.get('type', '')
    if timelines is not None and 'province' in wg and events and wg_type.startswith('take_'):
        pid = int(wg['province'])
        if pid in timelines:
            owner = owner_on(timelines, pid, events[0][1])
            pname = prov_names.get(pid, str(pid)) if prov_names else str(pid)
            if owner not in start_dfn:
                findings.append(
                    f'{filename}: WG_NOT_DEFENDER:{pid}({pname},owner={owner},dfn={sorted(start_dfn)})'
                )
    if timelines is not None and 'tag' in wg and events and wg_type == 'defend_capital_independence':
        wtag = wg['tag']
        if wtag not in (start_att | start_dfn):
            findings.append(f'{filename}: WG_INDEP_TAG_NOT_IN_WAR:{wtag}')
        elif not tag_provinces_on(timelines, wtag, events[0][1]):
            findings.append(f'{filename}: WG_INDEP_TAG_LANDLESS:{wtag}')

    return dict(
        name=name, war_goal=wg, events=events, tags=tags_seen,
        intervals=intervals, findings=findings,
    )


def summarize_overlaps(intervals):
    """Find strict overlaps where the same Ruthenian/steppe tag is in 2 wars at once."""
    by_tag = {tag: [] for tag in RUTHENIAN_OVERLAP_TAGS}
    for tag, side, st, en, fn in intervals:
        if tag in by_tag:
            by_tag[tag].append((date(st), date(en), st, en, side, fn))
    overlaps = []
    for tag, items in by_tag.items():
        items.sort(key=lambda item: item[0])
        for i, a in enumerate(items):
            for b in items[i + 1:]:
                if a[1] > b[0]:
                    overlaps.append(
                        f'- `{tag}`: `{a[5]}` ({a[2]}..{a[3]} {a[4]}) vs `{b[5]}` ({b[2]}..{b[3]} {b[4]})'
                    )
    return overlaps


def inspect_wars(vanilla):
    v = vanilla.resolve()
    if re.search(r'replace_path\s*=\s*"history(?:/wars)?"', read(ROOT / 'descriptor.mod')):
        raise RuntimeError('replace_path changes history/wars merging; update audit_war_history.py')
    if not (v / 'history/wars').is_dir():
        raise FileNotFoundError(f'missing vanilla history/wars under {v}')

    version = json.loads(read(v / 'launcher-settings.json'))['version']
    tags = set()
    for p in merged(v, 'common/country_tags'):
        tags.update(k for k, _ in parse(read(p)))
    cbs = set()
    for p in merged(v, 'common/cb_types'):
        cbs.update(re.findall(r'^([A-Za-z0-9_]+)\s*=\s*\{', read(p), re.M))
    wargoal_types = set()
    for p in merged(v, 'common/wargoal_types'):
        wargoal_types.update(re.findall(r'^([A-Za-z0-9_]+)\s*=\s*\{', read(p), re.M))

    timelines, prov_names = load_ownership(v)
    local = sorted((ROOT / 'history/wars').glob('*.txt'))
    local_names = {p.name for p in local}

    local_results = {}
    local_findings = []
    vanilla_ee_findings = []
    all_intervals = []
    summaries = []
    deltas = []

    for p in merged(v, 'history/wars'):
        is_mod = p.name in local_names
        text = read(p)
        res = analyze_war_text(
            text, filename=p.name, tags=tags, cbs=cbs,
            wargoal_types=wargoal_types, timelines=timelines,
            prov_names=prov_names, require_ascii=is_mod,
        )
        all_intervals.extend(res['intervals'])
        if is_mod:
            local_results[p.name] = res
            local_findings.extend(res['findings'])
        elif res['findings'] and (res['tags'] & EE_TAGS):
            vanilla_ee_findings.extend(res['findings'])

    for p in local:
        res = local_results[p.name]
        base = v / 'history/wars' / p.name
        mode = 'override' if base.exists() else 'addition'
        span = f"{res['events'][0][0]}..{res['events'][-1][0]}" if res['events'] else '?'
        wg = res['war_goal']
        wg_desc = f"{wg.get('type', '?')} ({wg.get('casus_belli', '?')})"
        if 'province' in wg:
            pid = int(wg['province'])
            wg_desc += f" @ {pid} {prov_names.get(pid, '')}".rstrip()
        summaries.append(
            f"| `{p.name}` | {res['name']} | {mode} | `{span}` | {wg_desc} | {len(res['findings'])} |"
        )
        deltas += [f'### {p.name}', '', f'RIP SHA256: `{hashlib.sha256(p.read_bytes()).hexdigest()}`', '']
        if base.exists():
            btext = read(base)
            deltas += [f'Vanilla SHA256: `{hashlib.sha256(base.read_bytes()).hexdigest()}`', '']
            diff_lines = list(difflib.unified_diff(
                btext.splitlines(), read(p).splitlines(),
                fromfile=f'vanilla/{p.name}', tofile=f'RIP/{p.name}', lineterm='',
            ))
            deltas += ['```diff', *(diff_lines if diff_lines else ['(no diff)']), '```', '']
        else:
            deltas += ['New RIP war file (`addition`).', '']

    overlaps = summarize_overlaps(all_intervals)
    lines = [
        '# War history comparison', '',
        f'Installed baseline: **{version}**', '',
        'Merged files use exact-name overrides without `replace_path`.',
        'Evaluation simulates merged `RIP + vanilla` province ownership on every dated war event.', '',
        '| File | War | Mode | Span | War goal | Local findings |',
        '|---|---|---|---|---|---|',
        *summaries, '',
        '## Local RIP findings', '',
        *(local_findings or ['- None (`0` errors across all local war files).']), '',
        '## Multi-war overlaps for Ruthenian / steppe tags', '',
        *(overlaps or ['- None across merged RIP + vanilla wars for `ZAZ`, `PDL`, `HET`, `CHR`, `KIE`, `HLC`, `VLN`, `OKA`, `CRI`.']), '',
        '## Inherited vanilla Eastern European findings (unoverridden files)', '',
        *(f'- {item}' for item in vanilla_ee_findings), '',
        '## Override diffs and SHA256 hashes', '',
        *deltas,
    ]
    return dict(
        version=version,
        local_count=len(local),
        local_results=local_results,
        local_findings=local_findings,
        vanilla_ee_findings=vanilla_ee_findings,
        overlaps=overlaps,
        report='\n'.join(lines) + '\n',
        tags=tags,
        cbs=cbs,
        wargoal_types=wargoal_types,
        timelines=timelines,
        prov_names=prov_names,
    )


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--vanilla', type=Path)
    ap.add_argument('--output', type=Path)
    args = ap.parse_args()
    vanilla = args.vanilla if args.vanilla else vanilla_root()
    if vanilla is None:
        donor_137 = ROOT / 'diagnostics/vanilla_donors/eu4_1.37.5'
        vanilla = donor_137 if donor_137.is_dir() else None
    if vanilla is None:
        ap.error('could not auto-detect EU4 1.37.5 installation; pass --vanilla PATH')
    result = inspect_wars(vanilla)
    if args.output:
        args.output.write_text(result['report'], encoding='utf-8')
    print(
        f"{result['local_count']} local war files; "
        f"{len(result['local_findings'])} local findings; "
        f"{len(result['overlaps'])} Ruthenian/steppe war overlaps; "
        f"{len(result['vanilla_ee_findings'])} inherited vanilla EE findings"
    )
    if result['local_findings']:
        print('\n'.join(result['local_findings']))
        sys.exit(1)


if __name__ == '__main__':
    main()
