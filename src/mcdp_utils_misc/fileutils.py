# -*- coding: utf-8 -*-
import codecs
from contextlib import contextmanager
import shutil
from tempfile import mkdtemp, NamedTemporaryFile


def get_mcdp_tmp_dir():
    """ Returns *the* temp dir for this process """
    from tempfile import gettempdir
    import os
    d0 = gettempdir()
    d = os.path.join(d0, 'mcdp_tmp_dir')
    if not os.path.exists(d):
        try:
            os.makedirs(d)
        except OSError:
            pass
    return d

def create_tmpdir(prefix='tmpdir'):
    mcdp_tmp_dir = get_mcdp_tmp_dir()
    d = mkdtemp(dir=mcdp_tmp_dir, prefix=prefix)
    return d

@contextmanager
def tmpdir(prefix='tmpdir', erase=True):
    ''' Yields a temporary dir that shall be deleted later. '''
    d = create_tmpdir(prefix)
    try:
        yield d
    finally:
        if erase:
            shutil.rmtree(d)

@contextmanager
def tmpfile(suffix):
    ''' Yields the name of a temporary file '''
    temp_file = NamedTemporaryFile(suffix=suffix)
    yield temp_file.name
    temp_file.close()
    

def read_file_encoded_as_utf8(filename):
    """
    Reads a file and ensures its content is in UTF-8 bytes.
    
    In Python 2: returns utf-8 encoded bytes from unicode
    In Python 3: returns utf-8 encoded bytes from str
    """
    import sys
    
    with codecs.open(filename, encoding='utf-8') as f:
        content = f.read()
        
    # In Python 3, str is already Unicode, in Python 2 it's read as unicode
    if sys.version_info[0] >= 3:
        # Convert Unicode string to UTF-8 encoded bytes
        return content.encode('utf-8')
    else:
        # In Python 2, content is already unicode, encode to utf-8
        return content.encode('utf-8')

