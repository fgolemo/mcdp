# zuper-commons ZLogger Issue

## Problem Description

During the Python 3 migration, we encountered the following error:

```
Dependency issue: cannot import name 'ZLogger' from 'zuper_commons.logs' (/Users/fugacity/.pyenv/versions/3.12.5/lib/python3.12/site-packages/zuper_commons/logs/__init__.py)
```

This error occurs because:

1. The `quickapp` package imports `ZLogger` from `zuper_commons.logs`
2. We installed `zuper-commons` package (v3.0.4), but it doesn't seem to provide the expected `ZLogger` class
3. This suggests a version mismatch or API change between the version of `zuper-commons` that `quickapp` was developed against and the current version available

## Investigation

Looking at the quickapp source code, we can see the import in question:

```python
# From /Users/fugacity/20sq/mcdp/vendor/quickapp/src/quickapp/__init__.py
from zuper_commons.logs import ZLogger
```

However, when examining the installed `zuper_commons` package:

```python
# Current zuper_commons.logs doesn't export ZLogger
```

## Solutions

Since this issue only affects `quickapp` and we've set `STRICT_DEPENDENCIES=False` to allow the migration to proceed, we have several options:

### Option 1: Create a Patched Version of zuper-commons

1. Fork the `zuper-commons` repository
2. Add the missing `ZLogger` class, using a minimal implementation that satisfies quickapp's needs
3. Install the forked version locally:
   ```bash
   cd /path/to/forked/zuper-commons
   pip install -e .
   ```

### Option 2: Patch quickapp to Avoid Using ZLogger

1. Modify our local fork of quickapp to use a standard Python logger instead:
   ```python
   # Replace:
   from zuper_commons.logs import ZLogger
   
   # With:
   import logging
   
   # Define a minimal ZLogger compatible class
   class ZLogger:
       def __init__(self, name):
           self.logger = logging.getLogger(name)
           
       def info(self, *args, **kwargs):
           return self.logger.info(*args, **kwargs)
           
       def debug(self, *args, **kwargs):
           return self.logger.debug(*args, **kwargs)
           
       def warning(self, *args, **kwargs):
           return self.logger.warning(*args, **kwargs)
           
       def error(self, *args, **kwargs):
           return self.logger.error(*args, **kwargs)
   ```

### Option 3: Find the Correct Version of zuper-commons

1. Check the quickapp requirements for the specific version it expects:
   ```bash
   pip show quickapp | grep Requires
   ```
   
2. Try to find and install that specific version:
   ```bash
   pip install zuper-commons==X.Y.Z
   ```

### Option 4: Maintain our Current Approach

1. Keep `STRICT_DEPENDENCIES=False`
2. Accept the warning as non-critical
3. Only use functionality that doesn't depend on the missing ZLogger

## Recommended Approach

For quick progress on the Python 3 migration, I recommend **Option 4** (maintain current approach) for now. 

If we need full quickapp functionality later, we should implement **Option 2** (patch quickapp) as it:
1. Is self-contained (doesn't require maintaining another fork)
2. Uses standard Python logging
3. Minimizes changes to the core codebase

## Implementation Steps for Option 2 (if needed)

1. Create a file `zlogger_patch.py` in the quickapp src directory
2. Implement the minimal ZLogger class
3. Update quickapp's `__init__.py` to use our patched version:
   ```python
   try:
       from zuper_commons.logs import ZLogger
   except ImportError:
       from .zlogger_patch import ZLogger
   ```
4. Update our fork's setup.py to remove the zuper-commons dependency if it's listed