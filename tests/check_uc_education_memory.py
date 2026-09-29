"""Source-state regression: small school foundations and evidenced remembrance.

Uses the bounded church interpreter, not EU4 runtime or AI scheduling.
"""
from copy import deepcopy
from church_testlib import fixture, TRIGGERS, EFFECTS, parse
from clausewitz_testlib import read, named_block, normalized

TRIGGERS.update(parse(read('common/scripted_triggers/rip_uc_education_memory_triggers.txt')))
EFFECTS.update(parse(read('common/scripted_effects/greek_catholic_effects.txt')))
events = {dict(b)['id']: dict(b) for k, b in parse(read('events/UniateChurch.txt'))
          if k == 'country_event'}
school = events['uniate_church.6']
martyrs = events['uniate_church.20']
cases = 0
for faith, patron, allowed in [('greek_catholic', False, True), ('catholic', True, True),
                              ('catholic', False, False), ('orthodox', False, False)]:
    w, c, p = fixture(faith)
    p['religion'] = 'greek_catholic'
    c.update(adm_power=50, treasury=75)
    if patron:
        c['flags']['rip_church_supports_union'] = w.day
    assert w.gate(school['trigger'], c) == allowed
    before = deepcopy(c)
    buildings = deepcopy(p['buildings'])
    w.run('establish_greek_catholic_education', c)
    if allowed:
        assert (c['adm_power'], c['treasury']) == (0, 0)
        assert 'uniate_education_established' in c['flags']
        assert not w.gate(school['trigger'], c)
    else:
        assert c == before
    assert c['religion'] == faith and p['buildings'] == buildings
    after = deepcopy(c)
    w.run('establish_greek_catholic_education', c)
    assert c == after  # No double payment/reward across event and decision.
    cases += 1

for failure in ('poor', 'adm', 'occupied', 'wrong_faith', 'no_church', 'war'):
    w, c, p = fixture('greek_catholic')
    if failure == 'poor': c['treasury'] = 74
    if failure == 'adm': c['adm_power'] = 49
    if failure == 'occupied': p['controlled_by'] = 'PAP'
    if failure == 'wrong_faith': p['religion'] = 'orthodox'
    if failure == 'no_church': p['buildings'] = set()
    if failure == 'war': c['is_at_war'] = True
    before = deepcopy(c)
    assert not w.gate(school['trigger'], c), failure
    w.run('establish_greek_catholic_education', c)
    assert c == before, failure
    cases += 1

w, c, p = fixture('greek_catholic')
p['buildings'] = {'cathedral'}
assert w.gate(school['trigger'], c)  # Upgrading a temple must not close the path.
# Declining the event closes the popup but preserves the paid decision.
c['flags']['uniate_education_established'] = w.day
assert not w.gate(school['trigger'], c)
assert w.gate([('rip_uc_can_found_schools', 'yes')], c)
cases += 2

for i in range(5): w.province(500 + i, c, 'greek_catholic')
assert not w.gate(martyrs['trigger'], c)
c['flags']['suffered_orthodox_persecution'] = w.day
assert not w.gate(martyrs['trigger'], c)  # Legacy neighbour hostility is insufficient.
c['flags']['rip_uc_persecution_recorded'] = w.day
assert w.gate(martyrs['trigger'], c)
c['flags']['greek_catholic_martyrs_honored'] = w.day
assert not w.gate(martyrs['trigger'], c)
cases += 4

source = read('events/UniateChurch.txt')
assert 'country_event = { id = uniate_church.18 days = 45 }' not in source
context = normalized(named_block(read('common/scripted_triggers/rip_uc_education_memory_triggers.txt'), 'rip_uc_persecution_context'))
assert 'controller = {' in context and 'war_with = ROOT' in context
recording = dict(events['uniate_church.18']['immediate'])['if']
assert dict(recording)['limit'] == [('rip_uc_persecution_context', 'yes')]
assert ('set_country_flag', 'rip_uc_persecution_recorded') in recording
assert ('set_country_flag', 'rip_uc_persecution_recorded') in EFFECTS['greek_catholic_persecution_effect']

martyr_body = next(b for k, b in parse(source)
                   if k == 'country_event' and dict(b)['id'] == 'uniate_church.20')
cause, memorial = [b for k, b in martyr_body if k == 'option']
assert 'trigger' not in dict(memorial)
for state in ('ready', 'poor', 'no_pope', 'war_with_pope'):
    w, c, p = fixture('greek_catholic')
    c.update(treasury=50, dip_power=25)
    if state == 'poor': c['treasury'] = 49
    if state == 'no_pope': del w.countries['PAP']
    if state == 'war_with_pope': c['wars'].add('PAP')
    assert w.gate(dict(cause)['trigger'], c) == (state == 'ready')
    before = (c['treasury'], c['dip_power'])
    w.execute([(k, v) for k, v in cause if k not in ('name', 'trigger', 'ai_chance')], c, c, None)
    if state == 'ready':
        assert (c['treasury'], c['dip_power']) == (0, 0)
        assert 'rip_uc_beatification_cause_supported' in c['flags']
    else:
        assert (c['treasury'], c['dip_power']) == before
        assert 'rip_uc_beatification_cause_supported' not in c['flags']
    cases += 1
for lang, path in [('english', 'localisation/uniate_and_raid_l_english.yml')] + [
    (lang, f'localisation/replace/zzz_RIP_untranslated_l_{lang}.yml') for lang in ('french', 'german', 'spanish')]:
    loc = read(path)
    assert 'uniate_church.20.a:0 "Support the beatification cause."' in loc
assert 'university' not in normalized(named_block(read('common/scripted_effects/greek_catholic_effects.txt'), 'establish_greek_catholic_education'))
print(f'PASS: {cases} school/remembrance source-state cases; occupation record, shared payment, no automatic university or canonization')
