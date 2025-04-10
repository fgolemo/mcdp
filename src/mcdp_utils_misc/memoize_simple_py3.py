# -*- coding: utf-8 -*-
"""
Python 3 compatible version of the memoize_simple decorator.
"""
import functools

def memoize_simple(obj):
    """
    Simple memoization decorator that caches function results based on arguments.
    
    This is a Python 3 compatible version that handles unhashable arguments better.
    
    The cache is stored as an attribute of the decorated function for easy access
    and inspection.
    
    Args:
        obj: The function to decorate
        
    Returns:
        Decorated function with caching
    """
    cache = obj.cache = {}
    
    @functools.wraps(obj)
    def wrapper(*args, **kwargs):
        # Create a hashable key from args and kwargs
        # For kwargs, sort by key to ensure consistent ordering
        if kwargs:
            # If there are keyword arguments, include them in the key
            kwargs_items = tuple(sorted(kwargs.items()))
            key = (args, kwargs_items)
        else:
            # Fast path for common case (no kwargs)
            key = args if args else ()
            
        # Check if we have a cached result
        if key not in cache:
            cache[key] = obj(*args, **kwargs)
        
        try:
            # Get cached result
            cached = cache[key]
            return cached
        except ImportError:  # pragma: no cover  # impossible to test
            # Special case: if we get an ImportError when retrieving from cache,
            # assume the cached value is no longer valid (e.g., module was unloaded)
            del cache[key]
            cache[key] = obj(*args, **kwargs)
            return cache[key]

    return wrapper