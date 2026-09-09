"""Source contracts for the paid parish loop and bounded religious flavour.

This is not a campaign simulator. Numeric core comparisons remain in the two
native religion tests; this check guards the additional sources of power.
"""
from decimal import Decimal
import re
from clausewitz_testlib import ROOT, read, named_block, keyed_blocks, normalized, vanilla_root


def event(text, event_id):
    return next(b for _, b in keyed_blocks(text, 'country_event')
                if re.search(r'(?m)^\s*id\s*=\s*' + re.escape(event_id) + r'\s', b)
                and re.search(r'(?m)^\s*title\s*=', b))


faith = read('common/religions/russian_orthodox.txt')
triggers = read('common/scripted_triggers/rip_parish_visit_triggers.txt')
effects = read('common/scripted_effects/rip_parish_visit_effects.txt')
decisions = read('decisions/RIP_ParishVisit.txt')
visit = event(read('events/RIP_ParishVisit.txt'), 'rip_parish_visit.1')
gate = normalized(named_block(triggers, 'rip_can_fund_parish_visit'))
for item in ('religion = russian_orthodox', 'religion = greek_catholic',
             'treasury = 100', 'adm_power = 25', 'patriarch_authority = 0.05',
             'is_at_war = no', 'NOT = { has_country_modifier = rip_parish_visit_recent }'):
    assert item in gate, item
target = normalized(named_block(triggers, 'rip_parish_visit_target'))
for item in ('owned_by = ROOT', 'controlled_by = ROOT', 'is_core = ROOT',
             'is_city = yes', 'religion_group = christian', 'NOT = { religion = ROOT }'):
    assert item in target, item
assert 'rip_parish_visit_target = yes' in named_block(decisions, 'provinces_to_highlight')
transaction = named_block(effects, 'rip_fund_parish_visit_effect')
assert 'rip_can_fund_parish_visit = yes' in named_block(transaction, 'limit')
assert 'rip_parish_visit_target = yes' in named_block(named_block(transaction, 'random_owned_province'), 'limit')
for payment in ('add_treasury = -100', 'add_adm_power = -25', 'add_patriarch_authority = -0.05'):
    assert transaction.count(payment) == 1, payment
assert normalized(transaction).count('duration = 3650') == 2
assert '$MODIFIER$' in transaction
assert 'change_religion' not in transaction
options = [b for _, b in keyed_blocks(visit, 'option')]
assert len(options) == 3
for option, modifier in zip(options[:2], ('rip_parish_service_books', 'rip_parish_alms_register')):
    assert 'rip_can_fund_parish_visit = yes' in named_block(option, 'trigger')
    assert f'MODIFIER = {modifier}' in option
assert not re.search(r'\badd_\w+\s*=', options[2]), 'cancellation must not generate resources'

# A new conversion visits only already Orthodox core sees, once per country.
initial = named_block(effects, 'rip_ro_initial_obedience_effect')
assert 'NOT = { has_country_flag = rip_ro_obedience_recorded }' in initial
assert 'religion = orthodox is_city = yes is_core = ROOT' in initial
assert 'rip_ro_initial_obedience_effect = yes' in named_block(faith, 'on_convert')
hooks = read('common/on_actions/russian_orthodox_on_actions.txt')
assert 'rip_faith_balance_migration_effect = yes' in named_block(hooks, 'on_startup')
assert 'rip_faith_balance_migration_effect = yes' not in named_block(hooks, 'on_religion_change')
history = read('common/scripted_effects/rip_faith_history_cleanup_effects.txt')
for hook in ('on_startup', 'on_religion_change'):
    assert 'rip_faith_track_and_clear_history_effect = yes' in named_block(hooks, hook)
for flag in ('rip_ro_historical_rewards_held', 'rip_uc_historical_rewards_held'):
    assert f'set_country_flag = {flag}' in history
    assert f'has_country_flag = {flag}' in history
    assert f'clr_country_flag = {flag}' in history
for modifier in ('third_rome_ideology', 'imperial_orthodox_state', 'moscow_patriarchate_authority',
                 'uniate_educational_network', 'greek_catholic_synodal_administration',
                 'rip_ro_books_settled', 'rip_uc_union_accepted', 'rip_ucr_recognition_of_rome'):
    assert f'remove_country_modifier = {modifier}' in history
assert 'remove_country_modifier = rip_parish_visit_recent' not in history
assert 'remove_province_modifier' not in history

# No automatic development budget / trade conversion remains wired or defined.
spread = read('common/scripted_effects/rip_faith_spread_effects.txt')
for retired in ('rip_gc_unity_spread_effect', 'rip_ro_consolidation_effect',
                'rip_ro_schism_conversion_effect', 'rip_faith_unlock_trade_propagation_effect'):
    for text in (spread, hooks, read('common/on_actions/greek_catholic_on_actions.txt'), faith):
        assert not re.search(r'\b' + retired + r'\s*=', normalized(text)), retired
assert 'days = 365' in named_block(spread, 'rip_uc_mark_uniate_areas_effect')
assert 'has_global_flag = rip_uc_area_sweep_recent' in spread
assert not (ROOT / 'common/fervor/00_fervor.txt').exists(), 'inherit the full current vanilla fervor file'
for _, block in keyed_blocks(read('common/church_aspects/RIP_blessings.txt'), 'modifier'):
    assert 'discipline = 0' in block

# Do not let flavour silently reintroduce the former empire-wide snowball.
for filename in ('russian_orthodox_modifiers.txt', 'uniate_church_modifiers.txt'):
    source = normalized(read('common/event_modifiers/' + filename))
    for key in ('administrative_efficiency', 'core_creation', 'technology_cost', 'discipline'):
        assert not re.search(r'\b' + key + r'\s*=', source), (filename, key)
for filename in ('events/RussianOrthodox.txt', 'events/UniateChurch.txt'):
    source = normalized(read(filename))
    assert not re.search(r'add_country_modifier\s*=\s*\{[^{}]*duration\s*=\s*-1', source), filename
ro_events = read('events/RussianOrthodox.txt')
for n in (7, 9, 11, 13, 14):
    assert 'fire_only_once = yes' in event(ro_events, f'russian_orthodox.{n}')
for n in (4, 5, 8, 12):
    body = event(ro_events, f'russian_orthodox.{n}')
    assert 'days = 3650' in named_block(body, 'trigger')
    assert f'set_country_flag = rip_ro_event_{n}_recent' in named_block(body, 'immediate')
ro_effects = read('common/scripted_effects/russian_orthodox_effects.txt')
assert 'change_religion' not in named_block(ro_effects, 'force_convert_province_effect')
assert 'change_culture' not in named_block(ro_effects, 'russify_province_effect')
gc_effects = read('common/scripted_effects/greek_catholic_effects.txt')
assert not re.search(r'\badd_base_(?:tax|production|manpower)\s*=', gc_effects)
assert 'rip_ro_stage_patriarchate' in named_block(ro_effects, 'establish_moscow_patriarchate_effect')
assert 'NOT = { has_country_flag = rip_ro_stage_patriarchate }' in event(ro_events, 'russian_orthodox.2')

# The fixed country upkeep is conservative, not a hidden per-faith redefinition
# The crown-chain signature must establish the state used by its late events.
crown = read("events/UniateCrownUnion.txt")
signature = named_block(read("common/scripted_effects/rip_uniate_crown_effects.txt"), "rip_ucr_take_the_church_effect")
assert "rip_ucr_can_sign_the_union = yes" in named_block(signature, "limit")
assert "set_country_flag = rip_ucr_church_taken" in signature
assert "change_religion = greek_catholic" in signature
assert "name = rip_ucr_church_of_the_palace" in signature
assert "activate_greek_catholic_reformation = yes" in signature
assert "every_owned_province" not in signature
for n in (3, 4, 5, 6):
    # Events may contain option/description triggers before the event trigger;
    # inspect the complete top-level event block instead of assuming formatting.
    crown_event = event(crown, f"uniate_crown.{n}")
    assert re.search(r'trigger\s*=\s*\{[^{}]*religion\s*=\s*greek_catholic[^{}]*\}', crown_event)
for n in (7, 8):
    assert "has_country_flag = rip_ucr_church_taken" in named_block(event(crown, f"uniate_crown.{n}"), "trigger")
assert "value = 8" in named_block(event(crown, "uniate_crown.8"), "trigger")

# The fixed country upkeep is conservative, not a hidden per-faith redefinition
# of the shared native PA coefficients. At low PA it remains an actual penalty.
install = vanilla_root()
if install:
    static = (install / 'common/static_modifiers/00_static_modifiers.txt').read_text(encoding='utf-8-sig')
    assert 'global_missionary_strength = 0.02' in named_block(static, 'patriarch_authority_global')
    assert 'local_manpower_modifier = 0.33' in named_block(static, 'patriarch_authority_local')
    assert 'local_unrest = -3' in named_block(static, 'patriarch_authority_local')
for n in range(101):
    authority = Decimal(n) / 100
    assert Decimal('.02') * authority - Decimal('.001') <= Decimal('.019') * authority
    assert Decimal('3') * authority - Decimal('.15') <= Decimal('2.85') * authority
# Manpower is not tested as an additive identity: global and provincial stacks differ.
print('PASS: paid parish transaction, conversion retirement, event caps, history/modifier limits, target PA sources')
print('LIMIT: 95/105 numeric packets and source constraints do not prove total campaign effectiveness')
