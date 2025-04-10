#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Compatibility module for Python 3.
This provides Python 3 alternatives for Python 2 functions and types.
"""
import sys
import inspect
import io

# Python version check
PY2 = sys.version_info[0] == 2

# String types
string_types = (str,)
integer_types = (int,)

# Dictionary methods
def iterkeys(d):
    """Return iterator over dictionary keys."""
    return iter(d.keys())

def itervalues(d):
    """Return iterator over dictionary values."""
    return iter(d.values())

def iteritems(d):
    """Return iterator over dictionary items."""
    return iter(d.items())

# String/bytes handling
def ensure_str(s):
    """Ensure string type (str in Python 3)."""
    if isinstance(s, bytes):
        return s.decode('utf-8')
    return s

# Exception handling
def raise_with_traceback(exc, tb):
    """Raise exception with traceback in Python 3."""
    raise exc.with_traceback(tb)

# Function argument inspection
def get_arg_spec(func):
    """Get function argument specification."""
    return inspect.getfullargspec(func)

# Range is already an iterable in Python 3
range = range

# IO classes
StringIO = io.StringIO
BytesIO = io.BytesIO

# Map, zip, filter return iterators in Python 3
def ensure_list(it):
    """Convert iterators to lists where compatibility with Python 2 is needed."""
    return list(it)

# Division always returns float in Python 3, use // for integer division
def ensure_integer_division(a, b):
    """Ensure integer division."""
    return a // b

# Common functionality
def is_string(obj):
    """Check if an object is a string."""
    return isinstance(obj, string_types)

def is_integer(obj):
    """Check if an object is an integer."""
    return isinstance(obj, integer_types)

def with_metaclass(meta, *bases):
    """Create a class with a metaclass."""
    # From six implementation
    class metaclass(meta):
        def __new__(cls, name, this_bases, d):
            return meta(name, bases, d)
    return type.__new__(metaclass, 'temporary_class', (), {})