# -*- coding: utf-8 -*-
from contracts import contract
from contracts.utils import check_isinstance, raise_desc
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
    def __init__(self, amap, amap_dual=None):
        check_isinstance(amap, Map)
            
        F = amap.get_domain()
        R = amap.get_codomain()
        check_isinstance(F, Poset)
        check_isinstance(R, Poset)
        
        if amap_dual is not None:
            check_isinstance(amap_dual, Map)
            ok = ( R == amap_dual.get_domain()) and \
            ( F == amap_dual.get_codomain())
            if not ok:
                msg = 'Maps not compatible.'
                msg += '\n h: %s -> %s' % (amap.get_domain(), amap.get_codomain())
                msg += '\n h*: %s -> %s' % (amap_dual.get_domain(), amap_dual.get_codomain())
                raise_desc(ValueError, msg, amap=amap, amap_dual=amap_dual)
            
        self.amap_dual = amap_dual
        self.amap = amap
        EmptyDP.__init__(self, F=F, R=R)

    def _set_map_dual(self, amap_dual):
        """ Used for late initialization """
        if self.amap_dual is not None:
            msg = 'Dual map already initialized.'
            raise_desc(ValueError, msg, amap_dual=self.amap_dual)
        self.amap_dual = amap_dual
        
    def solve_r(self, r):  # @UnusedVariable
        if self.amap_dual is None:
            msg = 'Map amap_dual not provided so solve_r() not implemented.' 
            raise_desc(NotImplementedError, msg, type=type(self), dp=self,
                       amap=self.amap)
        
        try:
            f = self.amap_dual(r)            
        except MapNotDefinedHere:
            return self.F.Ls([])

        return self.F.L(f)
        
    def solve(self, func):
        try:
            r = self.amap(func)            
        except MapNotDefinedHere:
            return self.R.Us([])

        return self.R.U(r)

    def diagram_label(self):  # XXX
        if hasattr(self.amap, '__name__'):
            return getattr(self.amap, '__name__')
        else:
            return self.amap.__repr__()

    def __repr__(self):
        if self.amap_dual is not None:
            return '%s(%r,%r)' % (type(self).__name__, self.amap, self.amap_dual)
        return '%s(%r)' % (type(self).__name__, self.amap)
