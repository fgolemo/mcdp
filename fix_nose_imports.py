#!/usr/bin/env python3
"""
Script to fix nose imports in Python files by replacing them with imports from
the local nose_compat.py module.
"""
import os
import re
import sys

def fix_nose_imports(file_path):
    """
    Replace nose.tools imports with local nose_compat imports.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Find existing imports from nose.tools
    nose_import_pattern = r'from\s+nose\.tools\s+import\s+([\w,\s]+)'
    
    # Check if we need to modify this file
    if not re.search(nose_import_pattern, content):
        return False
    
    # Extract the imported names from nose.tools
    match = re.search(nose_import_pattern, content)
    if match:
        imported_items = match.group(1).split(',')
        # Clean up the imported items (strip whitespace)
        imported_items = [item.strip() for item in imported_items if item.strip()]
        
        # Create the new import statement from nose_compat
        new_import = f"from .nose_compat import {', '.join(imported_items)}"
        
        # Replace the original import with the new one
        updated_content = re.sub(nose_import_pattern, new_import, content)
        
        # Write the updated content back to the file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(updated_content)
        
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
                    if fix_nose_imports(file_path):
                        files_modified += 1
                        print(f"Fixed nose imports in: {file_path}")
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
    return files_modified

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fix_nose_imports.py <directory>")
        sys.exit(1)
    
    directory = sys.argv[1]
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory")
        sys.exit(1)
    
    files_modified = process_directory(directory)
    print(f"Modified files: {files_modified}")