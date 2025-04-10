# Python 3 Compatibility Fixes for MCDP

## 1. Exception Handling Fixes

Fixed Python 2 style exception re-raising by updating:

- Fixed `raise e, None, traceback` to Python 3's `raise e.with_traceback(tb)` in multiple files:
  - `src/mcdp_library/library.py`
  - `src/mcdp_lang/parse_interface.py`
  - `src/mcdp_lang/parse_actions.py`
  - `src/mocdp/comp/template_for_nameddp.py`

## 2. Collections Module Compatibility

Updated imports to support Python 3.12's removal of ABC classes from collections module:

- Created compatibility imports for:
  - `Sequence`
  - `MutableMapping`
  - `Mapping`
  - `Set`
  - `MutableSet`
  - `Iterable`

- Added the compatibility layer to multiple files:
  - `vendor/py_contracts/src/contracts/library/seq.py`
  - `vendor/py_contracts/src/contracts/library/map.py`
  - `vendor/py_contracts/src/contracts/library/sets.py`
  - `src/mcdp_posets/poset_product.py`
  - `src/mcdp_lang/pyparsing_bundled.py`

## 3. String/Bytes Handling

Fixed string vs. bytes handling for Python 3:

- Updated the `decode_identifier` function in `src/mcdp_lang/syntax.py` to handle both Python 2 and 3
- Created helper functions in `pyparsing_compat.py` to handle string encoding/decoding
- Fixed `parse_wrap` function in `src/mcdp_lang/parse_actions.py` to handle Python 3 strings

## 4. Print Statement Conversion

- Automatically fixed over 500 instances of Python 2 print statements to use Python 3's print function syntax
- Created `fix_print_statements.py` script to automate this process

## 5. Pyparsing Compatibility Layer

Created a comprehensive compatibility layer to handle differences between pyparsing 2.x and 3.x:

- Created `src/mcdp_lang/pyparsing_compat.py` which:
  - Tries to import from modern pyparsing 3.x first, then falls back to bundled version
  - Handles API differences between versions (camelCase vs snake_case)
  - Provides helper functions for common operations
  - Adds string/bytes conversion utilities
  - Fixed issues with the `oneOf` function to handle keyword parameters correctly

The library now attempts to use the installed pyparsing 3.x when available, falling back to the bundled version only when necessary.

## Known Issues

- The test case `syntax_anyof.py` still doesn't run due to a memoization issue with unhashable types. This would require more significant changes to the codebase.

## Next Steps

1. Complete test fixes
2. Address remaining unhashable type issues in memoization
3. Fix invalid escape sequences in regex patterns
4. Continue Python 3 migration for other modules
5. Eventually phase out the bundled pyparsing entirely