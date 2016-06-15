# -*- coding: utf-8 -*-
from .primitive import PrimitiveDP
from contracts import contract
from mocdp.exceptions import mcdp_dev_warning
from mcdp_posets import Poset  # @UnusedImport
from mcdp_posets import PosetProduct, UpperSet


__all__ = [
    'Limit',
]


class Limit(PrimitiveDP):

    @contract(F='$Poset')
    def __init__(self, F, value):
        F.belongs(value)
        self.limit = value

        R = PosetProduct(())
        M = PosetProduct(())
        PrimitiveDP.__init__(self, F=F, R=R, M=M)

    def solve(self, f):
        if self.F.leq(f, self.limit):
            res = UpperSet(set([()]), self.R)
            # print('returning res %s' % res)
            return res
        else:
            mcdp_dev_warning('Alternative is to use Top; think about it')
            empty = UpperSet(set(), self.R)
            # print('returning empty %s' % empty)
            return empty

    def __repr__(self):
        return 'Limit(%s <= %s)' % (self.F, self.F.format(self.limit))


