# -*- coding: utf-8 -*-
from .primitive import PrimitiveDP
from contracts import contract
from mcdp_posets import Poset, PosetProduct


__all__ = [
    'Constant',
    'ConstantMinimals',
]


class Constant(PrimitiveDP):

    @contract(R=Poset)
    def __init__(self, R, value):
        self.c = value

        F = PosetProduct(())
        I = PosetProduct(())
        PrimitiveDP.__init__(self, F=F, R=R, I=I)

    def evaluate(self, i):
        assert i == ()
        fs = self.F.L(self.F.get_top())
        rs = self.R.U(self.c)
        return fs, rs
        
    def solve(self, _):
        return self.R.U(self.c)

    def __repr__(self):
        return 'Constant(%s:%r)' % (self.R, self.c)


class ConstantMinimals(PrimitiveDP):

    @contract(R=Poset)
    def __init__(self, R, values):
        F = PosetProduct(())
        I = PosetProduct(())
        self.values = values
        PrimitiveDP.__init__(self, F=F, R=R, I=I)

    def evaluate(self, i):
        assert i == ()
        fs = self.F.L(self.F.get_top())
        rs = self.R.Us(self.c)
        return fs, rs

    def solve(self, _):
        return self.R.Us(self.values)

    def __repr__(self):
        return 'ConstantMins(%s:%r)' % (self.R, self.values)

