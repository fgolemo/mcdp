Update mcdp_posets module for Python 3 compatibility

Migrated the complete mcdp_posets module to Python 3 with the following changes:
- Update metaclass syntax for Python 3 compatibility
- Convert string formatting to f-strings throughout
- Add __hash__ methods for classes with __eq__ methods
- Fix iterator handling (e.g., zip() returns iterator in Python 3)
- Replace deprecated time.clock() with time.process_time()
- Add explicit imports for functions no longer built-in (functools.reduce)
- Replace sys.maxint with sys.maxsize
- Fix invalid escape sequences in docstrings
- Update print statements in test files

Testing is blocked by dependencies requiring migration (mcdp_library module).
Created posets_py3_progress.md to track and document all changes.