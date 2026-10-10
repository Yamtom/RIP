"""Check the Muscovite Fervor cycle against the real scripts.

The cycle: Fervor founds mission nodes, nodes pay Fervor, Fervor keeps policies running.
A policy costs 10 to switch on and 3 a month; a node costs 10 to found and pays 3 a month;
the authority band adds 2 / 3 / 4 / 5. This test runs the source effects in the bounded church
interpreter, so the rule printed in the window, the rule in the script and the rule in the
documents cannot drift apart without a failure here.

What it proves: arithmetic, sustainable policy counts, the order in which an overdrawn pool
closes policies, where each policy modifier lands and when it is lifted.
What it cannot prove: how fast EU4 evaluates the province loops, rendering, AI behaviour in a
real campaign, or that a modifier's numbers are good. Those need a game run.
"""
from copy import deepcopy
from math import floor
import re

from church_testlib import EFFECTS, TRIGGERS, World, parse
from clausewitz_testlib import read

UPKEEP, NODE_YIELD, ACTIVATE, FOUND = 3, 3, 10, 10
BASE = {0: 2, 0.3: 3, 0.65: 4, 0.9: 5}
SLOTS = {0: 1, 0.3: 2, 0.65: 3, 0.9: 4}
POLICIES = ('war', 'mercy', 'building', 'mission')
MODIFIERS = dict((name, dict(body)) for name, body in parse(read('common/event_modifiers/RIP_church_redesign_modifiers.txt')))
cases = 0


def ro_country(authority=0.9, fervor=100, nodes=0):
    w = World()
    c = w.country('MOS', 'russian_orthodox')
    w.province(295, c, 'russian_orthodox')
    c['patriarch_authority'] = authority
    c['dlcs'] = {'Cradle of Civilization'}
    c['variables'].update(rip_church_fervor=fervor, rip_church_nodes=nodes)
    return w, c


# ---- 1. The arithmetic of one recount ---------------------------------------------------
for authority, base in BASE.items():
    for active in range(5):
        for nodes in range(3):
            w, c = ro_country(authority, nodes=nodes)
            for policy in POLICIES[:active]:
                c['flags'][f'rip_church_icon_{policy}'] = w.day
            w.run('rip_church_ro_recount_effect', c)
            v = c['variables']
            assert v['rip_church_capacity'] == SLOTS[authority], (authority, v)
            assert v['rip_church_icons'] == active
            assert v['rip_church_fervor_base'] == base
            assert v['rip_church_node_income'] == NODE_YIELD * nodes
            assert v['rip_church_fervor_income'] == base + NODE_YIELD * nodes
            assert v['rip_church_fervor_cost'] == UPKEEP * active
            assert v['rip_church_fervor_net'] == base + NODE_YIELD * nodes - UPKEEP * active
            cases += 1

# ---- 2. What can be kept for good -----------------------------------------------------
# The sustainable count is how many policies the income pays for. The design target:
# one policy with no node, two with one node, three with two (after renouncing communion),
# and never all four, whatever the authority.
def sustainable(base, nodes):
    return floor((base + NODE_YIELD * nodes) / UPKEEP)


for authority, base in BASE.items():
    assert sustainable(base, 0) == (1 if base >= 3 else 0), (base, 'no node: one policy at most')
    assert sustainable(base, 1) == (2 if base >= 3 else 1), (base, 'one node: two policies at most')
    assert sustainable(base, 2) == (3 if base >= 3 else 2), (base, 'two nodes: three policies at most')
    assert sustainable(BASE[0.9], 2) < 4, 'all four policies must never pay for themselves'
    cases += 1


# ---- 3. An overdrawn pool closes the newest policy first, and settles where the income pays ---
def settle(authority, nodes, months=600, start_fervor=100):
    """Switch on every policy the authority has a slot for, refill the pool, run months until nothing closes."""
    w, c = ro_country(authority, fervor=100)
    saved = EFFECTS['rip_church_ro_maintain_nodes_effect']
    EFFECTS['rip_church_ro_maintain_nodes_effect'] = []      # node flags need a trade map; the count is set by hand
    try:
        for policy in ('mission', 'war', 'mercy', 'building')[:SLOTS[authority]]:
            w.day += 400                                      # cooldowns are not under test here
            w.run(f'rip_church_toggle_{policy}_effect', c)
            assert c['flags'].get(f'rip_church_icon_{policy}') is not None, (authority, policy)
        c['variables']['rip_church_nodes'] = nodes
        c['variables']['rip_church_fervor'] = start_fervor
        history = []
        for month in range(months):
            w.day += 30
            before = c['variables']['rip_church_icons'] if 'rip_church_icons' in c['variables'] else 4
            w.run('rip_church_ro_monthly_effect', c)
            after = c['variables']['rip_church_icons']
            if after != before:
                history.append((month + 1, after))
        w.run('rip_church_ro_recount_effect', c)
        return c, history
    finally:
        EFFECTS['rip_church_ro_maintain_nodes_effect'] = saved


for authority, nodes, settles_at in ((0.9, 0, 1), (0.9, 1, 2), (0.9, 2, 3), (0.65, 1, 2), (0.3, 1, 2), (0.3, 0, 1)):
    c, history = settle(authority, nodes)
    assert c['variables']['rip_church_icons'] == settles_at, (authority, nodes, history, 'settles on what the income pays')
    assert c['variables']['rip_church_fervor_net'] >= 0, (authority, nodes, c['variables'])
    assert c['variables']['rip_church_fervor'] > 0, (authority, nodes, 'a settled church keeps a pool')
    # The oldest policies survive: Mission was switched on first, then war, mercy, building.
    survivors = [p for p in ('mission', 'war', 'mercy', 'building') if f'rip_church_icon_{p}' in c['flags']]
    assert survivors == ['mission', 'war', 'mercy', 'building'][:settles_at], (authority, nodes, survivors)
    assert history == [] or history[-1][1] == settles_at, (authority, nodes, history)
    cases += 1
# Four policies are a season, not a state: a full pool carries them for about a year or two (100 Fervor at
# -4 or -7 a month) and then collapses to what the income can pay, in one month, newest first.
c, history = settle(0.9, 1)
assert 20 <= history[0][0] <= 26 and history[-1][1] == 2, history
c, history = settle(0.9, 0)
assert 12 <= history[0][0] <= 15 and history[-1][1] == 1, ('no node, four policies: roughly a year', history)
cases += 2

# A short pool forgives nothing: with 12 Fervor the four policies fund themselves for three months only.
c, history = settle(0.9, 1, start_fervor=12)
assert history and history[0][0] == 4 and history[0][1] == 2, history
cases += 1

# ---- 3b. The Mission policy cannot be started without the price of its first node ----------------
# Its own upkeep would otherwise eat the income that could save for a node: with the authority band
# paying 3 and the policy costing 3, a church that switched Mission on at 10 Fervor could never found one.
for policy, need in (('war', 10), ('mercy', 10), ('building', 10), ('mission', 20)):
    w, c = ro_country(0.9, fervor=need - 0.01)
    assert not w.gate(TRIGGERS[f'rip_church_can_activate_{policy}'], c), (policy, 'one short')
    c['variables']['rip_church_fervor'] = need
    assert w.gate(TRIGGERS[f'rip_church_can_activate_{policy}'], c), (policy, 'enough')
    w.run(f'rip_church_toggle_{policy}_effect', c)
    assert c['variables']['rip_church_fervor'] == need - ACTIVATE, (policy, 'the price paid is 10 whatever the pool must hold')
    cases += 1
# A church with 20 Fervor can start Mission and found its first node in the same breath, and is then self-supporting.
# ---- 4. Switching a policy on and off ------------------------------------------------------
w, c = ro_country(0.9, fervor=25)
w.run('rip_church_toggle_war_effect', c)
assert c['variables']['rip_church_fervor'] == 25 - ACTIVATE and 'rip_church_icon_war' in c['flags']
assert c['variables']['rip_church_fervor_cost'] == UPKEEP
w.run('rip_church_toggle_war_effect', c)
assert c['variables']['rip_church_fervor'] == 25 - ACTIVATE, 'closing a policy refunds nothing'
assert c['variables']['rip_church_fervor_cost'] == 0
cases += 1

# ---- 5. Each policy lands where it was made for ---------------------------------------------
def land():
    w, c = ro_country(0.9, fervor=100)
    steppe = w.country('CRI', 'sunni')
    steppe['reforms'].add('steppe_horde')
    steppe['technology_group'] = 'nomad_group'
    other = w.country('POL', 'catholic')
    places = {}
    def province(number, name, owner=c, religion='russian_orthodox', **fields):
        p = w.province(number, owner, religion)
        p.update(fields)
        places[name] = p
        return p
    province(300, 'steppe_terrain', terrain='steppe')
    province(301, 'steppe_border', neighbors={'400'})
    province(302, 'interior')
    province(303, 'volga', religion='sunni', area='kazan_area')
    province(304, 'siberia', religion='orthodox', region='west_siberia_region')
    province(305, 'has_cathedral', buildings={'temple', 'cathedral'})
    province(306, 'town', is_city=False, religion='animism', area='kazan_area', terrain='steppe')
    province(307, 'polish_border', neighbors={'401'})
    province(400, 'tatar', owner=steppe, religion='sunni')
    province(401, 'polish', owner=other, religion='catholic')
    return w, c, places, steppe


def lands(w, places, modifier):
    """Provinces of MOS that carry an unexpired copy of the modifier on the world's clock."""
    return {name for name, p in places.items() if p['modifiers'].get(modifier, -1) > w.day and p['owner'] == 'MOS'}


w, c, places, steppe = land()
for policy in POLICIES:
    w.run(f'rip_church_toggle_{policy}_effect', c)
    assert f'rip_church_icon_{policy}' in c['flags']
frontier = lands(w, places, 'rip_church_frontier_watch')
assert frontier == {'steppe_terrain', 'steppe_border'}, frontier
eastern = lands(w, places, 'rip_church_eastern_clemency')
assert eastern == {'volga', 'siberia'}, ('a town is not a province to govern, a Polish border is not the east', eastern)
cathedral = lands(w, places, 'rip_church_cathedral_drive')
assert 'has_cathedral' not in cathedral and 'interior' in cathedral and 'volga' not in cathedral, cathedral
preaching = lands(w, places, 'rip_church_preaching')
assert preaching == {'volga'}, ('settled provinces of another faith, never Orthodox ones', preaching)
assert 'rip_church_icon_war_steppe' not in c['modifiers'], 'no war, no wartime bonus'
cases += 4

# A war with a steppe power adds the wartime bonus at the next sync; peace takes it away.
steppe['wars'].add('MOS')
w.run('rip_church_ro_sync_policies_effect', c)
assert c['modifiers']['rip_church_icon_war_steppe'] == float('inf')
other_war = w.country('LIT', 'orthodox')
steppe['wars'].discard('MOS')
other_war['wars'].add('MOS')
w.run('rip_church_ro_sync_policies_effect', c)
assert 'rip_church_icon_war_steppe' not in c['modifiers'], 'only a steppe power counts'
steppe['wars'].add('MOS')
w.run('rip_church_ro_sync_policies_effect', c)
w.run('rip_church_toggle_war_effect', c)                        # closing the policy lifts everything at once
assert 'rip_church_icon_war_steppe' not in c['modifiers'] and not lands(w, places, 'rip_church_frontier_watch')
assert lands(w, places, 'rip_church_preaching') == {'volga'}, 'another policy is untouched'
cases += 3

# Closing each policy lifts its own land modifier and nothing else.
for policy, modifier in (('mercy', 'rip_church_eastern_clemency'), ('building', 'rip_church_cathedral_drive'),
                         ('mission', 'rip_church_preaching')):
    assert lands(w, places, modifier), (policy, 'was laid')
    w.run(f'rip_church_toggle_{policy}_effect', c)
    assert not lands(w, places, modifier), (policy, 'lifted')
    cases += 1

# A province that changes hands or faith loses what the old owner laid on it.
w, c, places, steppe = land()
w.run('rip_church_toggle_war_effect', c)
assert lands(w, places, 'rip_church_frontier_watch')
steppe_province = places['steppe_terrain']
steppe_province['owner'] = 'CRI'
w.run('rip_church_province_change_effect', steppe_province)
assert 'rip_church_frontier_watch' not in steppe_province['modifiers']
cases += 1

# Every land modifier is a province modifier and every marker is a country one: no key crosses over.
LOCAL = {'rip_church_frontier_watch', 'rip_church_eastern_clemency', 'rip_church_cathedral_drive',
         'rip_church_preaching', 'rip_church_node_courtyards'}
for name in LOCAL:
    assert all(key.startswith(('local_', 'province_')) for key in MODIFIERS[name]), (name, MODIFIERS[name])
assert not any(key.startswith(('local_', 'province_')) for key in MODIFIERS['rip_church_icon_war_steppe'])
for policy in POLICIES:
    assert MODIFIERS[f'rip_church_icon_{policy}'] == {}, 'a policy marker carries no number of its own'
cases += 1

# ---- 6. Mission nodes: found, pay, carry the parishes, close -----------------------------------
def node_world(fervor=50):
    w = World()
    c = w.country('MOS', 'russian_orthodox')
    c['dlcs'].add('Cradle of Civilization')
    c['patriarch_authority'] = 0.9
    c['variables']['rip_church_fervor'] = fervor
    c['flags']['rip_church_icon_mission'] = w.day
    parish = w.province(295, c, 'russian_orthodox')
    parish['flags']['rip_church_ro_connected@MOS'] = w.day
    cathedral = w.province(296, c, 'russian_orthodox')
    cathedral.update(buildings={'cathedral'})
    cathedral['flags']['rip_church_ro_connected@MOS'] = w.day
    bare = w.province(297, c, 'russian_orthodox')
    bare.update(buildings=set())
    bare['flags']['rip_church_ro_connected@MOS'] = w.day
    parish['neighbors'] |= {'296', '297'}
    cathedral['neighbors'].add('295')
    bare['neighbors'].add('295')
    cut_off = w.province(298, c, 'russian_orthodox')                  # a temple, but not linked to the capital
    other = w.country('KAZ', 'sunni')
    anchor = w.province(33, other, 'russian_orthodox')
    anchor['traders'].add('MOS')
    anchor['shares']['MOS'] = 50
    target = w.province(34, other, 'sunni')
    target['neighbors'].add('295')
    w.from_scope = anchor
    return w, c, {'parish': parish, 'cathedral': cathedral, 'bare': bare, 'cut_off': cut_off, 'anchor': anchor, 'target': target}


w, c, p = node_world(fervor=FOUND - 0.01)
assert not w.gate(TRIGGERS['rip_church_node_novgorod_can_open'], c), 'a node needs the whole price in hand'
w, c, p = node_world(fervor=FOUND)
assert w.gate(TRIGGERS['rip_church_node_novgorod_can_open'], c)
w.run('rip_church_node_novgorod_toggle_effect', c)
v = c['variables']
assert 'rip_church_node_novgorod' in c['flags'] and v['rip_church_fervor'] == 0, 'founding costs exactly 10, once'
assert v['rip_church_nodes'] == 1 and v['rip_church_node_income'] == NODE_YIELD
assert v['rip_church_fervor_income'] == BASE[0.9] + NODE_YIELD
assert lands(w, p, 'rip_church_node_courtyards') == {'parish', 'cathedral'}, (
    'every connected parish with a temple or cathedral carries the node', lands(w, p, 'rip_church_node_courtyards'))
assert p['cut_off']['modifiers'] == {} and p['bare']['modifiers'] == {} and p['target']['modifiers'] == {}
cases += 3

w.run('rip_church_ro_monthly_effect', c)
assert c['variables']['rip_church_fervor'] == BASE[0.9] + NODE_YIELD - UPKEEP, 'one node and the Mission policy it needs: +5 net'
w.run('rip_church_node_novgorod_toggle_effect', c)               # closing: the courtyards go, no refund
assert 'rip_church_node_novgorod' not in c['flags'] and not lands(w, p, 'rip_church_node_courtyards')
assert c['variables']['rip_church_fervor'] == BASE[0.9] + NODE_YIELD - UPKEEP
assert c['variables']['rip_church_fervor_income'] == BASE[0.9]
cases += 2

# The whole start: 20 Fervor, Mission (10), the first node (10), and the church pays for itself from then on.
w, c, p = node_world(fervor=20)
c['flags'].pop('rip_church_icon_mission')
w.run('rip_church_toggle_mission_effect', c)
assert 'rip_church_icon_mission' in c['flags'] and c['variables']['rip_church_fervor'] == 10
assert w.gate(TRIGGERS['rip_church_node_novgorod_can_open'], c), 'the 10 left is exactly the price of a node'
w.run('rip_church_node_novgorod_toggle_effect', c)
assert c['variables']['rip_church_fervor'] == 0 and c['variables']['rip_church_nodes'] == 1
for month in range(6):
    w.day += 30
    w.run('rip_church_ro_monthly_effect', c)
assert c['variables']['rip_church_fervor'] == 6 * (BASE[0.9] + NODE_YIELD - UPKEEP), 'Mission and its node: net +5 at this authority'
assert 'rip_church_icon_mission' in c['flags'] and 'rip_church_node_novgorod' in c['flags']
cases += 1

# The same start at the middle authority band: Mission and the node cancel, the pool simply holds.
w, c, p = node_world(fervor=20)
c['patriarch_authority'] = 0.3
c['flags'].pop('rip_church_icon_mission')
w.run('rip_church_toggle_mission_effect', c)
w.run('rip_church_node_novgorod_toggle_effect', c)
for month in range(12):
    w.day += 30
    w.run('rip_church_ro_monthly_effect', c)
assert c['variables']['rip_church_fervor_net'] == BASE[0.3] + NODE_YIELD - UPKEEP == 3
assert 'rip_church_icon_mission' in c['flags'] and 'rip_church_node_novgorod' in c['flags']
cases += 1

# A node whose trade power falls below the line closes at the next monthly upkeep and its courtyards with it.
w, c, p = node_world()
w.run('rip_church_node_novgorod_toggle_effect', c)
assert 'rip_church_node_novgorod' in c['flags']
p['anchor']['shares']['MOS'] = 49
w.run('rip_church_ro_monthly_effect', c)
assert 'rip_church_node_novgorod' not in c['flags'] and not lands(w, p, 'rip_church_node_courtyards')
assert c['variables']['rip_church_nodes'] == 0 and c['variables']['rip_church_node_income'] == 0
cases += 1

# Dropping the Mission policy closes every node and lifts every courtyard.
w, c, p = node_world()
w.run('rip_church_node_novgorod_toggle_effect', c)
assert lands(w, p, 'rip_church_node_courtyards')
w.run('rip_church_toggle_mission_effect', c)
assert 'rip_church_icon_mission' not in c['flags'] and 'rip_church_node_novgorod' not in c['flags']
assert not lands(w, p, 'rip_church_node_courtyards') and c['variables']['rip_church_nodes'] == 0
cases += 1

# One node is the limit; a schismatic state may found a second. (Both anchors need their own parish and trade.)
w, c, p = node_world(fervor=100)
second = w.province(1082, w.countries['KAZ'], 'sunni')
second['traders'].add('MOS'); second['shares']['MOS'] = 60
w.run('rip_church_node_novgorod_toggle_effect', c)
w.from_scope = second
assert not w.gate(TRIGGERS['rip_church_node_kazan_can_open'], c), 'one node is the limit'
c['flags']['rip_church_ro_schismatic'] = w.day
# the second node still needs its own parish, target and trade share; the fixture models one node only
assert w.gate(TRIGGERS['rip_church_node_kazan_can_open'], c) == w.gate(TRIGGERS['rip_church_node_kazan_eligible'], c)
cases += 1

print(f'PASS: {cases} Muscovite Fervor cycle cases (arithmetic, sustainable counts, drain order, policy land, node economy)')
print('LIMIT: bounded interpreter over the real source effects; EU4 loop cost, rendering and campaign balance unverified.')
