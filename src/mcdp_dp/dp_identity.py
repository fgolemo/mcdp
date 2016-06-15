# -*- coding: utf-8 -*-
from contracts import contract
from .primitive import PrimitiveDP
from mcdp_posets import Poset, PosetProduct


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


