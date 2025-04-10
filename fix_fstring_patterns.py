#!/usr/bin/env python3
"""
Fix common f-string formatting issues in Python code.

This script identifies and fixes several common patterns of f-string
formatting errors in Python code. It can be run on a specific file
or directory to automatically fix these issues.

Common patterns fixed:
1. Attribute access after object in f-string: {obj}.attr -> {obj.attr}
2. Mixed f-string with %-style formatting
3. Chained string formatting with f-strings

Usage:
    python fix_fstring_patterns.py path/to/file_or_dir
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Pattern, Tuple, Union

# Pattern 1: Attribute access after object in f-string
# Example: f"Created from #{s}.creation_order" -> f"Created from #{s.creation_order}"
PATTERN_ATTR_ACCESS = re.compile(r'f([\'"])(.*?)\{(\w+)\}\.(\w+)(.*?)(\1)')

# Pattern 2: Mixed f-string with %-style formatting
# Example: f"Loop constraint not satisfied {F2.format(r} <= %s not satisfied." % F2.format(f2)
# This is more complex and needs more careful handling - often manual inspection

# Pattern 3: Chained string formatting with .format()
# Example: f"R = {UR}".format(si_next) -> f"R = {UR.format(si_next)}"
PATTERN_CHAINED_FORMAT = re.compile(r'f([\'"])(.*?)(\1)\.format\((.*?)\)')

def fix_attribute_access(match) -> str:
    """Fix attribute access in f-strings."""
    quote = match.group(1)
    prefix = match.group(2)
    obj = match.group(3)
    attr = match.group(4)
    suffix = match.group(5)
    
    return f'f{quote}{prefix}{{{obj}.{attr}}}{suffix}{quote}'

def fix_chained_format(match) -> str:
    """Fix chained format calls on f-strings."""
    quote = match.group(1)
    content = match.group(2)
    format_args = match.group(4)
    
    # This is a simplistic approach - might need manual review
    # Assuming there's just one format argument
    if ',' not in format_args and '=' not in format_args:
        return f'f{quote}{content}.format({format_args}){quote}'
    else:
        # More complex format args - mark for manual review
        return f'# MANUAL REVIEW NEEDED: {match.group(0)}'

def process_file(file_path: str) -> Tuple[int, int, List[str]]:
    """
    Process a single Python file, applying fixes for f-string patterns.
    
    Args:
        file_path: Path to the Python file to process
        
    Returns:
        Tuple containing: 
            - Number of fixes made
            - Number of potential issues that need manual review
            - List of lines needing manual review
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    fixes_made = 0
    manual_review_needed = 0
    manual_review_lines = []
    
    # Fix attribute access in f-strings
    new_content, attr_fixes = re.subn(PATTERN_ATTR_ACCESS, fix_attribute_access, content)
    fixes_made += attr_fixes
    content = new_content
    
    # Fix chained format calls
    new_content, format_fixes = re.subn(PATTERN_CHAINED_FORMAT, fix_chained_format, content)
    content = new_content
    
    # Count manual review markers
    manual_lines = re.findall(r'# MANUAL REVIEW NEEDED:', content)
    manual_review_needed += len(manual_lines)
    
    # Find line numbers for manual review
    if manual_review_needed > 0:
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if '# MANUAL REVIEW NEEDED:' in line:
                manual_review_lines.append(f"Line {i+1}: {line}")
    
    # Only write back if changes were made
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    return fixes_made, manual_review_needed, manual_review_lines

def process_directory(dir_path: str) -> Dict[str, Tuple[int, int, List[str]]]:
    """
    Process all Python files in a directory recursively.
    
    Args:
        dir_path: Path to the directory to process
        
    Returns:
        Dictionary mapping file paths to results (fixes, manual reviews needed, manual review lines)
    """
    results = {}
    
    for root, _, files in os.walk(dir_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    fixes, manual, lines = process_file(file_path)
                    if fixes > 0 or manual > 0:
                        results[file_path] = (fixes, manual, lines)
                except Exception as e:
                    print(f"Error processing {file_path}: {str(e)}")
                    
    return results

def main():
    parser = argparse.ArgumentParser(description='Fix common f-string formatting issues in Python code.')
    parser.add_argument('path', help='Path to the file or directory to process')
    args = parser.parse_args()
    
    path = args.path
    
    if not os.path.exists(path):
        print(f"Error: Path '{path}' does not exist.")
        return 1
    
    total_fixes = 0
    total_manual = 0
    
    if os.path.isfile(path):
        fixes, manual, lines = process_file(path)
        total_fixes += fixes
        total_manual += manual
        
        print(f"Processed {path}:")
        print(f"  - {fixes} fixes applied")
        print(f"  - {manual} issues need manual review")
        
        if manual > 0:
            print("\nLines needing manual review:")
            for line in lines:
                print(f"  {line}")
    
    elif os.path.isdir(path):
        results = process_directory(path)
        
        print(f"Processed {len(results)} files with issues in directory '{path}':")
        
        for file_path, (fixes, manual, lines) in results.items():
            rel_path = os.path.relpath(file_path, path)
            total_fixes += fixes
            total_manual += manual
            
            print(f"\n{rel_path}:")
            print(f"  - {fixes} fixes applied")
            print(f"  - {manual} issues need manual review")
            
            if manual > 0:
                print("  Lines needing manual review:")
                for line in lines:
                    print(f"    {line}")
    
    print(f"\nTotal: {total_fixes} fixes applied, {total_manual} issues need manual review")
    return 0

if __name__ == '__main__':
    sys.exit(main())