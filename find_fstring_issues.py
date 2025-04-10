#!/usr/bin/env python3
"""
Find common f-string formatting issues in Python code.

This script analyzes Python files to identify common patterns of f-string
formatting issues without making changes. It's useful for understanding
the scope of issues before applying fixes.

Usage:
    python find_fstring_issues.py path/to/file_or_dir
"""

import argparse
import os
import re
import sys
from collections import Counter
from typing import Dict, List, Tuple

# Patterns to search for
PATTERNS = {
    'attribute_access': re.compile(r'f([\'"])(.*?)\{(\w+)\}\.(\w+)(.*?)(\1)'),
    'mixed_format': re.compile(r'f([\'"])(.*?)\{.*?\}.*?(%[sdrf])(.*?)(\1)'),
    'chained_format': re.compile(r'f([\'"])(.*?)(\1)\.format\('),
    'percent_after': re.compile(r'f([\'"])(.*?)(\1)\s*%'),
    'incomplete_brace': re.compile(r'f([\'"])(.*?)\{(.*?[^}])(\1)'),
    'str_in_fstring': re.compile(r'f([\'"])(.*?)\{str\((.*?)\)\}(.*?)(\1)'),
}

def find_issues_in_file(file_path: str) -> Dict[str, List[Tuple[int, str]]]:
    """
    Find all f-string formatting issues in a file.
    
    Args:
        file_path: Path to the Python file to analyze
        
    Returns:
        Dictionary mapping issue type to list of (line_number, line_content) tuples
    """
    issues = {pattern_name: [] for pattern_name in PATTERNS}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines):
        for pattern_name, pattern in PATTERNS.items():
            if pattern.search(line):
                issues[pattern_name].append((i+1, line.strip()))
    
    return issues

def find_issues_in_directory(dir_path: str) -> Dict[str, Dict[str, List[Tuple[int, str]]]]:
    """
    Find all f-string formatting issues in Python files in a directory.
    
    Args:
        dir_path: Path to the directory to analyze
        
    Returns:
        Dictionary mapping file paths to issue dictionaries
    """
    all_issues = {}
    
    for root, _, files in os.walk(dir_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    issues = find_issues_in_file(file_path)
                    if any(len(issues_list) > 0 for issues_list in issues.values()):
                        all_issues[file_path] = issues
                except Exception as e:
                    print(f"Error processing {file_path}: {str(e)}")
    
    return all_issues

def main():
    parser = argparse.ArgumentParser(description='Find common f-string formatting issues in Python code.')
    parser.add_argument('path', help='Path to the file or directory to analyze')
    parser.add_argument('--summary', action='store_true', help='Show only summary counts')
    args = parser.parse_args()
    
    path = args.path
    
    if not os.path.exists(path):
        print(f"Error: Path '{path}' does not exist.")
        return 1
    
    if os.path.isfile(path):
        issues = find_issues_in_file(path)
        total_issues = sum(len(issue_list) for issue_list in issues.values())
        
        print(f"Found {total_issues} potential issues in {path}:")
        for pattern_name, issue_list in issues.items():
            if issue_list:
                print(f"\n{pattern_name}: {len(issue_list)} issues")
                if not args.summary:
                    for line_num, line in issue_list:
                        print(f"  Line {line_num}: {line}")
    
    elif os.path.isdir(path):
        all_issues = find_issues_in_directory(path)
        
        # Count total issues by type
        issue_counts = Counter()
        for file_issues in all_issues.values():
            for pattern_name, issue_list in file_issues.items():
                issue_counts[pattern_name] += len(issue_list)
        
        total_files = len(all_issues)
        total_issues = sum(issue_counts.values())
        
        print(f"Found {total_issues} potential issues in {total_files} files:")
        for pattern_name, count in issue_counts.most_common():
            print(f"  {pattern_name}: {count} issues")
        
        if not args.summary:
            print("\nIssues by file:")
            for file_path, file_issues in all_issues.items():
                rel_path = os.path.relpath(file_path, path)
                file_total = sum(len(issue_list) for issue_list in file_issues.values())
                if file_total > 0:
                    print(f"\n{rel_path}: {file_total} issues")
                    for pattern_name, issue_list in file_issues.items():
                        if issue_list:
                            print(f"  {pattern_name}: {len(issue_list)} issues")
                            for line_num, line in issue_list[:3]:  # Show first 3 examples
                                print(f"    Line {line_num}: {line}")
                            if len(issue_list) > 3:
                                print(f"    ... and {len(issue_list) - 3} more")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())