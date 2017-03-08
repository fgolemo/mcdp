# -*- coding: utf-8 -*-
from contextlib import contextmanager
import codecs

        
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

@contextmanager
def tmpfile(suffix):
    """ Yields the name of a temporary file """
    import tempfile
    temp_file = tempfile.NamedTemporaryFile(suffix=suffix)
    yield temp_file.name
    temp_file.close()
    

def read_file_encoded_as_utf8(filename):
    u = codecs.open(filename, encoding='utf-8').read()
    s = u.encode('utf-8')
    return s

