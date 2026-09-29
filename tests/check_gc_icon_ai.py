"""Execute icon AI source choices and guarded payments; not EU4 campaign evidence."""
from copy import deepcopy
from church_testlib import fixture
from clausewitz_testlib import read, named_block

def setup(**changes):
    w, c, p = fixture('greek_catholic')
    c.update(ai=True, num_of_rebel_armies=0, patriarch_authority=.4,
             prestige=50, treasury=0)
    p['unrest'] = 0
    c.update(changes)
    return w, c, p

cases = [
    ({'num_of_rebel_armies': 1}, 0, 'charity'),
    ({'stability': -1}, 0, 'charity'),
    ({}, 3, 'charity'),
    ({'prestige': 24}, 0, 'liturgy'),
    ({'adm_power': 600}, 0, 'learning'),
    ({'dip_power': 600}, 0, 'learning'),
    ({'mil_power': 600}, 0, 'learning'),
    ({'prestige': 24, 'adm_power': 600}, 0, 'liturgy'),
    ({'prestige': 24, 'adm_power': 600}, 3, 'charity'),
    ({'prestige': 25, 'adm_power': 600}, 0, 'learning'),
    ({'adm_power': 599}, 0, None),
    ({'is_at_war': True, 'adm_power': 600}, 0, None),
    ({'is_at_war': True, 'prestige': 0}, 0, 'liturgy'),
    ({'patriarch_authority': .399, 'prestige': 0}, 0, None),
    ({'patriarch_authority': .2}, 3, 'charity'),
    ({'patriarch_authority': .199}, 3, None),
    ({'ai': False, 'prestige': 0}, 3, None),
    ({'religion': 'catholic', 'prestige': 0}, 3, None),
    ({'religion': 'russian_orthodox', 'prestige': 0}, 3, None),
    ({'patriarch_authority': 1}, 0, None),
]
for changes, unrest, expected in cases:
    w, c, p = setup(**changes)
    p['unrest'] = unrest
    initial = c['patriarch_authority']
    w.run('rip_church_gc_ai_icons_effect', c)
    active = [key for key in ('liturgy', 'learning', 'charity')
              if c['modifiers'].get('rip_church_gc_icon_' + key, -1) > w.day]
    assert active == ([] if expected is None else [expected]), (changes, unrest, active)
    assert abs(c['patriarch_authority'] - (initial - (.2 if expected else 0))) < 1e-9
    if expected:
        assert c['modifiers']['rip_church_gc_icon_' + expected] == w.day + 1825
    before = deepcopy(c)
    w.run('rip_church_gc_ai_icons_effect', c)
    assert c == before  # Monthly repeat cannot refresh, replace or charge twice.

# The live lifecycle entry actually reaches the helper, with no institution funds.
w, c, p = setup(prestige=0)
w.run('rip_church_ai_effect', c)
assert 'rip_church_gc_icon_liturgy' in c['modifiers']

# GUI activation remains available to humans, and it blocks subsequent AI choices.
for icon in ('liturgy', 'learning', 'charity'):
    w, c, p = setup(ai=False)
    w.run('rip_church_gc_activate_icon_' + icon + '_effect', c)
    c.update(ai=True, prestige=0, num_of_rebel_armies=2, adm_power=900)
    before = deepcopy(c)
    w.run('rip_church_gc_ai_icons_effect', c)
    assert c == before

# Exact expiry: no replacement one day early; renewed crisis relief at 1825 days.
w, c, p = setup(num_of_rebel_armies=1)
w.run('rip_church_gc_ai_icons_effect', c)
w.day += 1824
before = deepcopy(c)
w.run('rip_church_gc_ai_icons_effect', c)
assert c == before
w.day += 1
w.run('rip_church_gc_ai_icons_effect', c)
assert abs(c['patriarch_authority']) < 1e-9
assert c['modifiers']['rip_church_gc_icon_charity'] == w.day + 1825

modifiers = read('common/event_modifiers/rip_church_gc_interaction_modifiers.txt')
assert 'prestige = 1 improve_relation_modifier = 0.1' in named_block(modifiers, 'rip_church_gc_icon_liturgy')
assert 'development_cost = -0.05' in named_block(modifiers, 'rip_church_gc_icon_learning')
assert 'global_unrest = -1' in named_block(modifiers, 'rip_church_gc_icon_charity')
assert 'on_monthly_pulse = { rip_church_v3_monthly_effect = yes }' in read('common/on_actions/zz_RIP_church_redesign_on_actions.txt')
print('PASS: 20 AI priority/boundary cases, live AI entry, three GUI locks and exact expiry; campaign balance unverified')
