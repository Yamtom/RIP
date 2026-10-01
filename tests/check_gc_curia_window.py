"""Contracts for the remaining Greek Catholic synod, icons and Rome audience."""
import re
from clausewitz_testlib import named_block, keyed_blocks, read

curia_triggers = read('common/scripted_triggers/rip_church_gc_curia_triggers.txt')
curia_effects = read('common/scripted_effects/rip_church_gc_curia_effects.txt')
opinion_modifiers = read('common/opinion_modifiers/RIP_church_relations.txt')
icon_triggers = read('common/scripted_triggers/rip_church_gc_interaction_triggers.txt')
icon_effects = read('common/scripted_effects/rip_church_gc_interaction_effects.txt')
union_triggers = read('common/scripted_triggers/rip_church_union_triggers.txt')
union_effects = read('common/scripted_effects/rip_church_union_effects.txt')
controls = read('common/custom_gui/RIP_church_controls.txt')
features = read('common/custom_gui/RIP_church_gc_features.txt')
gui_generator = read('tools/build_church_gui.py')
localisation_generator = read('tools/build_church_localisation.py')
english = read('localisation/replace/zzzz_RIP_church_redesign_l_english.yml')
interface = read('interface/countryreligionview.gui')
custom_text = read('customizable_localization/rip_church_redesign.txt')

def button(source, name):
    for _, block in keyed_blocks(source, 'custom_button'):
        if re.search(rf'\bname\s*=\s*{re.escape(name)}\b', block):
            return block
    raise AssertionError(f'missing button: {name}')

# No active numerical Communion/Papal Standing or paid petition menu.
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

# Curia contact offers a non-electoral audience and a direct diplomatic gift.
gate = named_block(curia_triggers, 'rip_church_gc_can_depute_to_curia')
effect = named_block(curia_effects, 'rip_church_gc_depute_to_curia_effect')
assert 'treasury = 50' in gate and 'patriarch_authority' not in gate
assert 'had_country_flag = { flag = rip_church_gc_deputation_sent days = 1825 }' in gate
assert 'add_treasury = -50' in effect
assert 'PAP = { add_opinion = { who = ROOT modifier = rip_church_opinion_gc_deputation } }' in effect
assert 'add_opinion = { who = PAP modifier = rip_church_opinion_gc_deputation }' in effect
deputation_opinion = named_block(opinion_modifiers, 'rip_church_opinion_gc_deputation')
assert 'opinion = 25' in deputation_opinion and 'yearly_decay = 2' in deputation_opinion
assert 'rip_church_gc_deputation_button' in features
assert 'rip_church_gc_curia_note' in gui_generator
assert 'name = "rip_church_gc_curia_note"' in interface
assert 'name = "rip_church_gc_controller_readout"' in interface
assert 'global_event_target = rip_church_gc_controller' in controls
assert 'event_target:rip_church_gc_controller = { is_papal_controller = yes }' in controls
assert 'Curia controller\\n' in english

# GC-only bishop art must not overwrite the native Orthodox patriarch sprites.
from pathlib import Path
import struct
from clausewitz_testlib import ROOT
for level in ('low', 'high'):
    assert f'name ="{level}_patriarch_authority" scripted = yes' in interface
    assert f'spriteType = "GFX_icon_{level}_patriarch_authority"' in interface
    assert f'name = {level}_patriarch_authority potential = {{ NOT = {{ religion = greek_catholic }} }}' in controls
    assert f'name = rip_church_gc_capacity_{level}_icon potential = {{ religion = greek_catholic }}' in controls
    data = (ROOT / f'gfx/interface/rip_church/gc_archbishop_{level}.dds').read_bytes()
    assert data[:4] == b'DDS ' and struct.unpack_from('<II', data, 12) == (38, 38)
assert 'grants +25 opinion in both directions, decaying by 2 per year' in localisation_generator
for language in ('english', 'french', 'german', 'spanish'):
    localisation = read(f'localisation/replace/zzzz_RIP_church_redesign_l_{language}.yml')
    assert 'grants +25 opinion in both directions, decaying by 2 per year' in localisation
    assert 'Effect: +25 opinion in both directions, decaying by 2 per year' in localisation
assert 'grants +10 opinion in both directions' not in english
assert 'may improve the Pope’s opinion temporarily' not in english
gift_gate = named_block(curia_triggers, 'rip_church_gc_can_offer_gift_to_holy_see')
gift_effect = named_block(curia_effects, 'rip_church_gc_offer_gift_to_holy_see_effect')
assert 'treasury = 100' in gift_gate
assert 'had_country_flag = { flag = rip_church_gc_holy_see_gift_sent days = 1825 }' in gift_gate
assert 'add_treasury = -100' in gift_effect
assert 'PAP = { add_opinion = { who = ROOT modifier = rip_church_opinion_gc_donation } }' in gift_effect
assert 'add_opinion = { who = PAP' not in gift_effect
assert 'rip_church_gc_holy_see_gift_button' in features
assert 'rip_church_gc_can_offer_gift_to_holy_see = yes' in button(
    features, 'rip_church_gc_holy_see_gift_button')
assert '100 ducats' in localisation_generator
assert '+25 opinion of us, decaying by 5 per year' in localisation_generator
assert 'no Patriarch Authority, Curia vote, cardinal or electoral influence' in localisation_generator
for language in ('english', 'french', 'german', 'spanish'):
    localisation = read(f'localisation/replace/zzzz_RIP_church_redesign_l_{language}.yml')
    assert 'rip_church_gc_holy_see_gift_button:0 "Send a gift to Rome — 100¤"' in localisation
    assert 'The Papal State gains +25 opinion of us, decaying by 5 per year' in localisation
    assert 'rip_church_opinion_gc_donation:0 "Donation from an Eastern Catholic church"' in localisation

# All three pages share a fixed header/navigation rail.  Devotional icon art is
# the click target's card, not an empty blue button floating above the icon.
for page in ('union', 'curia', 'parishes'):
    for tab in ('union', 'curia'):
        marker = f'name = "rip_church_gc_{tab}_tab_{page}" scripted = yes position = {{ x='
        start = interface.index(marker)
        assert ' y=110 }' in interface[start:start + 140]
assert interface.count('name = "rip_church_gc_heading" scripted = yes position = { x=28 y=43 }') >= 3
assert interface.count('spriteType = "GFX_rip_church_union_frame"') >= 3
assert 'small_tiles_dialog.dds' not in read('interface/RIP_church_panels.gfx')
assert 'name = "rip_church_authority_heading" scripted = yes' in interface
assert interface.count('spriteType = "GFX_rip_church_section_banner"') >= 7
assert 'name = "rip_church_gc_holy_see_gift_button" scripted = yes position = { x=91 y=50 }' in interface
assert 'GFX_standard_button_140' not in gui_generator
for key in ('liturgy', 'learning', 'charity'):
    start = interface.index(f'name = "rip_church_gc_icon_{key}_button"')
    assert 'quadTextureSprite = "GFX_coptic_blessing_select"' in interface[start:interface.index('buttonFont', start)]
assert 'name = "rip_church_gui_parish_empty_state"' in interface
assert 'name = GetChurchParishRegisterState' in custom_text

from church_testlib import fixture, TRIGGERS
w,c,p = fixture('greek_catholic')
c['treasury'] = 150
if 'PAP' not in w.countries:
    w.country('PAP','catholic')
deputation_gate = TRIGGERS['rip_church_gc_can_depute_to_curia']
assert w.gate(deputation_gate,c)
c['flags']['rip_church_gc_deputation_sent'] = w.day
assert not w.gate(deputation_gate,c)
w.day += 1824
assert not w.gate(deputation_gate,c)
w.day += 1
assert w.gate(deputation_gate,c)

gift_gate = TRIGGERS['rip_church_gc_can_offer_gift_to_holy_see']
gift_effect = 'rip_church_gc_offer_gift_to_holy_see_effect'
baseline_pap_opinion = w.opinion(w.countries['PAP'],c)
assert w.gate(gift_gate,c)
w.run(gift_effect,c)
assert c['treasury'] == 50
assert c['flags']['rip_church_gc_holy_see_gift_sent'] == w.day
assert w.opinion(w.countries['PAP'],c) == baseline_pap_opinion + 25
assert not w.gate(gift_gate,c)
w.day += 1824
assert not w.gate(gift_gate,c)
w.day += 1
c['treasury'] = 100
assert w.gate(gift_gate,c)
w.run(gift_effect,c)
assert c['treasury'] == 0
assert w.opinion(w.countries['PAP'],c) == 25
assert not w.gate(gift_gate,c)  # insufficient funds also disables the control
c['treasury'] = 100
c['is_at_war'] = True
assert not w.gate(gift_gate,c)
c['is_at_war'] = False
w.countries['PAP']['religion'] = 'orthodox'
assert not w.gate(gift_gate,c)
w.countries['PAP']['religion'] = 'catholic'
c['religion'] = 'catholic'
assert not w.gate(gift_gate,c)
c['religion'] = 'greek_catholic'
print('GC CURIA PASS: audience and gift transactions, opinion, visibility gates, cooldown boundaries')
