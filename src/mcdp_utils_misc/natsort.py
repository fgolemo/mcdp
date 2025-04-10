# -*- coding: utf-8 -*-
import re


def natural_sort_key(s):
    """
    Sort strings containing natural numbers correctly.
    
    This works the same in Python 2 and 3, but is included for completeness.
    """
    # If s is not a string, convert it to one
    if not isinstance(s, str):
        s = str(s)
    
    # Convert s to lowercase for case-insensitive sorting
    s = s.lower()
    
    # Split string into text and numeric parts
    return [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', s)]


def natural_sorted(seq):
    """
    Sort sequence in natural order (1, 2, 10 instead of 1, 10, 2).
    
    This implementation handles more complex cases than the original.
    """
    return sorted(seq, key=natural_sort_key)