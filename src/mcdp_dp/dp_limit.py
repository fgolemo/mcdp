# -*- coding: utf-8 -*-
from .primitive import PrimitiveDP
from contracts import contract
from mcdp_posets import LowerSet, NotBelongs, Poset  # @UnusedImport
from mcdp_posets import PosetProduct, UpperSet
from mocdp.exceptions import do_extra_checks, mcdp_dev_warning


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
        I = PosetProduct(())
        PrimitiveDP.__init__(self, F=F, R=R, I=I)

    def evaluate(self, i):
        assert i == ()
        rs = self.R.U(self.R.get_bottom())
        fs = self.F.L(self.limit)
        return fs, rs

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
        return 'Limit(%s, %s)' % (self.F, self.F.format(self.limit))

class LimitMaximals(PrimitiveDP):

    @contract(F='$Poset', values='seq|set')
    def __init__(self, F, values):
        if do_extra_checks():
            for value in values:
                F.belongs(value)

        self.limit = LowerSet(values, F)

        R = PosetProduct(())
        M = PosetProduct(())
        PrimitiveDP.__init__(self, F=F, R=R, I=M)

    def evaluate(self, m):
        assert m == ()
        LF = self.limit
        UR = UpperSet(set([()]), self.R)
        return LF, UR
        
    def solve(self, f):
        try:
            # check that it belongs
            self.limit.belongs(f)
        except NotBelongs:
            empty = UpperSet(set(), self.R)
            return empty
        res = UpperSet(set([()]), self.R)
        return res

    def __repr__(self):
        s = len(self.limit.maximals)
        return 'LimitMaximals(%s, %s els)' % (self.F, s)

