#!/usr/bin/env python3
"""
Script to fix invalid escape sequences in Python code.
"""
import os
import re
import sys

def fix_escape_sequences(file_path):
    """
    Find and fix invalid escape sequences in Python strings.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Track if we made changes
    changes_made = False
    
    # Define patterns for string literals (single, double, triple quotes)
    string_patterns = [
        r'r?"""(.*?)"""',  # Triple double quotes
        r"r?'''(.*?)'''",  # Triple single quotes
        r'r?"(.*?)"',      # Double quotes
        r"r?'(.*?)'",      # Single quotes
    ]
    
    # Known problematic escape sequences to fix
    escape_fixes = {
        r'\i': r'\\i',  # Invalid \i -> \\i (literal backslash + i)
        r'\g': r'\\g',  # Invalid \g -> \\g
        r'\d': r'\\d',  # This might actually be intended as a digit, careful
        r'\.': r'\\.',  # Invalid \. -> \\. (literal backslash + dot)
        r'\ ': r'\\ ',  # Invalid \  -> \\  (literal backslash + space)
    }
    
    for pattern in string_patterns:
        # Find all string literals
        for match in re.finditer(pattern, content, re.DOTALL):
            string_content = match.group(1)
            modified_content = string_content
            
            # Apply fixes to the string content
            for bad_escape, good_escape in escape_fixes.items():
                # Only fix if it's not in a raw string (r"...")
                if not match.group(0).startswith('r'):
                    # Use negative lookbehind to avoid fixing already escaped sequences
                    # e.g., don't convert \\i to \\\i
                    modified_content = re.sub(
                        r'(?<!\\)' + re.escape(bad_escape), 
                        good_escape, 
                        modified_content
                    )
            
            # Replace in the original content if changes were made
            if modified_content != string_content:
                content = content.replace(match.group(0), match.group(0).replace(string_content, modified_content))
                changes_made = True
    
    # Write back only if changes were made
    if changes_made:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        return True
    
    return False

def convert_percent_formatting(file_path):
    """
    Convert old-style % string formatting to f-strings where possible.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Track if we made changes
    changes_made = False
    
    # Match patterns like: "text %s more" % var or "text %d %s" % (num, str)
    # Be careful with multi-line strings and complex expressions
    simple_pattern = r'([\'"].*?[\'"])\s*%\s*(\w+)'
    tuple_pattern = r'([\'"].*?[\'"])\s*%\s*\((.*?)\)'
    
    # Process simple replacements first (single variable)
    for match in re.finditer(simple_pattern, content):
        try:
            string_part = match.group(1)
            var_part = match.group(2)
            
            # Skip if the string part doesn't contain formatting specifiers
            if '%' not in string_part:
                continue
                
            # Extract the string without quotes
            inner_string = string_part[1:-1]
            
            # Simple %s to {var} conversion
            if '%s' in inner_string:
                # Replace %s with the variable
                new_inner = inner_string.replace('%s', '{' + var_part + '}')
                # Create new f-string
                replacement = f'f"{new_inner}"'
                # Replace in content
                content = content.replace(match.group(0), replacement)
                changes_made = True
        except Exception:
            # Skip complex cases for now
            continue
    
    # Process tuple-based formatting (multiple variables)
    for match in re.finditer(tuple_pattern, content):
        try:
            string_part = match.group(1)
            vars_part = match.group(2)
            
            # Skip if the string part doesn't contain formatting specifiers
            if '%' not in string_part:
                continue
                
            # Extract the string without quotes
            inner_string = string_part[1:-1]
            
            # Split variables by comma, but handle nested parentheses properly
            vars_list = []
            current = ""
            paren_level = 0
            for char in vars_part:
                if char == ',' and paren_level == 0:
                    vars_list.append(current.strip())
                    current = ""
                else:
                    if char == '(':
                        paren_level += 1
                    elif char == ')':
                        paren_level -= 1
                    current += char
            if current:
                vars_list.append(current.strip())
            
            # Simple conversion for %s, %d, etc.
            # This is a simplified approach; full conversion would need more context
            new_inner = inner_string
            for i, var in enumerate(vars_list):
                if f'%s' in new_inner:
                    new_inner = new_inner.replace('%s', '{' + var + '}', 1)
                elif f'%d' in new_inner:
                    new_inner = new_inner.replace('%d', '{' + var + '}', 1)
                elif f'%f' in new_inner:
                    new_inner = new_inner.replace('%f', '{' + var + '}', 1)
                elif f'%.2f' in new_inner:
                    new_inner = new_inner.replace('%.2f', '{' + var + ':.2f}', 1)
                
            # Create new f-string if changes were made
            if new_inner != inner_string:
                replacement = f'f"{new_inner}"'
                content = content.replace(match.group(0), replacement)
                changes_made = True
        except Exception:
            # Skip complex cases for now
            continue
    
    # Write back only if changes were made
    if changes_made:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        return True
    
    return False

def fix_integer_division(file_path):
    """
    Fix integer division issues by converting / to // where appropriate.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Track if we made changes
    changes_made = False
    
    # Find potential integer division operations
    # Look for patterns like: number / number
    # This is simplified and won't catch all cases
    int_division_pattern = r'(\b\d+\s*/\s*\d+\b)|(\b\w+\s*/\s*\d+\b)|(\b\d+\s*/\s*\w+\b)'
    
    # Process matches
    for match in re.finditer(int_division_pattern, content):
        division_expr = match.group(0)
        # Skip if it's already integer division
        if '//' in division_expr:
            continue
        
        # Replace / with // if it appears to be integer division
        # This is a heuristic approach and may need manual review
        replacement = division_expr.replace('/', '//')
        content = content.replace(division_expr, replacement)
        changes_made = True
    
    # Write back only if changes were made
    if changes_made:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        return True
    
    return False

def process_directory(directory):
    """
    Process all Python files in a directory and its subdirectories.
    """
    escape_fixes = 0
    format_fixes = 0
    division_fixes = 0
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    if fix_escape_sequences(file_path):
                        escape_fixes += 1
                        print(f"Fixed escape sequences in: {file_path}")
                    
                    if convert_percent_formatting(file_path):
                        format_fixes += 1
                        print(f"Converted string formatting in: {file_path}")
                    
                    if fix_integer_division(file_path):
                        division_fixes += 1
                        print(f"Fixed integer division in: {file_path}")
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
    
    return {
        'escape_fixes': escape_fixes,
        'format_fixes': format_fixes,
        'division_fixes': division_fixes
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fix_escape_sequences.py <directory>")
        sys.exit(1)
    
    directory = sys.argv[1]
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory")
        sys.exit(1)
    
    results = process_directory(directory)
    print(f"Files with escape sequence fixes: {results['escape_fixes']}")
    print(f"Files with string formatting fixes: {results['format_fixes']}")
    print(f"Files with integer division fixes: {results['division_fixes']}")