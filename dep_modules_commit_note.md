Begin migrating dependent modules for Python 3 compatibility

Started migrating dependent modules needed to properly test mcdp_posets:

1. Fixed exception re-raising in several key modules:
   - mcdp_library/library.py
   - mcdp_lang/parse_interface.py
   - mcdp_lang/parse_actions.py
   - mocdp/comp/template_for_nameddp.py

2. Added compatibility for collections.abc module in Python 3.12:
   - Replaced collections.MutableMapping with collections.abc.MutableMapping
   - Replaced collections.Sequence with collections.abc.Sequence
   - Added fallback imports for Python 3.11 and below

3. Added fallback for nose.tools imports that rely on the removed imp module

Encountered significant compatibility issues with pyparsing_bundled.py that will
require replacing it with a Python 3 compatible version of pyparsing.

Created detailed progress documentation in posets_py3_progress.md.