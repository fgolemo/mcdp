# -*- coding: utf-8 -*-
from contracts.utils import check_isinstance
from mcdp_posets import Map, Rcomp, RcompUnits
from mcdp_posets.rcomp import tiny 
import numpy as np


__all__ = [
    'LinearMapComp',
]

class LinearMapComp(Map):
    """ Linear multiplication on R + top """

    def __init__(self, A, B, factor):
        check_isinstance(A, (Rcomp, RcompUnits))
        check_isinstance(B, (Rcomp, RcompUnits))
        Map.__init__(self, A, B)
        self.A = A
        self.B = B
        self.factor = factor

    def _call(self, x):
        if self.A.equal(x, self.A.get_top()):
            return self.B.get_top()

        try:
            res = x * self.factor
        except FloatingPointError as e:
            assert 'underflow' in str(e)
            # print x, self.factor
            res = tiny

        if np.isinf(res):
            return self.B.get_top()
        return res
