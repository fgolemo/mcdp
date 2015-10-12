# -*- coding: utf-8 -*-

from comptests.registrar import comptest
from mocdp.comp.connection import Connection, connect2
from mocdp.comp.wrap import SimpleWrap
from mocdp.dp.primitive import PrimitiveDP
from mocdp.posets import PosetProduct, Rcomp
from nose.tools import assert_equal


def get_dummy(fnames, rnames):
    
    base = (Rcomp(),)
    F = PosetProduct(base * len(fnames))
    R = PosetProduct(base * len(rnames))
    if len(fnames) == 1:
        F = F[0]
    if len(rnames) == 1:
        R = R[0]

    class Dummy(PrimitiveDP):
        def __init__(self):
            PrimitiveDP.__init__(self, F=F, R=R)
        def solve(self, _func):
            return self.R.bottom()

    if len(fnames) == 1:
        fnames = fnames[0]
    if len(rnames) == 1:
        rnames = rnames[0]

    return SimpleWrap(Dummy(), fnames, rnames)
    
@comptest
def check_connect2_a():
    #
    #  f2 -> |  | -r2:F0-> | c2 | -> R0

    ndp1 = get_dummy(['f2'], ['r2'])
    ndp2 = get_dummy(['F0'], ['R0'])

    connections = set([Connection('-', 'r2', '-', 'F0')])

    res = connect2(ndp1, ndp2, connections, split=[])

    assert_equal(res.get_fnames() , ['f2'])
    assert_equal(res.get_rnames() , ['R0'])


@comptest
def check_connect2_b():
    #  f1 -> | 1| --r1---------------->
    #  f2 -> | 1 | -r2:F0-> | c2 | -> R0

    ndp1 = get_dummy(['f1', 'f2'], ['r1', 'r2'])
    ndp2 = get_dummy(['F0'], ['R0'])

    connections = set([Connection('-', 'r2', '-', 'F0')])

    res = connect2(ndp1, ndp2, connections, split=[])

    assert_equal(res.get_fnames() , ['f1', 'f2'])
    assert_equal(res.get_rnames() , ['r1', 'R0'])



@comptest
def check_connect2_c():
    #  f1 -> | 1| --r1---------------->
    #  f2 -> | 1 | -r2:F0-> | c2 | -> R0
    #        | 1| --r3---------------->

    ndp1 = get_dummy(['f1', 'f2'], ['r1', 'r2', 'r3'])
    ndp2 = get_dummy(['F0'], ['R0'])

    connections = set([Connection('-', 'r2', '-', 'F0')])

    res = connect2(ndp1, ndp2, connections, split=[])

    assert_equal(res.get_fnames() , ['f1', 'f2'])
    assert_equal(res.get_rnames() , ['r1', 'r3', 'R0'])

@comptest
def check_connect2_d():
    # 
    #  f0 -> |  | -----> r0
    #  f1 -> |c1| -----> r1
    #  f2 -> |  | -r2:F0-> | c2 | -> R0
    #  F1----------------> |    | -> R1
    
    
    ndp1 = get_dummy(['f0', 'f1', 'f2'], ['r0', 'r1', 'r2'])
    ndp2 = get_dummy(['F0', 'F1'], ['R0', 'R1'])
    
    connections = set([Connection('-', 'r2', '-', 'F0')])

    res = connect2(ndp1, ndp2, connections, split=[])
