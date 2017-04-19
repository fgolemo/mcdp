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
    u = codecs.open(filename, encoding='utf-8').read()
    s = u.encode('utf-8')
    return s

