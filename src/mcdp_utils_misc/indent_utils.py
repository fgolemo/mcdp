# -*- coding: utf-8 -*-
"""
Utility functions for indentation that don't depend on external packages.
This module provides a replacement for contracts.utils.indent to avoid 
dependency on the PyContracts package.
"""

def indent(s, prefix='  ', first=None):
    """
    Indents a string using the given prefix for each line.
    
    Args:
        s: The string to indent
        prefix: The prefix to use for each line
        first: Optional different prefix for the first line
        
    Returns:
        The indented string
    """
    if first is None:
        first = prefix
        
    lines = s.split('\n')
    if not lines:
        return ''
        
    # Add prefix to first line
    if lines[0]:
        lines[0] = first + lines[0]
        
    # Add prefix to remaining lines
    for i in range(1, len(lines)):
        if lines[i]:
            lines[i] = prefix + lines[i]
            
    return '\n'.join(lines)