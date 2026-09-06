"""Native Orthodox mechanics and balance contract, independent of EU4 runtime."""
from decimal import Decimal
from pathlib import Path
import os
import re
from clausewitz_testlib import ROOT, read, named_block, keyed_blocks, normalized

icons = ('michael', 'eleusa', 'pancreator', 'nicholas')
faith = read('common/religions/russian_orthodox.txt')
assert not (ROOT / 'interface/countryreligionview.gui').exists()
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

# EU4_DIR is the variable CLAUDE.md documents and the other five vanilla-aware
# checks read. This one read only EU4_GAME_DIR, so anyone who set the documented
# variable got the hardcoded path instead - and on a machine where that path is
# wrong, every vanilla assertion below is skipped in silence rather than failing.
install = Path(os.environ.get('EU4_DIR')
               or os.environ.get('EU4_GAME_DIR')
               or 'D:/Programs Files(x86)/Steam/steamapps/common/Europa Universalis IV')
vanilla_path = install / 'common/religions/00_religion.txt'
if vanilla_path.exists():
    vanilla = named_block(vanilla_path.read_text(encoding='utf-8-sig'), 'orthodox')
    for name, values in baseline.items():
        block = named_block(vanilla, 'country' if name == 'country' else 'icon_' + name)
        assert payload(block) == {k: Decimal(v) for k,v in values.items()}, name
    defines = (install / 'common/defines.lua').read_text(encoding='utf-8-sig')
    assert re.search(r'ORTHODOX_ICON_DURATION_MONTHS\s*=\s*240', defines)
    assert re.search(r'ORTHODOX_ICON_AUTHORITY_COST\s*=\s*0\.1', defines)
    print('PASS: balance baseline and icon cost/duration match installed vanilla')
for name, values in baseline.items():
    actual = payload(named_block(faith, 'country' if name == 'country' else 'rip_ro_native_' + name))
    expected = {k: Decimal(v) * Decimal('.95') for k,v in values.items()}
    assert actual == expected, (name, actual, expected)
    print('95% payload:', name, ', '.join(k + '=' + str(v) for k,v in actual.items()))
native = named_block(faith, 'orthodox_icons')
assert re.findall(r'(?m)^\s*(rip_ro_native_\w+)\s*=\s*\{', native) == [
    *('rip_ro_native_' + name for name in icons), 'rip_ro_native_retired_climacus']
for name in icons:
    assert 'always = yes' in named_block(named_block(native, 'rip_ro_native_' + name), 'visible')
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

sites = read('events/RIP_OrthodoxHolyCities.txt')
events = [b for _,b in keyed_blocks(sites, 'country_event') if re.search(r'(?m)^\s*title\s*=',b)]
assert len(events) == 6
assert 'rip_ro_sites.1' in read('decisions/RIP_OrthodoxHolyCities.txt')
for number, province in enumerate((310, 295, 280, 151, 379), 2):
    assert f'{province} = {{ owned_by = ROOT controlled_by = ROOT religion = russian_orthodox }}' in events[0]
    event = next(b for b in events if f'id = rip_ro_sites.{number}\n' in b)
    assert f'{province} = {{ save_event_target_as = rip_ro_holy_city }}' in event
    assert 'goto = rip_ro_holy_city' in event and 'is_triggered_only = yes' in event
for forbidden in ('add_country_modifier', 'add_patriarch_authority', 'save_global_event_target_as'):
    assert forbidden not in sites
raskol = named_block(read('common/disasters/rip_faith_disasters.txt'), 'rip_ro_raskol')
assert 'rip_ro_icon_count' not in raskol
assert 'has_country_flag = rip_ro_stage_raskol' in named_block(raskol, 'can_start')
assert 'stability = 1 religious_unity = 0.9' in named_block(raskol, 'can_end')
assert 'monthly_fervor_increase' not in raskol
assert 'rip_ro_icon_count' not in read('common/scripted_effects/rip_faith_zeal_effects.txt')
print('PASS: one native panel, 95% configurable bonuses, legacy cleanup, site navigation and reachable Raskol conditions')
