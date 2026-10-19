"""Government readout contracts against gameplay sources, not runtime proof."""
import importlib.util
import re
import subprocess
import sys
from clausewitz_testlib import ROOT, read, keyed_blocks, named_block, normalized
spec = importlib.util.spec_from_file_location('government_status', ROOT/'tools/build_government_status_ui.py')
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)
subprocess.run([sys.executable, '-B', str(ROOT/'tools/build_government_status_ui.py'), '--check'], check=True)

# Every displayed rate/condition must match a gameplay branch, including stacked penalties.
source = read('common/government_mechanics/rip_kyivan_cesarstvo.txt')
for power, factors in [(g.concord,g.concord_factors),(g.gathering,g.gather_factors)]:
    actual = set()
    for _, branch in keyed_blocks(named_block(source,power),'range_modifier'):
        m = re.search(r'monthly_'+power+r'\s*=\s*(-?[\d.]+)',branch)
        if m:
            trigger=named_block(branch,'trigger')
            actual.add((normalized(trigger[trigger.index('{')+1:trigger.rfind('}')]),float(m[1])))
    displayed={(normalized(trigger),float(value)) for _,trigger,value,_ in factors}
    assert actual == displayed, (power, actual ^ displayed)
annual_source=normalized(read('events/RuthenianDecadence.txt'))
for _,trigger,value,_ in g.annual:
    expected=normalized('if = { limit = { '+trigger+' } change_variable = { which = ruthenian_decadence value = '+str(value)+' } }')
    assert expected in annual_source, expected

custom=read('common/custom_gui/rip_government_status.txt')
gui=read('interface/countrygovernmentview.gui')
dynamic=read('customizable_localization/rip_government_status.txt')
loc=g.LOC
for name in re.findall(r'custom_text_box = \{ name = (\w+)', custom):
    assert f'name = "{name}" scripted = yes' in gui
    assert name in loc and name+'_tt' in loc
for name in re.findall(r'custom_window = \{ name = (\w+)', custom):
    assert f'name = "{name}" scripted = yes' in gui
for key in re.findall(r'localisation_key = (\w+)',dynamic):
    assert key in loc, key
for func in re.findall(r'\[Root\.(\w+)\]', '\n'.join(loc.values())):
    assert f'name = {func}\n' in dynamic, func
assert not re.search(r'\b(effect|set_variable|change_variable|add_country_modifier)\s*=',custom)
# Explicit first-match semantics keep fallback and percentage buckets deterministic.
for _, block in keyed_blocks(dynamic,'defined_text'):
    assert 'random = no' in block
for name in ['RipGovMinorityShare','RipGovExcludedShare']:
    start=dynamic.index('name = '+name)
    chunk=dynamic[start:dynamic.index('\n}\n',start)]
    thresholds=[float(v) for v in re.findall(r'value = ([\d.]+)',chunk)]
    assert thresholds==[i/100 for i in range(100,0,-1)]
    for value,want in [(0,0),(.0999,9),(.1,10),(.1499,14),(.15,15),(.2999,29),(.3,30),(1,100)]:
        shown=next((round(t*100) for t in thresholds if value>=t),0)
        assert shown==want
# No native widget was modified or deleted; panels are appended inside the supported root.
start=gui.index('\n# Generated read-only RIP government explanations.\n')
end=gui.index('\n}',gui.index(f'name = "{g.PANEL_NAMES[-1]}"'))+2
assert gui[:start]+gui[end+1:]==g.native
assert 'x=550 y=72' in gui and 'x=470 y=290' in gui # within native root width 1024
# The Rada panel says what the bar says: the runner-up on the left, the dominant bloc on the right, the grip at the thresholds the generator uses.
kru_spec = importlib.util.spec_from_file_location('build_kru_rada', ROOT/'tools/build_kru_rada.py')
kru = importlib.util.module_from_spec(kru_spec)
kru_spec.loader.exec_module(kru)
tip = loc['rip_gov_kru_second_tt']
assert 'SECOND by influence stands on the LEFT' in tip and 'dominant bloc' in tip and 'on the RIGHT' in tip
for threshold, move in kru.GRIP:
    assert f'leader_influence_{threshold}' in dynamic or f'kru_leader_influence_{threshold} = yes' in dynamic, threshold
assert 'a quarter, a half and three quarters at 50, 55 and 60' in tip
assert [n for n, _ in kru.GRIP] == [60, 55, 50] and [m for _, m in kru.GRIP] == [0.75, 0.5, 0.25]
for key in ('rip_gov_kru_leader', 'rip_gov_kru_second', 'rip_gov_kru_opposition', 'rip_gov_kru_bar'):
    assert key in custom and key + '_tt' in loc, key
assert 'Right (leads)' in loc['rip_gov_kru_leader'] and 'Left (second)' in loc['rip_gov_kru_second']
assert 'tag = KRU kru_holds_rada_reform = yes' in read('common/custom_gui/rip_government_status.txt')
assert 'strictly below 15%' in loc['rip_gov_cesar_recovery_tt']
assert 'hlc_ordinance_slot_free' in loc['rip_gov_hlc_crown_slots_tt']
assert 'hlc_boyar_council_session' in loc['rip_gov_hlc_session_tt']
assert 'Rada Consent' in loc['rip_gov_lit_retinues_tt']

# --- Rows that quote numbers must quote the numbers the modifiers really have ---------------------------------------
MODIFIER_WORDS = {
    # modifier key: (words used in the panel, scale, unit). None = said together with another key.
    'advisor_cost': ('advisor costs', 100, '%'), 'diplomatic_reputation': ('diplomatic reputation', 1, ''),
    'improve_relation_modifier': ('improve relations', 100, '%'), 'global_unrest': ('national unrest', 1, ''),
    'culture_conversion_cost': ('culture conversion cost', 100, '%'), 'global_tax_modifier': ('national tax', 100, '%'),
    'nobles_loyalty_modifier': ("nobles' loyalty", 100, '%'), 'global_manpower_modifier': ('national manpower', 100, '%'),
    'tolerance_heretic': ('tolerance of heretics and heathens', 1, ''), 'tolerance_heathen': None,
    'church_loyalty_modifier': ('church loyalty', 100, '%'), 'defensiveness': ('defensiveness', 100, '%'),
    'hostile_attrition': ('hostile attrition', 1, ''), 'land_maintenance_modifier': ('land maintenance', 100, '%'),
    'production_efficiency': ('production efficiency', 100, '%'), 'burghers_loyalty_modifier': ("burghers' loyalty", 100, '%'),
    'max_absolutism': ('maximum absolutism', 1, ''), 'yearly_corruption': ('yearly corruption', 1, ''),
    'state_maintenance_modifier': ('state maintenance', 100, '%'), 'promote_culture_cost': ('culture promotion cost', 100, '%'),
    'manpower_recovery_speed': ('manpower recovery', 100, '%'),
}


def said(key, value):
    words, scale, unit = MODIFIER_WORDS[key]
    return f"{'+' if value > 0 else '-'}{abs(round(value * scale, 6)):g}{unit} {words}"


def modifier_values(source, name):
    body = named_block(source, name)
    return {k: float(v) for k, v in re.findall(r'(?m)^\s*(\w+)\s*=\s*(-?[\d.]+)\s*$', body[body.index('{') + 1:body.rindex('}')])}


def check_ordinances(mech, modifiers, tips, abilities=None):
    """The six crown ordinances: a button each, priced as its row says, a ten-year modifier whose numbers the row quotes."""
    problems = []
    names = re.findall(r'(?m)^\t\t(hlc_enact_\w+_ordinance) = \{', mech)
    if len(names) != 6 or len(set(re.findall(r'icon = (GFX_\w+)', mech))) != 6:
        problems.append(f'the crown mechanic must have six buttons with six different icons, found {names}')
    for key, label, power, _, modifier, effect in g.ORDINANCES:
        button = f'hlc_enact_{key.lower()}_ordinance'
        try:
            block = named_block(mech, button)
        except KeyError:
            problems.append(f'{button} is missing')
            continue
        flat = normalized(block)
        if flat.count(f'{power.lower()}_power_cost = 50') != 2:
            problems.append(f'{button} is not priced 50 {power} in both its trigger and its effect, as its row says')
        if f'name = {modifier} duration = 3650' not in flat or 'cooldown_years = 10' not in flat:
            problems.append(f'{button} does not add {modifier} for 3650 days with a ten-year cooldown')
        tip = tips.get(f'rip_gov_hlc_crown_{key.lower()}_tt', '')
        for mod_key, value in modifier_values(modifiers, modifier).items():
            if MODIFIER_WORDS[mod_key] and said(mod_key, value) not in tip:
                problems.append(f'the {label} row does not quote {said(mod_key, value)}')
    return problems


def snake(camel):
    return re.sub(r'(?<!^)(?=[A-Z])', '_', camel).lower()


def check_resolutions(mech, modifiers, reforms, tips, triggers):
    """The six institutional resolutions: priced, shared token, ten-year modifier, quoted numbers, held through the right reforms."""
    problems = []
    mechanics = {'Municipal': 'rip_municipal_resolutions_mechanic', 'Chancery': 'rip_chancery_resolutions_mechanic', 'Register': 'rip_register_resolutions_mechanic'}
    in_force = normalized(named_block(triggers, 'rip_gov_resolution_in_force'))
    for key, held, label, power, _, modifier, _ in g.RESOLUTIONS:
        button = 'rip_resolution_' + snake(key)
        institution = next(name for name in mechanics if key.startswith(name))
        try:
            block = named_block(named_block(mech, mechanics[institution]), button)
        except KeyError:
            problems.append(f'{button} is not a button of {mechanics[institution]}')
            continue
        flat = normalized(block)
        if flat.count(f'{power.lower()}_power_cost = 50') != 2 or 'add_treasury' in flat or 'rip_gov_review_cost_effect = yes' not in flat:
            problems.append(f'{button} does not pay {power} power in trigger and effect and then the shared ducat payment')
        for needle in ('is_at_war = no', 'stability = 0', 'treasury = 50', 'cooldown_token = rip_gov_institutional_resolution',
                       'cooldown_years = 10', f'name = {modifier} duration = 3650', 'rip_gov_resolution_lock_over = yes',
                       'NOT = { rip_gov_resolution_in_force = yes }'):
            if needle not in flat:
                problems.append(f'{button} lacks {needle}')
        if f'has_country_modifier = {modifier}' not in in_force:
            problems.append(f'rip_gov_resolution_in_force does not look for {modifier}')
        for mod_key, value in modifier_values(modifiers, modifier).items():
            if MODIFIER_WORDS[mod_key] and said(mod_key, value) not in tips['rip_gov_rev_res_lines_tt']:
                problems.append(f'the resolution list does not quote {said(mod_key, value)} for {label}')
    for reform, mechanic in (('vln_magdeburg_rights', 'rip_municipal_resolutions_mechanic'), ('lit_ruthenian_chancery_reform', 'rip_chancery_resolutions_mechanic'),
                             ('chr_kanceliaryst_republic_reform', 'rip_chancery_resolutions_mechanic'), ('het_regimental_system_reform', 'rip_register_resolutions_mechanic'),
                             ('rip_cossacks_reform', 'rip_register_resolutions_mechanic'), ('vln_cossack_host_reform', 'rip_register_resolutions_mechanic'),
                             ('prl_regimental_republic_reform', 'rip_register_resolutions_mechanic')):
        if mechanic not in named_block(named_block(reforms[reform][1], reform), 'government_abilities'):
            problems.append(f'{reform} does not enable {mechanic}')
    return problems


MODS_HLC = read('common/event_modifiers/west_ukraine_modifiers.txt')
MODS_RES = read('common/event_modifiers/rip_government_review_modifiers.txt')
REFORM_FILES = {}
for reform_path in sorted((ROOT / 'common/government_reforms').glob('*.txt')):
    source = reform_path.read_text(encoding='latin-1')
    for reform_name in re.findall(r'(?m)^(\w+) = \{', source):
        REFORM_FILES[reform_name] = (reform_path.name, source)
tips = {k: v for k, v in loc.items()}
MECH_HLC = read('common/government_mechanics/rip_hlc_austrian_reorganization.txt')
MECH_RES = read('common/government_mechanics/rip_institutional_resolutions.txt')
TRIG_RES = read('common/scripted_triggers/rip_government_review_triggers.txt')
for problem_list in (check_ordinances(MECH_HLC, MODS_HLC, tips), check_resolutions(MECH_RES, MODS_RES, REFORM_FILES, tips, TRIG_RES)):
    assert not problem_list, problem_list

# The decision and the events that used to carry the resolutions are gone: nothing may fire or read them.
assert not (ROOT / 'decisions/RIP_InstitutionalReviews.txt').exists() and not (ROOT / 'events/RIP_InstitutionalReviews.txt').exists()
for retired in ('rip_gov_review.1', 'rip_gov_review.2', 'rip_gov_review.3', 'rip_gov_can_review_', 'rip_gov_review_available', 'rip_gov_review_municipal', 'rip_gov_review_chancery', 'rip_gov_review_register'):
    for folder in ('common', 'decisions', 'events', 'missions', 'localisation', 'customizable_localization', 'interface'):
        for file in (ROOT / folder).rglob('*'):
            if file.is_file() and file.suffix in {'.txt', '.yml', '.gui', '.gfx'}:
                assert retired not in file.read_text(encoding='utf-8-sig', errors='replace'), (retired, file)

# --- Planted violations: the contracts above must notice what they are meant to notice -------------------------------
planted = {
    'a crown ordinance paid in the wrong power': lambda: check_ordinances(MECH_HLC.replace('mil_power_cost = 50', 'dip_power_cost = 50'), MODS_HLC, tips),
    'a crown ordinance that stays for ever': lambda: check_ordinances(MECH_HLC.replace('name = hlc_urbarial_ordinance_modifier\n\t\t\t\t\tduration = 3650', 'name = hlc_urbarial_ordinance_modifier\n\t\t\t\t\tduration = -1', 1), MODS_HLC, tips),
    'two crown ordinances on one picture': lambda: check_ordinances(MECH_HLC.replace('GFX_rip_toleration_ordinance', 'GFX_rip_urbarial_ordinance'), MODS_HLC, tips),
    'a row that quotes another number': lambda: check_ordinances(MECH_HLC, MODS_HLC.replace('global_tax_modifier = 0.05\n\tnobles_loyalty_modifier = -0.05\n}\n\n# The bottom row', 'global_tax_modifier = 0.08\n\tnobles_loyalty_modifier = -0.05\n}\n\n# The bottom row'), tips),
    'a resolution that forgets the shared token': lambda: check_resolutions(MECH_RES.replace('cooldown_token = rip_gov_institutional_resolution', 'cooldown_years = 10', 1), MODS_RES, REFORM_FILES, tips, TRIG_RES),
    'a resolution paid in the wrong power': lambda: check_resolutions(MECH_RES.replace('mil_power_cost = 50', 'adm_power_cost = 50'), MODS_RES, REFORM_FILES, tips, TRIG_RES),
    'a resolution with no stability condition': lambda: check_resolutions(MECH_RES.replace('stability = 0', 'always = yes', 1), MODS_RES, REFORM_FILES, tips, TRIG_RES),
    'a resolution missing from the in-force trigger': lambda: check_resolutions(MECH_RES, MODS_RES, REFORM_FILES, tips, TRIG_RES.replace('has_country_modifier = rip_gov_register_muster', 'always = no')),
    'a reform that lost its resolution buttons': lambda: check_resolutions(MECH_RES, MODS_RES, {**REFORM_FILES, 'chr_kanceliaryst_republic_reform': (REFORM_FILES['chr_kanceliaryst_republic_reform'][0], REFORM_FILES['chr_kanceliaryst_republic_reform'][1].replace('rip_chancery_resolutions_mechanic', 'x', 1))}, tips, TRIG_RES),
}
unseen = [name for name, run in planted.items() if not run()]
assert not unseen, f'planted violations not caught: {unseen}'
print(f'GOVERNMENT STATUS PASS: native wiring, source-matched rate branches, percentage boundaries and deterministic outputs; {len(g.ORDINANCES)} crown ordinances and {len(g.RESOLUTIONS)} resolutions pinned to their mechanics ({len(planted)} planted violations caught); runtime unverified.')
