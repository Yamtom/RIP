"""Check RIP/vanilla diplomatic overlaps and important scenario transitions."""
from collections import Counter
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from audit_diplomacy_history import ROOT, SUBJECTS, date, merged, records, signature
from clausewitz_testlib import vanilla_root


def main():
    vanilla = vanilla_root()
    if not vanilla:
        raise SystemExit('Set EU4_DIR to an installed EU4 1.37.5 directory')
    v = Path(vanilla)
    names = {p.name for p in (ROOT / 'history/diplomacy').glob('*.txt')}
    effective = [r for p in merged(v, 'history/diplomacy') for r in records(p, p.name in names)]
    vanilla_signatures = {signature(r) for p in (v / 'history/diplomacy').glob('*.txt') for r in records(p)}
    failures = []
    inherited = 0
    for i, a in enumerate(effective):
        for b in effective[i+1:]:
            if not (a['mod'] or b['mod']):
                continue
            x, y = a['fields'], b['fields']
            if not all(k in x and k in y for k in ('first', 'second', 'start_date', 'end_date')):
                continue
            if max(date(x['start_date']), date(y['start_date'])) >= min(date(x['end_date']), date(y['end_date'])):
                continue
            subject_collision = a['kind'] in SUBJECTS and b['kind'] in SUBJECTS and x['second'] == y['second']
            same_pair = (x['first'], x['second']) == (y['first'], y['second'])
            if a['kind'] in {'alliance', 'royal_marriage'}:
                same_pair |= (x['first'], x['second']) == (y['second'], y['first'])
            duplicate = a['kind'] == b['kind'] and same_pair
            if subject_collision or duplicate:
                if signature(a) in vanilla_signatures and signature(b) in vanilla_signatures:
                    inherited += 1
                else:
                    failures.append(f'{a["source"]} overlaps {b["source"]}')

    # A full-file override must not silently drop unrelated Baltic relations.
    baseline = records(v / 'history/diplomacy/Baltic_alliances.txt')
    expected = Counter(signature(r) for r in baseline if r['fields'].get('second') != 'ZAZ')
    actual = Counter(map(signature, records(ROOT / 'history/diplomacy/Baltic_alliances.txt')))
    if actual != expected:
        failures.append('Baltic override changed unrelated vanilla records')

    def overlords(tag, when):
        d = date(when)
        return {r['fields']['first'] for r in effective if r['kind'] in SUBJECTS
                and r['fields'].get('second') == tag
                and date(r['fields']['start_date']) <= d < date(r['fields']['end_date'])}

    for tag, when, expected in [
        ('ZAZ', '1560.1.1', {'LIT'}), ('ZAZ', '1570.1.1', {'PLC'}),
        ('ZAZ', '1709.1.1', set()), ('ZAZ', '1712.1.1', {'TUR'}),
        ('ZAZ', '1735.1.1', {'RUS'}), ('KUR', '1720.1.1', {'PLC'}),
        ('KIE', '1444.11.11', set()),
    ]:
        if overlords(tag, when) != expected:
            failures.append(f'{tag} {when}: unexpected overlord set')
    def relation(kind, first, second, when):
        d = date(when)
        return any(r['kind'] == kind and r['fields'].get('first') == first
                   and r['fields'].get('second') == second
                   and date(r['fields']['start_date']) <= d < date(r['fields']['end_date'])
                   for r in effective)
    if not relation('guarantee', 'LIT', 'KIE', '1444.11.11'):
        failures.append('Kyivan protection missing at standard start')
    if not relation('alliance', 'ZAZ', 'CRI', '1648.6.1'):
        failures.append('1648 Crimean alliance missing')
    if relation('alliance', 'ZAZ', 'CRI', '1556.1.1'):
        failures.append('Anachronistic continuous 1550-1570 alliance restored')
    if failures:
        raise SystemExit('\n'.join(failures))
    print(f'PASS: no new RIP overlaps; Baltic preservation and scenario transitions verified; {inherited} inherited vanilla overlap(s)')


if __name__ == '__main__':
    main()
