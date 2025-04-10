#!/usr/bin/env python3
"""
Script to automatically convert Python 2 print statements to Python 3 style.
"""
import os
import re
import sys

def fix_print_statements(file_path):
    """
    Replace Python 2 print statements with Python 3 print function calls.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # This regex finds print statements that are not already function calls
    # It handles print with and without trailing newlines and conditionals
    pattern = r'(^|\n)(\s*)print\s+([^(].*?)(?=\n|$)'
    conditional_pattern = r'(if|elif|else|while|for)(.*?):\s+print\s+([^(].*?)(?=\n|$)'
    
    # Replace print statements with print function calls
    # The re.DOTALL flag ensures it matches across newlines
    updated_content = re.sub(pattern, r'\1\2print(\3)', content, flags=re.DOTALL)
    
    # Replace conditional print statements
    updated_content = re.sub(conditional_pattern, r'\1\2: print(\3)', updated_content, flags=re.DOTALL)
    
    # Write the updated content back to the file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(updated_content)

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
                    fix_print_statements(file_path)
                    files_modified += 1
                    print(f"Fixed print statements in: {file_path}")
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
    return files_modified

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fix_print_statements.py <directory>")
        sys.exit(1)
    
    directory = sys.argv[1]
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory")
        sys.exit(1)
    
    files_modified = process_directory(directory)
    print(f"Processed files: {files_modified}")