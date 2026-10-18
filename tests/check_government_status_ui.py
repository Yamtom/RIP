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
assert 'PREVIOUS dominant faction, not the runner-up' in loc['rip_gov_kru_partner_tt']
assert 'strictly below 15%' in loc['rip_gov_cesar_recovery_tt']
assert 'hlc_ordinance_slot_free' in loc['rip_gov_hlc_slots_tt']
assert 'hlc_boyar_council_session' in loc['rip_gov_hlc_session_tt']
assert 'Rada Consent' in loc['rip_gov_lit_retinues_tt']
assert 'rip_gov_review_recent' in loc['rip_gov_rev_lockout_tt']
print('GOVERNMENT STATUS PASS: native wiring, source-matched rate branches, percentage boundaries and deterministic outputs; runtime unverified.')