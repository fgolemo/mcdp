# -*- coding: utf-8 -*-
from contracts import contract
from contracts.utils import check_isinstance
from mcdp_posets import Map, MapNotDefinedHere, Poset

from .primitive import EmptyDP


__all__ = [
    'WrapAMap',
]



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
