# Memoization Issues with Unhashable Types in MCDP

## Problem Analysis

During Python 3 migration testing, we encountered errors related to unhashable types in the memoization system:

```
TypeError: unhashable type: 'RcompUnits'
```

### Root Causes

1. **Python's Memoization Requirements**:
   - Dictionary keys in Python must be hashable (immutable)
   - Classes like `RcompUnits` appear to be unhashable in the current implementation

2. **Current Memoization Implementation**:
   - Located in `src/mcdp_utils_misc/memoize_simple_imp.py`
   - Uses a simple cache dictionary with tuples of arguments as keys
   - Does not handle unhashable object types

3. **Complex Object Types**:
   - Many MCDP objects like `RcompUnits` are complex custom classes
   - These classes don't implement `__hash__` or are mutable (thus unhashable)
   - Such objects cannot be used as dictionary keys in their current form

## Impact

This issue prevents running tests that use these unhashable types as function arguments, which affects:

1. The `syntax_anyof.py` tests, which use `RcompUnits` objects
2. Potentially many other tests throughout the codebase
3. Normal operation of functions that rely on memoization with these types

## Potential Solutions

### Approach 1: Make Objects Hashable

1. **Implement `__hash__` and `__eq__` Methods**:
   ```python
   class RcompUnits:
       def __hash__(self):
           # Generate a hash based on immutable attributes
           return hash(tuple(sorted(self.__dict__.items())))
           
       def __eq__(self, other):
           if not isinstance(other, RcompUnits):
               return False
           return self.__dict__ == other.__dict__
   ```

2. **Enforce Immutability**:
   - Make relevant classes immutable by using read-only properties
   - Prevent modification after initialization
   - Use frozen dataclasses for new implementations

**Pros**:
- Preserves existing memoization pattern
- More "Pythonic" approach for immutable objects

**Cons**:
- Requires changes to multiple object classes
- Must ensure true immutability to avoid hard-to-debug issues
- May be difficult to determine which attributes should contribute to hash

### Approach 2: Modify Memoization Strategy

1. **Object ID Based Memoization**:
   ```python
   def memoize_simple(f):
       cache = {}
       def memoized(*args, **kwargs):
           # Create a key based on object IDs instead of the objects themselves
           key = tuple(id(arg) for arg in args)
           if kwargs:
               key += tuple((k, id(v)) for k, v in sorted(kwargs.items()))
           
           if key not in cache:
               cache[key] = f(*args, **kwargs)
           return cache[key]
       return memoized
   ```

2. **String Representation Memoization**:
   ```python
   def memoize_simple(f):
       cache = {}
       def memoized(*args, **kwargs):
           # Create a key based on string representations
           key = tuple(str(arg) for arg in args)
           if kwargs:
               key += tuple((k, str(v)) for k, v in sorted(kwargs.items()))
           
           if key not in cache:
               cache[key] = f(*args, **kwargs)
           return cache[key]
       return memoized
   ```

**Pros**:
- No need to modify the object classes
- Works with any object regardless of hashability

**Cons**:
- Object ID memoization only works within a single execution (IDs can change between runs)
- String representation approach could be slower
- May lead to cache misses if string representation isn't unique

### Approach 3: Custom Cache Keys

1. **Custom Key Generation**:
   ```python
   def memoize_simple(f):
       cache = {}
       def memoized(*args, **kwargs):
           # Try using the objects directly if hashable
           try:
               if kwargs:
                   kwargs_items = tuple(sorted(kwargs.items()))
                   key = (args, kwargs_items)
               else:
                   key = args if args else ()
               
               # Test if key is hashable
               hash(key)
           except TypeError:
               # Fallback to string representation for unhashable objects
               key = tuple(str(arg) for arg in args)
               if kwargs:
                   key += tuple((k, str(v)) for k, v in sorted(kwargs.items()))
           
           if key not in cache:
               cache[key] = f(*args, **kwargs)
           return cache[key]
       return memoized
   ```

2. **Type-Specific Hash Functions**:
   - Register custom hash functions for known unhashable types
   - Use these functions to generate hashable keys

**Pros**:
- More robust than the other approaches
- Graceful fallback for unhashable types
- Preserves efficient hashing when possible

**Cons**:
- More complex implementation
- May still have edge cases with certain types

### Approach 4: Alternative Caching Libraries

1. **Use `functools.lru_cache` with Custom Keys**:
   ```python
   from functools import lru_cache
   
   def hashable_key(*args, **kwargs):
       """Convert potentially unhashable arguments to a hashable key."""
       # Convert args to a hashable representation
       hashable_args = tuple(str(arg) for arg in args)
       # Convert kwargs to a hashable representation
       hashable_kwargs = tuple(sorted((k, str(v)) for k, v in kwargs.items()))
       return hashable_args + hashable_kwargs
   
   def memoize(func):
       cached_func = lru_cache(maxsize=None)(
           lambda key: func(*key[0], **dict(key[1]))
       )
       def wrapper(*args, **kwargs):
           args_key = tuple(args)
           kwargs_key = tuple(sorted(kwargs.items()))
           return cached_func((args_key, kwargs_key))
       return wrapper
   ```

2. **Use External Caching Libraries**:
   - `cachetools` library offers flexible caching decorators
   - `joblib.Memory` for persistent caching

**Pros**:
- Leverages battle-tested caching implementations
- May offer additional features (size limits, TTL, etc.)

**Cons**:
- Adds external dependencies
- May require significant refactoring

## Recommended Path Forward

Given the analysis, here's the recommended approach:

1. **Short Term (Minimal Change)**: 
   - Implement Approach 3 (Custom Cache Keys) to handle both hashable and unhashable types
   - This minimizes changes to object classes while resolving the immediate issue

2. **Medium Term**:
   - Identify frequently memoized unhashable classes
   - Implement `__hash__` and `__eq__` for these classes using immutable attributes
   - Gradually convert key classes to be properly hashable

3. **Long Term**:
   - Consider moving to `functools.lru_cache` or another modern caching solution
   - Make all relevant classes properly hashable following Python best practices
   - Add proper cache size limits to prevent memory issues

## Implementation Plan

1. **Update Memoization Decorator**:
   - Modify `memoize_simple_imp.py` to handle unhashable types using the hybrid approach
   
2. **Test with Known Issue Cases**:
   - Try running `syntax_anyof.py` tests with the new implementation
   - Document any remaining issues
   
3. **Document Design Decision**:
   - Update code comments to explain the hybrid memoization approach
   - Add notes to Python 3 migration documentation about this issue

4. **Consider Class Refactoring**:
   - Create a plan for gradually making key classes hashable
   - Consider introducing a base class with consistent hash implementation

This approach balances immediate fixes with long-term code health, allowing tests to pass while setting the stage for better practices in the future.