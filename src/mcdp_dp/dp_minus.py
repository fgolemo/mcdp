# -*- coding: utf-8 -*-
from contracts.utils import check_isinstance
from mcdp_maps import (MinusValueNatMap, PlusValueNatMap, MinusValueRcompMap,
                       PlusValueRcompMap, PlusValueMap, MinusValueMap)
from mcdp_posets import Nat, Rcomp, RcompUnits

from .dp_generic_unary import WrapAMap


__all__ = [
    'MinusValueDP',
    'MinusValueRcompDP',
    'MinusValueNatDP',
]

class MinusValueDP(WrapAMap):
    """
        r + c ≥ f
        
        h:  f ⟼  max(0, r-c) if  c ≠ ⊤
                  0           if  c = ⊤
        h*: r ⟼  r + c
    """
    def __init__(self, F, c_value, c_space):
        """ Give a positive constant here """
        check_isinstance(F, RcompUnits)
        check_isinstance(c_space, RcompUnits)
        c_space.belongs(c_value)
        amap = MinusValueMap(P=F, c_value=c_value, c_space=c_space)
        amap_dual = PlusValueMap(P=F, c_value=c_value, c_space=c_space)
        WrapAMap.__init__(self, amap, amap_dual)
        
    def diagram_label(self):
        return self.amap.diagram_label()

class MinusValueRcompDP(WrapAMap):
    """
        r + c ≥ f
        
        h:  f ⟼  max(0, r-c) if  c ≠ ⊤
                  0           if  c = ⊤
        h*: r ⟼  r + c
    """
    def __init__(self, c_value):
        """ Give a positive constant here """
        Rcomp().belongs(c_value)
        amap = MinusValueRcompMap(c_value)
        amap_dual = PlusValueRcompMap(c_value=c_value)
        WrapAMap.__init__(self, amap, amap_dual)
        
    
    def diagram_label(self):
        return self.amap.diagram_label()
    
class MinusValueNatDP(WrapAMap):
    """
        r + c ≥ f
        
        h:  f ⟼  max(0, r-c) if  c ≠ ⊤
                  0           if  c = ⊤
        h*: r ⟼  r + c
    """
    def __init__(self, c_value):
        """ Give a positive constant here """
        N = Nat()
        N.belongs(c_value)
        amap = MinusValueNatMap(c_value)
        amap_dual = PlusValueNatMap(c_value)
        WrapAMap.__init__(self, amap, amap_dual)

    def diagram_label(self):
        return self.amap.diagram_label()