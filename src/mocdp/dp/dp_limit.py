# -*- coding: utf-8 -*-
from .primitive import PrimitiveDP
from contracts import contract
from mocdp.posets import Poset  # @UnusedImport
from mocdp.posets import PosetProduct, UpperSet
import warnings


__all__ = [
    'Limit',
]


class Limit(PrimitiveDP):

    @contract(F='$Poset|str|code_spec')
    def __init__(self, F, value):
        from mocdp import get_conftools_posets
        _, F = get_conftools_posets().instance_smarter(F)
        F.belongs(value)
        self.limit = value

        R = PosetProduct(())
        M = PosetProduct(())
        PrimitiveDP.__init__(self, F=F, R=R, M=M)

    def solve(self, f):
        if self.R.leq(f, self.limit):
            res = UpperSet(set([()]), self.R)
            return res
        else:
            warnings.warn('Alternative is to use Top; think about it')
            empty = UpperSet(set(), self.R)
            return empty

    def __repr__(self):
        return 'Limit(%s <= %s)' % (self.F, self.F.format(self.limit))


