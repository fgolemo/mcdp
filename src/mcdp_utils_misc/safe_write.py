# -*- coding: utf-8 -*-
from contextlib import contextmanager
import gzip
import os
import random
import sys


__all__ = [
    'safe_write',
    'safe_read',
]


def is_gzip_filename(filename):
    return '.gz' in filename


@contextmanager
def safe_write(filename, mode='wb', compresslevel=5, encoding=None):
    """ 
        Makes atomic writes by writing to a temp filename. 
        Also if the filename ends in ".gz", writes to a compressed stream.
        Yields a file descriptor.
        
        It is thread safe because it renames the file.
        If there is an error, the file will be removed if it exists.
        
        In Python 3, adds encoding support for text modes.
    """
    dirname = os.path.dirname(filename)
    if dirname:
        if not os.path.exists(dirname):
            try:
                os.makedirs(dirname)
            except:
                pass

    n = random.randint(0, 10000)
    if sys.version_info[0] >= 3:
        tmp_filename = f'{filename}.tmp.{os.getpid()}.{n}'
    else:
        tmp_filename = '%s.tmp.%s.%s' % (filename, os.getpid(), n)
        
    try:
        if is_gzip_filename(filename):
            # Handle Python 3's gzip.open with encoding for text modes
            if sys.version_info[0] >= 3 and 't' in mode and encoding:
                fopen = lambda fname, fmode: gzip.open(
                    filename=fname, 
                    mode=fmode,
                    compresslevel=compresslevel, 
                    encoding=encoding
                )
            else:
                fopen = lambda fname, fmode: gzip.open(
                    filename=fname, 
                    mode=fmode,
                    compresslevel=compresslevel
                )
        else:
            # Handle Python 3's open with encoding for text modes
            if sys.version_info[0] >= 3 and 't' in mode and encoding:
                fopen = lambda fname, fmode: open(
                    fname, 
                    fmode, 
                    encoding=encoding
                )
            else:
                fopen = open

        with fopen(tmp_filename, mode) as f:
            yield f
            # No need for explicit close as with statement handles it

        # On Unix, if dst exists and is a file, it will be replaced silently
        # if the user has permission.
        os.rename(tmp_filename, filename)
    except:
        if os.path.exists(tmp_filename):
            os.unlink(tmp_filename)
        if os.path.exists(filename):
            os.unlink(filename)
        raise


@contextmanager
def safe_read(filename, mode='rb', encoding=None):
    """ 
        If the filename ends in ".gz", reads from a compressed stream.
        Yields a file descriptor.
        
        In Python 3, adds encoding support for text modes.
    """
    try:
        if is_gzip_filename(filename):
            # Handle Python 3's gzip.open with encoding for text modes
            if sys.version_info[0] >= 3 and 't' in mode and encoding:
                f = gzip.open(filename, mode, encoding=encoding)
            else:
                f = gzip.open(filename, mode)
                
            try:
                yield f
            finally:
                f.close()
        else:
            # Handle Python 3's open with encoding for text modes
            if sys.version_info[0] >= 3 and 't' in mode and encoding:
                with open(filename, mode, encoding=encoding) as f:
                    yield f
            else:
                with open(filename, mode) as f:
                    yield f
    except:
        # Re-raise the exception with original traceback
        raise