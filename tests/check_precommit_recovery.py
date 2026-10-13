"""Exercise the real hook in an isolated index; never stage the user's files."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='rip-hook-test-') as directory:
    repo = Path(directory)
    for relative in ('.githooks/pre-commit', '.githooks/find-python.ps1',
                     'tests/check_file_encoding.py', 'tests/check_clausewitz_braces.py',
                     'tests/clausewitz_testlib.py'):
        target = repo / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
    (repo / '.githooks/pre-commit').chmod(0o755)
    env = os.environ.copy()
    # Ignore parent repository selectors when invoked from another Git hook.
    for key in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_COMMON_DIR'):
        env.pop(key, None)
    def git(*args):
        return subprocess.run(['git', *args], cwd=repo, env=env,
                              capture_output=True, text=True)
    assert git('init', '-q').returncode == 0
    assert git('config', 'core.hooksPath', '.githooks').returncode == 0
    for override in (sys.executable, '', str(repo / 'deleted-python.exe')):
        env['RIP_PYTHON'] = override
        result = git('hook', 'run', 'pre-commit')
        assert result.returncode == 0, (override, result.stdout, result.stderr)
    engine = repo / 'events/probe.txt'
    engine.parent.mkdir()
    engine.write_bytes(b'\xef\xbb\xbfprobe = {}\n')
    assert git('add', 'events/probe.txt').returncode == 0
    # Repair only the working copy: the staged BOM must still block the commit.
    engine.write_bytes(b'probe = {}\n')
    result = git('hook', 'run', 'pre-commit')
    assert result.returncode != 0 and 'ENCODING FAIL' in result.stdout + result.stderr, result
    assert git('add', 'events/probe.txt').returncode == 0
    engine.write_bytes(b'probe = {\n')
    result = git('hook', 'run', 'pre-commit')
    assert result.returncode != 0 and 'brace failures' in result.stdout + result.stderr, result
print('PASS: explicit, absent and stale Python; staged BOM and working-tree braces still block.')
