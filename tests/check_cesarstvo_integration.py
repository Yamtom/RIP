"""Evaluate monthly rate branches from source. Does not emulate EU4 scope execution."""
import re
from clausewitz_testlib import read, named_block, keyed_blocks, normalized

source = read('common/government_mechanics/rip_kyivan_cesarstvo.txt')
eligibility = named_block(read('common/scripted_triggers/rip_cesarstvo_triggers.txt'),
                          'rip_cesar_integration_eligible')

def parse(text):
    tokens = iter(re.findall(r'[{}=]|[^\s{}=]+', text))
    def block():
        result = []
        for key in tokens:
            if key == '}':
                return result
            assert next(tokens) == '='
            value = next(tokens)
            result.append((key, block() if value == '{' else value))
        return result
    return block()[0][1]

def evaluate(items, state):
    results = []
    for key, value in items:
        if key == 'NOT':
            result = not evaluate(value, state)
        elif key == 'rip_cesar_integration_eligible':
            result = evaluate(parse(eligibility), state)
        elif key == 'any_owned_province':
            result = state['minority'] > 0
        elif key == 'check_variable':
            args = dict(value)
            variable = {'rip_cesar_minority_share':'minority',
                        'rip_cesar_excluded_share':'excluded'}[args['which']]
            result = state[variable] >= float(args['value'])
        elif key == 'has_government_power':
            args = dict(value)
            result = state[args['power_type']] >= float(args['value'])
        elif key == 'any_subject_country':
            result = state['disloyal']
        else:
            result = state[key] >= float(value)
        results.append(result)
    return all(results)

def rate(power, **changes):
    state = dict(minority=0.3, excluded=0, num_accepted_cultures=3,
                 kyivan_throne_concord=60, kyivan_peoples_gathering=60,
                 war_exhaustion=0, legitimacy=90, stability=3, disloyal=False)
    state.update(changes)
    block = named_block(source, power)
    result = float(re.search(r'base_monthly_growth = ([\d.]+)', block)[1])
    for _, branch in keyed_blocks(block, 'range_modifier'):
        if 'monthly_'+power not in branch:
            continue
        if evaluate(parse(named_block(branch, 'trigger')), state):
            result += float(re.search(r'monthly_'+power+r' = (-?[\d.]+)', branch)[1])
    return round(result, 5)

p, c = 'kyivan_peoples_gathering', 'kyivan_throne_concord'
assert rate(p, minority=0, num_accepted_cultures=0) <= 0
assert rate(p, minority=0, num_accepted_cultures=5) <= 0
assert rate(p, minority=0.09) <= 0
assert rate(p, minority=0.1, num_accepted_cultures=1) == 0.4
assert rate(p) == 0.7
assert rate(p, num_accepted_cultures=1) == 0.55
assert rate(p, excluded=0.3, kyivan_throne_concord=20) < 0
assert rate(p, stability=-3, legitimacy=0) == rate(p)
assert rate(c, excluded=0.3) < rate(c)
assert rate(c, kyivan_peoples_gathering=10) < rate(c)
assert rate(p, kyivan_throne_concord=20) < rate(p)

payoff = normalized(named_block(named_block(source, p), 'on_max_reached'))
assert 'duration = 3650' in payoff and 'duration = -1' not in payoff
assert 'remove_country_modifier = kyivan_peoples_gathered' in payoff
assert 'value = 40' in payoff and 'value = 10' in payoff
effects = normalized(read('common/scripted_effects/rip_cesarstvo_effects.txt'))
assert 'value = development who = PREV' in effects
assert 'divide_variable' in effects and 'has_owner_accepted_culture = no' in effects
assert 'NOT = { has_country_flag = rip_cesar_breakdown }' in effects
assert 'value = 20' in effects and 'value = 0.3' in effects
assert 'clr_country_flag = rip_cesar_breakdown' in effects
assert 'rip_cesar_compact_migrated' in effects
assert 'on_monthly_pulse' in read('common/on_actions/rip_cesarstvo_on_actions.txt')
print('CESARSTVO PASS: 11 rate scenarios, reward renewal, census and crisis source contracts.')
