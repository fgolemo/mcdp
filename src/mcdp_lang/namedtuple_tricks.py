# -*- coding: utf-8 -*-
from collections import namedtuple

from contracts.utils import indent


def isnamedtupleinstance(x):
    t = type(x)
    b = t.__bases__
    if len(b) != 1 or b[0] != tuple: return False
    f = getattr(t, '_fields', None)
    if not isinstance(f, tuple): return False
    return all(type(n) == str for n in f)


def isnamedtuplewhere(x):
    if not isnamedtupleinstance(x):
        return False
    d = x._asdict()
    return 'where' in d

def namedtuplewhere(a, b):
    fields = b.split(" ")
    assert not 'where' in fields
    fields.append('where')
    base = namedtuple(a, fields)
    base.__new__.__defaults__ = (None,)
    F = base
    # make the name available
    g = globals()
    g[a] = F
    return F

def get_copy_with_where(x, where):
    d = x._asdict()
    del d['where']
    d['where'] = where
    T = type(x)
    x1 = T(**d)
    return x1

def remove_where_info(x):
    if not isnamedtupleinstance(x):
        return x
    d = x._asdict()
    for k, v in d.items():
        d[k] = remove_where_info(v)
    del d['where']
    d['where'] = None
    T = type(x)
    x1 = T(**d)
    return x1

def clean_print(x):
    y = remove_where_info(x)
    s = str(y)
    s = s.replace(', where=None', '')
    return s

def recursive_print(x):
    if not isnamedtupleinstance(x):
        return x.__repr__()
    s = type(x).__name__
    s += ':\n'
    for k, v in x._asdict().items():
        if k == 'where': continue
        first = ' %s: ' % k
        prefix = ' '* len(first)
        first += '|'
        prefix += '|'
        r = recursive_print(v).strip()
        s += indent(r, prefix, first=first)
        s += '\n'
    return s
        
    
    
