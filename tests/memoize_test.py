#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Completely independent test for memoize_simple functionality.
"""
import functools
import unittest
import time

def memoize_simple(obj):
    """
    Simple memoization decorator that caches function results based on arguments.
    """
    cache = obj.cache = {}
    
    @functools.wraps(obj)
    def wrapper(*args, **kwargs):
        if kwargs:
            # Include keyword arguments in the key
            kwargs_items = tuple(sorted(kwargs.items()))
            key = (args, kwargs_items)
        else:
            # Fast path for common case (no kwargs)
            key = args if args else ()
            
        if key not in cache:
            cache[key] = obj(*args, **kwargs)
        
        return cache[key]

    return wrapper

class TestMemoize(unittest.TestCase):
    """Basic tests for the memoize_simple decorator."""
    
    def test_basic_memoization(self):
        """Test that the function results are cached."""
        call_count = 0
        
        @memoize_simple
        def test_func(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # First call should execute the function
        result1 = test_func(10)
        self.assertEqual(result1, 20)
        self.assertEqual(call_count, 1)
        
        # Second call with the same argument should use the cache
        result2 = test_func(10)
        self.assertEqual(result2, 20)
        self.assertEqual(call_count, 1)  # Count should still be 1
        
        # Call with different argument should execute the function
        result3 = test_func(20)
        self.assertEqual(result3, 40)
        self.assertEqual(call_count, 2)
    
    def test_with_kwargs(self):
        """Test that the function caches results with keyword arguments."""
        call_count = 0
        
        @memoize_simple
        def test_func(x, y=10):
            nonlocal call_count
            call_count += 1
            return x * y
        
        # First call with kwargs
        result1 = test_func(5, y=10)
        self.assertEqual(result1, 50)
        self.assertEqual(call_count, 1)
        
        # Same call with kwargs should use cache
        result2 = test_func(5, y=10)
        self.assertEqual(result2, 50)
        self.assertEqual(call_count, 1)
        
        # Different kwargs should execute the function
        result3 = test_func(5, y=20)
        self.assertEqual(result3, 100)
        self.assertEqual(call_count, 2)

if __name__ == "__main__":
    unittest.main()