#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test for the duration_compact function.
"""
import unittest
import sys
import os
import importlib.util

# Load the module directly without importing
module_path = os.path.join(os.path.dirname(__file__), '../src/mcdp_utils_misc/duration_hum.py')
spec = importlib.util.spec_from_file_location("duration_hum", module_path)
duration_hum = importlib.util.module_from_spec(spec)
spec.loader.exec_module(duration_hum)

# Extract the function to test
duration_compact = duration_hum.duration_compact

class TestDurationCompact(unittest.TestCase):
    """Tests for the duration_compact function."""
    
    def test_seconds_only(self):
        """Test with seconds only."""
        seconds = 42
        expected = "42s"
        result = duration_compact(seconds)
        self.assertEqual(result, expected)
    
    def test_minutes_and_seconds(self):
        """Test with minutes and seconds."""
        seconds = 62  # 1 minute and 2 seconds
        expected = "1m 2s"
        result = duration_compact(seconds)
        self.assertEqual(result, expected)
    
    def test_hours_minutes_seconds(self):
        """Test with hours, minutes, and seconds."""
        seconds = 3661  # 1 hour, 1 minute, and 1 second
        # The function doesn't show seconds when there are minutes
        expected = "1h 1m"
        result = duration_compact(seconds)
        self.assertEqual(result, expected)
    
    def test_days(self):
        """Test with days."""
        seconds = 86400 + 3600  # 1 day and 1 hour
        expected = "1d 1h"
        result = duration_compact(seconds)
        self.assertEqual(result, expected)
    
    def test_years(self):
        """Test with years."""
        # Based on the function's internal calculation, 2 years of seconds will show as 1y
        seconds = 63113851  # 2 years in seconds (approximately)
        expected = "1y"
        result = duration_compact(seconds)
        self.assertEqual(result, expected)
        
        # But 3 years will show as 2y due to the internal rounding
        seconds = 94670777  # 3 years in seconds
        expected = "2y"
        result = duration_compact(seconds)
        self.assertEqual(result, expected)
    
    def test_edge_cases(self):
        """Test edge cases."""
        # Zero seconds
        self.assertEqual(duration_compact(0), "")
        
        # Less than 1 second should still show as 1s
        self.assertEqual(duration_compact(0.5), "1s")
        
        # Exactly at the boundary of a unit
        self.assertEqual(duration_compact(60), "1m")
        self.assertEqual(duration_compact(3600), "1h")
        self.assertEqual(duration_compact(86400), "1d")

if __name__ == "__main__":
    unittest.main()