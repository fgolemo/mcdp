# -*- coding: utf-8 -*-
import os
import tempfile
from mcdp.utils.fileutils import get_mcdp_tmp_dir

__all__ = ['create_hierarchy']

def create_hierarchy(files):
    """ 
        Creates a temporary directory with the given files 
    
        files = {
            'lib1.mcdplib/poset1': <contents>
        }
    
    """
    
    mcdp_tmp_dir = get_mcdp_tmp_dir()
    prefix = 'mcdp_library_tests_create_hierarchy()'
    d = tempfile.mkdtemp(dir=mcdp_tmp_dir, prefix=prefix)
    
    for filename, contents in files.items():
        fn = os.path.join(d, filename)
        dn = os.path.dirname(fn)
        if not os.path.exists(dn):
            os.makedirs(dn)
        with open(fn, 'w') as f:
            f.write(contents)
    return d

