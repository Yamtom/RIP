"""Execute historical branches and parish protections against live source.

This bounded interpreter is not evidence of native rendering or AI scheduling.
"""
from copy import deepcopy
from church_testlib import World, EFFECTS, parse
from clausewitz_testlib import read, named_block

events = {}
for path in ('events/RussianOrthodox.txt', 'events/RIP_RO_InstitutionalHistory.txt'):
    for kind, body in parse(read(path)):
        if kind == 'country_event' and 'title' in dict(body):
            events[dict(body)['id']] = body


class HistoryWorld(World):
    def condition(self, key, value, scope, root, prev):
        if key == 'primary_culture': return scope.get(key) == value
        return super().condition(key, value, scope, root, prev)


def setup(year=1448, religion='orthodox'):
    w = HistoryWorld(); w.year = year
    c = w.country('MOS', religion)
    c.update(primary_culture='russian', culture_group='east_slavic', num_of_cities=100,
             legitimacy=75, stability=1, normal_or_historical_nations=True)
    p = w.province(295, c, religion)
    other = w.province(280, c, 'orthodox')
    catholic = w.province(281, c, 'catholic')
    return w, c, p, other, catholic


def available(w, c, event):
    return w.gate(dict(events[event])['trigger'], c)


def choose(w, c, event, choice):
    body = events[event]
    if 'immediate' in dict(body): w.execute(dict(body)['immediate'], c)
    option = next(v for k, v in body if k == 'option' and dict(v)['name'] == choice)
    w.execute([(k, v) for k, v in option if k not in ('name', 'ai_chance', 'trigger')], c)


cases = 0
# A forged/legacy milestone cannot bypass the earliest supported date.
for year, flag, allowed in ((1588,'rip_church_ro_schismatic',False),
                            (1589,'rip_church_ro_schismatic',True),
                            (1665,'rip_ro_stage_raskol',False),
                            (1666,'rip_ro_stage_raskol',True)):
    w, c, p, other, catholic = setup(year)
    c['flags'][flag] = w.day
    w.run('rip_faith_adopt_muscovite_church_effect', c)
    assert (c['religion'] == 'russian_orthodox') == allowed
    cases += 1
# Neither the old helper nor the election can convert a country before schism.
for year in (1448, 1510, 1588, 1589, 1666):
    w, c, p, other, catholic = setup(year)
    before = deepcopy(c)
    w.run('rip_faith_adopt_muscovite_church_effect', c)
    assert c == before and p['religion'] == other['religion'] == 'orthodox'
    cases += 1
w, c, p, other, catholic = setup()
assert available(w, c, 'russian_orthodox.1')
choose(w, c, 'russian_orthodox.1', 'russian_orthodox.1.a')
assert c['religion'] == p['religion'] == other['religion'] == 'orthodox'
assert not available(w, c, 'russian_orthodox.1')
w.year = 1588
assert not available(w, c, 'russian_orthodox.2')
w.year = 1589
assert available(w, c, 'russian_orthodox.2')
choose(w, c, 'russian_orthodox.2', 'russian_orthodox.2.a')
assert c['religion'] == 'orthodox' and 'rip_church_ro_provisional' in c['flags']
w.year = 1593
w.run('rip_church_ro_history_monthly_effect', c)
assert c['religion'] == 'orthodox' and 'rip_church_ro_recognized' in c['flags']
assert available(w, c, 'russian_orthodox.14')
cases += 1

# A deliberate break converts only the state and eligible core capital once.
w.run('rip_church_ro_choose_schism_effect', c)
assert c['religion'] == p['religion'] == 'russian_orthodox'
assert other['religion'] == 'orthodox' and catholic['religion'] == 'catholic'
assert not available(w, c, 'russian_orthodox.14')
before = deepcopy(c)
w.run('rip_church_ro_choose_schism_effect', c)
assert c == before
assert not other['modifiers']
cases += 1

# The book reform does not change religion; the formal council is a later gate.
for choice, separates in (('russian_orthodox.6.b', True), ('russian_orthodox.6.c', False)):
    w, c, p, other, catholic = setup(1653)
    for flag in ('rip_ro_stage_autocephaly', 'rip_ro_stage_patriarchate', 'rip_church_ro_recognized'):
        c['flags'][flag] = w.day
    assert available(w, c, 'rip_ro_history.1')
    choose(w, c, 'rip_ro_history.1', 'rip_ro_history.1.a')
    assert c['religion'] == 'orthodox' and not available(w, c, 'russian_orthodox.6')
    w.year = 1666
    assert available(w, c, 'russian_orthodox.6')
    choose(w, c, 'russian_orthodox.6', choice)
    assert (c['religion'] == 'russian_orthodox') == separates
    assert ('raskol_schism' in w.flags) == separates
    assert ('rip_ro_stage_raskol' in c['flags']) == separates
    assert 'rip_church_ro_schismatic' not in c['flags'], 'Raskol is not a break with other Eastern sees'
    if not separates:
        assert 'rip_ro_raskol_settled' in c['flags']
        assert not available(w, c, 'russian_orthodox.6')
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
c['modifiers']['suppression_old_believers'] = w.day + 7300
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
assert c['religion'] == p['religion'] == other['religion'] == 'orthodox'
assert catholic['religion'] == 'catholic'
before = deepcopy(c)
w.run('rip_church_ro_history_monthly_effect', c)
assert c == before
cases += 1

source = read('decisions/RussianOrthodoxDecisions.txt')
for decision, year in (('russification_campaign_decision',1700), ('establish_orthodox_inquisition_decision',1667)):
    assert f'is_year = {year}' in named_block(named_block(source, decision), 'potential')
for event, year in (('russian_orthodox.4',1700), ('russian_orthodox.5',1667)):
    assert ('is_year', str(year)) in dict(events[event])['trigger']
assert 'date = 1589.1.1' in read('common/religions/russian_orthodox.txt')
assert 'NOT = { has_country_flag = rip_ro_ritual_compromise }' in named_block(read('common/disasters/rip_faith_disasters.txt'), 'rip_ro_raskol')
print(f'PASS: {cases} source-executed history/communion cases; historical gates and coercion periods.')
print('LIMIT: historical alternatives are explicit game abstractions; native branches and clicks require engine evidence.')
