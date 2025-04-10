#!/usr/bin/env python3
"""
Script to fix collections module imports for Python 3 compatibility.
This handles the change in Python 3.10+ where ABC classes moved from collections to collections.abc.
"""
import os
import re
import sys

def fix_collections_imports(file_path):
    """
    Find and fix imports of collections module for Python 3 compatibility.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Track if we made changes
    changes_made = False
    
    # Collection ABC classes that have moved
    abc_classes = [
        'Sequence', 'MutableSequence',
        'MutableMapping', 'Mapping',
        'Set', 'MutableSet',
        'Iterable', 'Iterator', 'Generator',
        'Container', 'Sized', 'Callable',
        'Collection', 'ByteString',
        'MappingView', 'KeysView', 'ItemsView', 'ValuesView',
        'Awaitable', 'Coroutine', 'AsyncIterable', 'AsyncIterator'
    ]
    
    # Create regex pattern for all ABC classes
    abc_pattern = '|'.join(abc_classes)
    collections_usage_pattern = rf'collections\.({abc_pattern})'
    
    # Check if any collection ABC classes are used
    if not re.search(collections_usage_pattern, content):
        return False
    
    # Build import compatibility code
    import_code = (
        "import collections\n"
        "try:\n"
        "    from collections.abc import "
    )
    
    # Find which classes are actually used
    used_classes = []
    for match in re.finditer(collections_usage_pattern, content):
        class_name = match.group(1)
        if class_name not in used_classes:
            used_classes.append(class_name)
    
    # Add the used classes to the import code
    import_code += ", ".join(used_classes)
    import_code += "\n"
    import_code += "except ImportError:\n"
    import_code += "    # Python 2 compatibility\n"
    
    # Add fallback for each used class
    for class_name in used_classes:
        import_code += f"    {class_name} = collections.{class_name}\n"
    
    # Different cases for adding the import
    if 'import collections' in content and 'collections.abc' not in content:
        # Replace simple import
        modified_content = re.sub(
            r'import collections(\s|;|$)',
            import_code,
            content
        )
        changes_made = True
    elif 'from collections import' in content:
        # Handle from collections import X, Y, Z
        import_pattern = r'from collections import (.*?)($|\n)'
        
        def process_import_match(match):
            imported_items = match.group(1).split(',')
            updated_imports = []
            abc_imports = []
            
            for item in imported_items:
                item = item.strip()
                if item in abc_classes:
                    abc_imports.append(item)
                else:
                    updated_imports.append(item)
            
            result = ""
            if updated_imports:
                result += f"from collections import {', '.join(updated_imports)}\n"
            
            if abc_imports:
                result += "try:\n"
                result += f"    from collections.abc import {', '.join(abc_imports)}\n"
                result += "except ImportError:\n"
                result += "    # Python 2 compatibility\n"
                for cls in abc_imports:
                    result += f"    from collections import {cls}\n"
            
            return result
        
        modified_content = re.sub(import_pattern, process_import_match, content)
        if modified_content != content:
            changes_made = True
    else:
        # Add import at the beginning of the file, after any module docstring
        docstring_pattern = r'^(""".*?"""|\'\'\'.*?\'\'\')?\s*'
        module_start = re.match(docstring_pattern, content, re.DOTALL)
        if module_start:
            insert_pos = module_start.end()
        else:
            insert_pos = 0
        
        modified_content = content[:insert_pos] + "\n" + import_code + "\n" + content[insert_pos:]
        changes_made = True
    
    # Replace direct usage (collections.X with just X)
    if changes_made:
        for class_name in used_classes:
            modified_content = re.sub(
                rf'collections\.{class_name}',
                class_name,
                modified_content
            )
        
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(modified_content)
    
    return changes_made

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
        print("Usage: python fix_collections_imports.py <directory>")
        sys.exit(1)
    
    directory = sys.argv[1]
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory")
        sys.exit(1)
    
    files_modified = process_directory(directory)
    print(f"Fixed collections imports in {files_modified} files")