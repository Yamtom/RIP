"""Catch missing custom religious helper implementations, including old callers."""
from pathlib import Path
import re

from clausewitz_testlib import ROOT, _mask_comments_and_strings

PREFIX = r'rip_(?:ro|ob|uc|ucr|faith|parish|crusade|kyiv|church)_[A-Za-z0-9_]+_(?:effect|trigger)'
CALL = re.compile(r'\b(' + PREFIX + r')\s*=\s*(?:yes\b|no\b|\{)')
# A condition-style helper has no _effect/_trigger suffix (rip_church_ro_can_separate = yes), so CALL never saw it:
# rip_church_ro_can_break_communion lost its definition and the decision calling it stayed, and that decision never loaded.
OWN_CALL = re.compile(r'\b(rip_[A-Za-z0-9_]+)\s*=\s*(?:yes|no)\b')


def helper_definitions(text):
    masked = _mask_comments_and_strings(text)
    return set(re.findall(r'(?m)^(' + PREFIX + r')\s*=\s*\{', masked))


def own_definitions(text):
    return set(re.findall(r'(?m)^[ \t]*(rip_[A-Za-z0-9_]+)\s*=\s*\{', _mask_comments_and_strings(text)))


def missing_calls(text, defined):
    masked = _mask_comments_and_strings(text)
    return [(match[1], masked.count('\n', 0, match.start()) + 1)
            for match in CALL.finditer(masked) if match[1] not in defined]


def unresolved_own_calls(text, defined):
    masked = _mask_comments_and_strings(text)
    return [(match[1], masked.count('\n', 0, match.start()) + 1)
            for match in OWN_CALL.finditer(masked) if match[1] not in defined]


assert helper_definitions('rip_ucr_fixture_effect = { }') == {'rip_ucr_fixture_effect'}
assert not helper_definitions('# rip_ucr_fake_effect = { }')
assert missing_calls('option = { rip_ucr_missing_effect = yes }', set()) == [('rip_ucr_missing_effect', 1)]
assert missing_calls('rip_faith_missing_effect = { MODIFIER = foo }', set())
assert not missing_calls('# rip_ucr_missing_effect = yes\ntext = "rip_ucr_missing_effect = yes"', set())
assert own_definitions('rip_church_ro_can_separate = { }\n rip_church_indented = { }\n# rip_church_fake = { }') == {'rip_church_ro_can_separate', 'rip_church_indented'}
assert unresolved_own_calls('allow = { rip_church_ro_can_break_communion = yes }', set()) == [('rip_church_ro_can_break_communion', 1)]
assert not unresolved_own_calls('allow = { rip_church_ro_can_separate = yes }', {'rip_church_ro_can_separate'})
assert not unresolved_own_calls('# rip_church_gone = yes\nhas_country_flag = rip_church_gone', set())

defined = set()
defined_own = set()
for directory in ('common/scripted_effects', 'common/scripted_triggers'):
    for path in (ROOT / directory).glob('*.txt'):
        text = path.read_bytes().decode('latin-1')
        defined |= helper_definitions(text)
        defined_own |= own_definitions(text)
failures = {}
for directory in ('common', 'events', 'decisions', 'missions'):
    for path in sorted((ROOT / directory).rglob('*.txt')):
        text = path.read_bytes().decode('latin-1')
        where = path.relative_to(ROOT)
        for name, line in missing_calls(text, defined):
            failures[(where, line, name)] = f'{where}:{line}: missing implementation {name}'
        for name, line in unresolved_own_calls(text, defined_own):
            failures.setdefault((where, line, name), f'{where}:{line}: {name} is called but no scripted trigger or effect defines it')
if failures:
    print('\n'.join(failures.values()))
    raise SystemExit(1)
print(f'FAITH SCRIPTED LINKS PASS: {len(defined)} religious helpers, {len(defined_own)} rip_ helpers; no unresolved direct custom calls.')
