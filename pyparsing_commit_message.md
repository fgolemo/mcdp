Add pyparsing 3.x compatibility layer for Python 3 migration

Implemented a new compatibility layer between the bundled pyparsing 2.x and
modern pyparsing 3.x to address Python 3 compatibility issues.

Key changes:
- Updated requirements.txt to specify pyparsing 3.x
- Created src/mcdp_lang/pyparsing_compat.py compatibility layer
- Updated imports in syntax.py, parse_actions.py, and related files
- Added detailed documentation for the migration approach

The compatibility layer handles:
- String/bytes conversion to fix Python 3 type issues
- camelCase vs snake_case method name differences
- API changes between pyparsing versions
- Backwards compatibility for parse result handling

This is part of the ongoing Python 3 migration effort and fixes the major
issues with pyparsing_bundled.py that were preventing testing.

See pyparsing_migration_status.md for detailed implementation notes.