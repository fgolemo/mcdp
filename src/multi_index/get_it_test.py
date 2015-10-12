from contracts.utils import raise_desc, raise_wrapped
from multi_index import get_it

A = ['a', ['b', 'c']]
   
   
cases = [
  (A, (), ['a', ['b', 'c']]),
  (A, 0, 'a'),
  (A, 1, ['b', 'c']),
  (A, [0, 0], ['a', 'a']),
  (A, [(), ()], [['a', ['b', 'c']], ['a', ['b', 'c']]]),
  (A, [0, (1, 1)], ['a', 'c']),
]     

def test_cases():

    for X, index, result in cases:
        yield check_case, X, index, result

def check_case(X, index, expected):

    res = get_it(X, index, reduce_list=list)
    if res != expected:
        msg = 'Result is different.'
        raise_desc(ValueError, msg, X=X, index=index, expected=expected, res=res)
    

cases = [
  (A, (), ['a', ['b', 'c']]),
  (A, 0, 'a'),
  (A, 1, ['b', 'c']),
  (A, [0, 0], ['a', 'a']),
  (A, [(), ()], [['a', ['b', 'c']], ['a', ['b', 'c']]]),
  (A, [0, (1, 1)], ['a', 'c']),
]

def compose_indices(A, i1, i2):
    i0 = get_id_indices(A)
    i0i1 = get_it(i0, i1, list)
    i0i1i2 = get_it(i0i1, i2, list)
    return i0i1i2

def check_associativity(A, i1, i2):
    G = lambda x, i: get_it(x, i, list)
    Ai1 = G(A, i1)
    r1 = G(Ai1, i2)
    i1i2 = compose_indices(A, i1, i2)
    r2 = G(A, i1i2)

    if r1 != r2:
        msg = 'Result is different.'
        raise_desc(ValueError, msg, A=A, i1=i1, i2=i2, i1i2=G(i1, i2),
                   r1=r1, r2=r2)

def test_compositions():
    ccases = [
        (A, [1, 0], 0),
        (A, [(), ()], (1, 0)),
    ]

    for X, i1, i2 in ccases:
        yield check_associativity, X, i1, i2

def get_id_indices(x, prefix=None):
    if prefix is None:
        prefix = ()

    def is_iterable(x):
        if isinstance(x, str):
            return False

        try:
            iter(x)
        except TypeError:
            return False
        else:
            return True

    if is_iterable(x):
        return [ get_id_indices(m, prefix=prefix + (i,))
                for i, m in enumerate(x)]

    if len(prefix) == 1:
        return prefix[0]

    return prefix
    
def test_get_id_indices():
    from mocdp.posets.poset_product import PosetProduct
    from mocdp.posets.rcomp import Rcomp

    icases = [
        ('a', ()),
        (1, ()),
        (['a'], [0]),
        (['a', 'b'], [0, 1]),
        ([ ['a', 'd'], 'b'], [ [(0, 0), (0, 1)], 1]),

        (PosetProduct((PosetProduct((Rcomp(), Rcomp())), Rcomp())),

                       [ [(0, 0), (0, 1)], 1]),
    ]
    for a, res in icases:
        yield check_get_id_indices, a, res
    
import numpy as np

def check_get_id_indices(a, res):
    got = get_id_indices(a)
    if got != res:
        msg = 'Result is different'
        raise_desc(ValueError, msg, a=a, res=res, got=got)

    # now compute the composition
    from mocdp.posets.poset_product import PosetProduct
    if isinstance(a, PosetProduct):
        reducel = PosetProduct
    else:
        reducel = list
    try:
        a2 = get_it(a, got, reducel)
    except Exception as e:
        raise_wrapped(ValueError, e, "invalid index produced", a=a, res=res, got=got)


    if str(a2) != str(a):
        msg = 'Not invertible'
        raise_desc(ValueError, msg, a=a, res=res, got=got, a2=a2)


    
    
    
    


