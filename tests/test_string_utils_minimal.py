#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Minimal test for string_utils functions without full imports.
"""
import unittest

# Direct import of the functions from the file
import sys
import os
import importlib.util

# Load the module directly without importing
module_path = os.path.join(os.path.dirname(__file__), '../src/mcdp_utils_misc/string_utils.py')
spec = importlib.util.spec_from_file_location("string_utils", module_path)
string_utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(string_utils)

# Extract the functions we want to test
get_md5 = string_utils.get_md5
get_sha1 = string_utils.get_sha1
format_list = string_utils.format_list

class TestStringUtils(unittest.TestCase):
    """Tests for string_utils functions."""
    
    def test_get_md5_with_string(self):
        """Test get_md5 with a string input."""
        # Known MD5 for "test"
        expected = "098f6bcd4621d373cade4e832627b4f6"
        result = get_md5("test")
        self.assertEqual(result, expected)
    
    def test_get_md5_with_bytes(self):
        """Test get_md5 with a bytes input."""
        # Known MD5 for "test"
        expected = "098f6bcd4621d373cade4e832627b4f6"
        result = get_md5(b"test")
        self.assertEqual(result, expected)
    
    def test_get_sha1_with_string(self):
        """Test get_sha1 with a string input."""
        # Known SHA1 for "test"
        expected = "a94a8fe5ccb19ba61c4c0873d391e987982fbbd3"
        result = get_sha1("test")
        self.assertEqual(result, expected)
    
    def test_get_sha1_with_bytes(self):
        """Test get_sha1 with a bytes input."""
        # Known SHA1 for "test"
        expected = "a94a8fe5ccb19ba61c4c0873d391e987982fbbd3"
        result = get_sha1(b"test")
        self.assertEqual(result, expected)
    
    def test_format_list_empty(self):
        """Test format_list with an empty list."""
        result = format_list([])
        self.assertEqual(result, "(empty)")
    
    def test_format_list_multiple(self):
        """Test format_list with multiple items."""
        result = format_list(["test1", "test2", "test3"])
        self.assertEqual(result, '"test1", "test2", "test3"')

if __name__ == "__main__":
    unittest.main()