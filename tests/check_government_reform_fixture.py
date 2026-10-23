"""Contracts for the government-reform test fixture in tests/dev_tools/.

tests/dev_tools/make_government_reform_test.py writes RIP_GovernmentReformTest.txt and
rip_gov_test_l_english.yml from common/governments and common/government_reforms. The game
does not load them. This check keeps three promises and nothing else: every RIP reform has an
option in the fixture, the two files are well formed, and the shipped mod never carries or
calls them. It does not run the fixture; the RIP_GOV_TEST markers in game.log do that, and
`make_government_reform_test.py --report game.log` reads them.
"""
import re
import sys

from clausewitz_testlib import ROOT, brace_error

sys.path.insert(0, str(ROOT / 'tests/dev_tools'))
import make_government_reform_test as gen  # noqa: E402

DEV = ROOT / 'tests/dev_tools'
EVENTS = DEV / 'RIP_GovernmentReformTest.txt'
LOC = DEV / 'rip_gov_test_l_english.yml'

# ---- the files exist and are well formed
raw = EVENTS.read_bytes()
assert not raw.startswith(b'\xef\xbb\xbf'), 'a BOM in a Clausewitz data file breaks the parser once the fixture is installed'
text = raw.decode('utf-8').replace('\r\n', '\n')  # a checkout with CRLF must pass too
assert brace_error(text) is None, brace_error(text)
assert 'namespace = rip_gov_test' in text
loc_raw = LOC.read_bytes()
assert loc_raw.startswith(b'\xef\xbb\xbf'), 'localisation needs the BOM'
assert not loc_raw[3:].startswith(b'\xef\xbb\xbf'), 'localisation needs exactly one BOM'
loc = loc_raw.decode('utf-8-sig').replace('\r\n', '\n')
assert loc.startswith('l_english:')
loc_keys = re.findall(r'^ (\S+):\d+ "', loc, re.M)
assert len(loc_keys) == len(set(loc_keys)), 'duplicate localisation key'

# ---- event ids are unique and every id the fixture fires exists
ids = re.findall(r'^\tid = rip_gov_test\.(\d+)$', text, re.M)
assert len(ids) == len(set(ids)), 'duplicate event id'
fired = set(re.findall(r'country_event = \{ id = rip_gov_test\.(\d+)', text))
assert fired <= set(ids), f'events fired but not defined: {sorted(fired - set(ids))}'
assert '1' in ids, 'event rip_gov_test.1 is the entry point'

# ---- every key an event names has a text
for key in set(re.findall(r'\b(?:title|desc|name)\s*=\s*(rip_gov_test\.[\w.]+)', text)):
    assert key in loc_keys, f'missing localisation: {key}'

# ---- coverage: one apply event per reform and government type that lists it
gov = gen.load_governments()
reforms = gen.load_reforms()
basic = {gov[g]['basic']: g for g in gov}
expected = set()
for rid in reforms:
    if rid in basic:
        expected.add((rid, basic[rid]))
        continue
    found = [g for g in gen.TYPE_ORDER if g in gov and any(rid in ids_ for _, ids_ in gov[g]['tiers'])]
    assert found, f'{rid} is in no tier of common/governments/00_governments.txt'
    expected.update((rid, g) for g in found)
present = set(re.findall(r'RIP_GOV_TEST BEGIN (\S+) ([^\s"]+)', text))
missing = sorted(expected - present)
extra = sorted(present - expected)
assert not missing, ('no fixture option for ' + ', '.join(f'{r} ({g})' for r, g in missing) +
                     ' - run python tests/dev_tools/make_government_reform_test.py')
assert not extra, 'fixture options for reforms that no longer exist: ' + ', '.join(f'{r} ({g})' for r, g in extra)
for rid, g in expected:
    assert f'log = "RIP_GOV_TEST HELD_OK {rid} {g}"' in text, f'{rid} has no held check'

# ---- the shipped mod never carries or calls the fixture
for installed in gen.INSTALLED:
    assert not installed.exists(), (f'{installed.relative_to(ROOT)} is an installed copy of the fixture; '
                                    'run python tests/dev_tools/make_government_reform_test.py --remove')
for directory in ('common', 'events', 'decisions', 'missions', 'interface', 'localisation', 'customizable_localization'):
    for path in (ROOT / directory).rglob('*'):
        if path.suffix not in ('.txt', '.yml', '.gui', '.gfx'):
            continue
        body = re.sub(r'#[^\n]*', '', path.read_bytes().decode('latin-1'))
        assert 'rip_gov_test' not in body, f'{path.relative_to(ROOT)} refers to the test fixture'

# ---- soft: stale output is reported, not failed (a regenerate is one command)
fresh = gen.generate()
stale = [p.name for p, new in ((EVENTS, fresh[3]), (LOC, fresh[4]))
         if p.read_text(encoding='utf-8').replace('\r\n', '\n') != new.replace('\r\n', '\n')]
note = f'; STALE vs the live script: {", ".join(stale)} (run make_government_reform_test.py)' if stale else ''
print(f'PASS: {len(expected)} reform variants have an option, events and texts are well formed, '
      f'the shipped mod does not carry the fixture{note}')
