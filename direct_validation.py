#!/usr/bin/env python3
"""Direct validation of church localization generator."""

import sys
import os
from pathlib import Path

# Set up paths
os.chdir(Path(__file__).resolve().parent)
ROOT = Path.cwd()

# Simulate argparse setup for check mode
class MockArgs:
    check = True

# Import key components needed for validation
import json
import re

# Load the build script and extract outputs dictionary
exec(compile(
    open(ROOT / 'tools' / 'build_church_localisation.py').read(),
    str(ROOT / 'tools' / 'build_church_localisation.py'),
    'exec'
), {'__name__': '__main__', 'args': MockArgs()})
