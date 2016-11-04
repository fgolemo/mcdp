# -*- coding: utf-8 -*-
# TODO: move 
from contracts.utils import check_isinstance
from mcdp_maps import (PlusValueMap, PlusValueRcompMap, PlusValueNatMap,
                       PlusValueDualMap, PlusValueDualRcompMap, PlusValueDualNatMap)
from mcdp_posets import RcompUnits

from .dp_generic_unary import WrapAMap


__all__ = [
    'PlusValueDP',
    'PlusValueRcompDP',
    'PlusValueNatDP',
]

class PlusValueDP(WrapAMap):
    """ RCompUnits """
    def __init__(self, F, c_value, c_space):
        check_isinstance(F, RcompUnits)
        check_isinstance(c_space, RcompUnits)
        amap = PlusValueMap(P=F, c_value=c_value, c_space=c_space)
        amap_dual = PlusValueDualMap(P=F, c_value=c_value, c_space=c_space)
        WrapAMap.__init__(self, amap, amap_dual)
    
    def diagram_label(self):  
        return self.amap.diagram_label()
        
class PlusValueRcompDP(WrapAMap):
    def __init__(self,  c_value):
        amap = PlusValueRcompMap(c_value)
        amap_dual = PlusValueDualRcompMap(c_value)
        WrapAMap.__init__(self, amap, amap_dual)
        
        
class PlusValueNatDP(WrapAMap):
    def __init__(self,  c_value):
        amap = PlusValueNatMap(c_value)
        amap_dual = PlusValueDualNatMap(c_value)
        WrapAMap.__init__(self, amap, amap_dual)
        
        
        