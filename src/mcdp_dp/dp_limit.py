# -*- coding: utf-8 -*-
from .primitive import PrimitiveDP
from contracts import contract
from mcdp_posets import Poset  # @UnusedImport
from mcdp_posets import PosetProduct, UpperSet
from mocdp.exceptions import mcdp_dev_warning, do_extra_checks
from mcdp_posets.uppersets import LowerSet
from mcdp_posets.space import NotBelongs


__all__ = [
    'Limit',
    'LimitMaximals',
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

class LimitMaximals(PrimitiveDP):

    @contract(F='$Poset', values='seq')
    def __init__(self, F, values):
        if do_extra_checks():
            for value in values:
                F.belongs(value)

        self.limit = LowerSet(values, F)

        R = PosetProduct(())
        M = PosetProduct(())
        PrimitiveDP.__init__(self, F=F, R=R, M=M)

    def solve(self, f):
        try:
            self.limit.belongs(f)
            res = UpperSet(set([()]), self.R)
            return res
        except NotBelongs:
            empty = UpperSet(set(), self.R)
            return empty

    def __repr__(self):
        return 'Limit(%s <= %s)' % (self.F, self.F.format(self.limit))

