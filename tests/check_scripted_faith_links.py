"""Catch missing custom religious helper implementations, including old callers."""
from pathlib import Path
import re

from clausewitz_testlib import ROOT, _mask_comments_and_strings

PREFIX = r'rip_(?:ro|uc|ucr|faith|parish|crusade|kyiv|church)_[A-Za-z0-9_]+_(?:effect|trigger)'
CALL = re.compile(r'\b(' + PREFIX + r')\s*=\s*(?:yes\b|no\b|\{)')


def helper_definitions(text):
    masked = _mask_comments_and_strings(text)
    return set(re.findall(r'(?m)^(' + PREFIX + r')\s*=\s*\{', masked))


def missing_calls(text, defined):
    masked = _mask_comments_and_strings(text)
    return [(match[1], masked.count('\n', 0, match.start()) + 1)
            for match in CALL.finditer(masked) if match[1] not in defined]


assert helper_definitions('rip_ucr_fixture_effect = { }') == {'rip_ucr_fixture_effect'}
assert not helper_definitions('# rip_ucr_fake_effect = { }')
assert missing_calls('option = { rip_ucr_missing_effect = yes }', set()) == [('rip_ucr_missing_effect', 1)]
assert missing_calls('rip_faith_missing_effect = { MODIFIER = foo }', set())
assert not missing_calls('# rip_ucr_missing_effect = yes\ntext = "rip_ucr_missing_effect = yes"', set())

defined = set()
for directory in ('common/scripted_effects', 'common/scripted_triggers'):
    for path in (ROOT / directory).glob('*.txt'):
        defined |= helper_definitions(path.read_bytes().decode('latin-1'))
failures = []
for directory in ('common', 'events', 'decisions', 'missions'):
    for path in sorted((ROOT / directory).rglob('*.txt')):
        for name, line in missing_calls(path.read_bytes().decode('latin-1'), defined):
            failures.append(f'{path.relative_to(ROOT)}:{line}: missing implementation {name}')
if failures:
    print('\n'.join(failures))
    raise SystemExit(1)
print(f'FAITH SCRIPTED LINKS PASS: {len(defined)} religious helpers; no unresolved direct custom calls.')
