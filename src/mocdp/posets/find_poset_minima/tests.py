# -*- coding: utf-8 -*-
from comptests.registrar import comptest
import random
from contracts import contract
from mocdp.posets.nat import Nat
from mocdp.posets.poset_product import PosetProduct
from mocdp.posets.find_poset_minima.baseline_n2 import poset_minima


@contract(n='>=1', ndim='>=1', m='>0')
def get_random_points(n, ndim, m):
    """ Gets a set of n points in [0,m]*[0,m]*... (ndim dimensions) """
    res = set()
    for _ in range(n):
        s = []
        for _ in range(ndim):
            x = random.randint(0, m)
            s.append(x)
        r = tuple(s)
        res.add(r)
    return res


@comptest
def pmin1():
    n = 100
    ndim = 2
    m = 43
    Ps = get_random_points(n, ndim, m)
    N2 = PosetProduct(Nat(), Nat())

    r = poset_minima(Ps, N2.leq)
    print r


@comptest
def pmin2():
    pass


@comptest
def pmin3():
    pass


@comptest
def pmin4():
    pass


@comptest
def pmin5():
    pass


@comptest
def pmin6():
    pass


@comptest
def pmin7():
    pass


@comptest
def pmin8():
    pass


@comptest
def pmin9():
    pass
