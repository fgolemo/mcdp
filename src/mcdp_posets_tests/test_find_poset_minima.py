# -*- coding: utf-8 -*-
from comptests.registrar import comptest
from contracts import contract
from mcdp_posets import Poset, PosetProduct, Rcomp
from mcdp_posets.find_poset_minima.baseline_n2 import poset_minima_n2
import numpy as np
import random

@contract(n='>=1', ndim='>=1', m='>0')
def get_random_points(n, ndim, m):
    """ Gets a set of n points in [0,m]*[0,m]*... (ndim dimensions) """
    res = set()
    while len(res) < n:
        s = []
        for _ in range(ndim):
            # x = random.randint(0, m)
            x = np.random.rand() * m
            s.append(x)
        r = tuple(s)
        res.add(r)
    return res

def wrap_with_counts(P, maxleq=None):
    if isinstance(P, PosetProduct):
        base = PosetProduct
    else:
        base = Poset
    class P2(base):
        def __init__(self, P):
            self.P = P
            self.reset_counters()

        def reset_counters(self):
            self.nleq = 0
            self.nleq_true = 0
            self.nleq_false = 0

        def belongs(self, x):
            return self.P.belongs(x)
        def check_equal(self, a, b):
            return self.P.check_equal(a, b)

        def check_leq(self, a, b):
            return self.check_leq(a, b)

        def witness(self):
            return self.P.witness()

        def leq(self, a, b):
            res = self.P.leq(a, b)
            if res:
                self.nleq_true += 1
            else:
                self.nleq_false += 1
            self.nleq += 1
            if maxleq is not None:
                if self.nleq >= maxleq:
                    msg = ('%d leqs (true: %d, false: %d)' %
                           (self.nleq, self.nleq_true, self.nleq_false))
                    raise ValueError(msg)
            return res

        def __getattr__(self, method_name):
            return getattr(P, method_name)
    return P2(P)

@contract(P=PosetProduct, xs='set')
def stats_for_poset_minima(P, xs, f, maxleq):
    """
        
        f(P, x)
    """
    for s in P:
        s.reset_counters()

    xs_ = list(xs)
    random.shuffle(xs_)
    res = f(P, xs_)

    print('n: %d' % len(xs))
    print('nres: %d' % len(res))

    for s in P:
        print('component %s' % s)
        print(' nleq:  %d' % s.nleq)
        print(' nleqt: %d' % s.nleq_true)
        print(' nleqf: %d' % s.nleq_false)
    return res

if False:
    # Rcomp' object has no attribute 'reset_counters'
    @comptest
    def pmin1():
        n = 1000
        ndim = 3
        m = 430000
        Ps = get_random_points(n, ndim, m)
        Pbase = Rcomp()
        N2 = PosetProduct((Pbase,) * ndim)

        method = poset_minima_n2
        N2w = wrap_with_counts(N2)
        r = stats_for_poset_minima(N2w, Ps, method, maxleq=None)
        print r

#
# def get_random_antichain(n, point_generation, leq):
#     cur = set()
#     while len(cur) < n:
#         print('Current size: %d < %d' % (len(cur), n))
#         remaining = n - len(cur)
#         Ps = point_generation(n * 10)
#         cur.update(Ps)
#         cur = poset_minima(cur, leq)
#     return cur

def get_random_antichain(n, ndim):
    if ndim != 2:
        raise NotImplementedError()
    
    xs = np.linspace(0, 100, n)
    deltas = np.random.rand(n)
    ys = 1.0 / np.cumsum(deltas)
    return zip(xs, ys)


@comptest
def pmin2():
    n = 300
    ndim = 2
    Pbase = wrap_with_counts(Rcomp())
    N2 = PosetProduct((Pbase,) * ndim)

    print('Using random antichain')
    # point_generation = lambda n: get_random_points(n, ndim, m)
    # Ps = get_random_antichain(n, point_generation, N2.leq)
    P1 = get_random_antichain(n, ndim)
    P2 = get_random_antichain(n, ndim)
    Ps = set()
    Ps.update(P1)
    Ps.update(P2)

    run_all(N2, Ps)

def run_all(poset, Ps):
    method = poset_minima_n2
    print('method: %s' % method)
    r = stats_for_poset_minima(poset, Ps, method, maxleq=None)
    def poset_minima_n2_sort_first(P, ps):
        f = sorted(ps)
        return poset_minima_n2(P, f)

    method = poset_minima_n2_sort_first
    print('method: %s' % method)
    r = stats_for_poset_minima(poset, Ps, method, maxleq=None)

    method = poset_minima_n2_optimizedPP
    print('method: %s' % method)
    r = stats_for_poset_minima(poset, Ps, method, maxleq=None)

@comptest
def pmin3():
    n = 200000
    ndim = 2
    Pbase = wrap_with_counts(Rcomp())
    N2 = PosetProduct((Pbase,) * ndim)

    print('Using random antichain')
    Ps = get_random_points(n, ndim, m=1000)

    run_all(N2, Ps)


def poset_minima_n2_optimizedPP(P, ps):
    assert isinstance(P, PosetProduct) and len(P) == 2
    l1 = P[0].leq
    l2 = P[1].leq
    # Sort by x
    def cmp1(a, b):
        if l1(a, b):
            return -1
        if l1(b, a):
            return +1
        return 0

    sx = sorted(ps, cmp=cmp1)
    res = set()
    min_y = None
    for p in sx:
        # print('p: %s min_y: %s' % (str(p), min_y))
        if min_y is None or (l2(p[1], min_y)):
            res.add(p)
            min_y = p[1]
        
    return res
    





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
