#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test the memoize_simple function for Python 3 compatibility."""

import unittest
import time
from mcdp_utils_misc.memoize_simple_imp import memoize_simple, memoize_simple_lru

class TestMemoizeSimple(unittest.TestCase):
    """Tests for the memoize_simple decorator."""
    
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
    
    def test_cache_attribute(self):
        """Test that the cache attribute is accessible."""
        @memoize_simple
        def test_func(x):
            return x * 2
        
        # Call the function to populate the cache
        test_func(10)
        test_func(20)
        
        # Check that cache contains the expected keys
        self.assertIn((10,), test_func.cache)
        self.assertIn((20,), test_func.cache)
        
        # Check that cache contains the expected values
        self.assertEqual(test_func.cache[(10,)], 20)
        self.assertEqual(test_func.cache[(20,)], 40)
    
    def test_performance(self):
        """Test that memoization improves performance."""
        @memoize_simple
        def slow_func(x):
            time.sleep(0.01)  # Simulate a slow function
            return x * 2
        
        # First call should be slow
        start = time.time()
        slow_func(10)
        first_duration = time.time() - start
        
        # Second call should be much faster
        start = time.time()
        slow_func(10)
        second_duration = time.time() - start
        
        # Cached call should be significantly faster (at least 10x)
        self.assertLess(second_duration, first_duration / 10)
    
    def test_memoize_simple_lru(self):
        """Test the alternative lru_cache implementation."""
        call_count = 0
        
        @memoize_simple_lru
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
        
        # Check that cache info is available
        info = test_func.cache_info()
        self.assertEqual(info.hits, 1)  # We've had one cache hit
        self.assertEqual(info.misses, 2)  # And two cache misses

if __name__ == '__main__':
    unittest.main()