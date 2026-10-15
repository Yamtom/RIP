"""Execute historical branches and parish protections against live source.

This bounded interpreter is not evidence of native rendering or AI scheduling.
"""
from copy import deepcopy
from church_testlib import World, EFFECTS, TRIGGERS, parse
from clausewitz_testlib import read, named_block

events = {}
for path in ('events/RussianOrthodox.txt', 'events/RIP_RO_InstitutionalHistory.txt'):
    for kind, body in parse(read(path)):
        if kind == 'country_event' and 'title' in dict(body):
            events[dict(body)['id']] = body
EFFECTS.update(parse(read('common/scripted_effects/rip_faith_history_cleanup_effects.txt')))


class HistoryWorld(World):
    def execute(self, items, scope, root=None, prev=None):
        # Record rebel requests, not native rebel behavior or outcomes.
        for key, value in items:
            if key == 'spawn_rebels':
                scope.setdefault('rebel_requests', []).append(dict(value))
        super().execute([(k, v) for k, v in items if k != 'spawn_rebels'], scope, root, prev)

    def condition(self, key, value, scope, root, prev):
        if key == 'primary_culture': return scope.get(key) == value
        if key == 'is_capital':
            return (self.countries[scope['owner']]['capital'] == scope['id']) == (value == 'yes')
        return super().condition(key, value, scope, root, prev)

    def execute(self, items, scope, root=None, prev=None):
        # The interpreter has no rebels or unrest of its own; record where they land.
        rest = []
        for key, value in items:
            if key == 'spawn_rebels':
                scope.setdefault('rebel_requests', []).append(dict(value))
                scope.setdefault('rebels', []).append(dict(value))
            elif key == 'add_unrest': scope['unrest'] = scope.get('unrest', 0) + float(value)
            else: rest.append((key, value))
        super().execute(rest, scope, root, prev)


def setup(year=1448, religion='orthodox'):
    w = HistoryWorld(); w.year = year
    c = w.country('MOS', religion)
    c.update(primary_culture='russian', culture_group='east_slavic', num_of_cities=100,
             legitimacy=75, stability=1, normal_or_historical_nations=True)
    p = w.province(295, c, religion)
    p['region'] = 'russia_region'
    other = w.province(280, c, 'orthodox')
    catholic = w.province(281, c, 'catholic')
    return w, c, p, other, catholic


def available(w, c, event):
    return w.gate(dict(events[event])['trigger'], c)

def contains_pair(items, target):
    for key, value in items:
        if (key, value) == target:
            return True
        if isinstance(value, list) and contains_pair(value, target):
            return True
    return False


def choose(w, c, event, choice):
    body = events[event]
    if 'immediate' in dict(body): w.execute(dict(body)['immediate'], c)
    option = next(v for k, v in body if k == 'option' and dict(v)['name'] == choice)
    w.execute([(k, v) for k, v in option if k not in ('name', 'ai_chance', 'trigger')], c)


cases = 0
# Affiliation is independent of diplomatic schism and never converts a capital.
for year in (1448, 1510, 1589, 1666):
    w, c, p, other, catholic = setup(year)
    w.run('rip_faith_adopt_muscovite_church_effect', c)
    assert c['religion'] == 'russian_orthodox'
    assert p['religion'] == other['religion'] == 'orthodox'
    assert catholic['religion'] == 'catholic'
    assert 'rip_church_ro_schismatic' not in c['flags']
    cases += 1
w, c, p, other, catholic = setup()
assert available(w, c, 'russian_orthodox.1')
choose(w, c, 'russian_orthodox.1', 'russian_orthodox.1.a')
assert c['religion'] == 'russian_orthodox' and p['religion'] == other['religion'] == 'orthodox'
assert 'rip_ro_stage_autocephaly' in c['flags']
assert w.gate(TRIGGERS['rip_church_ro_jurisdiction'], c)
assert not available(w, c, 'russian_orthodox.1')
w.year = 1588
assert not available(w, c, 'russian_orthodox.2')
w.year = 1589
assert available(w, c, 'russian_orthodox.2')
choose(w, c, 'russian_orthodox.2', 'russian_orthodox.2.a')
assert c['religion'] == 'russian_orthodox' and 'rip_church_ro_provisional' in c['flags']
w.year = 1593
w.run('rip_church_ro_history_monthly_effect', c)
assert c['religion'] == 'russian_orthodox' and 'rip_church_ro_recognized' in c['flags']
assert available(w, c, 'russian_orthodox.14')
cases += 1

# Orthodox jurisdictions retain the institutional content; declining the 1448
# election still leaves the state outside Moscow's jurisdiction.
w_without_jurisdiction, c_without_jurisdiction, _, _, _ = setup()
choose(w_without_jurisdiction, c_without_jurisdiction, 'russian_orthodox.1', 'russian_orthodox.1.b')
assert c_without_jurisdiction['religion'] == 'orthodox'
assert not w_without_jurisdiction.gate(TRIGGERS['rip_church_ro_jurisdiction'], c_without_jurisdiction)
w_without_jurisdiction.year = 1589
assert not available(w_without_jurisdiction, c_without_jurisdiction, 'russian_orthodox.2')
cases += 1

# The national church events are jurisdiction-gated, not confession-gated.
province_event_3 = next(body for kind, body in parse(read('events/RussianOrthodox.txt'))
                        if kind == 'province_event' and dict(body)['id'] == 'russian_orthodox.3')
assert contains_pair(dict(province_event_3)['trigger'], ('rip_church_ro_jurisdiction', 'yes'))
for event_id in ('russian_orthodox.4', 'russian_orthodox.5', 'russian_orthodox.7',
                 'russian_orthodox.8', 'russian_orthodox.9',
                 'russian_orthodox.10', 'russian_orthodox.11', 'russian_orthodox.12'):
    assert contains_pair(dict(events[event_id])['trigger'], ('rip_church_ro_jurisdiction', 'yes')), event_id
    assert ('religion', 'russian_orthodox') not in dict(events[event_id])['trigger'], event_id
    cases += 1

# Expansion events belong to Muscovy/Russia after secure control of their targets.
for event_id in ('russian_orthodox.7', 'russian_orthodox.10', 'russian_orthodox.12'):
    trigger = dict(events[event_id])['trigger']
    assert contains_pair(trigger, ('tag', 'MOS')) and contains_pair(trigger, ('tag', 'RUS')), event_id
    assert contains_pair(trigger, ('controlled_by', 'ROOT'))
    assert contains_pair(trigger, ('is_core', 'ROOT'))
    cases += 1

# A deliberate break converts only the state and eligible core capital once.
w.run('rip_church_ro_choose_schism_effect', c)
assert c['religion'] == 'russian_orthodox' and p['religion'] == 'orthodox'
assert other['religion'] == 'orthodox' and catholic['religion'] == 'catholic'
assert not available(w, c, 'russian_orthodox.14')
before = deepcopy(c)
w.run('rip_church_ro_choose_schism_effect', c)
assert c == before
assert not other['modifiers']
cases += 1

# The book reform does not change religion; the formal council is a later gate.
for choice, internal_schism in (('russian_orthodox.6.a', True), ('russian_orthodox.6.b', True), ('russian_orthodox.6.c', False)):
    w, c, p, other, catholic = setup(1653)
    for flag in ('rip_ro_stage_autocephaly', 'rip_ro_stage_patriarchate', 'rip_church_ro_recognized'):
        c['flags'][flag] = w.day
    assert available(w, c, 'rip_ro_history.1')
    choose(w, c, 'rip_ro_history.1', 'rip_ro_history.1.a')
    assert c['religion'] == 'orthodox' and not available(w, c, 'russian_orthodox.6')
    w.year = 1666
    assert available(w, c, 'russian_orthodox.6')
    c['patriarch_authority'] = 0.5
    stability_before = c['stability']
    choose(w, c, 'russian_orthodox.6', choice)
    assert c['religion'] == p['religion'] == other['religion'] == 'orthodox'
    assert catholic['religion'] == 'catholic'
    assert ('raskol_schism' in w.flags) == internal_schism
    assert ('rip_ro_stage_raskol' in c['flags']) == internal_schism
    if choice.endswith('.a'):
        assert p['rebel_requests'] == [{'type': 'old_believer_rebels', 'size': '2'}]
        assert 'suppression_old_believers' in c['modifiers']
    if choice.endswith('.b'):
        assert 'old_believer_underground' in c['modifiers']
    assert 'rip_church_ro_schismatic' not in c['flags'], 'Raskol is not a break with other Eastern sees'
    if not internal_schism:
        assert abs(c['patriarch_authority'] - 0.4) < 1e-9
        assert c['stability'] == stability_before + 1
        assert 'rip_ro_raskol_settled' in c['flags']
        assert not available(w, c, 'russian_orthodox.6')
    cases += 1

# Raskol remains reachable without adopting the separate confession or its wave.
raskol = named_block(read('common/disasters/rip_faith_disasters.txt'), 'rip_ro_raskol')
for religion in ('orthodox', 'russian_orthodox'):
    w, c, p, other, catholic = setup(1666, religion)
    c['flags'].update(rip_ro_stage_autocephaly=w.day, rip_ro_stage_raskol=w.day)
    c.update(patriarch_authority=0.8, has_any_disaster=False)
    assert w.gate(dict(parse(named_block(raskol, 'potential')))['potential'], c)
    assert w.gate(dict(parse(named_block(raskol, 'can_start')))['can_start'], c)
    c['flags']['rip_ro_ritual_compromise'] = w.day
    assert not w.gate(dict(parse(named_block(raskol, 'potential')))['potential'], c)
    cases += 1

# A legacy Raskol-only conversion is repaired; an explicit external break stays.
for external_break in (False, True):
    w, c, p, other, catholic = setup(1667, 'russian_orthodox')
    c['flags']['rip_ro_stage_raskol'] = w.day
    if external_break:
        c['flags']['rip_church_ro_schismatic'] = w.day
    w.run('rip_church_ro_history_monthly_effect', c)
    expected = 'russian_orthodox'
    assert c['religion'] == p['religion'] == expected
    assert other['religion'] == 'orthodox' and catholic['religion'] == 'catholic'
    assert 'rip_ro_stage_raskol' in c['flags']
    cases += 1

# Only Orthodox parishes get the full/limited guarantees; expiration restores it.
w, c, p, other, catholic = setup(1653)
c['flags'].update(rip_ro_stage_autocephaly=w.day, rip_ro_stage_patriarchate=w.day)
choose(w, c, 'rip_ro_history.1', 'rip_ro_history.1.b')
w.year = 1667
assert not available(w, c, 'russian_orthodox.6')
assert not available(w, c, 'rip_ro_history.1')
assert c['religion'] == 'orthodox' and 'raskol_schism' not in w.flags
cases += 1

w, c, p, other, catholic = setup(1667, 'russian_orthodox')
c['flags']['rip_ro_stage_raskol'] = w.day
w.run('rip_church_ro_refresh_communion_effect', c)
assert 'rip_ro_shared_communion' in other['modifiers'] and not catholic['modifiers']
assert not p['modifiers']
c['modifiers']['orthodox_inquisition'] = w.day + 7300
w.run('rip_church_ro_refresh_communion_effect', c)
assert 'rip_ro_restricted_communion' in other['modifiers'] and 'rip_ro_shared_communion' not in other['modifiers']
w.day += 7301
w.run('rip_church_ro_refresh_communion_effect', c)
assert 'rip_ro_shared_communion' in other['modifiers'] and 'rip_ro_restricted_communion' not in other['modifiers']
c['flags']['rip_church_ro_schismatic'] = w.day
w.run('rip_church_ro_refresh_communion_effect', c)
assert not other['modifiers']
c['flags'].pop('rip_church_ro_schismatic')
w.run('rip_church_ro_refresh_communion_effect', c)
other['religion'] = 'catholic'
w.run('rip_church_ro_refresh_communion_effect', c)
assert not other['modifiers'], 'converted provinces cannot retain sister-church protection'
cases += 1

# Both institutional outcomes remain available to an Orthodox jurisdiction.
for religion in ('orthodox', 'russian_orthodox'):
    for choice in ('rip_ro_history.3.a', 'rip_ro_history.3.b'):
        w, c, p, other, catholic = setup(1700, religion)
        c['flags'].update(rip_ro_stage_autocephaly=w.day, rip_ro_stage_patriarchate=w.day)
        assert available(w, c, 'rip_ro_history.2')
        choose(w, c, 'rip_ro_history.2', 'rip_ro_history.2.a')
        assert not available(w, c, 'rip_ro_history.3')
        w.year = 1721
        assert available(w, c, 'rip_ro_history.3')
        choose(w, c, 'rip_ro_history.3', choice)
        assert not available(w, c, 'rip_ro_history.3')
        assert 'rip_ro_patriarchal_vacancy' not in c['modifiers']
        assert c['religion'] == religion and 'rip_church_ro_schismatic' not in c['flags']
        selected = 'rip_ro_synodal_government' if choice.endswith('.a') else 'rip_ro_preserved_patriarchate'
        assert selected in c['modifiers']
        assert not {'rip_ro_synodal_government','rip_ro_preserved_patriarchate'} <= c['modifiers'].keys()
        cases += 1

# Existing early saves are relabelled once without touching other religions.
w, c, p, other, catholic = setup(1700)
c['flags'].update(rip_ro_stage_autocephaly=w.day, rip_ro_stage_patriarchate=w.day)
choose(w, c, 'rip_ro_history.2', 'rip_ro_history.2.b')
w.year = 1721
assert not available(w, c, 'rip_ro_history.3')
assert 'rip_ro_preserved_patriarchate' in c['modifiers']
assert 'rip_ro_patriarchal_vacancy' not in c['modifiers']
cases += 1

w, c, p, other, catholic = setup(1500, 'russian_orthodox')
w.run('rip_church_ro_history_monthly_effect', c)
assert c['religion'] == p['religion'] == 'russian_orthodox' and other['religion'] == 'orthodox'
assert catholic['religion'] == 'catholic'
before = deepcopy(c)
w.run('rip_church_ro_history_monthly_effect', c)
assert c == before
cases += 1

# The Old Believers live in the Orthodox parishes, never in the relabelled capital.
# The formal council's internal Raskol does not break communion or change faith.
EFFECTS.update(parse(read('common/scripted_effects/rip_faith_zeal_effects.txt')))
parish = TRIGGERS['rip_ro_old_believer_parish']
assert ('is_city', 'yes') in parish
assert ('has_province_flag', 'rip_ob_community') in dict(parish)['OR']
assert ('religion', 'old_believer') in dict(parish)['OR']

w, c, p, other, catholic = setup(1653)
for flag in ('rip_ro_stage_autocephaly', 'rip_ro_stage_patriarchate', 'rip_church_ro_recognized'):
    c['flags'][flag] = w.day
choose(w, c, 'rip_ro_history.1', 'rip_ro_history.1.a')
w.year = 1666
c['patriarch_authority'] = 0.5
choose(w, c, 'russian_orthodox.6', 'russian_orthodox.6.a')
assert c['religion'] == p['religion'] == other['religion'] == 'orthodox'
assert 'rip_ro_stage_raskol' in c['flags'] and 'rip_church_ro_schismatic' not in c['flags']
assert 'raskol_schism' in w.flags
assert 'rebels' not in other and 'rebels' not in catholic, 'ordinary Orthodox parishes are not Old Believers'
assert p['rebels'] == [{'type': 'old_believer_rebels', 'size': '2'}]
cases += 1

w, c, p, other, catholic = setup(1667, 'russian_orthodox')
other['flags']['rip_ob_community'] = w.day
w.run('rip_ro_old_believer_rising_effect', c)
assert 'rebels' not in p and 'rebels' not in catholic and 'unrest' not in p
assert other['rebels'] == [{'type': 'old_believer_rebels', 'size': '1'}] and other['unrest'] == 3
cases += 1

# The pulse is only armed while a parish outside the capital can carry the dissent.
pulse = dict([v for k, v in EFFECTS['rip_ro_zealot_backlash_effect'] if k == 'if'][1])['limit']
w, c, p, other, catholic = setup(1667, 'russian_orthodox')
c['flags']['rip_ro_stage_raskol'] = w.day
c['flags']['rip_ob_repression'] = w.day
other['flags']['rip_ob_community'] = w.day
assert w.gate(pulse, c)
other['flags'].pop('rip_ob_community')
other['religion'] = 'catholic'
assert not w.gate(pulse, c), 'the capital alone is not a parish of the old books'
cases += 1


def walk(nodes):
    for key, value in nodes:
        yield key, value
        if isinstance(value, list):
            yield from walk(value)


faith_events = {dict(body)['id']: body for kind, body in parse(read('events/RIP_FaithDisasters.txt'))
                if kind == 'country_event'}
searches = [('russian_orthodox.6', events['russian_orthodox.6']),
            ('rip_ro_old_believer_rising_effect', EFFECTS['rip_ro_old_believer_rising_effect'])]
searches += [(e, faith_events[e]) for e in ('rip_faith_disaster.1', 'rip_faith_disaster.3', 'rip_faith_disaster.4')]
for label, body in searches:
    limits = [v for k, v in walk(body) if k == 'limit']
    assert limits, label
    for limit in limits:
        assert ('religion', 'russian_orthodox') not in limit, label + ': dissent aimed at the converted capital'
        assert ('rip_ro_old_believer_parish', 'yes') in limit, label
cases += 1

source = read('decisions/RussianOrthodoxDecisions.txt')
for decision, year in (('russification_campaign_decision',1700), ('establish_orthodox_inquisition_decision',1667)):
    assert f'is_year = {year}' in named_block(named_block(source, decision), 'potential')
for event, year in (('russian_orthodox.4',1700), ('russian_orthodox.5',1667)):
    assert ('is_year', str(year)) in dict(events[event])['trigger']
assert 'date = 1589.1.1' in read('common/religions/russian_orthodox.txt')
assert 'NOT = { has_country_flag = rip_ro_ritual_compromise }' in named_block(read('common/disasters/rip_faith_disasters.txt'), 'rip_ro_raskol')

# Reform desire is a one-time historical meter, not an automatic schism switch.
w, c, p, other, catholic = setup(1448)
choose(w, c, 'russian_orthodox.1', 'russian_orthodox.1.a')
assert c['variables']['rip_ro_reform_desire'] == 20
assert 'rip_church_ro_schismatic' not in c['flags']
w.year = 1589
choose(w, c, 'russian_orthodox.2', 'russian_orthodox.2.a')
assert c['variables']['rip_ro_reform_desire'] == 40
w.year = 1593
w.run('rip_church_ro_history_monthly_effect', c)
assert c['variables']['rip_ro_reform_desire'] == 50
w.year = 1653
choose(w, c, 'rip_ro_history.1', 'rip_ro_history.1.a')
assert c['variables']['rip_ro_reform_desire'] == 70
w.year = 1666
choose(w, c, 'russian_orthodox.6', 'russian_orthodox.6.b')
assert c['variables']['rip_ro_reform_desire'] == 90
w.year = 1700
choose(w, c, 'rip_ro_history.2', 'rip_ro_history.2.a')
assert c['variables']['rip_ro_reform_desire'] == 105
w.year = 1721
choose(w, c, 'rip_ro_history.3', 'rip_ro_history.3.b')
assert c['variables']['rip_ro_reform_desire'] == 125
assert 'rip_church_ro_schismatic' not in c['flags']
w.run('rip_church_ro_choose_schism_effect', c)
assert 'rip_church_ro_schismatic' in c['flags']
assert c['variables']['rip_ro_reform_desire'] == 125
assert not w.gate(TRIGGERS['rip_church_can_reconcile'], c)
cases += 1

# A legacy save seeds already reached milestones once, without replaying events.
w, c, p, other, catholic = setup(1721, 'russian_orthodox')
c['flags'].update(
    rip_ro_stage_autocephaly=w.day,
    rip_ro_stage_patriarchate=w.day,
    rip_church_ro_recognized=w.day,
    rip_ro_books_reformed=w.day,
    rip_ro_stage_raskol=w.day,
    rip_ro_synodal_settlement=w.day,
    rip_ro_synodal_government=w.day,
)
w.run('rip_ro_reform_desire_migrate_effect', c)
assert c['variables']['rip_ro_reform_desire'] == 125
w.run('rip_ro_reform_desire_migrate_effect', c)
assert c['variables']['rip_ro_reform_desire'] == 125
cases += 1

# A 1653 ritual compromise is not falsely migrated as the later 1666 council.
w, c, p, other, catholic = setup(1667, 'russian_orthodox')
c['flags'].update(
    rip_ro_stage_autocephaly=w.day,
    rip_ro_stage_patriarchate=w.day,
    rip_ro_ritual_compromise=w.day,
    rip_ro_raskol_settled=w.day,
)
w.run('rip_ro_reform_desire_migrate_effect', c)
assert c['variables']['rip_ro_reform_desire'] == 60
cases += 1

# Exactly 100 remains reconcilable; 101 blocks both the gate and direct effects.
for desire, can_reconcile in ((100, True), (101, False)):
    w, c, p, other, catholic = setup(1700, 'russian_orthodox')
    c.update(stability=2, dip_power=100, is_at_war=False, patriarch_authority=0.5)
    c['flags']['rip_church_ro_schismatic'] = w.day
    c['flags']['rip_ro_reform_desire_migration_done'] = w.day
    c['variables']['rip_ro_reform_desire'] = desire
    assert w.gate(TRIGGERS['rip_church_can_reconcile'], c) is can_reconcile
    if can_reconcile:
        w.run('rip_church_ro_begin_reconciliation_effect', c)
        assert 'rip_church_reconciliation_pending' in c['flags']
    else:
        w.run('rip_church_ro_recognize_effect', c)
        assert 'rip_church_ro_schismatic' in c['flags']
        assert 'rip_church_ro_recognized' not in c['flags']
cases += 1

print(f'PASS: {cases} source-executed history/communion cases; historical gates and coercion periods.')
print('LIMIT: historical alternatives are explicit game abstractions; native branches and clicks require engine evidence.')
