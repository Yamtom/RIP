"""Source-state regression: small school foundations; no generic occupation event.

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

source = read('events/UniateChurch.txt')
assert 'country_event = { id = uniate_church.18 days = 45 }' not in source
trigger_source = read('common/scripted_triggers/rip_uc_education_memory_triggers.txt')
assert 'uniate_church.18' not in events and 'uniate_church.20' not in events
assert 'rip_uc_persecution_context' not in trigger_source
assert 'rip_uc_persecution_context' not in source
assert 'rip_uc_persecution_recorded' not in source
effect_source = read('common/scripted_effects/greek_catholic_effects.txt')
assert 'greek_catholic_persecution_effect' not in effect_source
assert 'persecution_of_greek_catholics' not in effect_source
on_actions = read('common/on_actions/greek_catholic_on_actions.txt')
assert 'uniate_church.18' not in on_actions and 'uniate_church.20' not in on_actions
english_loc = read('localisation/uniate_and_raid_l_english.yml')
assert 'uniate_church.18.' not in english_loc and 'uniate_church.20.' not in english_loc
assert 'persecution_of_greek_catholics:0 "Legacy: Wartime Parish Disruption"' in english_loc
assert 'Retired inert identifier retained for old saves' in english_loc
for lang in ('french', 'german', 'spanish'):
    fallback = read(f'localisation/replace/zzz_RIP_untranslated_l_{lang}.yml')
    assert 'uniate_church.20.a:0 "Fund a local inquiry."' not in fallback
retired_modifier = normalized(named_block(
    read('common/event_modifiers/uniate_church_modifiers.txt'),
    'persecution_of_greek_catholics',
))
assert retired_modifier == 'persecution_of_greek_catholics = { }'
docs = read('docs/UC_EDUCATION_AND_REMEMBRANCE.uk.md')
assert 'будь-якого християнського окупанта іншої конфесії' in docs
assert 'Події `uniate_church.18` і `.20` вилучено' in docs
assert 'university' not in normalized(named_block(read('common/scripted_effects/greek_catholic_effects.txt'), 'establish_greek_catholic_education'))
# The decision tooltip states the payoff in words; keep it equal to the modifier.
mod = normalized(named_block(read('common/event_modifiers/uniate_church_modifiers.txt'), 'uniate_educational_network'))
assert 'advisor_pool = 1' in mod and 'advisor_cost = -0.1' in mod and 'global_missionary_strength = 0.02' in mod
tooltip = next(l for l in read('localisation/uniate_and_raid_l_english.yml').splitlines() if 'greek_catholic_education_effect_tt:0' in l)
assert '+1§! advisor pool' in tooltip and '-10%§! advisor cost' in tooltip and '+2%§! missionary strength' in tooltip
assert 'custom_tooltip = greek_catholic_education_effect_tt' in normalized(read('decisions/GreekCatholicDecisions.txt'))
print(f'PASS: {cases} school source-state cases; unsupported generic occupation and dependent remembrance events retired')
