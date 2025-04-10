#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script to verify imports of Python 3 migrated modules.
Run this after each module is converted to check for issues.
"""
import importlib
import sys
import traceback

def test_import_module(module_name):
    """Test importing a specific module."""
    try:
        if '.' in module_name:
            parent, child = module_name.rsplit('.', 1)
            module = importlib.import_module(parent)
            getattr(module, child)
            print(f"✅ Successfully imported {module_name}")
            return True
        else:
            module = importlib.import_module(module_name)
            print(f"✅ Successfully imported {module_name}")
            return module
    except Exception as e:
        print(f"❌ Failed to import {module_name}: {e}")
        traceback.print_exc()
        return False

def test_all_modules(modules):
    """Test importing multiple modules."""
    results = {}
    success_count = 0
    
    for module_name in modules:
        result = test_import_module(module_name)
        results[module_name] = result is not False
        if results[module_name]:
            success_count += 1
    
    print(f"\nSummary: Successfully imported {success_count}/{len(modules)} modules")
    
    # Print failed modules
    if success_count < len(modules):
        print("\nFailed modules:")
        for module, success in results.items():
            if not success:
                print(f"  - {module}")
    
    return success_count == len(modules)

if __name__ == "__main__":
    # Define the modules to test, in dependency order
    core_modules = [
        "mcdp.py_compatibility",
        "mcdp.branch_info",
        "mcdp.logs",
        "mcdp.constants",
        "mcdp.dependencies",
        "mcdp.development",
        "mcdp"  # Test importing the main package
    ]
    
    # Test core modules
    print("Testing core modules...")
    core_success = test_all_modules(core_modules)
    
    # Exit with status code based on test results
    sys.exit(0 if core_success else 1)