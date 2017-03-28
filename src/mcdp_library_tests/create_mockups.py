# -*- coding: utf-8 -*-
import os
import tempfile
from mcdp_utils_misc.fileutils import get_mcdp_tmp_dir
from mcdp_utils_misc.locate_files_imp import locate_files
from contracts.utils import check_isinstance

__all__ = ['create_hierarchy']

def create_hierarchy(files0):
    """ 
        Creates a temporary directory with the given files 
    
        files = {
            'lib1.mcdplib/poset1': <contents>
        }
    
    """
    
    mcdp_tmp_dir = get_mcdp_tmp_dir()
    prefix = 'mcdp_library_tests_create_hierarchy'
    d = tempfile.mkdtemp(dir=mcdp_tmp_dir, prefix=prefix)
    write_hierarchy(d, files0)
    return d

def write_hierarchy(where, files0):
    flattened = mockup_flatten(files0)
    for filename, contents in flattened.items():
        check_isinstance(contents, str)
        fn = os.path.join(where, filename)
        dn = os.path.dirname(fn)
        if not os.path.exists(dn):
            os.makedirs(dn)
        with open(fn, 'w') as f:
            f.write(contents)
            
def read_hierarchy(where):
    # read all files
    res = {}
    for filename in locate_files(where,'*'):
        r = os.path.relpath(filename, where)
        res[r] = open(filename).read()
    return unflatten(res)

def mockup_flatten(d): 
    '''
        from
            a:
                b:
                    x
        to 
            'a/b': x
    '''
    res = {}
    for k, v in d.items():
        if isinstance(v, dict):
            x = mockup_add_prefix(k, mockup_flatten(v))
            res.update(x)
        else:
            res[k] = v
    return res

from collections import defaultdict

def unflatten(x):
    def empty():
        return defaultdict(empty)
    res = empty()
    for fn, data in x.items():
        components = fn.split('/')
        assert len(components) >= 1
        w = res
        while len(components) > 1:
            w = w[components.pop(0)]
        last = components[0]
        w[last] = data
        
    # re-convert to dicts
    def conv(dd):
        if isinstance(dd, defaultdict):
            return dict((k, conv(d)) for k,d in dd.items())
        else:
            return dd
        
    return conv(res)
    
def mockup_add_prefix(prefix, d):
    res = {}
    for k, v in d.items():
        res['%s/%s' % (prefix, k)] = v
    return res

