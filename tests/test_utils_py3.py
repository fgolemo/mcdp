#!/usr/bin/env python3
# Test for Python 3 compatibility of mcdp_utils_misc

import os
import sys
import tempfile
import unittest
import gzip

# Add the src directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

class TestUtilsPy3(unittest.TestCase):
    """Tests for Python 3 compatibility of mcdp_utils_misc."""
    
    def test_fileutils(self):
        """Test fileutils functions."""
        from mcdp_utils_misc.fileutils import read_file_encoded_as_utf8, create_tmpdir, tmpdir, tmpfile
        
        # Create a temporary file with UTF-8 content
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False) as f:
            f.write("Test UTF-8 file with unicode: αβγδε")
            temp_file = f.name
        
        try:
            # Test read_file_encoded_as_utf8
            content = read_file_encoded_as_utf8(temp_file)
            self.assertIsInstance(content, bytes)
            self.assertEqual(content.decode('utf-8'), "Test UTF-8 file with unicode: αβγδε")
            
            # Test create_tmpdir
            temp_dir = create_tmpdir(prefix='test_py3_')
            self.assertTrue(os.path.exists(temp_dir))
            os.rmdir(temp_dir)
            
            # Test tmpdir context manager
            with tmpdir(prefix='test_py3_') as d:
                self.assertTrue(os.path.exists(d))
            self.assertFalse(os.path.exists(d))  # Should be cleaned up
            
            # Test tmpfile context manager
            with tmpfile(suffix='.txt') as f:
                self.assertTrue(os.path.exists(f))
            self.assertFalse(os.path.exists(f))  # Should be cleaned up
                
        finally:
            # Clean up
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_safe_write(self):
        """Test safe_write functions."""
        from mcdp_utils_misc.safe_write import safe_write, safe_read
        
        # Test safe_write with text mode and encoding
        test_file = os.path.join(tempfile.gettempdir(), 'test_safe_write.txt')
        if os.path.exists(test_file):
            os.unlink(test_file)
            
        # Write with encoding
        with safe_write(test_file, mode='wt', encoding='utf-8') as f:
            f.write("Test UTF-8 file with unicode: αβγδε")
            
        # Read back with encoding
        with safe_read(test_file, mode='rt', encoding='utf-8') as f:
            content = f.read()
            self.assertEqual(content, "Test UTF-8 file with unicode: αβγδε")
            
        # Test with gzip
        test_gz_file = os.path.join(tempfile.gettempdir(), 'test_safe_write.txt.gz')
        if os.path.exists(test_gz_file):
            os.unlink(test_gz_file)
            
        # Write with gzip
        with safe_write(test_gz_file, mode='wt', encoding='utf-8') as f:
            f.write("Test gzipped UTF-8 file with unicode: αβγδε")
            
        # Read with gzip
        with safe_read(test_gz_file, mode='rt', encoding='utf-8') as f:
            content = f.read()
            self.assertEqual(content, "Test gzipped UTF-8 file with unicode: αβγδε")
            
        # Clean up
        os.unlink(test_file)
        os.unlink(test_gz_file)
    
    def test_yaml(self):
        """Test YAML utilities."""
        from mcdp_utils_misc.my_yaml import yaml_load, yaml_dump
        
        # Test simple data structures
        data = {
            'string': 'test',
            'int': 123,
            'list': [1, 2, 3],
            'dict': {'a': 1, 'b': 2},
            'none': None
        }
        
        # Dump and load
        yaml_str = yaml_dump(data)
        loaded_data = yaml_load(yaml_str)
        
        # Check that it loaded correctly
        self.assertEqual(loaded_data['string'], 'test')
        self.assertEqual(loaded_data['int'], 123)
        self.assertEqual(loaded_data['list'], [1, 2, 3])
        self.assertEqual(loaded_data['dict'], {'a': 1, 'b': 2})
        self.assertIsNone(loaded_data['none'])
    
    def test_natsort(self):
        """Test natural sorting."""
        from mcdp_utils_misc.natsort import natural_sorted
        
        # Test with mixed strings and numbers
        items = ['file10.txt', 'file1.txt', 'file2.txt', 'file20.txt']
        sorted_items = natural_sorted(items)
        
        # Check that it's sorted correctly (1, 2, 10, 20)
        self.assertEqual(sorted_items, ['file1.txt', 'file2.txt', 'file10.txt', 'file20.txt'])
    
    def test_pickling(self):
        """Test pickling utilities."""
        from mcdp_utils_misc.safe_pickling import safe_pickle_dump, safe_pickle_load
        
        # Create a temporary file
        test_pickle = os.path.join(tempfile.gettempdir(), 'test_pickle.pkl')
        if os.path.exists(test_pickle):
            os.unlink(test_pickle)
            
        # Data to pickle
        data = {
            'string': 'test',
            'int': 123,
            'list': [1, 2, 3],
            'dict': {'a': 1, 'b': 2},
            'none': None
        }
        
        # Dump and load
        safe_pickle_dump(data, test_pickle)
        loaded_data = safe_pickle_load(test_pickle)
        
        # Check that it loaded correctly
        self.assertEqual(loaded_data['string'], 'test')
        self.assertEqual(loaded_data['int'], 123)
        self.assertEqual(loaded_data['list'], [1, 2, 3])
        self.assertEqual(loaded_data['dict'], {'a': 1, 'b': 2})
        self.assertIsNone(loaded_data['none'])
        
        # Clean up
        os.unlink(test_pickle)

    def test_timing(self):
        """Test timing utilities."""
        from mcdp_utils_misc.timing import timeit, timeit_wall
        import time
        from io import StringIO
        from contextlib import redirect_stdout
        
        # Test timeit
        # Capture the output
        output = StringIO()
        
        # Define a dummy logger
        class DummyLogger:
            def debug(self, msg):
                print(msg)
        
        # Use timeit with our dummy logger
        with redirect_stdout(output):
            with timeit("test operation", logger=DummyLogger()):
                # Simulate work
                for _ in range(10000):
                    pass
        
        # Check that the output contains expected text
        result = output.getvalue()
        self.assertIn("timeit result:", result)
        self.assertIn("for test operation", result)
        
        # Test timeit_wall
        output = StringIO()
        with redirect_stdout(output):
            with timeit_wall("test wall operation", logger=DummyLogger()):
                # Sleep for a predictable amount of time
                time.sleep(0.01)
        
        # Check that the output contains expected text
        result = output.getvalue()
        self.assertIn("timeit test wall operation", result)
        self.assertIn("timeit result:", result)
    
    def test_locate_files(self):
        """Test locate_files function."""
        from mcdp_utils_misc.locate_files_imp import locate_files
        
        # Create a temporary directory structure
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create some files
            file1 = os.path.join(tmp_dir, "test1.txt")
            file2 = os.path.join(tmp_dir, "test2.log")
            subdir = os.path.join(tmp_dir, "subdir")
            os.mkdir(subdir)
            file3 = os.path.join(subdir, "test3.txt")
            
            # Create the files
            for filename in [file1, file2, file3]:
                with open(filename, 'w') as f:
                    f.write("test")
            
            # Test finding txt files
            files = locate_files(tmp_dir, "*.txt")
            self.assertEqual(len(files), 2)
            
            # Test finding all files
            files = locate_files(tmp_dir, "*.*")
            self.assertEqual(len(files), 3)
            
            # Test finding files with specific pattern
            files = locate_files(tmp_dir, ["*.txt", "*.log"])
            self.assertEqual(len(files), 3)
    
    def test_memo_disk_cache(self):
        """Test memo_disk_cache2 function."""
        from mcdp_utils_misc.memos_selection import memo_disk_cache2
        
        # Create a temporary directory for the cache
        with tempfile.TemporaryDirectory() as tmp_dir:
            cache_file = os.path.join(tmp_dir, "cache.pickle")
            
            # Define a function to memoize
            call_count = 0
            def expensive_func():
                nonlocal call_count
                call_count += 1
                return "result"
            
            # Call the function with memoization
            data = "test_data"
            result = memo_disk_cache2(cache_file, data, expensive_func)
            self.assertEqual(result, "result")
            self.assertEqual(call_count, 1)
            
            # Call again with the same data - should use cache
            result = memo_disk_cache2(cache_file, data, expensive_func)
            self.assertEqual(result, "result")
            self.assertEqual(call_count, 1)  # Should not have incremented
            
            # Call with different data - should recompute
            result = memo_disk_cache2(cache_file, "different_data", expensive_func)
            self.assertEqual(result, "result")
            self.assertEqual(call_count, 2)  # Should have incremented
    
    def test_good_identifiers(self):
        """Test good_identifiers module."""
        from mcdp_utils_misc.good_identifiers import is_good_plain_identifier
        
        # Valid identifiers
        self.assertTrue(is_good_plain_identifier("valid"))
        self.assertTrue(is_good_plain_identifier("Valid"))
        self.assertTrue(is_good_plain_identifier("valid_name"))
        self.assertTrue(is_good_plain_identifier("valid_name_123"))
        self.assertTrue(is_good_plain_identifier("_valid"))
        
        # Invalid identifiers
        self.assertFalse(is_good_plain_identifier("123invalid"))
        self.assertFalse(is_good_plain_identifier("invalid-name"))
        self.assertFalse(is_good_plain_identifier("invalid.name"))
        self.assertFalse(is_good_plain_identifier("invalid name"))
        self.assertFalse(is_good_plain_identifier(""))
        
    def test_dir_from_package_name(self):
        """Test dir_from_package_name function."""
        from mcdp_utils_misc.dir_from_package_nam import dir_from_package_name
        
        # Test with a known package
        # We'll use the mcdp package itself since we know it exists
        path = dir_from_package_name("mcdp")
        self.assertTrue(os.path.exists(path))
        self.assertTrue(os.path.isdir(path))

if __name__ == '__main__':
    unittest.main()