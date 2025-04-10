#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test importing the mcdp_utils_misc modules to verify Python 3 compatibility.
"""
import importlib
import sys

def test_import_module(module_name):
    """Test importing a specific module."""
    try:
        module = importlib.import_module(module_name)
        print(f"✅ Successfully imported {module_name}")
        return module
    except Exception as e:
        print(f"❌ Failed to import {module_name}: {e}")
        return False

if __name__ == "__main__":
    # Test importing the memoize_simple modules and string_repr
    modules = [
        "mcdp_utils_misc.memoize_simple_py3",
        "mcdp_utils_misc.indent_utils",
        "mcdp_utils_misc.string_repr",
        "mcdp_utils_misc",  # Test that the whole package can be imported
    ]
    
    success_count = 0
    for module_name in modules:
        result = test_import_module(module_name)
        if result is not False:
            success_count += 1
    
    print(f"\nSummary: Successfully imported {success_count}/{len(modules)} modules")
    sys.exit(0 if success_count == len(modules) else 1)