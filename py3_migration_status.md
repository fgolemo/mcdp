# Python 3 Migration Status Report

This document captures the current state of the Python 3 migration effort for PyMCDP as of April 9, 2025.

## Overall Status

The Python 3 migration is progressing well, with several major components successfully updated:

- Core infrastructure modules are now Python 3 compatible
- Key dependencies have been patched or replaced
- Basic unit tests are passing
- Import structure has been fixed for Python 3 compatibility

## Latest Progress (April 9, 2025)

### Recent Achievements (Latest)
- Fixed f-string formatting in critical files:
  - `/Users/fugacity/20sq/mcdp/src/mcdp_dp/dp_loop2.py`
  - `/Users/fugacity/20sq/mcdp/src/mcdp_opt/actions.py`
- Created helper scripts for f-string migration:
  - `find_fstring_issues.py`: Identifies common f-string formatting issues
  - `fix_fstring_patterns.py`: Attempts to automatically fix common issues
- Updated documentation with common patterns and fixes
- Initial analysis shows approximately 82 f-string issues in mcdp_lang module

### Previous Progress

### 1. Work on mcdp_lang
- Migrated several key files to Python 3:
  - eval_ndp_imp.py
  - eval_resources_imp.py
  - eval_lfunction_imp.py
  - eval_constant_imp.py
  - eval_space_imp.py
  - parse_actions.py
  - blocks.py
  - find_parsing_el.py
  - helpers.py
  - eval_constant_asserts.py
  - eval_resources_imp_unary.py
  - misc_math.py

### 2. Pyparsing Replacement
- Replaced bundled pyparsing (pyparsing_bundled.py) with:
  - Official pyparsing 3.1.0 installed as a dependency
  - Renamed old bundle to pyparsing_bundled.py.bak
  - Using pyparsing_compat.py as compatibility layer between versions

### 3. F-string Formatting Fixes
- Fixed numerous f-string formatting issues throughout the codebase
- Common patterns identified and fixed:
  ```python
  # Incorrect: Missing closing parentheses
  f"some {var} text"(other_var)
  
  # Incorrect: Extra closing braces
  f"some {var} text"
  
  # Incorrect: String interpolation in f-strings 
  f"some %s text" % var
  
  # Incorrect: Calling str() on variable in f-string
  f"some {str}(var) text"
  
  # Incorrect: Attribute access after object in f-string
  f"some {obj}.attribute text"
  
  # Incorrect: Mixed f-string with .format()
  f"some {var}".format(other_var)
  ```

### 4. Iterator Optimization Strategy Established
- Refined approach to avoid unnecessary `list()` calls around iterators
- Only using `list()` when absolutely necessary:
  - Direct indexing of iterator results
  - Multiple passes through same data
  - Dictionary modification during iteration

## Vendor Submodules Status

### PyContracts (vendor/py_contracts)

- **Status**: ✅ Successfully migrated
- **Branch**: fix-python38-compatibility
- **Latest Commit**: 899f932ce96703c2a4bbbe7aa8f66bec4a5b89c9
- **Key Changes**: 
  - Fixed compatibility with Python 3.8+ by addressing `inspect.ArgSpec` deprecation
  - Updated collection imports to use `collections.abc`
  - Fixed NumPy deprecated types
  - Fixed escape sequences in regexes
- **Notes**: Now properly set up as a git submodule

### Compmake (vendor/compmake)

- **Status**: ✅ Successfully migrated
- **Branch**: py3_migration
- **Latest Commit**: 4064a44117172ad534328b244e5476dd02e66e41
- **Key Changes**:
  - Fixed deprecated `imp` module with `importlib`
  - Fixed `inspect.getargspec()` with `inspect.getfullargspec()`
  - Fixed invalid escape sequences in regexes
- **Notes**: All changes maintain backward compatibility

### QuickApp (vendor/quickapp)

- **Status**: ✅ Patched for Python 3
- **Branch**: py3_migration
- **Latest Commit**: 929e6ebb135c742f3054dfc9d7d0233823e98813
- **Key Changes**:
  - Added `zuper_commons_patch` module to handle missing functionality
  - Implemented `ZLogger` replacement for zuper_commons.logs.ZLogger
  - Implemented `natsorted` replacement for zuper_commons.text.natsorted
  - Fixed import patterns with try/except for graceful fallbacks
- **Notes**: See `quickapp_zuper_commons_patch.md` for details

### ConfTools (vendor/conf_tools)

- **Status**: ✅ Patched for Python 3
- **Latest Commit**: 46b65ebc31700fcb51791645d017e6842f5e6706
- **Key Changes**:
  - Removed upper version bound for PyContracts
  - Updated version to 1.9.10
  - Added as new git submodule
- **Notes**: Still has some SyntaxWarnings for invalid escape sequences in regexes

## Resolved Issues

1. **PyContracts Compatibility**: Fixed by forking and updating PyContracts to work with Python 3.8+

2. **Deprecated imp Module**: Fixed in compmake with conditional imports based on Python version

3. **inspect.getargspec Removal**: Fixed with conditional code using appropriate function by Python version

4. **ZLogger Missing**: Implemented custom replacement in quickapp/zuper_commons_patch

5. **PyContracts Version Conflict**: Resolved by updating conf_tools to accept PyContracts 2.0.1

6. **Pyparsing Compatibility**: Used pyparsing_compat.py to bridge between pyparsing 2.x and 3.x

## Known Issues

1. **ZLogger Warning**: The warning about missing `ZLogger` from zuper_commons.logs is expected and handled

2. **natsorted Import**: The warning about missing `natsorted` from zuper_commons.text is expected and handled

3. **SyntaxWarnings in conf_tools**: Escape sequences in regexes need to be updated to raw strings

4. **STRICT_DEPENDENCIES=False**: Currently needed to bypass some dependency issues

5. **F-string Formatting Errors**: Numerous syntax errors throughout the codebase due to improper f-string formatting
   - Fixed several files (dp_loop2.py, actions.py) but many more need fixing
   - Common patterns include:
     - Attribute access after object reference in f-strings: `{obj}.attr` → `{obj.attr}`
     - Mixed f-strings with %-style formatting: `f"text {var} %s" % value` → `f"text {var} {value}"`
     - Improperly chained string formatting: `f"text {var}".format(other)` → `f"text {var} {other}"` 
     - Need to develop a script to automate fixing these patterns

## Tests Status

| Test                     | Status | Notes                               |
|--------------------------|--------|-------------------------------------|
| test_imports.py          | ✅ Pass | All 7 core modules import successfully |
| test_utils_py3.py        | ✅ Pass | All 5 tests pass                    |
| test_string_utils.py     | ✅ Pass | All 9 tests pass                    |
| test_memoize_simple.py   | ✅ Pass | All 5 tests pass after fix          |
| pytest (excluding imports)| ✅ Pass | 47 tests pass, 3 skipped           |

## Next Steps

1. **Address f-string formatting issues systematically**:
   - Create a script to identify and fix common f-string patterns (highest priority)
   - Implement fixes for the following patterns:
     ```python
     # Find and fix attribute access after object in f-string
     pattern = r'f[\'"].*?\{(\w+)\}\.(\w+).*?[\'"]'
     replacement = r'f"\1.\2"'
     
     # Find and fix mixed f-string with %-style formatting
     pattern = r'f[\'"].*?\{.*?\}.*?%.*?[\'"].*?%'
     # (Custom replacement needed for each case)
     
     # Find and fix chained formatting
     pattern = r'f[\'"].*?[\'"]\.format\('
     # (Custom replacement needed for each case)
     ```

2. **Continue pyparsing compatibility validation**:
   - Verify existing parsers work with pyparsing 3.x
   - Fix any compatibility issues that arise

3. **Continue mcdp_lang module migration**:
   - Apply automated f-string fixes to all files
   - Test each fixed module for functionality

4. **Progress on mcdp_dp module migration**:
   - Apply lessons learned from dp_loop2.py fixes
   - Apply automated f-string fixes to all mcdp_dp files

5. **Update test infrastructure for Python 3**:
   - Fix test runners and utilities
   - Ensure tests are using Python 3 compatible assertions and methods

6. **Document fixes for future reference**:
   - Update py3_migration_status.md with all patterns fixed
   - Create a reference guide for common Python 3 migration patterns in this codebase

## Common Migration Patterns

1. **String Handling**:
   ```python
   # Use ensure_str from compatibility layer for string/bytes conversion
   from mcdp.py_compatibility import ensure_str
   string = ensure_str(string)
   ```

2. **Exception Re-raising**:
   ```python
   # Use raise_with_traceback from compatibility layer
   from mcdp.py_compatibility import raise_with_traceback
   raise_with_traceback(exception, tb)
   ```

3. **F-string Formatting**:
   ```python
   # Before
   msg = 'Value is %s' % value
   # After
   msg = f'Value is {value}'
   
   # Before (with repr)
   msg = 'Value is %r' % value
   # After
   msg = f'Value is {value!r}'
   ```

4. **Dictionary Views**:
   ```python
   # When iteration only needed once (preferred)
   for k, v in dictionary.items():
       # process k, v
   
   # When dictionary might be modified during iteration
   for k, v in list(dictionary.items()):
       # process k, v
       # possibly modify dictionary
   ```

5. **Maps and Filters**:
   ```python
   # When direct iteration is enough
   for item in map(func, iterable):
       # process item
   
   # When indexing is needed
   items = list(map(func, iterable))
   item_zero = items[0]
   ```

## Dependencies Configuration

A setup script (`setup_py3_deps.sh`) has been created to install the patched dependencies:

```bash
# Install patched PyContracts
pip install -e vendor/py_contracts

# Install patched compmake
pip install -e vendor/compmake

# Install patched quickapp
pip install -e vendor/quickapp

# Install pyparsing 3.x
pip install pyparsing>=3.1.0
```

## Reference Documentation

1. [py3_migration.md](/py3_migration.md) - Overall migration plan
2. [py3_migrate_details.md](/py3_migrate_details.md) - Detailed migration notes
3. [zuper.md](/zuper.md) - Notes on ZLogger issue
4. [vendor/quickapp/quickapp_zuper_commons_patch.md](/vendor/quickapp/quickapp_zuper_commons_patch.md) - QuickApp patching details
5. [src/mcdp_lang/README_PYPARSING_MIGRATION.md](/src/mcdp_lang/README_PYPARSING_MIGRATION.md) - Pyparsing migration strategy