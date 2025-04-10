# -*- coding: utf-8 -*-
import sys

from contracts import describe_type
from mcdp import logger

from .debug_pickler import find_pickling_error
from .safe_write import safe_read, safe_write


if sys.version_info[0] >= 3:
    import pickle  # @UnusedImport
else:
    import cPickle as pickle  # @Reimport

__all__ = [
    'safe_pickle_dump',
    'safe_pickle_load',
]


def safe_pickle_dump(value, filename, protocol=pickle.HIGHEST_PROTOCOL,
                     **safe_write_options):
    with safe_write(filename, **safe_write_options) as f:
        try:
            pickle.dump(value, f, protocol)
        except KeyboardInterrupt:
            raise
        except Exception:
            msg = f"Cannot pickle object of class {describe_type(value)}"
            logger.error(msg)
            msg = find_pickling_error(value, protocol)
            logger.error(msg)
            raise


def safe_pickle_load(filename):
    """
    Load a pickle file safely, handling Python 2//3 differences.
    
    In Python 3, pickle.load() requires bytes-like object, not str,
    and needs to handle encoding issues when loading pickles created in Python 2.
    """
    # TODO: add debug check
    with safe_read(filename) as f:
        try:
            return pickle.load(f)
        except UnicodeDecodeError:
            # This may happen when loading Python 2 pickles in Python 3
            if sys.version_info[0] >= 3:
                logger.warning('UnicodeDecodeError when loading pickle, trying with encoding="latin1"')
                # Rewind file and try again with encoding
                f.seek(0)
                return pickle.load(f, encoding='latin1')
            else:
                raise
        # TODO: add pickling debug
