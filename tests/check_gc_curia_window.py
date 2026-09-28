"""Contracts for the remaining Greek Catholic synod, icons and Rome audience."""
import re
from clausewitz_testlib import named_block, keyed_blocks, read

curia_triggers = read('common/scripted_triggers/rip_church_gc_curia_triggers.txt')
curia_effects = read('common/scripted_effects/rip_church_gc_curia_effects.txt')
icon_triggers = read('common/scripted_triggers/rip_church_gc_interaction_triggers.txt')
icon_effects = read('common/scripted_effects/rip_church_gc_interaction_effects.txt')
union_triggers = read('common/scripted_triggers/rip_church_union_triggers.txt')
union_effects = read('common/scripted_effects/rip_church_union_effects.txt')
controls = read('common/custom_gui/RIP_church_controls.txt')
features = read('common/custom_gui/RIP_church_gc_features.txt')
gui_generator = read('tools/build_church_gui.py')
english = read('localisation/replace/zzzz_RIP_church_redesign_l_english.yml')
interface = read('interface/countryreligionview.gui')
custom_text = read('customizable_localization/rip_church_redesign.txt')

def button(source, name):
    for _, block in keyed_blocks(source, 'custom_button'):
        if re.search(rf'\bname\s*=\s*{re.escape(name)}\b', block):
            return block
    raise AssertionError(f'missing button: {name}')

# No active numerical Communion/Papal Standing, petition menu, or donation.
active_sources = (curia_triggers, curia_effects, controls, features,
                  gui_generator, interface, custom_text, english)
for source in active_sources:
    for stale in ('rip_church_communion', 'rip_church_papal_standing',
                  'rip_church_standing_income', 'rip_church_gc_petition_',
                  'rip_church_gc_donate_', 'GetChurchCuriaRate',
                  'GetChurchDonationState', 'GetChurchCuriaPrivilege'):
        assert stale not in source, stale
assert 'Papal Standing' not in english
assert 'Communion Balance' not in english
assert 'Papal petitions' not in english

# Local synod remains a single ten-year institution, using only Patriarch
# Authority and ducats. It is not blocked by Curia interaction state.
assert 'rip_church_gc_can_infrastructure = yes' in union_effects
assert 'rip_church_gc_can_coexistence = yes' in union_effects
assert 'patriarch_authority = 0.2' in named_block(union_triggers, 'rip_church_gc_can_infrastructure')
assert 'patriarch_authority = 0.2' in named_block(union_triggers, 'rip_church_gc_can_coexistence')
assert 'rip_church_gc_has_curia_petition' not in union_triggers

# The three devotional icons remain a separately gated PA-priced system.
for key in ('liturgy', 'learning', 'charity'):
    assert f'rip_church_gc_can_activate_icon_{key} = yes' in icon_effects
    assert 'add_patriarch_authority = -0.2' in named_block(
        icon_effects, f'rip_church_gc_activate_icon_{key}_effect')
    assert f'rip_church_gc_can_activate_icon_{key} = yes' in button(
        features, f'rip_church_gc_icon_{key}_button')

# The only remaining Curia interaction is the transparent 50-ducat audience.
gate = named_block(curia_triggers, 'rip_church_gc_can_depute_to_curia')
effect = named_block(curia_effects, 'rip_church_gc_depute_to_curia_effect')
assert 'treasury = 50' in gate and 'patriarch_authority' not in gate
assert 'had_country_flag = { flag = rip_church_gc_deputation_sent days = 1825 }' in gate
assert 'add_treasury = -50' in effect and 'add_opinion' in effect
assert 'rip_church_gc_deputation_button' in features
assert 'rip_church_gc_curia_note' in gui_generator
assert 'name = "rip_church_gc_curia_note"' in interface

print('GC CURIA PASS: local synod/icons retained; Curia is a non-electoral diplomatic audience only')
