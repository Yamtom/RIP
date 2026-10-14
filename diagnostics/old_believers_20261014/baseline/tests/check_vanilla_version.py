"""Do not let a 1.30 donor silently certify a 1.37 mod."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from clausewitz_testlib import vanilla_version, vanilla_matches_target, target_vanilla_series

assert target_vanilla_series() == '1.37', 'Update target-version contracts if the mod is ported'
with TemporaryDirectory(prefix='rip_version_') as temp:
    root = Path(temp)
    for data, expected, supported in (
        ({'rawVersion': '1.30.3'}, '1.30.3', False),
        ({'rawVersion': 'v1.37.5.0'}, '1.37.5.0', True),
        ({'version': 'EU4 v1.37.5.0 Inca'}, '1.37.5.0', True),
        ({'rawVersion': '1.3.7'}, '1.3.7', False),
        ({'rawVersion': '1.38.0'}, '1.38.0', False),
        ({}, None, False),
    ):
        (root / 'launcher-settings.json').write_text(json.dumps(data), encoding='utf-8')
        assert vanilla_version(root) == expected, data
        assert vanilla_matches_target(root, '1.37') is supported, data
    (root / 'launcher-settings.json').write_text('not json', encoding='utf-8')
    assert vanilla_version(root) is None
    assert not vanilla_matches_target(root)
print('PASS: target metadata, donor rejection, unknown metadata and version boundaries')
