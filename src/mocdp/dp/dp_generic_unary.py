# -*- coding: utf-8 -*-
from .primitive import PrimitiveDP
from contracts import contract
from mocdp.posets.poset_product import PosetProduct


__all__ = [
    'GenericUnary',
]

class GenericUnary(PrimitiveDP):

    def __init__(self, F, R, function):
        M = PosetProduct(())
        PrimitiveDP.__init__(self, F=F, R=R, M=M)
        self.function = function

    def solve(self, func):
        r = self.function(func)

        return self.R.U(r)

    def __repr__(self):
        return self.function.__name__


