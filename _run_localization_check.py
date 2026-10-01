#!/usr/bin/env python3
"""Quick validator for build_church_localisation.py --check logic."""

from pathlib import Path
import sys
import json
import re

ROOT = Path(__file__).resolve().parents[1]

# Import the build script by reading and executing it
build_script = (ROOT / 'tools' / 'build_church_localisation.py').read_text(encoding='utf-8')

# Replace the main execution with our check
build_script = build_script.replace(
    "ap=argparse.ArgumentParser(); ap.add_argument('--check',action='store_true'); args=ap.parse_args()",
    "class Args: check=True\nargs=Args()"
)

# Execute the build script
namespace = {'__file__': str(ROOT / 'tools' / 'build_church_localisation.py'), '__name__': '__main__'}
exec(build_script, namespace)
