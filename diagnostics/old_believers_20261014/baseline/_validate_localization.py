#!/usr/bin/env python3
"""Validate church localization generator output."""
import sys
from pathlib import Path

# Add tools to path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'tools'))

# Import and run the localization builder in check mode
import argparse
original_argv = sys.argv
try:
    sys.argv = ['build_church_localisation.py', '--check']
    exec(open(ROOT / 'tools' / 'build_church_localisation.py').read())
finally:
    sys.argv = original_argv
