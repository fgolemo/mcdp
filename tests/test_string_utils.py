#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test the string_utils module for Python 3 compatibility.
"""
import unittest
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

# Import the module to test
from mcdp_utils_misc.string_utils import get_md5, get_sha1, format_list

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
    
    def test_get_md5_with_unicode(self):
        """Test get_md5 with Unicode characters."""
        # MD5 for "café" (with an accented e)
        result1 = get_md5("café")
        # Should be consistent when passed as bytes with utf-8 encoding
        result2 = get_md5("café".encode('utf-8'))
        self.assertEqual(result1, result2)
    
    def test_format_list_empty(self):
        """Test format_list with an empty list."""
        result = format_list([])
        self.assertEqual(result, "(empty)")
    
    def test_format_list_single(self):
        """Test format_list with a single item."""
        result = format_list(["test"])
        self.assertEqual(result, '"test"')
    
    def test_format_list_multiple(self):
        """Test format_list with multiple items."""
        result = format_list(["test1", "test2", "test3"])
        self.assertEqual(result, '"test1", "test2", "test3"')
    
    def test_format_list_objects(self):
        """Test format_list with objects that need string conversion."""
        class TestObj:
            def __str__(self):
                return "TestObj"
        
        result = format_list([TestObj(), TestObj()])
        self.assertEqual(result, '"TestObj", "TestObj"')

if __name__ == "__main__":
    unittest.main()