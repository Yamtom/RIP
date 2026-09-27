"""Source contracts for Greek Catholic Curia, icons, and independent slots."""
import re
from clausewitz_testlib import keyed_blocks, named_block, read

keys = ('church_tax', 'blessing', 'indulgence', 'saint', 'usury',
        'holy_war', 'legate', 'monopoly')

curia_triggers = read('common/scripted_triggers/rip_church_gc_curia_triggers.txt')
curia_effects = read('common/scripted_effects/rip_church_gc_curia_effects.txt')
icon_triggers = read('common/scripted_triggers/rip_church_gc_interaction_triggers.txt')
icon_effects = read('common/scripted_effects/rip_church_gc_interaction_effects.txt')
local_triggers = read('common/scripted_triggers/rip_church_union_triggers.txt')
local_effects = read('common/scripted_effects/rip_church_union_effects.txt')
life_effects = read('common/scripted_effects/rip_church_lifecycle_effects.txt')
curia_modifiers = read('common/event_modifiers/RIP_church_gc_curia_modifiers.txt')
icon_modifiers = read('common/event_modifiers/rip_church_gc_interaction_modifiers.txt')
controls = read('common/custom_gui/RIP_church_controls.txt')
features = read('common/custom_gui/RIP_church_gc_features.txt')
gui_generator = read('tools/build_church_gui.py')
loc_generator = read('tools/build_church_localisation.py')
english = read('localisation/replace/zzzz_RIP_church_redesign_l_english.yml')
interface = read('interface/countryreligionview.gui')

def block(source, name):
    return named_block(source, name)

def button_block(source, name):
    for _, candidate in keyed_blocks(source, 'custom_button'):
        if re.search(rf'\bname\s*=\s*{re.escape(name)}\b', candidate):
            return candidate
    raise AssertionError(f'missing custom_button {name}')

# The local synod retains its own one-at-a-time slot, while Curia petitions
# gate only against other Curia petitions. Neither system checks the other.
local_gate = block(local_triggers, 'rip_church_gc_has_privilege')
assert 'rip_church_gc_infrastructure' in local_gate
assert 'rip_church_gc_coexistence' in local_gate
for key in keys:
    assert f'has_country_modifier = rip_church_gc_petition_{key}' not in local_gate
assert 'rip_church_gc_has_curia_petition' not in local_gate
for key in ('infrastructure', 'coexistence'):
    gate = block(local_triggers, f'rip_church_gc_can_{key}')
    assert 'rip_church_gc_has_privilege = yes' in gate
    assert 'rip_church_gc_has_curia_petition' not in gate
petition_slot = block(curia_triggers, 'rip_church_gc_has_curia_petition')
for key in keys:
    assert f'rip_church_gc_petition_{key}' in petition_slot
base_gate = block(curia_triggers, 'rip_church_gc_can_petition_base')
assert 'rip_church_gc_has_curia_petition' in base_gate
assert 'rip_church_gc_has_privilege' not in base_gate
assert 'rip_church_gc_infrastructure' not in base_gate
assert 'rip_church_gc_coexistence' not in base_gate
assert 'rip_church_gc_has_active_icon' not in base_gate
assert 'PAP = { has_opinion = { who = ROOT value = 50 } }' in base_gate
assert 'treasury = 100' in base_gate
assert 'check_variable = { which = rip_church_communion value = -40 }' in base_gate
assert 'rip_church_gc_curia_contact = yes' in base_gate
assert 'rip_church_gc_can_petition_base = yes' not in base_gate

# Every petition has a guarded GUI action, a 100-ducat charge, a single
# 3,650-day Curia modifier, and one shared standing threshold (saint: 60).
for key in keys:
    gate = block(curia_triggers, f'rip_church_gc_can_petition_{key}')
    effect = block(curia_effects, f'rip_church_gc_petition_{key}_effect')
    button = button_block(controls, f'rip_church_gc_petition_{key}_button')
    assert 'rip_church_gc_can_petition_base = yes' in gate
    assert f'rip_church_gc_can_petition_{key} = yes' in effect
    assert 'add_treasury = -100' in curia_effects
    assert 'duration = 3650' in curia_effects
    assert f'rip_church_gc_can_petition_{key} = yes' in button
    assert f'rip_church_gc_petition_{key}_effect = yes' in button
    assert f'rip_church_gc_petition_{key} = {{' in curia_modifiers
    assert 'rip_church_gc_has_privilege' not in gate
assert 'value = 60' in block(curia_triggers, 'rip_church_gc_can_petition_saint')
for key in set(keys) - {'saint'}:
    assert 'value = 30' in block(curia_triggers, f'rip_church_gc_can_petition_{key}')
clear_petitions = block(curia_effects, 'rip_church_gc_clear_curia_petitions_effect')
for key in keys:
    assert f'remove_country_modifier = rip_church_gc_petition_{key}' in clear_petitions
assert 'rip_church_gc_clear_curia_petitions_effect = yes' in block(life_effects, 'rip_church_v3_exit_effect')

# Greek Catholic icons are a separate, exclusive, PA-priced five-year set.
# Their single-active gate must not be coupled to either church slot.
icon_slot = block(icon_triggers, 'rip_church_gc_has_active_icon')
for key in ('liturgy', 'learning', 'charity'):
    assert f'rip_church_gc_icon_{key}' in icon_slot
    gate = block(icon_triggers, f'rip_church_gc_can_activate_icon_{key}')
    effect = block(icon_effects, f'rip_church_gc_activate_icon_{key}_effect')
    button = button_block(features, f'rip_church_gc_icon_{key}_button')
    assert 'rip_church_gc_can_activate_icons = yes' in gate
    assert 'patriarch_authority = 0.2' in block(icon_triggers, 'rip_church_gc_can_activate_icons')
    assert f'rip_church_gc_can_activate_icon_{key} = yes' in effect
    assert 'add_patriarch_authority = -0.2' in effect
    assert 'duration = 1825' in effect
    assert f'rip_church_gc_can_activate_icon_{key} = yes' in button
    assert 'rip_church_gc_has_privilege' not in gate
    assert 'rip_church_gc_has_curia_petition' not in gate
assert 'prestige = 0.5' in block(icon_modifiers, 'rip_church_gc_icon_liturgy')
assert 'development_cost = -0.05' in block(icon_modifiers, 'rip_church_gc_icon_learning')
assert 'global_unrest = -0.5' in block(icon_modifiers, 'rip_church_gc_icon_charity')

# Deputation is explicitly non-electoral and has only diplomatic/resource
# effects; it cannot appoint cardinals or add Catholic papal influence.
deputation_gate = block(curia_triggers, 'rip_church_gc_can_depute_to_curia')
deputation_effect = block(curia_effects, 'rip_church_gc_depute_to_curia_effect')
deputation_button = button_block(features, 'rip_church_gc_deputation_button')
assert 'treasury = 50' in deputation_gate
assert 'patriarch_authority = 0.1' in deputation_gate
assert 'days = 1825' in deputation_gate
assert 'add_treasury = -50' in deputation_effect
assert 'add_patriarch_authority = -0.1' in deputation_effect
assert 'value = 5' in deputation_effect
assert 'rip_church_opinion_gc_deputation' in deputation_effect
assert 'rip_church_gc_can_depute_to_curia = yes' in deputation_button
for forbidden in ('appoint_cardinal', 'add_cardinal', 'papal_influence',
                  'add_papal_influence', 'papal_election'):
    assert forbidden not in deputation_effect.lower()

# The Curia pane is reachable from the main church tab. Visible text disclaims
# electoral power, and the localization generator describes independent slots.
assert 'rip_church_gc_open_curia_effect = yes' in controls
assert 'rip_church_gc_curia_panel' in controls
assert 'name = "rip_church_gc_curia_panel"' in interface
assert 'name = "rip_church_gc_panel"' in interface
assert 'name = "rip_church_gc_icons_title"' in interface
assert 'rip_church_gc_curia_vote_disclaimer' in features
assert 'casts no Curia vote' in loc_generator
assert 'One Curia petition can coexist' in loc_generator
assert 'separate ten-year slot' in loc_generator
assert 'rip_church_gc_curia_tab_' in gui_generator
assert 'rip_church_gc_curia_vote_disclaimer:0' in english
assert 'rip_church_gc_deputation_button_tt:0' in english
assert 'rip_church_gc_curia_privilege:0' in english
assert 'rip_church_opinion_gc_deputation:0' in english
assert 'rip_church_opinion_gc_donation:0' in english
for key in keys:
    assert f'rip_church_gc_petition_{key}_button_tt:0' in english
for key in ('liturgy', 'learning', 'charity'):
    assert f'rip_church_gc_icon_{key}_button_tt:0' in english

print('GC CURIA PASS: separate bounded petition/local-synod slots, exclusive PA icons, non-voting deputation and GUI bindings.')
