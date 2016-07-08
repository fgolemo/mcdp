# -*- coding: utf-8 -*-
from contracts import contract
from .primitive import PrimitiveDP
from mcdp_posets import Poset
from mcdp_dp.primitive import EmptyDP


__all__ = [
    'Identity',
    'IdentityDP',
]


class IdentityDP(EmptyDP):

    @contract(F=Poset)
    def __init__(self, F):
        R = F
        EmptyDP.__init__(self, F=F, R=R)

    def solve(self, f):
        return self.R.U(f)

    def __repr__(self):
        return 'Id(%r)' % self.F


Identity = IdentityDP
