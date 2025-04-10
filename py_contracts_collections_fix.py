#!/usr/bin/env python3
"""
Script to fix collections imports in vendor/py_contracts files.
"""
import os
import re
import sys

def fix_collections_imports(file_path):
    """
    Find and fix imports of collections.Sequence and other ABC classes.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Check if file uses collections.Sequence or other collections.ABC types
    if not re.search(r'collections\.(Sequence|MutableMapping|Mapping|Set|MutableSet|Iterable)', content):
        return False
        
    # Add import for collections.abc
    if 'import collections' in content and 'collections.abc' not in content:
        modified_content = re.sub(
            r'import collections(\s|;|$)',
            'import collections\n'
            'try:\n'
            '    from collections.abc import Sequence, MutableMapping, Mapping, Set, MutableSet, Iterable\n'
            'except ImportError:\n'
            '    # Python 2 compatibility\n'
            '    Sequence = collections.Sequence\n'
            '    MutableMapping = collections.MutableMapping\n'
            '    Mapping = collections.Mapping\n'
            '    Set = collections.Set\n'
            '    MutableSet = collections.MutableSet\n'
            '    Iterable = collections.Iterable\n',
            content
        )
        
        # Replace usages of collections.ABC with direct ABC
        modified_content = re.sub(
            r'collections\.(Sequence|MutableMapping|Mapping|Set|MutableSet|Iterable)',
            r'\1',
            modified_content
        )
        
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(modified_content)
        
        return True
    
    return False

def process_directory(directory):
    """
    Process all Python files in a directory and its subdirectories.
    """
    files_modified = 0
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    if fix_collections_imports(file_path):
                        files_modified += 1
                        print(f"Fixed collections imports in: {file_path}")
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
    return files_modified

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python py_contracts_collections_fix.py <directory>")
        sys.exit(1)
    
    directory = sys.argv[1]
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory")
        sys.exit(1)
    
    files_modified = process_directory(directory)
    print(f"Modified files: {files_modified}")