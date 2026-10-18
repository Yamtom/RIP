"""Native Orthodox mechanics and balance contract, independent of EU4 runtime."""
from decimal import Decimal
from pathlib import Path
import os
import re
from clausewitz_testlib import ROOT, read, named_block, keyed_blocks, normalized, vanilla_root

icons = ('michael', 'eleusa', 'pancreator', 'nicholas')
faith = read('common/religions/russian_orthodox.txt')
assert (ROOT / 'interface/countryreligionview.gui').exists()
assert not (ROOT / 'interface/blessings.gui').exists()
for forbidden in ('fervor = yes', 'holy_sites =', 'blessings =', 'uses_piety ='):
    assert forbidden not in normalized(faith), forbidden
assert 'has_patriarchs = yes' in faith
assert 'misguided_heretic = yes' in faith

# Snapshot of EU4 1.37.5. Verified against the install below when available.
baseline = {
    'country': {'stability_cost_modifier': '-0.1', 'tolerance_own': '1'},
    'michael': {'discipline': '0.05', 'manpower_recovery_speed': '0.1'},
    'eleusa': {'global_unrest': '-3', 'harsh_treatment_cost': '-0.25'},
    'pancreator': {'development_cost': '-0.1', 'build_cost': '-0.1'},
    'nicholas': {'improve_relation_modifier': '0.25', 'ae_impact': '-0.1'},
}
def payload(block):
    # Modifier scalars before the first nested allow/visible/AI block.
    inside = block[block.index('{') + 1:]
    inside = re.split(r'\b(?:allow|visible|ai_will_do)\s*=', inside)[0]
    inside = re.sub(r'#.*', '', inside)
    return {k: Decimal(v) for k,v in re.findall(r'(\w+)\s*=\s*(-?\d+(?:\.\d+)?)', inside)}

# Only target-version data may refresh this snapshot; 1.30 is a donor.
install = vanilla_root()
if install is not None:
    vanilla_path = install / 'common/religions/00_religion.txt'
    vanilla = named_block(vanilla_path.read_text(encoding='utf-8-sig'), 'orthodox')
    for name, values in baseline.items():
        block = named_block(vanilla, 'country' if name == 'country' else 'icon_' + name)
        assert payload(block) == {k: Decimal(v) for k,v in values.items()}, name
    defines = (install / 'common/defines.lua').read_text(encoding='utf-8-sig')
    assert re.search(r'ORTHODOX_ICON_DURATION_MONTHS\s*=\s*240', defines)
    assert re.search(r'ORTHODOX_ICON_AUTHORITY_COST\s*=\s*0\.1', defines)
    print('PASS: balance baseline and icon cost/duration match installed vanilla')
assert payload(named_block(faith, 'country')) == {
    'stability_cost_modifier': Decimal('-.05'), 'tolerance_own': Decimal('.5')}
for name in icons:
    old = named_block(faith, 'rip_ro_native_' + name)
    assert all(v == 0 for v in payload(old).values())
    assert 'always = no' in named_block(old, 'allow')

native = named_block(faith, 'orthodox_icons')
assert re.findall(r'(?m)^\s*(rip_ro_native_\w+)\s*=\s*\{', native) == [
    *('rip_ro_native_' + name for name in icons), 'rip_ro_native_retired_climacus']
for name in icons:
    assert 'always = no' in named_block(named_block(native, 'rip_ro_native_' + name), 'visible')
assert 'always = no' in named_block(named_block(native, 'rip_ro_native_retired_climacus'), 'visible')
assert 'rip_ro_select_' not in read('decisions/RIP_OrthodoxIcons.txt')

cleanup = read('common/scripted_effects/rip_ro_icon_effects.txt')
for name in (*icons, 'climacus'):
    assert 'remove_country_modifier = rip_ro_icon_' + name in cleanup
    assert payload(named_block(read('common/event_modifiers/RIP_faith_modifiers.txt'), 'rip_ro_icon_' + name)) == {'discipline': 0}
for name in ('sobor_of_war', 'sobor_of_the_market', 'sobor_of_the_canons'):
    assert 'remove_active_fervor = ' + name in cleanup
    retired = named_block(read('common/fervor/RIP_sobor_fervor.txt'), name)
    assert 'always = no' in named_block(retired, 'potential')
    assert payload(named_block(retired, 'effect')) == {'discipline': 0}
for _, blessing in keyed_blocks(read('common/church_aspects/RIP_ro_holy_blessings.txt'), 'modifier'):
    assert payload(blessing) == {'discipline': 0}
hooks = read('common/on_actions/russian_orthodox_on_actions.txt')
assert 'rip_ro_icon_upkeep_effect = yes' in named_block(hooks, 'on_startup')
assert 'rip_ro_icon_upkeep_effect = yes' in named_block(hooks, 'on_religion_change')
assert 'country_event =' not in read('events/RIP_OrthodoxAuthority.txt').split('immediate =')[1]

decision = read('decisions/RIP_OrthodoxHolyCities.txt')
assert 'rip_ro_holy_city_register' not in decision, 'the register decision is retired in favor of the UI button'
assert not (ROOT / 'events/RIP_OrthodoxHolyCities.txt').exists(), 'the old event-popup route must be retired'

controls = read('common/custom_gui/RIP_church_controls.txt')
gui = read('interface/countryreligionview.gui')
site_localisation = read('localisation/rip_ro_blessing_window_l_english.yml')
custom_loc = read('customizable_localization/rip_ro_holy_cities_custom_loc.txt')
modifiers = read('common/event_modifiers/RIP_faith_modifiers.txt')
pulse_effects = read('common/scripted_effects/rip_ro_holy_cities_effects.txt')
hooks = read('common/on_actions/russian_orthodox_on_actions.txt')

assert 'custom_window = { name = rip_ro_holy_cities_panel potential = { rip_church_ro_jurisdiction = yes has_country_flag = rip_ro_holy_city_register_open } }' in controls
assert 'custom_window = { name = rip_church_ro_panel potential = { rip_church_ro_jurisdiction = yes NOT = { has_country_flag = rip_church_ro_window_hidden } NOT = { has_country_flag = rip_ro_holy_city_register_open } } }' in controls

open_button = next(
    block for _, block in keyed_blocks(controls, 'custom_button')
    if re.search(r'(?m)^\s*name\s*=\s*rip_ro_holy_cities_open\b', block)
)
assert 'set_country_flag = rip_ro_holy_city_register_open' in open_button

close_button = next(
    block for _, block in keyed_blocks(controls, 'custom_button')
    if re.search(r'(?m)^\s*name\s*=\s*rip_ro_holy_cities_close\b', block)
)
assert 'clr_country_flag = rip_ro_holy_city_register_open' in close_button

city_panel = next(
    block for _, block in keyed_blocks(gui, 'windowType')
    if re.search(r'(?m)^\s*name\s*=\s*"rip_ro_holy_cities_panel"\s*', block)
)
assert 'position = { x=540 y=8 }' in city_panel and 'size = { x=475 y=560 }' in city_panel

orthodox_panel = next(
    block for _, block in keyed_blocks(gui, 'windowType')
    if re.search(r'(?m)^\s*name\s*=\s*"orthodox_specific_window"\s*', block)
)
assert 'position = { x=-24 y=0 }' in orthodox_panel, 'do not move the vanilla Orthodox panel'
assert 'rip_ro_holy_cities_open' in orthodox_panel, 'open button must be placed in the native orthodox window'
assert 'GFX_coptic_blessing_select' in orthodox_panel, 'uses the Holy Sites medallion sprite'

for city, province in (
    ('novgorod', 310),
    ('moscow', 295),
    ('kyiv', 280),
    ('constantinople', 151),
    ('jerusalem', 379),
):
    assert f'name = "rip_ro_holy_city_{city}_row"' in city_panel
    assert f'rip_ro_holy_city_{city}_name' in city_panel
    assert f'rip_ro_holy_city_{city}_owner' in city_panel
    assert f'rip_ro_holy_city_{city}_faith' in city_panel
    assert f'rip_ro_holy_city_{city}_faith_icon' in city_panel
    assert f'rip_ro_holy_city_{city}_myth_progress' in city_panel
    assert f'rip_ro_holy_city_{city}_bonus_active' in city_panel
    assert f'rip_ro_holy_city_{city}_bonus_pending' in city_panel
    assert f'[{province}.GetName]' in site_localisation
    assert f'[{province}.Owner.GetName]' in site_localisation
    assert f'[{province}.Religion.GetName]' in site_localisation
    assert f'rip_ro_myth_{city}' in modifiers, f'bonus modifier for {city} must be defined'
    assert f'rip_ro_myth_years_{city}' in pulse_effects, f'30-year pulse must advance {city}'
    assert f'rip_ro_myth_complete_{city}' in pulse_effects

assert 'rip_ro_holy_cities_open' in site_localisation
assert 'Holy Cities Register' in site_localisation
assert 'Sees, Sacred Myths and Pilgrimage Destinations' in site_localisation
assert 'rip_ro_sites.' not in site_localisation and 'rip_ro_site_' not in site_localisation
assert 'rip_ro_holy_city_count' not in controls + gui + site_localisation
assert 'rip_ro_holy_cities_yearly_pulse_effect = yes' in hooks

assert 'has_patriarchs = yes' in faith
raskol = named_block(read('common/disasters/rip_faith_disasters.txt'), 'rip_ro_raskol')
assert 'rip_ro_icon_count' not in raskol
assert 'has_country_flag = rip_ro_stage_raskol' in named_block(raskol, 'can_start')
assert 'patriarch_authority = 0.6' in named_block(raskol, 'can_end')
assert 'religious_unity' not in named_block(raskol, 'can_end'), 'a unity exit closes the Raskol on its first check'
assert 'monthly_fervor_increase' not in raskol
assert 'rip_ro_icon_count' not in read('common/scripted_effects/rip_faith_zeal_effects.txt')
print('PASS: dedicated UI medallion, 30-year myth bars with right-aligned bonus icons, and Raskol guards verified')
