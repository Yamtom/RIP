"""Read one uncompressed EU4txt save of a v5 run and check every ordered country pair against an oracle.

usage: python analyze_v5.py <save> [label]

The oracle is written from the design of the diplomacy scale, NOT from the effect's text, so it is an independent
reading: for each ordered pair (holder -> target) it lists the church opinion modifiers that must exist, from the two
countries' religion and flags as stored in the save. The report gives the mismatches, the per-pair table of what the
save actually holds (modifier, value, count) and the state of the scenario countries.
"""
import collections
import re
import sys

path = sys.argv[1]
label = sys.argv[2] if len(sys.argv) > 2 else path
P = 'rip_church_opinion_'
EFFECT_MODIFIERS = {P + name for name in (
    'union_opposition', 'ro_recognized', 'ro_unrecognized', 'ro_schism',
    'gc_catholic_middle', 'gc_orthodox_middle', 'gc_ecumenical')}
SCENARIO = ('MOS', 'BYZ', 'NOV', 'TVE', 'RYA', 'PSK')

with open(path, encoding='latin-1') as handle:
    lines = handle.read().split('\n')
print('save:', path.replace('\\', '/').split('/')[-1], '|', lines[1], '| run:', label)

start = next(i for i, line in enumerate(lines) if line == 'countries={')
blocks, current, first = {}, None, 0
i = start + 1
while lines[i] != '}':
    match = re.match(r'^\t([A-Z0-9]{3})=\{$', lines[i])
    if match:
        current, first = match.group(1), i
    elif lines[i] == '\t}' and current:
        blocks[current] = (first, i)
        current = None
    i += 1

religion, flags, held = {}, {}, {}   # held[(holder, target)] = {modifier: value}
for tag, (a, b) in blocks.items():
    religion[tag], flags[tag] = None, set()
    in_flags = False
    for k in range(a, b):
        line = lines[k]
        if line.startswith('\t\treligion=') and religion[tag] is None:
            religion[tag] = line.split('=')[1]
        if line == '\t\tflags={':
            in_flags = True
        elif in_flags:
            if line == '\t\t}':
                in_flags = False
            else:
                flags[tag].add(line.strip().split('=')[0])
    k = a
    while k < b and lines[k] != '\t\tactive_relations={':
        k += 1
    partner = None
    while k < b and lines[k] != '\t\t}':
        match = re.match(r'^\t\t\t([A-Z0-9]{3})=\{$', lines[k])
        if match:
            partner = match.group(1)
        match = re.match(r'^\t\t\t\t\tmodifier="(.+)"$', lines[k])
        if match and match.group(1) in EFFECT_MODIFIERS:
            value = next((lines[q].strip().split('=')[1] for q in range(k + 1, k + 5)
                          if lines[q].strip().startswith('current_opinion=')), '?')
            held.setdefault((tag, partner), {})[match.group(1)] = float(value)
        k += 1

ORTHODOX_FAMILY = ('orthodox', 'russian_orthodox')


def expected(a, b):
    """Modifiers the holder `a` must hold toward `b`; the scale is symmetric."""
    ra, rb = religion[a], religion[b]
    want = set()
    if {ra, rb} == set(ORTHODOX_FAMILY):
        ro = a if ra == 'russian_orthodox' else b
        if 'rip_church_ro_schismatic' in flags[ro]:
            want.add('ro_schism')
        elif 'rip_church_ro_recognized' in flags[ro]:
            want.add('ro_recognized')
        else:
            want.add('ro_unrecognized')
    if {ra, rb} == {'catholic', 'greek_catholic'}:
        want.add('gc_catholic_middle')
    if 'greek_catholic' in (ra, rb) and (ra in ORTHODOX_FAMILY or rb in ORTHODOX_FAMILY):
        want.add('gc_orthodox_middle')
    for gc, other in ((a, b), (b, a)):
        if religion[gc] == 'greek_catholic' and 'rip_church_ecumenical' in flags[gc] and religion[other] in ('orthodox', 'catholic'):
            want.add('gc_ecumenical')
    for opposed, gc in ((a, b), (b, a)):
        if 'rip_church_opposes_union' in flags[opposed] and religion[gc] == 'greek_catholic':
            want.add('union_opposition')
    return {P + name for name in want}


mismatches, table, pairs_checked = [], collections.defaultdict(collections.Counter), 0
for a in blocks:
    for b in blocks:
        if a == b:
            continue
        pairs_checked += 1
        got = held.get((a, b), {})
        want = expected(a, b)
        if set(got) != want:
            mismatches.append((a, religion[a], b, religion[b], sorted(m.replace(P, '') for m in got),
                               sorted(m.replace(P, '') for m in want)))
        for modifier, value in got.items():
            table[(religion[a], religion[b], modifier.replace(P, ''), value)][0] += 1

print('\nordered pairs checked: %d | pairs where the save differs from the oracle: %d' % (pairs_checked, len(mismatches)))
for a, ra, b, rb, got, want in mismatches[:40]:
    print('  MISMATCH %s(%s) -> %s(%s): save holds %s, oracle wants %s' % (a, ra, b, rb, got, want))
if len(mismatches) > 40:
    print('  ... %d more' % (len(mismatches) - 40))

print('\nchurch opinion modifiers held in the save, by holder religion -> target religion:')
print('  %-16s %-16s %-20s %8s %7s' % ('holder', 'target', 'modifier', 'value', 'entries'))
for (rh, rt, modifier, value), counter in sorted(table.items()):
    print('  %-16s %-16s %-20s %8.1f %7d' % (rh, rt, modifier, value, counter[0]))
if not table:
    print('  (none)')

print('\nscenario countries (religion, flags of the harness/church, opinions others hold TOWARD them):')
for tag in SCENARIO:
    relevant = sorted(f for f in flags[tag] if f.startswith(('rip_gcr_step', 'rip_church_ecumenical', 'rip_church_opposes_union',
                                                             'rip_church_ro_recognized', 'rip_church_ro_schismatic')))
    toward = collections.Counter()
    for holder in blocks:
        for modifier in held.get((holder, tag), {}):
            toward[(religion[holder], modifier.replace(P, ''))] += 1
    print('  %s (%s) flags=%s' % (tag, religion[tag], relevant))
    for (rh, modifier), count in sorted(toward.items()):
        print('      %3d x %-16s holds %s' % (count, rh, modifier))
sys.exit(1 if mismatches else 0)
