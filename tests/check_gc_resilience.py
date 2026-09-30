"""Greek Catholic resilience layer: eparchial sees, synod of bishops, programs, base.

Executes the real scripts with the bounded church interpreter and checks the
magnitudes against the installed vanilla. This is not an EU4 run: native
missionary progress, the yearly PA tick, AI timing and rendering are unverified.
"""
from copy import deepcopy
import io
from decimal import Decimal
import re

from church_testlib import World, TRIGGERS, EFFECTS, parse
from clausewitz_testlib import ROOT, read, named_block, keyed_blocks, normalized, vanilla_root

PROGRAMS = ('rite', 'schools', 'mission', 'synod', 'rome')
cases = 0


def checked():
    global cases
    cases += 1


class NetworkWorld(World):
    """Adds the one native trigger this layer needs beyond the church fixture."""

    def condition(self, key, value, scope, root, prev):
        if key == 'area_for_scope_province':
            fields = [(k, v) for k, v in value if k != 'type']
            members = [p for p in self.provinces.values() if p['area'] == scope['area']]
            test = all if dict(value).get('type') == 'all' else any
            return test(self.gate(fields, p, root, scope) for p in members)
        return super().condition(key, value, scope, root, prev)


def fixture():
    w = NetworkWorld()
    c = w.country('MOS', 'greek_catholic')
    seat = w.province(295, c, 'greek_catholic')
    pope = w.country('PAP', 'catholic')
    pope['opinions']['MOS'] = 100
    return w, c, seat


def link(a, b):
    a['neighbors'].add(b['id'])
    b['neighbors'].add(a['id'])


def parish(w, number, owner, faith, area, development=12):
    p = w.province(number, owner, faith)
    p.update(area=area, development=development)
    return p


def visited(w):
    return {p['id'] for p in w.provinces.values() if 'rip_church_gc_pastoral_visitation' in p['modifiers']}


def bands(c):
    return {m for m in c['modifiers'] if m.startswith('rip_church_gc_bishops_')}


def sees(w):
    return {p['id'] for p in w.provinces.values() if 'rip_church_gc_see' in p['flags']}


def programs(c):
    return {k for k in PROGRAMS if 'rip_church_gc_program_' + k in c['modifiers']}


# --- 1. A see supports missionaries in its eparchy, and nowhere else. -------
w, c, seat = fixture()
same_area = parish(w, 296, c, 'orthodox', 'a')
beside = parish(w, 297, c, 'russian_orthodox', 'b')
link(seat, beside)
far = parish(w, 298, c, 'orthodox', 'c')
foreign = parish(w, 299, w.country('POL', 'catholic'), 'orthodox', 'a')
compact = parish(w, 300, c, 'orthodox', 'a')
compact['flags']['rip_church_rite_recognized'] = 0
latin = parish(w, 301, c, 'catholic', 'a')
# The metropolitan see needs no decision and no payment; the paid decision
# only adds sees once it exists.
assert not w.gate(TRIGGERS['rip_church_gc_can_erect_see'], c)
w.run('rip_church_gc_network_monthly_effect', c)
assert (c['adm_power'], c['treasury']) == (500, 1000)
assert 'rip_church_gc_see_erected' not in c['flags']
assert sees(w) == {'295'} and 'rip_church_gc_eparchial_see' in seat['modifiers']
assert visited(w) == {'296', '297'}, visited(w)
assert bands(c) == {'rip_church_gc_bishops_1'}
assert [c['variables'][k] for k in ('rip_church_gc_sees', 'rip_church_gc_active_sees', 'rip_church_gc_see_capacity')] == [1, 1, 1]
assert not any('rip_church_gc_eparchy_marked' in p['flags'] for p in w.provinces.values())
assert 'rip_church_gc_self_government' not in c['modifiers']
snapshot = deepcopy((c, w.provinces))
w.run('rip_church_gc_network_monthly_effect', c)
assert (c, w.provinces) == snapshot, 'monthly maintenance must be idempotent'
checked()

# Conversion ends the visitation; a recognised rite never receives it.
same_area['religion'] = 'greek_catholic'
w.run('rip_church_gc_see_religion_change_effect', same_area)
assert 'rip_church_gc_pastoral_visitation' not in same_area['modifiers']
w.run('rip_church_gc_network_monthly_effect', c)
assert visited(w) == {'297'} and '300' not in visited(w)
checked()

# --- 2. Capacity, interval, one see per area and site preference. -----------
paid = deepcopy(c)
w.run('rip_church_gc_erect_see_effect', c)
assert c == paid, 'a second see needs capacity and a year'
w.day = 365
w.run('rip_church_gc_erect_see_effect', c)
assert c == paid, 'fewer than 8 Greek Catholic parishes support one see'
# Eight Greek Catholic parishes support a second see.
same_area_site = parish(w, 310, c, 'greek_catholic', 'a', 30)      # area already has a see
quiet_site = parish(w, 311, c, 'greek_catholic', 'd', 20)          # no Orthodox flock
small_flock_site = parish(w, 312, c, 'greek_catholic', 'e', 10)    # flock, low development
large_flock_site = parish(w, 313, c, 'greek_catholic', 'f', 16)    # flock, development 15+
for number, site in ((320, small_flock_site), (321, large_flock_site)):
    flock = parish(w, number, c, 'orthodox', site['area'] + '_x')
    link(site, flock)
for number in (314, 315):
    parish(w, number, c, 'greek_catholic', 'g', 5)                  # too small to host
assert sum(p['religion'] == 'greek_catholic' and p['owner'] == 'MOS' for p in w.provinces.values()) == 8
w.run('rip_church_gc_erect_see_effect', c)
assert sees(w) == {'295', '313'}, sees(w)
assert (c['adm_power'], c['treasury']) == (450, 900)
assert c['variables']['rip_church_gc_see_capacity'] == 2 and bands(c) == {'rip_church_gc_bishops_2'}
w.day = 730
w.run('rip_church_gc_erect_see_effect', c)
assert sees(w) == {'295', '313'}, 'capacity two is full'
checked()
# Each rule on its own. Capacity ladder at 8/16/24 Greek Catholic parishes, with
# eligible sites in separate areas and every interval allowed to pass.
for parishes, capacity in ((7, 1), (8, 2), (15, 2), (16, 3), (23, 3), (24, 4), (40, 4)):
    ww, cc, ss = fixture()
    for n in range(parishes - 1):
        parish(ww, 600 + n, cc, 'greek_catholic', 'cap_' + str(n), 10)
    ww.run('rip_church_gc_network_monthly_effect', cc)
    for year in range(8):
        ww.day = 365 * year
        ww.run('rip_church_gc_erect_see_effect', cc)
    assert len(sees(ww)) == capacity, (parishes, sees(ww))
    assert cc['variables']['rip_church_gc_see_capacity'] == capacity
    checked()
# The one-year interval, with capacity and sites to spare.
ww, cc, ss = fixture()
for n in range(15):
    parish(ww, 600 + n, cc, 'greek_catholic', 'gap_' + str(n), 10)
ww.run('rip_church_gc_network_monthly_effect', cc)
ww.run('rip_church_gc_erect_see_effect', cc)
ww.day = 364
ww.run('rip_church_gc_erect_see_effect', cc)
assert len(sees(ww)) == 2, 'a year between two paid sees'
ww.day = 365
ww.run('rip_church_gc_erect_see_effect', cc)
assert len(sees(ww)) == 3
checked()
# One see of ours per area; another country's see does not block ours.
ww, cc, ss = fixture()
ss['flags']['rip_church_gc_see'] = 0
rival = parish(ww, 700, cc, 'greek_catholic', 'a', 20)
elsewhere = parish(ww, 701, cc, 'greek_catholic', 'b', 20)
site = TRIGGERS['rip_church_gc_see_site']
assert not ww.gate(site, rival, cc) and ww.gate(site, elsewhere, cc)
neighbour_state = ww.country('POL', 'greek_catholic')
parish(ww, 702, neighbour_state, 'greek_catholic', 'b', 20)['flags']['rip_church_gc_see'] = 0
assert ww.gate(site, elsewhere, cc)
del ss['flags']['rip_church_gc_see']
assert ww.gate(site, rival, cc)
for defect in ('occupied', 'noncore', 'small', 'no_temple', 'latin'):
    probe = deepcopy(elsewhere)
    if defect == 'occupied': probe['controlled_by'] = 'POL'
    if defect == 'noncore': probe['core'] = 'POL'
    if defect == 'small': probe['development'] = 7
    if defect == 'no_temple': probe['buildings'] = set()
    if defect == 'latin': probe['religion'] = 'catholic'
    assert not ww.gate(site, probe, cc), defect
probe['buildings'] = {'cathedral'}
probe['religion'] = 'greek_catholic'
assert ww.gate(site, probe, cc), 'a cathedral also hosts a see'
checked()
# Preference order when the best tier is absent: flock first, then development.
for removed, expected in ((None, '312'), ('312', '311')):
    ww, cc, ss = fixture()
    for number, area, dev in ((311, 'd', 20), (312, 'e', 10)):
        parish(ww, number, cc, 'greek_catholic', area, dev)
    flock = parish(ww, 320, cc, 'orthodox', 'e_x')
    link(ww.provinces['312'], flock)
    for n in range(5):
        parish(ww, 330 + n, cc, 'greek_catholic', 'z', 5)
    ss['flags']['rip_church_gc_see'] = 0
    if removed:
        ww.provinces[removed]['buildings'] = set()
    ww.run('rip_church_gc_erect_see_effect', cc)
    assert sees(ww) == {'295', expected}, (removed, sees(ww))
    checked()

# --- 3. Occupation leaves the see vacant; the rest of the network works. -----
seat['controlled_by'] = 'POL'
w.run('rip_church_gc_network_monthly_effect', c)
assert 'rip_church_gc_vacant_see' in seat['modifiers'] and 'rip_church_gc_eparchial_see' not in seat['modifiers']
assert visited(w) == {'321'}, visited(w)
assert (c['variables']['rip_church_gc_sees'], c['variables']['rip_church_gc_active_sees']) == (2, 1)
assert bands(c) == {'rip_church_gc_bishops_1'}
seat['controlled_by'] = 'MOS'
w.run('rip_church_gc_network_monthly_effect', c)
assert 'rip_church_gc_vacant_see' not in seat['modifiers'] and 'rip_church_gc_eparchial_see' in seat['modifiers']
assert visited(w) == {'297', '321'} and bands(c) == {'rip_church_gc_bishops_2'}
checked()

# --- 4. Loss or conversion dissolves only that see. --------------------------
large_flock_site['owner'] = 'POL'
w.run('rip_church_gc_see_owner_change_effect', large_flock_site)
assert 'rip_church_gc_see' not in large_flock_site['flags'] and not large_flock_site['modifiers']
w.run('rip_church_gc_network_monthly_effect', c)
assert sees(w) == {'295'} and bands(c) == {'rip_church_gc_bishops_1'}
seat['religion'] = 'orthodox'
w.run('rip_church_gc_see_religion_change_effect', seat)
assert not sees(w) and 'rip_church_gc_eparchial_see' not in seat['modifiers']
# With every see gone the metropolitan see moves, free, to the best parish:
# 310 is developed and now has the converted 295 as its flock.
w.run('rip_church_gc_network_monthly_effect', c)
assert sees(w) == {'310'} and bands(c) == {'rip_church_gc_bishops_1'}, sees(w)
assert visited(w) == {'295'}, visited(w)
for p in w.provinces.values():
    p['buildings'] = set()
    w.run('rip_church_gc_dissolve_see_effect', p)
w.run('rip_church_gc_network_monthly_effect', c)
assert not sees(w) and not bands(c) and not visited(w), 'no eligible parish, no see'
checked()

# --- 5. Synod of bishops: exactly one income band, capped at four sees. ------
for active in range(6):
    w, c, seat = fixture()
    for n in range(active):
        p = parish(w, 400 + n, c, 'greek_catholic', 'band_' + str(n))
        p['flags']['rip_church_gc_see'] = 0
    occupied = parish(w, 450, c, 'greek_catholic', 'band_x')
    occupied.update(controlled_by='POL')
    occupied['flags']['rip_church_gc_see'] = 0
    w.run('rip_church_gc_network_monthly_effect', c)
    expected = {'rip_church_gc_bishops_' + str(min(active, 4))} if active else set()
    assert bands(c) == expected, (active, bands(c))
    assert c['variables']['rip_church_gc_active_sees'] == active
    assert c['variables']['rip_church_gc_sees'] == active + 1
    checked()

# --- 6. Self-government exactly when Rome cannot be petitioned. -------------
for case in ('supported', 'absent', 'not_catholic', 'war', 'cold', 'warm_enough'):
    for with_see in (True, False):
        w, c, seat = fixture()
        if with_see:
            seat['flags']['rip_church_gc_see'] = 0
        else:
            seat['buildings'] = set()
        if case == 'absent':
            del w.countries['PAP']
        elif case == 'not_catholic':
            w.countries['PAP']['religion'] = 'protestant'
        elif case == 'war':
            c['wars'].add('PAP')
        elif case == 'cold':
            w.countries['PAP']['opinions']['MOS'] = 49
        elif case == 'warm_enough':
            w.countries['PAP']['opinions']['MOS'] = 50
        w.run('rip_church_gc_network_monthly_effect', c)
        unavailable = case not in ('supported', 'warm_enough')
        assert ('rip_church_gc_self_government' in c['modifiers']) == (unavailable and with_see), (case, with_see)
        checked()

# --- 7. Programs: one slot, a second from three sees, interval and lapse. ----
w, c, seat = fixture()
w.run('rip_church_gc_adopt_program_rite_effect', c)
assert programs(c) == {'rite'} and abs(c['patriarch_authority'] - .8) < 1e-9
assert (c['variables']['rip_church_gc_programs'], c['variables']['rip_church_gc_program_slots']) == (1, 1)
paid = deepcopy(c)
for key in PROGRAMS:
    w.run('rip_church_gc_adopt_program_' + key + '_effect', c)
assert c == paid, 'one slot and a five-year interval'
w.day = 1825
w.run('rip_church_gc_adopt_program_schools_effect', c)
assert c == paid, 'fewer than three sees support one program'
for n in range(3):
    parish(w, 500 + n, c, 'greek_catholic', 'p' + str(n))['flags']['rip_church_gc_see'] = 0
w.run('rip_church_gc_network_monthly_effect', c)
assert c['variables']['rip_church_gc_program_slots'] == 2
w.run('rip_church_gc_adopt_program_schools_effect', c)
assert programs(c) == {'rite', 'schools'} and abs(c['patriarch_authority'] - .6) < 1e-9
assert 'rip_church_gc_program_late_schools' in c['flags'] and 'rip_church_gc_program_late_rite' not in c['flags']
w.day = 2000
w.run('rip_church_gc_adopt_program_mission_effect', c)
assert programs(c) == {'rite', 'schools'}, 'two slots are full'
# Dropping is free; the remaining program becomes the first one.
before = c['patriarch_authority']
w.run('rip_church_gc_drop_program_rite_effect', c)
assert programs(c) == {'schools'} and c['patriarch_authority'] == before
assert not any(f.startswith('rip_church_gc_program_late_') for f in c['flags'])
w.run('rip_church_gc_adopt_program_mission_effect', c)
assert programs(c) == {'schools'}, 'five years since the last adoption have not passed'
w.day = 3650
w.run('rip_church_gc_adopt_program_mission_effect', c)
assert programs(c) == {'schools', 'mission'} and 'rip_church_gc_program_late_mission' in c['flags']
# Losing a see drops the later program, never the earlier one.
w.provinces['502']['flags'].pop('rip_church_gc_see')
w.run('rip_church_gc_network_monthly_effect', c)
assert programs(c) == {'schools'} and c['variables']['rip_church_gc_program_slots'] == 1
checked()
# The order marker decides, not the listing: for every later program pick a
# first one that the unordered fallback would drop instead.
for later in PROGRAMS:
    first = 'synod' if later == 'rome' else 'rome'
    w, c, seat = fixture()
    for n in range(3):
        parish(w, 500 + n, c, 'greek_catholic', 'p' + str(n))['flags']['rip_church_gc_see'] = 0
    w.run('rip_church_gc_network_monthly_effect', c)
    w.run('rip_church_gc_adopt_program_' + first + '_effect', c)
    w.day = 1825
    w.run('rip_church_gc_adopt_program_' + later + '_effect', c)
    assert programs(c) == {first, later}
    w.run('rip_church_gc_dissolve_see_effect', w.provinces['502'])
    w.run('rip_church_gc_network_monthly_effect', c)
    assert programs(c) == {first}, (first, later, programs(c))
    checked()
# Every program pays exactly 20 PA and needs it.
for key in PROGRAMS:
    w, c, seat = fixture()
    c['patriarch_authority'] = .19
    denied = deepcopy(c)
    w.run('rip_church_gc_adopt_program_' + key + '_effect', c)
    assert c == denied, key
    c['patriarch_authority'] = .5
    w.run('rip_church_gc_adopt_program_' + key + '_effect', c)
    assert programs(c) == {key} and abs(c['patriarch_authority'] - .3) < 1e-9, key
    checked()
# An edited save with two unordered programs and one slot keeps the first listed.
w, c, seat = fixture()
for key in ('rite', 'rome'):
    c['modifiers']['rip_church_gc_program_' + key] = float('inf')
w.run('rip_church_gc_network_monthly_effect', c)
assert programs(c) == {'rite'}
checked()

# --- 8. Leaving the faith ends the network; interval flags survive. ----------
w, c, seat = fixture()
beside = parish(w, 297, c, 'orthodox', 'a')
w.run('rip_church_gc_network_monthly_effect', c)
w.run('rip_church_gc_adopt_program_synod_effect', c)
w.year = 1622
w.run('rip_church_gc_greek_college_effect', c)
w.run('rip_church_gc_propaganda_fide_effect', c)
assert {'rip_church_gc_greek_college', 'rip_church_gc_propaganda_fide'} <= set(c['modifiers'])
c['wars'].add('PAP')
w.run('rip_church_gc_network_monthly_effect', c)
assert 'rip_church_gc_self_government' in c['modifiers'] and visited(w) == {'297'}
c['religion'] = 'orthodox'
w.run('rip_church_gc_network_monthly_effect', c)
assert not sees(w) and not visited(w) and not seat['modifiers']
assert not any(m.startswith('rip_church_gc_') for m in c['modifiers']), c['modifiers']
assert 'rip_church_gc_network_active' not in c['flags']
assert 'rip_church_gc_program_adopted' in c['flags']
assert all(c['variables'][k] == 0 for k in ('rip_church_gc_sees', 'rip_church_gc_active_sees', 'rip_church_gc_programs'))
left = deepcopy((c, w.provinces))
w.run('rip_church_gc_network_monthly_effect', c)
assert (c, w.provinces) == left
checked()

# --- 9. Decisions and the synod event call the checked transactions. --------
decisions = dict(dict(parse(read('decisions/RIP_GreekCatholicNetwork.txt')))['country_decisions'])
erect = dict(decisions['rip_church_gc_erect_see'])
assert erect['effect'] == [('rip_church_gc_erect_see_effect', 'yes')]
assert erect['provinces_to_highlight'] == [('rip_church_gc_see_site', 'yes')]
assert erect['potential'] == [('religion', 'greek_catholic')]
# The decision shows the same gates the transaction rechecks in full.
shown = normalized(named_block(read('decisions/RIP_GreekCatholicNetwork.txt'), 'allow'))
full = normalized(named_block(read('common/scripted_triggers/rip_church_gc_network_triggers.txt'), 'rip_church_gc_can_erect_see'))
for gate in ('any_owned_province = { has_province_flag = rip_church_gc_see }',
             'adm_power = 50', 'treasury = 100', 'rip_church_gc_see_capacity_free = yes',
             'rip_church_gc_see_interval_passed = yes', 'any_owned_province = { rip_church_gc_see_site = yes }'):
    assert gate in shown and gate in full, gate
transaction = EFFECTS['rip_church_gc_erect_see_effect']
assert transaction[0][0] == 'if' and dict(transaction[0][1])['limit'] == [('rip_church_gc_can_erect_see', 'yes')]
synod = dict(decisions['rip_church_gc_synod_programs'])
assert synod['effect'] == [('rip_church_gc_convene_bishops_effect', 'yes')]
w, c, seat = fixture()
w.run('rip_church_gc_convene_bishops_effect', c)
assert w.events == [('MOS', 'rip_church_gc_network.1')]
c['patriarch_authority'] = .1
w.events.clear()
w.run('rip_church_gc_convene_bishops_effect', c)
assert not w.events, 'nothing to decide without authority or a program'
checked()
events = read('events/RIP_GreekCatholicNetwork.txt')
event = next(block for _, block in keyed_blocks(events, 'country_event') if 'id = rip_church_gc_network.1' in block)
options = [dict(body) for key, body in parse(event)[0][1] if key == 'option']
names = [o['name'] for o in options]
assert names == ['rip_church_gc_network.1.' + x for x in 'abcefghijkl'], names
for option, key in zip(options[:5], PROGRAMS):
    assert option['trigger'] == [('rip_church_gc_can_adopt_program_' + key, 'yes')]
    assert option['rip_church_gc_adopt_program_' + key + '_effect'] == 'yes'
for option, key in zip(options[5:10], PROGRAMS):
    assert option['trigger'] == [('has_country_modifier', 'rip_church_gc_program_' + key)]
    assert option['rip_church_gc_drop_program_' + key + '_effect'] == 'yes'
    assert dict(option['ai_chance'])['factor'] == '0'
assert set(options[10]) == {'name', 'ai_chance'}
checked()

# --- 9b. Rome: protection follows papal opinion; two paid institutions. ----
for opinion, state, expected in ((100, 'peace', True), (99, 'peace', False), (150, 'war', False),
                                 (150, 'absent', False), (150, 'protestant', False)):
    w, c, seat = fixture()
    w.countries['PAP']['opinions']['MOS'] = opinion
    if state == 'war': c['wars'].add('PAP')
    if state == 'absent': del w.countries['PAP']
    if state == 'protestant': w.countries['PAP']['religion'] = 'protestant'
    w.run('rip_church_gc_network_monthly_effect', c)
    assert ('rip_church_gc_papal_protection' in c['modifiers']) == expected, (opinion, state)
    checked()
w, c, seat = fixture()
w.run('rip_church_gc_network_monthly_effect', c)
assert 'rip_church_gc_papal_protection' in c['modifiers']
w.countries['PAP']['opinions']['MOS'] = 60
w.run('rip_church_gc_network_monthly_effect', c)
assert 'rip_church_gc_papal_protection' not in c['modifiers'], 'protection lapses with the opinion'
checked()
for act, year, price, duration in (('greek_college', 1577, (900, 475), 7300), ('propaganda_fide', 1622, (950, 450), 3650)):
    name = 'rip_church_gc_' + act
    for defect in ('early', 'cold', 'war', 'absent', 'poor', None):
        w, c, seat = fixture()
        w.year = year - 1 if defect == 'early' else year
        if defect == 'cold': w.countries['PAP']['opinions']['MOS'] = 49
        if defect == 'war': c['wars'].add('PAP')
        if defect == 'absent': del w.countries['PAP']
        if defect == 'poor': c['treasury'] = 40
        before = deepcopy(c)
        w.run(name + '_effect', c)
        if defect:
            assert c == before, (act, defect)
        else:
            assert (c['treasury'], c['dip_power']) == price and c['modifiers'][name] == duration, act
            again = deepcopy(c)
            w.run(name + '_effect', c)
            assert c == again, 'one at a time while it runs'
            w.day = duration
            w.run(name + '_effect', c)
            assert c['treasury'] < again['treasury'], 'renewable once it lapses'
        checked()

# --- 10. Static contracts: no automatic conversion, bounded magnitudes. -----
layer = [read(path) for path in (
    'common/scripted_effects/rip_church_gc_network_effects.txt',
    'common/scripted_triggers/rip_church_gc_network_triggers.txt',
    'decisions/RIP_GreekCatholicNetwork.txt',
    'events/RIP_GreekCatholicNetwork.txt')]
for text in layer:
    assert not re.search(r'\b(?:change_religion|add_reform_center|add_church_power|add_papal_influence)\s*=', normalized(text))
modifiers = dict(parse(read('common/event_modifiers/RIP_greek_catholic_network_modifiers.txt')))
payload = {name: {k: Decimal(v) for k, v in body if k != 'religion'} for name, body in modifiers.items()}
assert payload['rip_church_gc_eparchial_see'] == {'local_unrest': Decimal('-.5'), 'local_missionary_strength': Decimal('-.02')}
assert payload['rip_church_gc_vacant_see'] == {}
assert payload['rip_church_gc_pastoral_visitation'] == {'local_missionary_strength': Decimal('.02')}
for n in range(1, 5):
    assert payload['rip_church_gc_bishops_' + str(n)] == {'yearly_patriarch_authority': Decimal('.005') * n}
assert payload['rip_church_gc_self_government'] == {'yearly_patriarch_authority': Decimal('.005')}
assert payload['rip_church_gc_papal_protection'] == {'diplomatic_reputation': Decimal('.5'), 'improve_relation_modifier': Decimal('.1')}
assert payload['rip_church_gc_greek_college'] == {'yearly_patriarch_authority': Decimal('.005'), 'same_religion_advisor_cost': Decimal('-.1')}
assert payload['rip_church_gc_propaganda_fide'] == {'missionary_maintenance_cost': Decimal('-.25')}
expected_programs = {
    'rite': {'global_unrest': Decimal('-1')},
    'schools': {'idea_cost': Decimal('-.05')},
    'mission': {'global_heretic_missionary_strength': Decimal('.01')},
    'synod': {'yearly_patriarch_authority': Decimal('.005')},
    'rome': {'improve_relation_modifier': Decimal('.15')},
}
for key, value in expected_programs.items():
    assert payload['rip_church_gc_program_' + key] == value, key
banned = {'technology_cost', 'discipline', 'administrative_efficiency', 'core_creation'}
assert not banned & {k for body in payload.values() for k in body}
# This layer adds at most 3.5 PA a year: four sees, self-government, one
# program and the Greek College. Self-government and the College exclude each
# other in practice (the College needs a cordial Rome), so 3 is the real top.
ceiling = sum(payload[m]['yearly_patriarch_authority'] for m in (
    'rip_church_gc_bishops_4', 'rip_church_gc_self_government',
    'rip_church_gc_program_synod', 'rip_church_gc_greek_college'))
assert ceiling == Decimal('.035')
hooks = read('common/on_actions/zz_RIP_church_gc_network_on_actions.txt')
for hook, effect in (('on_startup', 'rip_church_gc_network_monthly_effect'),
                     ('on_monthly_pulse', 'rip_church_gc_network_monthly_effect'),
                     ('on_religion_change', 'rip_church_gc_network_monthly_effect'),
                     ('on_province_owner_change', 'rip_church_gc_see_owner_change_effect'),
                     ('on_province_religion_changed', 'rip_church_gc_see_religion_change_effect'),
                     ('on_province_religion_converted', 'rip_church_gc_see_religion_change_effect')):
    assert effect + ' = yes' in named_block(hooks, hook), hook
checked()

# --- 11. Base: a realm-wide mission field and parishes that resist. ---------
faith = named_block(read('common/religions/zz_greek_catholic.txt'), 'greek_catholic')
base = {k: Decimal(v) for k, v in parse(named_block(faith, 'country'))[0][1]}
province = {k: Decimal(v) for k, v in parse(named_block(faith, 'province'))[0][1]}
assert base == {'church_loyalty_modifier': Decimal('.05'), 'global_heretic_missionary_strength': Decimal('.01')}
assert province == {'local_missionary_strength': Decimal('-.01')}
install = vanilla_root()
if install:
    religions = (install / 'common/religions/00_religion.txt').read_text(encoding='utf-8-sig')
    vanilla = named_block(religions, 'christian')
    catholic = {k: Decimal(v) for k, v in parse(named_block(named_block(vanilla, 'catholic'), 'country'))[0][1]}
    orthodox = {k: Decimal(v) for k, v in parse(named_block(named_block(vanilla, 'orthodox'), 'province'))[0][1]}
    assert base['global_heretic_missionary_strength'] == catholic['global_heathen_missionary_strength']
    assert province == orthodox, 'Greek Catholic parishes resist conversion as Orthodox ones do'
    # Positive values in a religion's province block belong to pagan faiths only.
    positive = set()
    for path in (install / 'common/religions').glob('*.txt'):
        text = re.sub(r'#[^\n]*', '', path.read_text(encoding='utf-8-sig', errors='replace'))
        for offset, block in keyed_blocks(text, 'province'):
            value = re.search(r'local_missionary_strength\s*=\s*(-?[\d.]+)', block)
            if value and Decimal(value.group(1)) > 0:
                positive.add(re.findall(r'(?m)^\t(\w+)\s*=\s*\{', text[:offset])[-1])
    assert positive and not positive & {'catholic', 'orthodox', 'coptic', 'protestant', 'reformed'}, positive
    checked()
else:
    print('SKIP: installed vanilla unavailable; base magnitudes checked against the recorded values only')

# --- 12. Every new key is localised, and carried into the three fallbacks. --
english = read('localisation/rip_church_gc_network_l_english.yml')
entries = dict(re.findall(r'(?m)^ ([\w.]+):0 "(.*)"$', english))
needed = set(modifiers) | {'desc_' + m for m in modifiers}
needed |= {'rip_church_gc_network.1.' + x for x in 'tdabcefghijkl'}
needed |= {d + suffix for d in decisions for suffix in ('_title', '_desc')}
needed |= set(re.findall(r'tooltip = (\w+)', read('decisions/RIP_GreekCatholicNetwork.txt')))
assert needed <= set(entries), sorted(needed - set(entries))
assert not re.search(r'(?<!§)!', english), 'no exclamation marks in the church register'
for language in ('french', 'german', 'spanish'):
    carried = read('localisation/replace/zzz_rip_church_gc_network_l_' + language + '.yml')
    assert carried.startswith('l_' + language + ':')
    assert dict(re.findall(r'(?m)^ ([\w.]+):0 "(.*)"$', carried)) == entries, language
# No later-loading file may override these names; the church localisation
# generator once did exactly that for every RIP_church* modifier file.
import glob as _glob
for path in _glob.glob(str(ROOT / 'localisation' / '**' / '*_l_english.yml'), recursive=True):
    if path.endswith('rip_church_gc_network_l_english.yml'):
        continue
    other = set(re.findall(r'(?m)^ ([\w.]+):\d* "', io.open(path, encoding='utf-8-sig').read()))
    assert not other & set(entries), (path, sorted(other & set(entries))[:5])
religion_desc = read('localisation/uniate_and_raid_l_english.yml')
assert 'modest missionary advantage' not in religion_desc
assert 'resist conversion as Orthodox ones do' in religion_desc
checked()

# --- 13. What the first in-game run found: engine-level text and modifiers. --
# EU4 renders localisation through Latin-1/cp1252; anything else prints as
# "Couldn't find Latin1 character" in error.log and shows garbled in game.
import glob, io
for path in glob.glob(str(ROOT / 'localisation' / '**' / '*.yml'), recursive=True):
    for number, line in enumerate(io.open(path, encoding='utf-8-sig').read().splitlines(), 1):
        if line.lstrip().startswith('#'):
            continue
        try:
            line.replace('§', '').encode('cp1252')
        except UnicodeEncodeError as problem:
            raise AssertionError(f'{path}:{number}: EU4 cannot render {line[problem.start]!r}')
# Removing a modifier nobody defines logs "Unknown modifier-type" on every call.
defined = set()
for folder in (ROOT / 'common/event_modifiers', (vanilla_root() or ROOT) / 'common/event_modifiers'):
    for path in folder.glob('*.txt'):
        defined |= set(re.findall(r'(?m)^([A-Za-z0-9_]+)\s*=\s*\{', path.read_text(encoding='utf-8', errors='replace')))
if vanilla_root():
    for path in list((ROOT / 'common/scripted_effects').glob('rip_church_*.txt')) + list((ROOT / 'common/scripted_triggers').glob('rip_church_*.txt')):
        for name in re.findall(r'(?:remove|has)_country_modifier\s*=\s*(\w+)', normalized(path.read_text(encoding='latin-1'))):
            assert name in defined, f'{path.name}: {name} is not a defined modifier'
checked()

print(f'GC RESILIENCE PASS: {cases} source-executed and static cases; sees, synod income, programs, base.')
print('LIMIT: native missionary progress, the yearly PA tick, AI choices and EU4 rendering are unverified.')
