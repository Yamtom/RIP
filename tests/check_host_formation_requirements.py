"""Exercise the two formation decisions against their actual Clausewitz triggers."""
from itertools import product

from church_testlib import parse
from clausewitz_testlib import named_block, read


def conditions(filename, name, field):
    decision = named_block(read('decisions/' + filename), name)
    return dict(parse(named_block(decision, field)))[field]


def passes(items, state):
    branch = False
    for key, value in items:
        if key == 'if':
            branch = passes(dict(value)['limit'], state)
            if branch and not passes([(k, v) for k, v in value if k != 'limit'], state):
                return False
        elif key == 'else':
            if not branch and not passes(value, state):
                return False
        elif key == 'custom_trigger_tooltip':
            if not passes([(k, v) for k, v in value if k != 'tooltip'], state):
                return False
        elif key == 'rip_het_dnieper_base':
            if not passes(BASE, state):
                return False
        elif key == 'num_of_provinces_owned_or_owned_by_non_sovereign_subjects_with':
            fields = dict(value)
            areas = {v for k, v in fields['OR'] if k == 'area'}
            if sum(a in areas and held for a, held in state['lands']) < int(fields['value']):
                return False
        elif key == 'owns_core_province':
            if int(value) not in state['cores']:
                return False
        elif key in ('tag', 'has_institution', 'is_at_war'):
            if state[key] != value:
                return False
        elif state[key] < float(value):
            return False
    return True


BASE = dict(parse(named_block(read('common/scripted_triggers/zaz_het_triggers.txt'),
                              'rip_het_dnieper_base')))['rip_het_dnieper_base']
host = conditions('CossackHostDecisions.txt', 'form_cossack_host', 'allow')
for infantry, cavalry, artillery, tech in product((0, 5, 6, 7), (0, 2, 3, 10), (0, 1), (6, 7)):
    total = infantry + cavalry + artillery
    state = dict(stability=1, army_tradition=40, total_development=50,
                 legitimacy_equivalent=50, mil_tech=tech, army_size=total,
                 num_of_infantry=infantry, num_of_cavalry=cavalry, num_of_artillery=artillery)
    assert passes(host, state) == (infantry >= 6 and cavalry >= 3 and
                                   (total >= 10 if tech < 7 else artillery >= 1)), state

het = conditions('HetmanateNation.txt', 'hetmanate_nation', 'allow')
for tag, anchor, capital, count in product(('ZAZ', 'PRL'), (283, 2407), (False, True), (5, 6)):
    state = dict(tag=tag, cores={anchor, 1944} if capital else {anchor},
                 lands=[('east_dniepr_area', True)] * count +
                       [('minsk_area', True), ('zaporizhia_area', False)],
                 adm_tech=15, stability=2, has_institution='renaissance', is_at_war='no')
    assert passes(het, state) == (capital and count == 6 and
                                  anchor == {'ZAZ': 283, 'PRL': 2407}[tag]), state

print('PASS: 64 Host muster and 16 Hetmanate origin/territory scenarios (source model).')
