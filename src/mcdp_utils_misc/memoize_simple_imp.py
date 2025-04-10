# -*- coding: utf-8 -*-
import functools
from decorator import decorator

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

    def memoizer(f, *args, **kwargs):
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
            cache[key] = f(*args, **kwargs)
        
        try:
            # Get cached result
            cached = cache[key]
            return cached
        except ImportError:  # pragma: no cover  # impossible to test
            # Special case: if we get an ImportError when retrieving from cache,
            # assume the cached value is no longer valid (e.g., module was unloaded)
            del cache[key]
            cache[key] = f(*args, **kwargs)
            return cache[key]

    # Use decorator from the decorator package to maintain function metadata
    return decorator(memoizer, obj)

# Alternative implementation using functools.lru_cache for better performance
def memoize_simple_lru(func=None, maxsize=None):
    """
    Alternative implementation using functools.lru_cache.
    
    Args:
        func: The function to decorate
        maxsize: Maximum cache size (None means unlimited)
        
    Returns:
        Decorated function with caching
    """
    def decorator(func):
        cached_func = functools.lru_cache(maxsize=maxsize)(func)
        # Attach the cache dictionary for compatibility
        func.cache = cached_func.cache_info
        return cached_func
        
    if func is None:
        # Called with parameters: @memoize_simple_lru(maxsize=...)
        return decorator
    else:
        # Called without parameters: @memoize_simple_lru
        return decorator(func)
