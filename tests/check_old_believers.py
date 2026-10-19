"""Execute the Old Believer chapter against the live source.

Communities (province flags that never change a province's faith), the two
policies, the yearly upkeep, events rip_ob.2/3, the three decisions, and - the
point of this file - the Raskol exit: the disaster ends when the patriarch's
authority falls below 60%, and the Old Believer policy only moves the pace of
that fall. It is NOT a second exit and no timer decides it.

This bounded interpreter is a source model, not evidence of native rendering,
AI scheduling or save/load behaviour; those need the game.
"""
from copy import deepcopy
import re

from church_testlib import World, EFFECTS, TRIGGERS, parse
from clausewitz_testlib import ROOT, read, named_block

EFFECTS.update(parse(read('common/scripted_effects/rip_faith_history_cleanup_effects.txt')))
EFFECTS.update(parse(read('common/scripted_effects/rip_faith_zeal_effects.txt')))


class Fixture(World):
    """Church fixture plus the few conditions and effects these scripts add."""

    def condition(self, key, value, scope, root, prev):
        if key == 'is_capital':
            return (self.countries[scope['owner']]['capital'] == scope['id']) == (value == 'yes')
        if key == 'dominant_religion':
            owned = [p['religion'] for p in self.provinces.values() if p['owner'] == scope['id']]
            return bool(owned) and max(set(owned), key=owned.count) == value
        if key == 'num_of_rebel_armies' or key == 'num_of_rebel_controlled_provinces':
            return scope.get(key, 0) >= float(value)
        return super().condition(key, value, scope, root, prev)

    def execute(self, items, scope, root=None, prev=None):
        # Rebels and unrest are recorded, not simulated.
        rest = []
        for key, value in items:
            if key == 'spawn_rebels':
                scope.setdefault('rebels', []).append(dict(value))
            elif key == 'add_unrest':
                scope['unrest'] = scope.get('unrest', 0) + float(value)
            else:
                rest.append((key, value))
        super().execute(rest, scope, root, prev)


def load_events(*paths):
    found = {}
    for path in paths:
        for kind, body in parse(read(path)):
            if kind in ('country_event', 'province_event') and isinstance(body, list) and 'id' in dict(body):
                found[dict(body)['id']] = body
    return found


EVENTS = load_events('events/RussianOrthodox.txt', 'events/RIP_FaithDisasters.txt', 'events/RIP_OldBelievers.txt')


def choose(world, scope, event, option):
    body = EVENTS[event]
    if 'immediate' in dict(body):
        world.execute(dict(body)['immediate'], scope)
    chosen = next(v for k, v in body if k == 'option' and dict(v)['name'] == option)
    world.execute([(k, v) for k, v in chosen if k not in ('name', 'ai_chance', 'trigger')], scope)


def available(world, scope, event):
    return world.gate(dict(EVENTS[event])['trigger'], scope)


DECISIONS = {}
for name, body in parse(read('decisions/RIP_OldBelievers.txt'))[0][1]:
    DECISIONS[name] = dict(body)

# --- fixtures -------------------------------------------------------------


def realm(year=1667, religion='orthodox', parishes=5):
    """A Muscovite jurisdiction with `parishes` settled Russian parishes beside
    its capital, one Ruthenian Orthodox city and a Catholic one."""
    w = Fixture()
    w.year = year
    c = w.country('MOS', religion)
    c.update(num_of_rebel_armies=0, num_of_rebel_controlled_provinces=0, patriarch_authority=0.8,
             stability=1, adm_power=500)
    c['flags']['rip_ro_stage_autocephaly'] = w.day
    c['flags']['rip_ro_stage_raskol'] = w.day
    capital = w.province(295, c, religion)
    capital['region'] = 'russia_region'
    russian = []
    for number in range(296, 296 + parishes):
        p = w.province(number, c, 'orthodox')
        p['region'] = 'russia_region'
        russian.append(p)
    kyiv = w.province(280, c, 'orthodox')
    catholic = w.province(281, c, 'catholic')
    return w, c, capital, russian, kyiv, catholic


def communities(w, owner=None):
    return sorted(p['id'] for p in w.provinces.values()
                  if 'rip_ob_community' in p['flags'] and (owner is None or p['owner'] == owner['id']))


def faiths(w):
    return {k: p['religion'] for k, p in w.provinces.items()}


cases = 0

# --- 1. who can be a community --------------------------------------------
for religion in ('orthodox', 'russian_orthodox'):
    w, c, capital, russian, kyiv, catholic = realm(religion=religion)
    seed = TRIGGERS['rip_ob_seed_eligible']
    assert all(w.gate(seed, p) for p in russian), 'a settled Russian parish is a candidate'
    assert not w.gate(seed, kyiv), 'Kyivan Orthodoxy is not Old Believer by being Orthodox'
    assert not w.gate(seed, catholic)
    foreign = w.country('LIT', 'catholic')
    abroad = w.province(901, foreign, 'orthodox'); abroad['region'] = 'russia_region'
    assert not w.gate(seed, abroad), 'a foreign province is never a candidate'
    occupied = russian[0]; occupied['controlled_by'] = 'LIT'
    assert not w.gate(seed, occupied), 'an occupied parish is not a candidate'
    occupied['controlled_by'] = 'MOS'; occupied['core'] = 'LIT'
    assert not w.gate(seed, occupied), 'a non-core parish is not a candidate'
    occupied['core'] = 'MOS'
    c['flags'].pop('rip_ro_stage_raskol')
    assert not w.gate(seed, russian[1]), 'no schism, no candidates'
    c['flags']['rip_ro_stage_raskol'] = w.day
    c['flags'].pop('rip_ro_stage_autocephaly')
    if religion == 'orthodox':
        assert not w.gate(seed, russian[1]), 'outside the Muscovite jurisdiction, nobody is a candidate'
    cases += 1

# --- 2. a community is a mark, never a conversion --------------------------
w, c, capital, russian, kyiv, catholic = realm()
before = faiths(w)
w.run('rip_ob_mark_community_effect', russian[0])
assert faiths(w) == before and 'rip_ob_local_community' in russian[0]['modifiers']
assert not w.gate(TRIGGERS['rip_ob_seed_eligible'], russian[0]), 'a marked parish is not marked twice'
w.day = 100
w.run('rip_ob_mark_community_effect', russian[0])
assert russian[0]['flags']['rip_ob_community'] == 0, 'upkeep must not reset a community\'s age'
cases += 1

# --- 3. the schism marks up to three, once ---------------------------------
for parishes, expected in ((5, 3), (1, 2), (0, 1)):   # the capital is a candidate too
    w, c, capital, russian, kyiv, catholic = realm(parishes=parishes)
    before = faiths(w)
    w.run('rip_ob_begin_schism_effect', c)
    assert len(communities(w)) == expected, (parishes, communities(w))
    assert 'old_believer' in getattr(w, 'enabled', set())
    assert faiths(w) == before, 'seeding communities converts nothing'
    assert 'rip_ob_schism_initialized' in c['flags']
    w.run('rip_ob_begin_schism_effect', c)
    assert len(communities(w)) == expected, 'the schism marks its communities once'
    cases += 1

# --- 4. the council of 1666 marks the communities and chooses the policy ---
def council(choice, parishes=5):
    w, c, capital, russian, kyiv, catholic = realm(year=1666, parishes=parishes)
    c['flags'].pop('rip_ro_stage_raskol')
    for flag in ('rip_ro_stage_patriarchate', 'rip_ro_books_reformed', 'rip_church_ro_recognized'):
        c['flags'][flag] = w.day
    c['patriarch_authority'] = 0.8
    before = faiths(w)
    choose(w, c, 'russian_orthodox.6', 'russian_orthodox.6.' + choice)
    assert faiths(w) == before, 'the council changes no province faith'
    return w, c, capital, russian, kyiv, catholic

w, c, capital, russian, kyiv, catholic = council('a')
assert len(communities(w)) == 3 and 'rip_ro_stage_raskol' in c['flags']
assert 'rip_ob_repression' in c['flags'] and 'rip_ob_toleration' not in c['flags']
assert 'rip_ob_repressive_policy' in c['modifiers'] and 'suppression_old_believers' in c['modifiers']
assert kyiv['religion'] == 'orthodox' and 'rip_ob_community' not in kyiv['flags']
assert 'rebels' not in capital and 'rebels' not in catholic, 'rebels rise in no capital and in no other faith'
assert [p['rebels'] for p in w.provinces.values() if 'rebels' in p] == [[{'type': 'old_believer_rebels', 'size': '2'}]]
cases += 1

w, c, capital, russian, kyiv, catholic = council('b')
assert len(communities(w)) == 3
assert 'rip_ob_toleration' in c['flags'] and 'rip_ob_repression' not in c['flags']
assert 'rip_ob_tolerant_policy' in c['modifiers'] and 'old_believer_underground' in c['modifiers']
assert 'suppression_old_believers' not in c['modifiers']
cases += 1

w, c, capital, russian, kyiv, catholic = council('c')
assert communities(w) == [] and 'rip_ob_schism_initialized' not in c['flags']
assert not ({'rip_ob_toleration', 'rip_ob_repression', 'rip_ob_policy_changed'} & set(c['flags']))
assert not ({'rip_ob_tolerant_policy', 'rip_ob_repressive_policy'} & set(c['modifiers']))
assert all(
    not ({'rip_ob_local_toleration', 'rip_ob_local_repression'} & set(p['modifiers']))
    for p in w.provinces.values()
)
assert 'rip_ro_raskol_settled' in c['flags'] and 'rip_ro_stage_raskol' not in c['flags']
w.run('rip_ob_upkeep_effect', c)
assert communities(w) == [], 'a compromise leaves nothing for the yearly upkeep to seed'
cases += 1

# --- 5. the disaster's opening options choose the policy again --------------
for first, second, expected in (('a', 'rip_faith_disaster.1.b', 'rip_ob_toleration'),
                                ('b', 'rip_faith_disaster.1.a', 'rip_ob_repression')):
    w, c, capital, russian, kyiv, catholic = council(first)
    marked = communities(w)
    choose(w, c, 'rip_faith_disaster.1', second)
    other = 'rip_ob_repression' if expected == 'rip_ob_toleration' else 'rip_ob_toleration'
    assert expected in c['flags'] and other not in c['flags']
    assert ('rip_ob_tolerant_policy' in c['modifiers']) != ('rip_ob_repressive_policy' in c['modifiers'])
    assert communities(w) == marked, 'the policy never adds or removes a community'
    if first == 'a':
        assert 'suppression_old_believers' not in c['modifiers'], 'toleration ends the legacy repression'
    else:
        assert 'old_believer_underground' not in c['modifiers'], 'repression ends the legacy toleration'
    cases += 1

# --- 6. the policies exclude each other and touch no province -----------------
w, c, capital, russian, kyiv, catholic = realm()
w.run('rip_ob_begin_schism_effect', c)
snapshot = deepcopy(w.provinces)
w.run('rip_ob_tolerate_effect', c)
assert 'rip_ob_toleration' in c['flags'] and 'rip_ob_policy_changed' in c['flags']
w.run('rip_ob_repress_effect', c)
assert 'rip_ob_toleration' not in c['flags'] and 'rip_ob_repression' in c['flags']
assert 'rip_ob_tolerant_policy' not in c['modifiers'] and 'rip_ob_repressive_policy' in c['modifiers']
w.run('rip_ob_tolerate_effect', c)
assert 'rip_ob_repression' not in c['flags'] and 'rip_ob_repressive_policy' not in c['modifiers']
assert w.provinces == snapshot, 'a policy does not repaint or erase communities'
cases += 1

# --- 7. upkeep: consequences follow the current owner; communities stay -----
w, c, capital, russian, kyiv, catholic = realm()
w.run('rip_ob_begin_schism_effect', c)
marked = communities(w)
parish = w.provinces[marked[0]]
w.run('rip_ob_tolerate_effect', c)
w.run('rip_ob_upkeep_effect', c)
assert 'rip_ob_local_toleration' in parish['modifiers'] and 'rip_ob_local_repression' not in parish['modifiers']
w.run('rip_ob_repress_effect', c)
w.run('rip_ob_upkeep_effect', c)
assert 'rip_ob_local_repression' in parish['modifiers'] and 'rip_ob_local_toleration' not in parish['modifiers']
conqueror = w.country('LIT', 'catholic')
parish['owner'] = parish['controlled_by'] = 'LIT'
w.run('rip_ob_upkeep_effect', conqueror)
assert 'rip_ob_local_repression' not in parish['modifiers'] and 'rip_ob_local_toleration' not in parish['modifiers']
assert 'rip_ob_community' in parish['flags'] and parish['religion'] == 'orthodox'
cases += 1

# an Old Believer majority is a community too
w, c, capital, russian, kyiv, catholic = realm()
russian[0]['religion'] = 'old_believer'
w.run('rip_ob_upkeep_effect', c)
assert 'rip_ob_community' in russian[0]['flags']
cases += 1

# a save made before this chapter seeds its communities once, and not before 1666
for year, expected in ((1665, 0), (1666, 3)):
    w, c, capital, russian, kyiv, catholic = realm(year=year)
    w.run('rip_ob_upkeep_effect', c)
    assert len(communities(w)) == expected
    w.run('rip_ob_upkeep_effect', c)
    assert len(communities(w)) == expected
    cases += 1

# a ruler who has left the jurisdiction keeps no policy; one who took the old rite does
w, c, capital, russian, kyiv, catholic = realm()
w.run('rip_ob_tolerate_effect', c)
c['religion'] = 'catholic'
c['flags'].pop('rip_ro_stage_autocephaly')
w.run('rip_ob_upkeep_effect', c)
assert not ({'rip_ob_toleration', 'rip_ob_repression'} & set(c['flags']))
assert not ({'rip_ob_tolerant_policy', 'rip_ob_repressive_policy'} & set(c['modifiers']))
w, c, capital, russian, kyiv, catholic = realm()
w.run('rip_ob_tolerate_effect', c)
c['religion'] = 'old_believer'
w.run('rip_ob_upkeep_effect', c)
assert 'rip_ob_toleration' in c['flags'] and 'rip_ob_tolerant_policy' in c['modifiers']
cases += 1

# --- 8. events rip_ob.2 and rip_ob.3 ----------------------------------------
w, c, capital, russian, kyiv, catholic = realm()
parish = russian[0]
assert not available(w, parish, 'rip_ob.2'), 'no community, no majority shift'
w.run('rip_ob_mark_community_effect', parish)
assert not available(w, parish, 'rip_ob.2'), 'a new community needs a decade'
w.day = 3649
assert not available(w, parish, 'rip_ob.2')
w.day = 3650
assert available(w, parish, 'rip_ob.2')
parish['has_missionary'] = True
assert not available(w, parish, 'rip_ob.2'), 'a missionary at work stops the review'
parish['has_missionary'] = False
parish['religion'] = 'catholic'
assert not available(w, parish, 'rip_ob.2')
parish['religion'] = 'orthodox'
before = faiths(w)
choose(w, parish, 'rip_ob.2', 'rip_ob.2.b')
assert faiths(w) == before and parish['local_autonomy'] == 10 and 'rip_ob_community' in parish['flags']
w.day = 3650 + 3649
assert not available(w, parish, 'rip_ob.2'), 'a refused review is not repeated within ten years'
w.day = 3650 + 3650
assert available(w, parish, 'rip_ob.2')
choose(w, parish, 'rip_ob.2', 'rip_ob.2.a')
assert parish['religion'] == 'old_believer' and 'rip_ob_community' in parish['flags']
assert all(p['religion'] == before[k] for k, p in w.provinces.items() if p is not parish), 'one province only'
assert 'old_believer' in getattr(w, 'enabled', set())
assert not available(w, parish, 'rip_ob.2'), 'an Old Believer majority is not asked again'

# spreading needs a decade-old neighbour and a free, eligible parish
w, c, capital, russian, kyiv, catholic = realm()
w.run('rip_ob_mark_community_effect', russian[0])
russian[0]['religion'] = 'old_believer'
target = russian[1]
target['neighbors'] = {russian[0]['id']}
assert not available(w, target, 'rip_ob.3'), 'the neighbour is too young'
w.day = 3650
assert available(w, target, 'rip_ob.3')
target['neighbors'] = set()
assert not available(w, target, 'rip_ob.3'), 'spread is adjacency-bound'
target['neighbors'] = {russian[0]['id']}
kyiv['neighbors'] = {russian[0]['id']}
assert not available(w, kyiv, 'rip_ob.3'), 'Kyivan Orthodoxy never receives a community'
before = faiths(w)
choose(w, target, 'rip_ob.3', 'rip_ob.3.a')
assert 'rip_ob_community' in target['flags'] and faiths(w) == before
cases += 1

# --- 9. the decisions -------------------------------------------------------
assert set(DECISIONS) == {'rip_ob_tolerate', 'rip_ob_repress', 'rip_ob_adopt_old_rite'}


def allowed(world, decision, scope):
    return world.gate(DECISIONS[decision]['potential'], scope) and world.gate(DECISIONS[decision]['allow'], scope)


w, c, capital, russian, kyiv, catholic = realm()
w.run('rip_ob_begin_schism_effect', c)
assert allowed(w, 'rip_ob_tolerate', c) and allowed(w, 'rip_ob_repress', c)
assert not allowed(w, 'rip_ob_adopt_old_rite', c), 'no Old Believer majority anywhere yet'
c['adm_power'] = 49
assert not allowed(w, 'rip_ob_tolerate', c) and not allowed(w, 'rip_ob_repress', c)
c['adm_power'] = 500
c['is_at_war'] = True
assert not allowed(w, 'rip_ob_tolerate', c)
c['is_at_war'] = False
w.run('rip_ob_tolerate_effect', c)
assert not w.gate(DECISIONS['rip_ob_tolerate']['potential'], c), 'the policy in force is not offered again'
assert not allowed(w, 'rip_ob_repress', c), 'one policy change in ten years'
w.day = 3649
assert not allowed(w, 'rip_ob_repress', c)
w.day = 3650
assert allowed(w, 'rip_ob_repress', c)
before = faiths(w)
adm = c['adm_power']
w.execute(DECISIONS['rip_ob_repress']['effect'], c)
assert c['adm_power'] == adm - 50 and 'rip_ob_repression' in c['flags'] and 'rip_ob_toleration' not in c['flags']
assert any('rip_ob_local_repression' in p['modifiers'] for p in w.provinces.values()),     'the decision refreshes the communities at once'
assert faiths(w) == before, 'a policy converts nothing'
# a realm with no community is offered neither policy
w, c, capital, russian, kyiv, catholic = realm()
assert not allowed(w, 'rip_ob_tolerate', c) and not allowed(w, 'rip_ob_repress', c)
# only the Muscovite jurisdiction may repress; a ruler of the old rite may only tolerate
w, c, capital, russian, kyiv, catholic = realm()
russian[0]['religion'] = 'old_believer'
c['religion'] = 'old_believer'
assert allowed(w, 'rip_ob_tolerate', c) and not allowed(w, 'rip_ob_repress', c)
cases += 1

# the old rite as a state confession needs a dominant faith AND an Old Believer capital
w, c, capital, russian, kyiv, catholic = realm()
for p in (capital, *russian):
    p['religion'] = 'old_believer'
w.run('rip_ob_upkeep_effect', c)
assert allowed(w, 'rip_ob_adopt_old_rite', c)
capital['religion'] = 'orthodox'
assert not allowed(w, 'rip_ob_adopt_old_rite', c), 'the capital must hold the old rite'
capital['religion'] = 'old_believer'
for p in russian[1:]:
    p['religion'] = 'orthodox'
assert not allowed(w, 'rip_ob_adopt_old_rite', c), 'the old rite must be the dominant faith'
for p in russian[1:]:
    p['religion'] = 'old_believer'
others = faiths(w)
w.execute(DECISIONS['rip_ob_adopt_old_rite']['effect'], c)
assert c['religion'] == 'old_believer' and c['adm_power'] == 400 and c['stability'] == 0
assert 'rip_ob_toleration' in c['flags'] and 'rip_ob_tolerant_policy' in c['modifiers']
assert faiths(w) == others, 'the state confession changes; no province does'
assert not w.gate(TRIGGERS['rip_church_ro_jurisdiction'], c), 'the old rite leaves the Muscovite jurisdiction'
cases += 1

# --- 10. the Raskol exit: authority, not the Old Believer policy -------------
disaster = named_block(read('common/disasters/rip_faith_disasters.txt'), 'rip_ro_raskol')
can_end = re.sub(r'#[^\n]*', '', named_block(disaster, 'can_end'))   # the block starts after the comment
assert 'patriarch_authority = 0.6' in can_end and 'rip_ob_' not in can_end
assert 'religious_unity' not in can_end, 'the unity exit closed the Raskol on its first check'
end_gate = dict(parse(can_end))['can_end']

w, c, capital, russian, kyiv, catholic = realm()
w.run('rip_ob_begin_schism_effect', c)
for policy in (None, 'rip_ob_tolerate_effect', 'rip_ob_repress_effect'):
    if policy:
        w.run(policy, c)
    for day in (0, 1825, 3650, 36500):
        w.day = day
        c['patriarch_authority'] = 0.61
        assert not w.gate(end_gate, c), f'{policy}: authority 0.61 on day {day} must not end the Raskol'
        c['patriarch_authority'] = 0.59
        assert w.gate(end_gate, c), f'{policy}: authority 0.59 on day {day} must end it'
    c['num_of_rebel_controlled_provinces'] = 1
    assert not w.gate(end_gate, c), 'a rebel-held province still holds the Raskol open'
    c['num_of_rebel_controlled_provinces'] = 0
cases += 1

# The pace: the disaster takes authority every year, the policy moves that.
def modifier_value(text, name):
    return float(re.search(r'\b' + name + r'\s*=\s*(-?[0-9.]+)', text).group(1))

live = re.sub(r'#[^\n]*', '', disaster)
assert live.count('yearly_patriarch_authority') == 1, 'the disaster carries one yearly authority term'
fall = modifier_value(live, 'yearly_patriarch_authority')
modifiers = read('common/event_modifiers/rip_old_believer_modifiers.txt')
tolerant = modifier_value(named_block(modifiers, 'rip_ob_tolerant_policy'), 'yearly_patriarch_authority')
repressive = modifier_value(named_block(modifiers, 'rip_ob_repressive_policy'), 'yearly_patriarch_authority')
assert fall < 0 and tolerant < 0 < repressive and abs(tolerant) == abs(repressive) < abs(fall) / 2
years = {name: (0.85 - 0.60) / -(fall + delta) for name, delta in
         (('neutral', 0), ('toleration', tolerant), ('repression', repressive))}
assert years['toleration'] < years['neutral'] < years['repression'], years
assert 9.9 < years['toleration'] < 10.1 and 12.4 < years['neutral'] < 12.6 and 16.6 < years['repression'] < 16.8, years
# Without another source of authority repression can never hold the Raskol open for good.
assert fall + repressive < 0
cases += 1

# The end of the Raskol changes neither a faith nor a community.
w, c, capital, russian, kyiv, catholic = council('b')
russian_parish = w.provinces[communities(w)[0]]
russian_parish['religion'] = 'old_believer'
before_flags = {k: dict(p['flags']) for k, p in w.provinces.items()}
before = faiths(w)
choose(w, c, 'rip_faith_disaster.2', 'rip_faith_disaster.2.a')
assert 'rip_ro_raskol_settled' in c['flags']
assert faiths(w) == before and {k: dict(p['flags']) for k, p in w.provinces.items()} == before_flags
assert 'rip_ob_toleration' in c['flags'], 'the policy outlives the disaster'
ending = read('events/RIP_FaithDisasters.txt').split('id = rip_faith_disaster.2', 1)[1].split('country_event', 1)[0]
assert 'change_religion' not in ending and 'clr_province_flag' not in ending and 'rip_ob_' not in ending
cases += 1

# The recurring Old Believer rising limit is armed by repression, not by the
# mere existence of an Orthodox-family parish.
backlash = dict([v for k, v in EFFECTS['rip_ro_zealot_backlash_effect'] if k == 'if'][1])['limit']
w, c, capital, russian, kyiv, catholic = realm(religion='russian_orthodox')
w.run('rip_ob_mark_community_effect', russian[0])
assert not w.gate(backlash, c), 'without an Old Believer policy, no Old Believer rising is armed'
w.run('rip_ob_repress_effect', c)
assert w.gate(backlash, c), 'repression does not spare it'
w.run('rip_ob_tolerate_effect', c)
assert not w.gate(backlash, c), 'toleration does'
w.run('rip_ob_repress_effect', c)
assert w.gate(backlash, c), 'repression arms the rising limit again'
c['flags']['rip_ro_raskol_settled'] = w.day
assert not w.gate(backlash, c), 'settlement stops further Old Believer risings'
cases += 1

# --- 11. wiring -------------------------------------------------------------
hooks = read('common/on_actions/RIP_religion_old_believer_on_actions.txt')
for hook in ('on_startup', 'on_yearly_pulse', 'on_religion_change'):
    assert 'rip_ob_upkeep_effect = yes' in named_block(hooks, hook), hook
history = read('common/scripted_effects/rip_church_ro_history_effects.txt')
assert 'rip_ob_begin_schism_effect = yes' in named_block(history, 'rip_church_ro_formal_raskol_effect')
assert 'rip_ob_' not in named_block(history, 'rip_church_ro_ritual_compromise_effect'), 'a compromise founds no community'
for path in ('common/scripted_effects/rip_old_believer_effects.txt', 'common/scripted_triggers/rip_old_believer_triggers.txt',
             'common/event_modifiers/rip_old_believer_modifiers.txt', 'events/RIP_OldBelievers.txt',
             'decisions/RIP_OldBelievers.txt', 'common/on_actions/RIP_religion_old_believer_on_actions.txt'):
    text = read(path)
    assert 'add_opinion' not in text, path + ': add_opinion is dropped inside else_if/else bodies of scripted effects'
    assert not re.search(r'\belse(_if)?\s*=', text), path + ': else/else_if is the trap the engine measured; use exclusive ifs'
for path in ('common/scripted_triggers/rip_old_believer_triggers.txt', 'common/scripted_effects/rip_old_believer_effects.txt',
             'events/RIP_FaithDisasters.txt', 'common/disasters/rip_faith_disasters.txt'):
    assert 'rip_ob_crisis' not in read(path), path
assert 'rip_ob_test' not in ''.join(p.read_bytes().decode('cp1252', 'replace') for p in (ROOT / 'events').glob('*.txt')), \
    'the console fixture belongs in tests/dev_tools; in events/ the game loads it'
fixture = read('tests/dev_tools/RIP_OldBelieverTest.txt')
for call in sorted(set(re.findall(r'\brip_ob_\w+_effect\b', fixture))):
    assert call in EFFECTS, 'the console fixture calls an undefined helper: ' + call
for trigger in sorted(set(re.findall(r'\brip_ob_\w+\s*=\s*yes', fixture))):
    assert trigger.split()[0] in EFFECTS or trigger.split()[0] in TRIGGERS, \
        'the console fixture reads an undefined helper: ' + trigger
ids = re.findall(r'^\s*id = (rip_ob\.\d+)', read('events/RIP_OldBelievers.txt'), re.M)
assert ids == ['rip_ob.2', 'rip_ob.3', 'rip_ob.4'] and len(set(ids)) == len(ids)
rebels = read('common/rebel_types/old_believer.txt')
assert 'dominant_religion = old_believer' in rebels and 'religion = orthodox' not in rebels
# The opening repression option has one Old Believer rebel spawn, and only in
# an eligible non-capital parish; victory there may change the majority faith.
disaster_text = read('events/RIP_FaithDisasters.txt')
assert disaster_text.count('type = old_believer_rebels') == 1
disaster_repression = next(
    dict(body)
    for key, body in EVENTS['rip_faith_disaster.1']
    if key == 'option' and dict(body)['name'] == 'rip_faith_disaster.1.a'
)
disaster_target = next(value for key, value in disaster_repression.items()
                       if key == 'random_owned_province')
assert ('rip_ro_old_believer_parish', 'yes') in dict(disaster_target)['limit']
disaster_spawn = next(value for key, value in disaster_target if key == 'spawn_rebels')
assert dict(disaster_spawn) == {'type': 'old_believer_rebels', 'size': '2'}
parish_gate = TRIGGERS['rip_ro_old_believer_parish']
assert ('is_capital', 'no') in parish_gate
assert ('is_city', 'yes') in parish_gate
assert ('OR', [('has_province_flag', 'rip_ob_community'),
               ('religion', 'old_believer')]) in parish_gate

# The other historical Old Believer rebel spawn is the 1666 council's explicit
# repression choice, not part of the Orthodox conversion wave.
russian_orthodox_text = read('events/RussianOrthodox.txt')
assert russian_orthodox_text.count('type = old_believer_rebels') == 1
council_repression = next(
    dict(body)
    for key, body in EVENTS['russian_orthodox.6']
    if key == 'option' and dict(body)['name'] == 'russian_orthodox.6.a'
)
council_target = next(value for key, value in council_repression.items()
                      if key == 'random_owned_province')
assert ('rip_ro_old_believer_parish', 'yes') in dict(council_target)['limit']

# The ordinary Old-Rite rising remains orthodox_rebels. The separate recurring
# Old-Believer rising uses the dedicated type and the same bounded parish gate.
zeal_text = read('common/scripted_effects/rip_faith_zeal_effects.txt')
assert zeal_text.count('type = old_believer_rebels') == 1
old_rite_rising = named_block(zeal_text, 'rip_ro_old_rite_rising_effect')
assert 'type = orthodox_rebels' in old_rite_rising
assert 'type = old_believer_rebels' not in old_rite_rising
old_believer_rising = named_block(zeal_text, 'rip_ro_old_believer_rising_effect')
assert 'type = old_believer_rebels' in old_believer_rising
assert 'rip_ro_old_believer_parish = yes' in old_believer_rising
cases += 1

# --- 12. the Raskol's conversion wave ---------------------------------------
# While the disaster runs, rip_ob.4 gives every Orthodox city a monthly chance to
# move to the state church or the old rite. The best matching culture tier applies.
def wave_realm(owner_culture='russian', owner_religion='russian_orthodox'):
    w, c, capital, russian, kyiv, catholic = realm(religion=owner_religion)
    c['culture'] = owner_culture
    c['disasters'] = {'rip_ro_raskol'}
    return w, c, capital, russian, kyiv, catholic


def month(w, province, first, second=0):
    """The faith one monthly pass leaves `province` when the dice show `first`, then `second`."""
    saved = (province['religion'], dict(province['flags']), dict(province['modifiers']), set(getattr(w, 'enabled', set())))
    w.rolls = [first, second]
    w.execute([('rip_ob_wave_pass_effect', 'yes')], province)
    result, flags, modifiers = province['religion'], dict(province['flags']), dict(province['modifiers'])
    province['religion'], province['flags'], province['modifiers'] = saved[0], saved[1], saved[2]
    w.enabled, w.rolls = saved[3], []
    return result, flags, modifiers


def chance(w, province):
    return sum(month(w, province, roll)[0] != 'orthodox' for roll in range(10000)) / 10000


def city(w, c, number, culture, group, religion='orthodox'):
    p = w.province(number, c, religion)
    p['culture'], p['culture_group'], p['region'] = culture, group, 'russia_region'
    return p


# 12a. one tier per city, the best match only, never a product.
w, c, capital, russian, kyiv, catholic = wave_realm('russian')
tiers = (
    (0.0150, 'the primary culture', ('russian', 'east_slavic')),
    (0.0045, 'East Slavic, whatever the Muscovite set', ('ruthenian', 'east_slavic')),
    (0.0015, 'a Polish city', ('polish', 'west_slavic')),
)
for expected, label, (culture, group) in tiers:
    assert abs(chance(w, city(w, c, 700 + int(expected * 10000), culture, group)) - expected) < 1e-9, label
w, c, capital, russian, kyiv, catholic = wave_realm('ruthenian')
for number, (culture, group, expected, label) in enumerate((
        ('ruthenian', 'east_slavic', 0.0150, 'the primary culture (a Ruthenian realm)'),
        ('russian', 'east_slavic', 0.0075, 'Muscovite'),
        ('russian_new', 'slavic', 0.0075, 'Muscovite, new set'),
        ('byelorussian', 'east_slavic', 0.0045, 'East Slavic group'),
        ('ruthenian_new', 'slavic', 0.0045, 'East Slavic outside its group (slavic)'),
        ('rusyn_new_new', 'carpathian', 0.0045, 'East Slavic outside its group (carpathian)'),
        ('uralic', 'finno_ugric', 0.0045, 'Uralic'),
        ('kazani', 'tartar', 0.0045, 'Tatar'),
        ('polish', 'west_slavic', 0.0015, 'West Slavic'),
        ('transylvanian', 'carpathian', 0.0015, 'Carpathian, not East Slavic'),
        ('lithuanian', 'baltic', 0.0015, 'Baltic')), start=800):
    assert abs(chance(w, city(w, c, number, culture, group)) - expected) < 1e-9, label
cases += 1

# The wave lasts as long as the Raskol, so the tiers decide how much of a realm it takes.
share = lambda p, years: 1 - (1 - p) ** (12 * years)
assert 0.83 < share(0.015, years['toleration']) and share(0.015, years['repression']) < 0.96
assert 0.16 < share(0.0015, years['toleration']) and share(0.0015, years['repression']) < 0.27
cases += 1

# 12b. who it moves: Orthodox cities that the owner holds, in the Muscovite jurisdiction.
w, c, capital, russian, kyiv, catholic = wave_realm()
eligible = TRIGGERS['rip_ob_wave_eligible']
assert all(w.gate(eligible, p) for p in russian + [kyiv]), 'an Orthodox city held by the owner'
assert not w.gate(eligible, catholic), 'a Catholic city is not moved'
assert not w.gate(eligible, capital), 'the state church already holds its capital'
old_rite = city(w, c, 900, 'russian', 'east_slavic', 'old_believer')
assert not w.gate(eligible, old_rite), 'an Old Believer city stays'
village = city(w, c, 901, 'russian', 'east_slavic'); village['is_city'] = False
assert not w.gate(eligible, village), 'a settlement that is not a city is not moved'
occupied = city(w, c, 902, 'russian', 'east_slavic'); occupied['controlled_by'] = 'LIT'
assert not w.gate(eligible, occupied), 'an occupied city is not moved'
w.country('LIT', 'orthodox')
abroad = w.province(903, w.countries['LIT'], 'orthodox')
assert not w.gate(eligible, abroad), 'a realm outside the Muscovite jurisdiction is not touched'
cases += 1

# 12c. where it moves them. A community leans to the old rite, any other city does
# not, and the capital never goes to the old rite.
w, c, capital, russian, kyiv, catholic = wave_realm()
community, plain = russian[0], russian[1]
w.run('rip_ob_mark_community_effect', community)
for province, expected in ((community, 60), (plain, 10)):
    split = [month(w, province, 0, roll)[0] for roll in range(100)]
    assert split.count('old_believer') == expected and split.count('russian_orthodox') == 100 - expected, (province['id'], split)
capital['religion'] = 'orthodox'
capital_dice = [month(w, capital, 0, roll)[0] for roll in range(100)]
assert set(capital_dice) == {'russian_orthodox'}, 'the capital takes the state church whatever the dice'
faith, flags, modifiers = month(w, plain, 0, 0)
assert faith == 'old_believer' and 'rip_ob_community' in flags and 'rip_ob_local_community' in modifiers, \
    'a city that takes the old rite is a community from then on'
faith, flags, modifiers = month(w, community, 0, 99)
assert faith == 'russian_orthodox' and 'rip_ob_community' in flags, 'joining the state church does not unmake a community'
w.rolls = [0, 0]
w.execute([('rip_ob_wave_pass_effect', 'yes')], plain)
assert {'old_believer'} <= getattr(w, 'enabled', set()), 'a faith has to be enabled before a city can take it'
cases += 1

# Under an Orthodox state with Muscovite jurisdiction, the same wave can still
# create Old Believer parishes, but its state-church outcome leaves them Orthodox.
w, c, capital, russian, kyiv, catholic = wave_realm(owner_religion='orthodox')
community, plain = russian[0], russian[1]
w.run('rip_ob_mark_community_effect', community)
for province, old_rite_count in ((community, 60), (plain, 10)):
    outcomes = [month(w, province, 0, roll)[0] for roll in range(100)]
    assert outcomes.count('old_believer') == old_rite_count, (province['id'], outcomes)
    assert outcomes.count('orthodox') == 100 - old_rite_count, (province['id'], outcomes)
    assert 'russian_orthodox' not in getattr(w, 'enabled', set())
faith, _, _ = month(w, plain, 0, 99)
assert faith == 'orthodox', 'the state-church outcome cannot convert an Orthodox owner’s parish'
capital_dice = [month(w, capital, 0, roll)[0] for roll in range(100)]
assert set(capital_dice) == {'orthodox'}, 'an Orthodox jurisdiction keeps its capital Orthodox'
cases += 1

# 12d. wiring: the disaster calls rip_ob.4 monthly, and the event runs only inside the Raskol.
w, c, capital, russian, kyiv, catholic = wave_realm()
capital['religion'] = 'orthodox'
wave = dict(EVENTS['rip_ob.4'])
assert wave['hidden'] == 'yes' and wave['is_triggered_only'] == 'yes' and 'option' not in wave
assert available(w, c, 'rip_ob.4')
c['disasters'] = set()
assert not available(w, c, 'rip_ob.4'), 'no Raskol, no wave'
c['disasters'] = {'rip_ro_raskol'}
before = faiths(w)
w.rolls = [9999] * 40
w.execute(wave['immediate'], c)
assert faiths(w) == before, 'the dice show nothing, so nothing moves'
w.rolls = [0, 0] * 40
w.execute(wave['immediate'], c)
after = faiths(w)
assert after[catholic['id']] == 'catholic', 'a Catholic city is never touched'
assert after[capital['id']] == 'russian_orthodox'
assert all(after[p['id']] == 'old_believer' for p in russian + [kyiv]), 'with the dice at zero every other Orthodox city moves'
assert 'rip_ob.4' in re.sub(r'#[^\n]*', '', named_block(disaster, 'on_monthly')), 'the disaster has to call the wave'
named_in = sorted(p.name for p in (ROOT / 'events').glob('*.txt') if 'rip_ob.4' in p.read_bytes().decode('cp1252', 'replace'))
assert named_in == ['RIP_OldBelievers.txt'], 'no other event may fire the wave: ' + str(named_in)
cases += 1

print(f'OLD BELIEVER PASS: {cases} source-executed cases; a community is a mark, only rip_ob.2 and the Raskol\'s '
      f'conversion wave move a city\'s faith; the policy only sets the pace of the Raskol exit (authority below 60%), '
      f'no separate crisis clock; source model, not engine evidence.')
