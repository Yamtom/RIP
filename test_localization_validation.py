"""Test church localization generator output."""
import sys
from pathlib import Path
import subprocess

def test_build_church_localisation_check():
    """Validate church localization using --check mode."""
    root = Path(__file__).resolve().parent.parent
    result = subprocess.run(
        [sys.executable, str(root / 'tools' / 'build_church_localisation.py'), '--check'],
        cwd=str(root),
        capture_output=True,
        text=True
    )
    print(f"\nOutput: {result.stdout}")
    if result.stderr:
        print(f"Errors: {result.stderr}")
    assert result.returncode == 0, f"Localization check failed with exit code {result.returncode}"

if __name__ == '__main__':
    test_build_church_localisation_check()
