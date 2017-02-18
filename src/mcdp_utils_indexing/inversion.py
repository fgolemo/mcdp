# -*- coding: utf-8 -*-
from contracts.utils import raise_desc

from .get_it_test import is_iterable
from .imp import get_it


def get_letter_proxy(P, start_letter='a'):
    """ Returns a tuple (proxy, dict) """
    def get_unique(P, prefix, d):
        def next_key():
            k = chr(ord(start_letter) + len(d))
            return k
        if is_iterable(P):
            x = []
            for i, sub in enumerate(P):
                x.append(get_unique(sub, prefix + (i,), d))
            return x
        else:
            k = next_key()
            assert not k in d
            d[k] = prefix
            return k
    d = {}
    proxy = get_unique(P, (), d)
    return proxy, d

def transform_pretty_print(P, coords, start_letter='a'):
    proxy, _ = get_letter_proxy(P, start_letter)
    transformed = get_it(proxy, coords, list)
    def pretty(x):
        if is_iterable(x):
            m = [pretty(_) for _ in x]
            return '⟨' + ', '.join(m) + '⟩'
        else:
            return str(x)
    t1 = pretty(proxy)
    t2 = pretty(transformed)
    s = '{} ⟼ {}'.format(t1, t2)
    return s

def transform_right_inverse(P, coords, reduce_list):
    """ Returns coords2 such that coords * coords2 == () """
    # first, add unique identifiers for parts of P
#     
#     print 'P', P
#     print 'coords', coords
    # coords [(1, 1), [(0, 0, 1), (1, 0), (0, 0, 0), (0, 1)]]
    # d  = {'a': (0, 0, 0), 'c': (0, 1), 'b': (0, 0, 1), 'e': (1, 1), 'd': (1, 0)}
    # proxy =  [[['a', 'b'], 'c'], ['d', 'e']]
    proxy, d = get_letter_proxy(P)
#     
#     print 'proxy', proxy
#     print 'd', d
    transformed = get_it(proxy, coords, list)
#     print 'transformed', transformed
    
    def search(P, prefix, res):
        if isinstance(P, list):
            for i, sub in enumerate(P):
                search(sub, prefix + (i,), res)
        else:
            assert P in d
            res[P] = prefix
            
    res = {}
    search(transformed, (), res)
#     print 'res', res
    
    # it is an isomorphism if we have found all the letters
    for k in d:
        if not k in res:
            msg = 'Not an isomorphism.'
            raise_desc(ValueError, msg, proxy=proxy, transformed=transformed)
    
    # now substitute the keys in res in d
    def go(proxy):
        if isinstance(proxy, list):
            return [go(_) for _ in proxy ]
        else:
            assert proxy in res
            return res[proxy]
        
    coords2 = go(proxy)
#     print('coords2: {}'.format(coords2))
    
    # verify that when applied to transformed, we get the proxy 
    proxy2 = get_it(transformed, coords2, list)
#     print('proxy2: {}'.format(proxy2))
    if proxy2 != proxy:
        msg = 'Did not work.'
        raise_desc(AssertionError, msg, proxy=proxy, proxy2=proxy2)
    
    Q = get_it(P, coords, reduce_list)
#     print('I have map:\n %s \n %s' % (transform_pretty_print(P, coords), 
#                                       transform_pretty_print(Q, coords2, 'A')))
    # this should be equal to P
    _P2 = get_it(Q, coords2, reduce_list)
    return Q, coords2
#     composition = compose_indices(P, coords, coords2, list)
#     print('composition: {}'.format(composition))

