"""Bounded source-state tests for synodal payments, provincial filters and diplomacy."""
from copy import deepcopy
from church_testlib import World
from clausewitz_testlib import read, named_block

class SynodWorld(World):
    def collection(self, key, scope):
        if key == 'every_neighbor_country':
            return [self.countries[tag] for tag in scope['neighbors']]
        return super().collection(key, scope)

    def condition(self, key, value, scope, root, prev):
        if key == 'religion_group':
            assert value == 'christian'
            return scope['religion'] in ('catholic', 'orthodox', 'russian_orthodox', 'greek_catholic', 'protestant')
        return super().condition(key, value, scope, root, prev)

for institution in ('infrastructure', 'coexistence'):
    w = SynodWorld()
    c = w.country('KIE', 'greek_catholic')
    c['neighbors'] = {'GRC', 'POL', 'MOS', 'TUR', 'FOE', 'OPP'}
    for tag, faith in [('GRC','greek_catholic'), ('POL','catholic'), ('MOS','orthodox'),
                       ('TUR','sunni'), ('FOE','catholic'), ('OPP','catholic'), ('FAR','catholic')]:
        other = w.country(tag, faith)
        if tag == 'FOE': other['wars'].add('KIE')
        if tag == 'OPP': other['flags']['rip_church_opposes_union'] = w.day
    for number, faith in [(1,'greek_catholic'), (2,'orthodox'), (3,'catholic'), (4,'orthodox'), (5,'greek_catholic')]:
        p = w.province(number, c, faith)
        p['local_autonomy'] = 50
        if number in (2, 4): p['flags']['rip_church_rite_recognized'] = w.day
        if number in (4, 5): p['controlled_by'] = 'FOE'
    before_pa, before_cash = c['patriarch_authority'], c['treasury']
    w.run('rip_church_gc_' + institution + '_effect', c)
    expected = [45,50,50,50,50] if institution == 'infrastructure' else [50,55,50,50,50]
    assert [w.provinces[str(n)]['local_autonomy'] for n in range(1,6)] == expected
    assert abs(c['patriarch_authority'] - (before_pa - .2)) < 1e-9
    assert c['treasury'] == before_cash - (75 if institution == 'infrastructure' else 100)
    opinion = 'rip_church_opinion_synod_' + ('schools' if institution == 'infrastructure' else 'compact')
    recipients = {tag for tag, other in w.countries.items()
                  if ('KIE', opinion) in other.get('opinion_modifiers', set())}
    assert recipients == ({'GRC'} if institution == 'infrastructure' else {'GRC','POL','MOS'})
    before = deepcopy((w.countries, w.provinces))
    for action in ('infrastructure', 'coexistence'):
        w.run('rip_church_gc_' + action + '_effect', c)
    assert (w.countries, w.provinces) == before
    c['modifiers'].clear()
    c['patriarch_authority'] = .19
    before = deepcopy((w.countries, w.provinces))
    w.run('rip_church_gc_' + institution + '_effect', c)
    assert (w.countries, w.provinces) == before

source = read('common/scripted_effects/rip_church_union_effects.txt')
for key in ('infrastructure','coexistence'):
    body = named_block(source, 'rip_church_gc_' + key + '_effect')
    assert 'years = 10' in body and 'duration = 3650' in body
    assert 'else_if' not in body and 'else =' not in body
print('PASS: both synods pay once, affect eligible provinces and peaceful neighbours only; opinion expiry checked statically')
