# -*- coding: utf-8 -*-
from contracts import contract
from contracts.utils import raise_wrapped, raise_desc
from mcdp_dp import PrimitiveDP
from mcdp_posets import Map, MapNotDefinedHere, NotBelongs, PosetProduct
from mocdp.exceptions import mcdp_dev_warning, DPSemanticError
import numpy as np
from mcdp_dp.primitive import EmptyDP


__all__ = [
    'GenericUnary',
    'WrapAMap',
]

# # XXX: this should be replaced by GenericUnaryMap

class GenericUnary(EmptyDP):
    """ Meant for scalar values. Top maps to Top"""
    def __init__(self, F, R, function):
        EmptyDP.__init__(self, F=F, R=R)
        self.function = function

    def solve(self, func):
        if isinstance(func, int):
            msg = 'Expecting a float, not an int.'
            mcdp_dev_warning('Which exception to throw?')
            raise_desc(ValueError, msg, func=func)
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


class WrapAMap(EmptyDP):
    """
        solve(f) = map(f)
        
        If map is not defined at f (raises MapNotDefinedHere),
        then it returns an empty set. 
    """

    @contract(amap=Map)
    def __init__(self, amap):
        F = amap.get_domain()
        R = amap.get_codomain()
        EmptyDP.__init__(self, F=F, R=R)
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
