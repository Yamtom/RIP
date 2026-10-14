"""Donor audit recognizes definitions rather than nested event calls."""
import sys
from pathlib import Path
import tempfile

from clausewitz_testlib import ROOT
sys.path.insert(0, str(ROOT / 'tools'))
from audit_eu4_flavor import definitions, top_blocks, values

fixture = '''namespace = rip_fixture
# country_event = { id = rip_fixture.fake }
country_event = {
 id = rip_fixture.1
 title = rip_fixture.1.t
 desc = "Ignored } brace"
 trigger = { has_reform = principality has_dlc = "Third Rome" }
 option = { name = rip_fixture.1.a country_event = { id = rip_fixture.2 } }
}
country_event = {
 id = rip_fixture.2
 title = rip_fixture.2.t
 is_triggered_only = yes
}
'''
with tempfile.TemporaryDirectory(prefix='rip_donor_contract_') as temporary:
    path = Path(temporary) / 'events.txt'
    path.write_text(fixture, encoding='utf-8')
    events = list(definitions(path))
assert [e[0] for e in events] == ['rip_fixture.1', 'rip_fixture.2']
assert values(events[0][2], 'has_dlc') == ['Third Rome']
assert values(events[0][2], 'has_reform') == ['principality']
for damaged in (fixture + '}', fixture + 'country_event = {'):
    try:
        list(top_blocks(damaged))
    except ValueError:
        pass
    else:
        raise AssertionError('Unbalanced source accepted')
print('DONOR AUDIT PASS: definitions, nested callers, quoted braces, DLC and reform dependencies.')
