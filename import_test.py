#!/usr/bin/env python
"""Simple script to test imports."""

import sys
print(f"Python version: {sys.version}")

try:
    from mcdp import __version__ as mcdp_version
    print(f"MCDP version: {mcdp_version}")
except Exception as e:
    print(f"Error importing mcdp: {e}")

try:
    from mcdp.constants import MCDPConstants
    print(f"MCDPConstants defined: {bool(MCDPConstants)}")
except Exception as e:
    print(f"Error importing MCDPConstants: {e}")