# -*- coding: utf-8 -*-
from .primitive import PrimitiveDP
from contracts import contract
from mcdp_posets import Poset 
from mcdp_posets import PosetProduct


__all__ = [
    'Identity',
]


class Identity(PrimitiveDP):

    @contract(F=Poset)
    def __init__(self, F):
        R = F
        M = PosetProduct(())
        PrimitiveDP.__init__(self, F=F, R=R, M=M)

    def solve(self, f):
        return self.R.U(f)

    def __repr__(self):
        return 'Id(%r)' % self.F


