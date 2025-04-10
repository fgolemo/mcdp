"""
Utility for running comptests with pytest.
This file adds test prefix to comptests.
"""
import functools
import inspect
import sys

from comptests.registrar import comptest


def make_test_functions():
    """Create test functions for all comptests in the module."""
    # Get all modules in mcdp_lang_tests
    module_names = [
        name for name in sys.modules
        if name.startswith('mcdp_lang_tests.') and
        not name.endswith('test_prefix')
    ]
    
    # For each module
    for module_name in module_names:
        module = sys.modules.get(module_name)
        if not module:
            continue
        
        # Find all functions with @comptest decorator
        comptests = []
        for name in dir(module):
            item = getattr(module, name)
            if callable(item) and hasattr(item, '__comptests__'):
                comptests.append(item)
        
        # Skip modules without comptests
        if not comptests:
            continue
        
        # Create test functions for this module
        module_shortname = module_name.split('.')[-1]
        for func in comptests:
            func_name = func.__name__
            test_name = f"test_{module_shortname}_{func_name}"
            
            # Create the test function as a wrapper
            @functools.wraps(func)
            def test_func():
                return func()
            
            # Set name and add to globals
            test_func.__name__ = test_name
            globals()[test_name] = test_func


# Run this at import time to create test functions
make_test_functions()