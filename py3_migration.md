# Python 3 Migration Plan for PyMCDP

This document outlines the step-by-step process for migrating the PyMCDP codebase from Python 2 to Python 3, with a focus on incremental testing and recovery strategies.

## Migration Progress

### Completed Tasks ✅

1. **Core Infrastructure**
   - Created compatibility module `py_compatibility.py`
   - Set up core module import structure with fallbacks
   - Added STRICT_DEPENDENCIES flag to control dependency enforcement

2. **Core Module Migration**
   - Migrated `mcdp.branch_info`, `mcdp.logs`, `mcdp.constants`
   - Updated `mcdp.dependencies` with Python 3 compatibility
   - Updated `mcdp.development` with fallbacks

3. **Basic Utilities**
   - Created Python 3 compatible version of `memoize_simple` 
   - Updated string/bytes handling in `string_utils.py`
   - Updated formatting in `duration_hum.py`
   - Fixed imports in `debug_pickler.py` and `string_repr.py`

4. **PyContracts Compatibility**
   - Fixed PyContracts to work with Python 3.8+ by creating a patched fork
   - Added handling for `inspect.ArgSpec` removal in Python 3.8+
   - Updated collection ABC imports to use `collections.abc`
   - Fixed NumPy deprecated types
   - Created PR for upstream project

5. **More Utility Functions**
   - Updated `fileutils.py` for proper string/bytes handling
   - Enhanced `natsort.py` with improved natural sorting for Python 3
   - Updated `safe_pickling.py` with Python 3 pickle protocol handling
   - Improved `safe_write.py` with encoding support for text modes
   - Updated `my_yaml.py` to handle both old and new ruamel.yaml API 
   - Added comprehensive Python 3 compatibility tests

For detailed progress and implementation notes, see [py3_migrate_details.md](py3_migrate_details.md).

## Table of Contents

1. [Preparation](#1-preparation)
2. [Core Module Migration](#2-core-module-migration)
3. [Testing Strategy](#3-testing-strategy)
4. [Recovery Strategies](#4-recovery-strategies)
5. [Migration Steps](#5-migration-steps)
6. [Post-Migration Verification](#6-post-migration-verification)

## 1. Preparation

### 1.1 Setup Branching Strategy

```bash
# Create a new branch for the Python 3 migration (DONE)
# git checkout -b py3_update # DONE

# Create savepoints for key stages (or use Git's stash functionality)
# After each major component is converted:
git commit -m "[py3] Migrated <component_name>"
```

### 1.2 Create Safe Test Environment

```bash
# Create a Python virtual environment
python -m venv py3_env
source py3_env/bin/activate

# Install development dependencies
pip install -e .
pip install -r requirements-dev.txt

# Save package dependency state at beginning
pip freeze > requirements-pre-migration.txt
```

### 1.3 Install Migration Tools

```bash
# Install tools to help with the migration
pip install modernize 2to3 six future

# For automated fixes
pip install flynt  # Converts string formatting to f-strings
```

## 2. Core Module Migration

Identify the minimum core modules needed to import the package:

1. `mcdp.__init__` and direct dependencies
2. Basic utility modules with no complex dependencies
3. Posets (mathematical foundation)
4. Core language components

## 3. Testing Strategy

### 3.1 Create Simple Import Tests

For each module converted, create a simple test script that imports and performs basic operations:

```python
# test_imports.py
def test_import_module(module_name):
    """Test importing a specific module."""
    try:
        module = __import__(module_name, fromlist=['*'])
        print(f"✅ Successfully imported {module_name}")
        return module
    except Exception as e:
        print(f"❌ Failed to import {module_name}: {e}")
        raise
```

### 3.2 Create Feature Tests

For core functionality, create tests that verify behavior:

```python
# test_core_features.py
def test_poset_operations():
    """Test basic poset operations."""
    try:
        from mcdp_posets import Nat
        n = Nat()
        assert n.join(1, 2) == 2
        print("✅ Poset operations working correctly")
    except Exception as e:
        print(f"❌ Poset operations failed: {e}")
        raise
```

### 3.3 Compatibility Layer

Create a compatibility module to handle differences between Python 2 and 3:

```python
# src/mcdp/py_compatibility.py
import sys

PY3 = sys.version_info[0] == 3

if PY3:
    from inspect import getfullargspec as get_arg_spec
    string_types = (str,)
    def raise_with_traceback(exc, tb):
        raise exc.with_traceback(tb)
else:
    from inspect import getargspec as get_arg_spec
    string_types = (basestring,)
    def raise_with_traceback(exc, tb):
        raise exc, None, tb
```

## 4. Recovery Strategies

### 4.1 Git-Based Recovery

```bash
# If a migration step fails, revert to the last known good state
git reset --hard LAST_GOOD_COMMIT
git clean -fd  # Remove untracked files

# Or use stash to save/restore changes
git stash
# Try different approach
git stash pop  # When ready to go back to previous work
```

### 4.2 Module Isolation

During migration, temporarily modify `__init__.py` files to import fewer modules:

```python
# Original src/mcdp/__init__.py
from .logs import logger
from .branch_info import *
from .constants import *
from .dependencies import *
from .development import *

# Modified for testing
from .logs import logger
from .branch_info import __version__
# Other imports temporarily commented out
# from .constants import *
# from .dependencies import *
# from .development import *
```

### 4.3 Fallback Implementations

For complex modules, create simplified versions that allow testing to proceed:

```python
# src/mcdp/mock_dependencies.py
# Mock implementations of critical functions
def mock_function(*args, **kwargs):
    """Simplified implementation for testing."""
    return True
```

## 5. Migration Steps

### 5.1 Fix Standard Library Changes

1. **File Operations**
   - Update imports: `from io import open`
   - Update file opening: `with open(filename, 'r', encoding='utf-8') as f:`

2. **Print Statements**
   - Convert `print x` to `print(x)`
   - Handle complex cases: `print >>sys.stderr, "Error"` to `print("Error", file=sys.stderr)`

3. **Exception Handling**
   - Replace `except Exception, e:` with `except Exception as e:`
   - Convert `raise ValueError, "message"` to `raise ValueError("message")`
   - Replace `raise e, None, tb` with `raise e.with_traceback(tb)`

4. **Imports**
   - Update renamed modules: `import ConfigParser` to `import configparser`
   - Update removed modules: replace `import urllib2` with `import urllib.request, urllib.error`

### 5.2 Fix Data Types and Iterators

1. **String Handling**
   - Replace `u"unicode string"` with `"string"` (all strings are Unicode in Python 3)
   - Use `b"bytes"` for byte strings
   - Fix string operations: `.encode()`, `.decode()`

2. **Iterator Changes**
   - Replace `d.iteritems()` with `d.items()`
   - Replace `xrange()` with `range()`
   - Update `map()`, `filter()`, `zip()` to handle return of iterators vs. lists

3. **Division**
   - Ensure integer division is handled correctly: replace `a / b` with `a // b` where integer division is intended

### 5.3 Fix Library-Specific Issues

1. **NumPy**
   - Update numpy array indexing and handling
   - Fix numpy ufunc usage

2. **Inspect Module**
   - Replace `inspect.getargspec()` with `inspect.getfullargspec()`

3. **Custom Libraries**
   - Review and update custom dependencies for Python 3 compatibility

### 5.4 Migration Order

1. **Utilities First**
   - Start with self-contained utility modules
   - Migrate basic type handling and string operations

2. **Core Mathematical Components**
   - Migrate posets and mathematical foundations
   - Test mathematical operations thoroughly

3. **Language Components**
   - Migrate syntax and language parsing components
   - Fix string handling and operations

4. **Web and UI Components**
   - Migrate web interfaces last as they depend on other components

## 6. Post-Migration Verification

### 6.1 Comprehensive Testing

1. **Unit Tests**
   - Run the newly created pytest suite: `pytest tests/`
   - Incrementally enable original tests as modules are converted

2. **Integration Testing**
   - Test core workflows: model definition, solving, visualization
   - Validate mathematical correctness of solutions

3. **Performance Testing**
   - Compare performance between Python 2 and Python 3 versions
   - Identify and fix performance regressions

### 6.2 Code Quality Checks

1. **Style Consistency**
   - Run Black: `black src/ tests/`
   - Ensure consistent Python 3 idioms

2. **Linting**
   - Run Flake8: `flake8 src/ tests/`
   - Fix remaining issues and warnings

3. **Type Checking**
   - Run mypy: `mypy src/`
   - Add type annotations where beneficial

### 6.3 Documentation Updates

1. **Update Installation Instructions**
   - Document Python 3 requirements
   - Update dependency information

2. **Update API Documentation**
   - Note any API changes due to Python 3 migration
   - Document any new features or improvements

## Appendix: Common Python 2 to 3 Migration Issues

### A.1 Common Syntax Changes

| Python 2 | Python 3 | Notes |
|----------|----------|-------|
| `print x` | `print(x)` | Print is a function in Python 3 |
| `except E, v:` | `except E as v:` | Exception binding syntax |
| `raise E, v` | `raise E(v)` | Exception raising syntax |
| `raise E, v, tb` | `raise E(v).with_traceback(tb)` | Re-raising with traceback |
| `u'unicode'` | `'unicode'` | All strings are Unicode in Python 3 |
| `d.iteritems()` | `d.items()` | Dict methods return views not lists |
| `xrange(10)` | `range(10)` | Range is now lazy in Python 3 |
| `map(f, l)` | `list(map(f, l))` | map returns iterator, not list |
| `a / b` | `a // b` | Integer division requires // |

### A.2 Updated Imports

| Python 2 | Python 3 | Notes |
|----------|----------|-------|
| `import __builtin__` | `import builtins` | Built-in functions module renamed |
| `import ConfigParser` | `import configparser` | Lowercase module names |
| `import urlparse` | `from urllib.parse import ...` | URL handling reorganized |
| `import urllib2` | `import urllib.request, urllib.error` | URL handling reorganized |
| `import Queue` | `import queue` | Lowercase module names |
| `import SocketServer` | `import socketserver` | Lowercase module names |

### A.3 Key Library Changes

| Python 2 | Python 3 | Notes |
|----------|----------|-------|
| `inspect.getargspec()` | `inspect.getfullargspec()` | Function inspection updated |
| `dict.has_key()` | `key in dict` | Method removed in favor of `in` operator |
| `basestring` | `str` | Unicode and string unified |
| `cmp(a, b)` | `(a > b) - (a < b)` | cmp function removed |
| `file` | `open` | file type removed |
| `long` | `int` | int and long unified |
| `reduce()` | `functools.reduce()` | Moved to functools |