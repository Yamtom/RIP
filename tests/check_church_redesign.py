"""Regression contracts for the retired Union-centre and Curia resource systems."""
from pathlib import Path
from clausewitz_testlib import ROOT, read

def text(path):
    return read(path)

# Every active game script is free of the retired numeric resources and
# purchasable petition routes. The lifecycle file is allowed to mention them
# only inside the one-time old-save cleanup.
retired = (
    'rip_church_communion',
    'rip_church_papal_standing',
    'rip_church_standing_income',
    'rip_church_gc_petition_',
    'rip_church_gc_can_donate',
    'rip_church_gc_donate_effect',
    'rip_church_union_ring_',
    'rip_church_center_suspended',
)
for folder in ('common', 'events', 'decisions', 'missions'):
    for path in (ROOT / folder).rglob('*'):
        if not path.is_file() or path.suffix.lower() not in ('.txt', '.gui', '.gfx'):
            continue
        # This contract searches ASCII identifiers, so a byte-preserving
        # single-byte decode also covers legacy files with mixed encodings.
        source = path.read_text(encoding='latin-1')
        if path.name == 'rip_church_lifecycle_effects.txt':
            source = source.split(
                'rip_church_retire_removed_union_mechanics_effect =', 1
            )[0]
        for token in retired:
            assert token not in source, f'{token} remains active in {path.relative_to(ROOT)}'

# The old saves are cleaned once; no other active path writes either numeric
# store or re-establishes a Centre of Union.
lifecycle = text('common/scripted_effects/rip_church_lifecycle_effects.txt')
assert 'rip_church_retire_removed_union_mechanics_effect = yes' in lifecycle
retirement = lifecycle.split('rip_church_retire_removed_union_mechanics_effect =', 1)[1]
assert 'rip_church_communion value = 0' in retirement
assert 'rip_church_papal_standing value = 0' in retirement
assert 'remove_reform_center = greek_catholic' in retirement

# Local synodal actions, devotional icons, historic adoption and diplomatic
# audience remain independent of any retired resource or Curia vote.
union = text('common/scripted_effects/rip_church_union_effects.txt')
triggers = text('common/scripted_triggers/rip_church_gc_curia_triggers.txt')
audience = text('common/scripted_effects/rip_church_gc_curia_effects.txt')
for name in ('rip_church_gc_infrastructure_effect', 'rip_church_gc_coexistence_effect',
             'rip_church_begin_florence_effect', 'rip_church_complete_florence_effect'):
    assert name in union
for name in ('liturgy', 'learning', 'charity'):
    assert f'rip_church_gc_activate_icon_{name}_effect' in text(
        'common/scripted_effects/rip_church_gc_interaction_effects.txt')
assert 'rip_church_gc_can_depute_to_curia = {' in triggers
assert 'treasury = 50' in triggers and 'patriarch_authority' not in triggers
assert 'add_treasury = -50' in audience and 'add_opinion' in audience
assert 'rip_church_papal_standing' not in audience
assert 'rip_church_communion' not in audience

# Orientation is no longer a player-controlled axis; migration-only state
# cleanup must not become a trigger, modifier, display or scripted gate.
orientation = text('common/scripted_triggers/rip_church_redesign_triggers.txt')
assert 'rip_church_gc_eastern = { always = no }' in orientation
assert 'rip_church_gc_roman = { always = no }' in orientation
custom_loc = text('customizable_localization/rip_church_redesign.txt')
for name in ('GetChurchCuriaRate', 'GetChurchDonationState', 'GetChurchCuriaPrivilege'):
    assert name not in custom_loc
english = text('localisation/replace/zzzz_RIP_church_redesign_l_english.yml')
for stale in ('Papal Standing', 'Communion Balance', 'Papal petitions',
              'rip_church_gc_rome_resources', 'GetChurchCuriaRate',
              'rip_church_gc_petition_', 'rip_church_gui_ring_'):
    assert stale not in english, stale

print('PASS: obsolete Union-centre and Curia resource mechanics retired; independent church paths retained')
