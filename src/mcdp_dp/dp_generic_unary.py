# -*- coding: utf-8 -*-
from contracts import contract
from contracts.utils import raise_wrapped
from mcdp_dp import PrimitiveDP
from mcdp_posets import Map, MapNotDefinedHere, NotBelongs, PosetProduct
from mocdp.exceptions import mcdp_dev_warning
import numpy as np


__all__ = [
    'GenericUnary',
    'WrapAMap',
]

class GenericUnary(PrimitiveDP):
    """ Meant for scalar values. Top maps to Top"""
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
        return "GenericUnary(%s)" % self.function  # .__name__


class WrapAMap(PrimitiveDP):

    @contract(amap=Map)
    def __init__(self, amap):
        M = PosetProduct(())
        F = amap.get_domain()
        R = amap.get_codomain()
        PrimitiveDP.__init__(self, F=F, R=R, M=M)
        self.amap = amap

    def solve(self, func):
        try:
            r = self.amap(func)
        except NotBelongs as e:
            msg = 'Wrapped map gives inconsistent results.'
            raise_wrapped(ValueError, e, msg, f=func, amap=self.amap)
        except MapNotDefinedHere as e:
            return self.R.Us([])

        return self.R.U(r)

    def diagram_label(self):  # XXX
        if hasattr(self.amap, '__name__'):
            return getattr(self.amap, '__name__')
        else:
            return self.amap.__repr__()

    def __repr__(self):
        return 'WrapAMap(%r)' % self.amap
