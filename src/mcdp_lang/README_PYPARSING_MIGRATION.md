# Pyparsing Migration Strategy

This document outlines the strategy for migrating from the bundled pyparsing 2.x (pyparsing_bundled.py) to the modern pyparsing 3.x package for Python 3 compatibility.

## Background

The mcdp codebase includes a bundled version of pyparsing 2.x in `pyparsing_bundled.py`. This bundled version has compatibility issues with Python 3, particularly:

1. String vs bytes handling issues
2. Use of removed collections classes (collections.Sequence, collections.MutableMapping)
3. Incompatible exception re-raising syntax

## Migration Strategy

We've adopted the following approach:

1. Add pyparsing 3.x as an explicit dependency in requirements.txt
2. Create a compatibility layer (`pyparsing_compat.py`) that:
   - Imports from the installed pyparsing 3.x when available
   - Falls back to the bundled version if needed
   - Handles API differences between pyparsing 2.x and 3.x
   - Provides helper functions for common operations with Python 3 compatible signatures

3. Update imports in the codebase to use the compatibility layer
   - Replace imports from `.pyparsing_bundled` with `.pyparsing_compat`
   - Use the provided helper functions for methods that have been renamed

## Usage Guidelines

### Import Changes

Instead of:
```python
from .pyparsing_bundled import Literal, oneOf
```

Use:
```python
from .pyparsing_compat import Literal, oneOf
```

### Method Naming

The compatibility layer provides functions that handle the different method naming conventions:

- `set_name()` - instead of `setName()`
- `set_results_name()` - instead of `setResultsName()`
- `set_parse_action()` - instead of `setParseAction()`
- `parse_string()` - instead of `parseString()`

Example:
```python
# Before:
expr = Literal("foo").setName("foo_literal").setParseAction(some_func)
result = expr.parseString(text)

# After:
from .pyparsing_compat import Literal, set_name, set_parse_action, parse_string

expr = Literal("foo")
expr = set_name(expr, "foo_literal")
expr = set_parse_action(expr, some_func)
result = parse_string(expr, text)

# Alternatively, for simple method calls, direct usage is still supported
# through monkey-patched backward compatibility:
expr = Literal("foo").setName("foo_literal").setParseAction(some_func)
result = expr.parseString(text)
```

### String/Bytes Handling

The compatibility layer automatically handles string/bytes conversion:

```python
# In pyparsing_compat.py:
def oneOf(symbols, caseless=False, asKeyword=False):
    # ... string conversion happens here ...
    symbols = [ensure_str(sym) for sym in symbols]
```

## Future Steps

1. Complete the migration to pyparsing 3.x throughout the codebase
2. Run comprehensive tests to ensure parsing behavior remains consistent
3. Eventually remove the bundled version (`pyparsing_bundled.py`) once compatibility is assured

## Known Issues

1. ParseResults differences - some subtle differences in behavior may exist
2. Performance - the compatibility layer adds some overhead
3. Advanced features - some advanced pyparsing features might need additional compatibility work