# Pyparsing Migration Status

## Changes Implemented

1. Updated requirements.txt to specify pyparsing 3.x:
   ```
   pyparsing>=3.0.0
   ```

2. Created a compatibility layer in `src/mcdp_lang/pyparsing_compat.py` that:
   - Imports from installed pyparsing 3.x when available
   - Falls back to bundled version if needed
   - Handles API differences between versions
   - Provides compatibility functions for common parsing operations
   - Adds backwards-compatible method names to ParseResults in pyparsing 3.x

3. Updated imports in key files to use the new compatibility layer:
   - `src/mcdp_lang/syntax.py`
   - `src/mcdp_lang/parse_actions.py`
   - `src/mcdp_lang/syntax_utils.py`
   - `src/mcdp_lang/syntax_codespec.py`

4. Added comprehensive documentation in `src/mcdp_lang/README_PYPARSING_MIGRATION.md` about:
   - Migration strategy
   - Usage guidelines
   - Method naming conventions
   - String/bytes handling
   - Future steps and known issues

## Benefits

1. **Better Python 3 Compatibility**: Addresses the string vs bytes issues, collections.abc usage, and other Python 3.12 compatibility issues.

2. **Simplified Maintenance**: Moving to a standard, actively maintained package will reduce maintenance burden.

3. **Gradual Migration Path**: The compatibility layer allows for a phased migration rather than a high-risk complete rewrite.

4. **Improved Code Quality**: Modern pyparsing has better error messages, type annotations, and other improvements.

## Next Steps

1. **Testing**: Comprehensive testing of the parsing functionality with the compatibility layer.

2. **Complete Migration**: Identify and update any remaining direct uses of pyparsing_bundled.

3. **Optimization**: Once all functionality is working, optimize the compatibility layer for performance.

4. **Removal of Bundled Version**: Eventually remove pyparsing_bundled.py once compatibility is assured.

## Implementation Notes

The compatibility layer is designed to be as transparent as possible to the rest of the codebase. It handles:

- API differences (camelCase vs snake_case method names)
- String/bytes conversion automatically
- Collection type changes from Python 2 to Python 3
- Exception handling differences

This approach should make the migration much smoother while minimizing risks.

## Related Changes

This builds on the earlier work to fix Python 3 compatibility issues in:
- Exception re-raising syntax
- collections.abc module imports
- Python 3 compatibility helpers in py_compatibility.py