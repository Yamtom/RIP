"""Contracts for retiring the artificial Union centre and Curia economy."""
from clausewitz_testlib import ROOT, read

triggers = read('common/scripted_triggers/rip_church_gc_curia_triggers.txt')
effects = read('common/scripted_effects/rip_church_gc_curia_effects.txt')
controls = read('common/custom_gui/RIP_church_controls.txt')
features = read('common/custom_gui/RIP_church_gc_features.txt')
gui_source = read('interface/countryreligionview.gui')
gui_builder = read('tools/build_church_gui.py')
loc_builder = read('tools/build_church_localisation.py')
lifecycle = read('common/scripted_effects/rip_church_lifecycle_effects.txt')
religion_events = read('events/UniateChurch.txt')
union_decisions = read('decisions/GreekCatholicDecisions.txt')
crown_effect = read('common/scripted_effects/rip_uniate_crown_effects.txt')
on_actions = read('common/on_actions/greek_catholic_on_actions.txt')

# The old balance, Standing store, purchasable petition menu and bonuses are
# not connected to any live trigger, effect, GUI binding or generator.
for source in (triggers, effects, controls, features, gui_source, gui_builder):
    for retired in ('rip_church_gc_petition_', 'rip_church_gc_can_donate',
                    'rip_church_gc_donate_effect', 'rip_church_communion.GetValue',
                    'rip_church_papal_standing.GetValue',
                    'rip_church_standing_income.GetValue'):
        assert retired not in source, retired
assert "custom+=defined('GetChurchCuriaRate'" not in loc_builder
assert "custom+=defined('GetChurchDonationState'" not in loc_builder
assert "custom+=defined('GetChurchCuriaPrivilege'" not in loc_builder
assert 'for key in list(DATA)' in loc_builder
assert not (ROOT / 'common/event_modifiers/RIP_church_gc_curia_modifiers.txt').exists()

# A Curia visit remains only as a limited diplomatic audience; no invented
# electoral standing or authority payment is attached to it.
assert 'rip_church_gc_can_depute_to_curia = {' in triggers
assert 'treasury = 50' in triggers and 'patriarch_authority' not in triggers
assert 'add_treasury = -50' in effects and 'add_opinion' in effects
assert 'rip_church_papal_standing' not in effects
assert 'rip_church_papal_standing' not in triggers
assert 'rip_church_gc_deputation_button' in features

# Local synod and devotional icons remain wired and separately accessible.
for name in ('rip_church_gc_can_infrastructure', 'rip_church_gc_can_coexistence'):
    assert name in read('common/scripted_triggers/rip_church_union_triggers.txt')
for name in ('rip_church_gc_infrastructure_effect', 'rip_church_gc_coexistence_effect'):
    assert name in read('common/scripted_effects/rip_church_union_effects.txt')
for name in ('liturgy', 'learning', 'charity'):
    assert f'rip_church_gc_activate_icon_{name}_effect' in read(
        'common/scripted_effects/rip_church_gc_interaction_effects.txt')
assert 'rip_church_gc_petition_' not in controls

# No active route can establish a global Greek Catholic center or run its
# former auto-conversion event chain. Historical faith adoption is retained.
assert 'establish_greek_catholic_center_decision' not in union_decisions
assert 'greek_catholic_missionary_campaign_decision' not in union_decisions
assert 'greek_catholic_education_decision' in union_decisions
assert 'activate_greek_catholic_reformation' not in crown_effect
assert 'uniate_church.9' not in on_actions
assert 'id = uniate_church.9' not in religion_events
assert not (ROOT / 'events/UniateReformationSpread.txt').exists()
assert not (ROOT / 'decisions/RIP_UniateCuria.txt').exists()

# One-time old-save cleanup is intentional: it removes, rather than revives,
# old numeric state, province-ring flags and obsolete modifiers.
retirement = lifecycle.split('rip_church_retire_removed_union_mechanics_effect =', 1)[1]
assert 'rip_church_communion value = 0' in retirement
assert 'rip_church_papal_standing value = 0' in retirement
assert 'rip_church_union_ring_0' in retirement
assert 'remove_reform_center = greek_catholic' in retirement

print('PASS: obsolete Union centre and Curia resource contracts retired; local synod retained')
