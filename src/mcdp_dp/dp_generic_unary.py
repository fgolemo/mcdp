# -*- coding: utf-8 -*-
from .primitive import EmptyDP
from contracts import contract
from contracts.utils import raise_desc, raise_wrapped, check_isinstance
from mcdp_posets import Map, MapNotDefinedHere, NotBelongs, Poset
# from mocdp.exceptions import mcdp_dev_warning
# import numpy as np


__all__ = [
#     'GenericUnary',
    'WrapAMap',
]

# # XXX: this should be replaced by GenericUnaryMap
# 
# class GenericUnary(EmptyDP):
#     """ Meant for scalar values. Top maps to Top"""
#     @contract(F=Poset, R=Poset)
#     def __init__(self, F, R, function):
#         EmptyDP.__init__(self, F=F, R=R)
#         self.function = function
# 
#         self.top = self.F.get_top()
# 
#     def solve(self, func):
#         if isinstance(func, int):
#             msg = 'Expecting a float, not an int.'
#             mcdp_dev_warning('Which exception to throw?')
#             raise_desc(ValueError, msg, func=func)
# 
#         if isinstance(func, float):
#             r = self.function(func)
# 
#             # mcdp_dev_warning('give much more thoguth')
#             if isinstance(r, float) and np.isinf(r):
#                 r = self.R.get_top()
#         else:
#             if self.F.equal(func, self.top):
#                 r = self.R.get_top()
#             else:
#                 raise ValueError(func)
# 
#         return self.R.U(r)
# 
#     def __repr__(self):
#         return "GenericUnary(%s)" % self.function  # .__name__


class WrapAMap(EmptyDP):
    """
        solve(f) = map(f)
        
        If map is not defined at f (raises MapNotDefinedHere),
        then it returns an empty set. 
    """

    @contract(amap=Map)
    def __init__(self, amap):
        check_isinstance(amap, Map)
        F = amap.get_domain()
        R = amap.get_codomain()
        check_isinstance(F, Poset)
        check_isinstance(R, Poset)
#             msg = 'Expect that F is a Poset.'
#             raise_desc(ValueError, msg, F=F, amap=amap)
#         if not isinstance(R, Poset):
#             msg = 'Expect that R is a Poset.'
#             raise_desc(ValueError, msg, R=R, amap=amap)

        EmptyDP.__init__(self, F=F, R=R)
        self.amap = amap

    def solve(self, func):
        try:
            r = self.amap(func)            
#         except NotBelongs as e:
#             msg = 'Wrapped map gives inconsistent results.'
#             raise_wrapped(ValueError, e, msg, f=func, amap=self.amap)
        except MapNotDefinedHere:
            return self.R.Us([])

        return self.R.U(r)

    def diagram_label(self):  # XXX
        if hasattr(self.amap, '__name__'):
            return getattr(self.amap, '__name__')
        else:
            return self.amap.__repr__()

    def __repr__(self):
        return 'WrapAMap(%r)' % self.amap
