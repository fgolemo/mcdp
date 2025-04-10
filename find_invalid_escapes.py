#!/usr/bin/env python3
"""
Script to find and report invalid escape sequences in Python strings.
"""
import os
import re
import sys

def scan_file_for_invalid_escapes(file_path):
    """
    Scan a file for strings with invalid escape sequences.
    """
    with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
        try:
            content = file.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return []
    
    # Define patterns for string literals (single, double, triple quotes)
    string_patterns = [
        r'r?"""(.*?)"""',  # Triple double quotes
        r"r?'''(.*?)'''",  # Triple single quotes
        r'r?"(.*?)"',      # Double quotes
        r"r?'(.*?)'",      # Single quotes
    ]
    
    # Known problematic escape sequences to check
    invalid_escapes = [r'\i', r'\g', r'\d', r'\.', r'\ ']
    
    results = []
    
    line_offsets = [m.start() for m in re.finditer('\n', content)]
    line_offsets.insert(0, 0)
    
    def get_line_number(pos):
        for i, offset in enumerate(line_offsets):
            if pos < offset:
                return i
            if i == len(line_offsets) - 1 or pos < line_offsets[i+1]:
                return i + 1
        return len(line_offsets)
    
    for pattern in string_patterns:
        # Find all string literals that aren't raw strings
        for match in re.finditer(pattern, content, re.DOTALL):
            if match.group(0).startswith('r'):
                continue  # Skip raw strings
                
            string_content = match.group(1)
            
            # Check for each invalid escape
            for bad_escape in invalid_escapes:
                # Use negative lookbehind to avoid matching already escaped sequences
                positions = [m.start() for m in re.finditer(r'(?<!\\)' + re.escape(bad_escape), string_content)]
                
                for pos in positions:
                    abs_pos = match.start(1) + pos
                    line_num = get_line_number(abs_pos)
                    
                    # Extract the line context
                    line_start = line_offsets[line_num - 1] if line_num > 0 else 0
                    line_end = line_offsets[line_num] if line_num < len(line_offsets) else len(content)
                    line = content[line_start:line_end].strip()
                    
                    results.append({
                        'file': file_path,
                        'line': line_num,
                        'escape': bad_escape,
                        'context': line
                    })
    
    return results

def process_directory(directory):
    """
    Process all Python files in a directory and its subdirectories.
    """
    all_results = []
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    results = scan_file_for_invalid_escapes(file_path)
                    all_results.extend(results)
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
    
    return all_results

def report_results(results):
    """
    Generate a report of all found issues.
    """
    if not results:
        print("No invalid escape sequences found.")
        return
    
    print(f"Found {len(results)} potential invalid escape sequences:")
    current_file = None
    
    for result in sorted(results, key=lambda x: (x['file'], x['line'])):
        if result['file'] != current_file:
            current_file = result['file']
            print(f"\n{current_file}:")
        
        print(f"  Line {result['line']}: {result['escape']} in {result['context'][:70]}...")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python find_invalid_escapes.py <directory>")
        sys.exit(1)
    
    directory = sys.argv[1]
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory")
        sys.exit(1)
    
    results = process_directory(directory)
    report_results(results)