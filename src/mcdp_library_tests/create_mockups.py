# -*- coding: utf-8 -*-
import os
import tempfile


def create_hierarchy(files):
    """ 
        Creates a temporary directory with the given files 
    
        files = {
            'lib1.mcdplib/poset1': <contents>
        }
    
    """
    d = tempfile.mkdtemp(prefix='mcdplibrary_cache')
    for filename, contents in files.items():
        fn = os.path.join(d, filename)
        dn = os.path.dirname(fn)
        if not os.path.exists(dn):
            os.makedirs(dn)
        with open(fn, 'w') as f:
            f.write(contents)
    return d

