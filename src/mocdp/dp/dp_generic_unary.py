# -*- coding: utf-8 -*-
from .primitive import PrimitiveDP
from mocdp.exceptions import mcdp_dev_warning
from mocdp.posets import PosetProduct
import numpy as np
from mocdp.posets.space import Map
from contracts import contract


__all__ = [
    'GenericUnary',
    'WrapAMap',
]

class GenericUnary(PrimitiveDP):
    """ Meant for scalar values...."""
    def __init__(self, F, R, function):
        M = PosetProduct(())
        PrimitiveDP.__init__(self, F=F, R=R, M=M)
        self.function = function

    def get_implementations_f_r(self, f, r):  # @UnusedVariable
        return set([()])

    def solve(self, func):
        if self.F.equal(func, self.F.get_top()):
            r = self.R.get_top()
        else:
            r = self.function(func)

            mcdp_dev_warning('give much more thoguth')
            if isinstance(r, float) and np.isinf(r):
                r = self.R.get_top()
            
        return self.R.U(r)

    def __repr__(self):
        return "GenericUnary(%s) %% %s -> %s" % (self.function.__name__, self.F, self.R)



class WrapAMap(PrimitiveDP):

    @contract(amap=Map)
    def __init__(self, amap):
        M = PosetProduct(())
        F = amap.get_domain()
        R = amap.get_codomain()
        PrimitiveDP.__init__(self, F=F, R=R, M=M)
        self.amap = amap

    def solve(self, func):
        r = self.amap(func)
        return self.R.U(r)

    def __repr__(self):
        return 'WrapAMap(%r)' % self.amap
