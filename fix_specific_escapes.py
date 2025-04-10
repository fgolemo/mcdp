#!/usr/bin/env python3
"""
Script to fix specific invalid escape sequences identified in the codebase.
"""
import os

# Define specific files and their fixes
# These are manual, text-based substitutions, not regex patterns
fixes = {
    'src/mcdp_dp/dp_limit.py': [
        ('h: f \\in \\downarrow values', 'h: f \\\\in \\\\downarrow values')
    ],
    'src/mcdp_dp/dp_loop2.py': [
        ('Returns the next iteration  si \\in UR', 'Returns the next iteration  si \\\\in UR')
    ],
    'src/mcdp_dp/dp_parallel.py': [
        ("indent(r1, '. ', first='\\ ')", "indent(r1, '. ', first='\\\\ ')"),
        ("indent(r2, '. ', first='\\ ')", "indent(r2, '. ', first='\\\\ ')")
    ],
    'src/mcdp_dp/dp_parallel_n.py': [
        ("indent(r, '. ', first='\\ ')", "indent(r, '. ', first='\\\\ ')")
    ],
    'src/mcdp_dp/dp_series.py': [
        ("indent(r1, '. ', first='\\ ')", "indent(r1, '. ', first='\\\\ ')"),
        ("indent(r2, '. ', first='\\ ')", "indent(r2, '. ', first='\\\\ ')")
    ],
    'src/mcdp_dp/opaque_dp.py': [
        ("indent(r1, '. ', first='\\ ')", "indent(r1, '. ', first='\\\\ ')")
    ],
    'src/mcdp_dp/primitive.py': [
        ("f' \\in eval(I).f", "f' \\\\in eval(I).f")
    ],
    'src/mcdp_dp_tests/inv_mult_plots.py': [
        ("f0 \\in h(-, f0)", "f0 \\\\in h(-, f0)")
    ],
    'src/mcdp_lang/pyparsing_bundled.py': [
        ("xmlcharref = Regex('&#\\d+;')", "xmlcharref = Regex('&#\\\\d+;')"),
        ('ret = re.sub(self.escCharReplacePattern,"\\g<1>",ret)', 'ret = re.sub(self.escCharReplacePattern,"\\\\g<1>",ret)')
    ],
    'src/mcdp_lang/suggestions.py': [
        ("r = '%s.*\\..*%s' % (dp, s)", "r = '%s.*\\\\..*%s' % (dp, s)"),
        ("r = '%s.*\\..*%s' % (dp, s)", "r = '%s.*\\\\..*%s' % (dp, s)")
    ]
}

def fix_specific_file(file_path, replacements):
    """
    Apply specific text replacements to a file.
    """
    # First check if the file exists
    if not os.path.exists(file_path):
        print(f"Warning: File {file_path} does not exist")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
            content = file.read()
        
        original_content = content
        for old_text, new_text in replacements:
            content = content.replace(old_text, new_text)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            return True
        
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def fix_all_identified_issues():
    """
    Apply all the specific fixes identified in the codebase.
    """
    fixed_files = 0
    
    for file_path, replacements in fixes.items():
        if fix_specific_file(file_path, replacements):
            fixed_files += 1
            print(f"Fixed escape sequences in: {file_path}")
    
    return fixed_files

if __name__ == "__main__":
    fixed_files = fix_all_identified_issues()
    print(f"Fixed escape sequences in {fixed_files} files")