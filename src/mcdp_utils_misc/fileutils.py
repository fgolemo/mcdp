# -*- coding: utf-8 -*-
import codecs
from contextlib import contextmanager
import shutil
from tempfile import mkdtemp, NamedTemporaryFile


def get_mcdp_tmp_dir():
    """ Returns *the* temp dir for this project.
	Note that we need to customize with username, otherwise
	there will be permission problems.  """
    from tempfile import gettempdir
    import os
    d0 = gettempdir()
    import getpass
    username = getpass.getuser()
    d = os.path.join(d0, 'mcdp_tmp_dir-%s' % username)
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
def tmpdir(prefix='tmpdir', erase=True, keep_on_exception=False):
    ''' Yields a temporary dir that shall be deleted later.
    
        If keep_on_exception is True, does not erase.
        This is helpful for debugging problems.
     '''
    d = create_tmpdir(prefix)
    try:
        yield d
    except:
        if erase and (not keep_on_exception):
            shutil.rmtree(d)
        raise
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
