# -*- coding: utf-8 -*-
import sys

from contracts.utils import check_isinstance
from contracts.utils import raise_desc


def printable_length_where(w):
    """ Returns the printable length of the substring """
    from mcdp.py_compatibility import PY2
    
    sub = w.string[w.character:w.character_end]
    
    if PY2:
        # Python 2 handling
        if isinstance(sub, str):
            return len(unicode(sub, 'utf-8'))
        else:
            return len(sub)
    else:
        # Python 3 handling
        return len(sub)


def line_and_col(loc, strg):
    """Returns (line, col), both 0 based."""
    
    check_isinstance(loc, int)
    check_isinstance(strg, str)
    # first find the line 
    lines = strg.split('\n')
    
    if loc == len(strg):
        # Special case: we mark the end of the string
        last_line = len(lines) - 1
        last_char = len(lines[-1]) 
        return last_line, last_char  
        
    if loc > len(strg):
        msg = (f"Invalid loc = {loc} for s of len {len(strg} (%r)", strg))
        raise ValueError(msg)
    
    res_line = 0
    l = loc
    while True:
        if not lines:
            assert loc == 0, (loc, strg.__repr__())
            break

        first = lines[0]
        if l >= len(first) + len('\n'):
            lines = lines[1:]
            l -= (len(first) + len('\n'))
            res_line += 1
        else:
            break
    res_col = l
    inverse = location(res_line, res_col, strg)
    if inverse != loc:
        msg = 'Could not find line and col'
        
        raise_desc(AssertionError, msg, s=strg, loc=loc, res_line=res_line,
                   res_col=res_col, loc_recon=inverse)
        
    return (res_line, res_col)

def location(line, col, s):
    check_isinstance(line, int)
    check_isinstance(col, int)
    check_isinstance(s, str)
    
    lines = s.split('\n')
    previous_lines = sum(len(l) + len('\n') for l in lines[:line])
    offset = col
    return previous_lines + offset

def add_prefix(s, prefix):
    result = ""
    for l in s.split('\n'):
        result += prefix + l + '\n'
    # chop last newline
    result = result[:-1]
    return result