# TODO: move 
from contracts.utils import check_isinstance
from mcdp_maps.plus_nat import PlusValueNatMap, MinusValueNatMap
from mcdp_maps.plus_value_map import PlusValueMap, MinusValueMap, \
    PlusValueRcompMap, MinusValueRcompMap
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
        amap = PlusValueMap(F=F, c_value=c_value, c_space=c_space, R=F)
        #setattr(amap, '__name__', '+ %s' % (c_space.format(c_value)))
        amap_dual = MinusValueMap(P=F, c_value=c_value, c_space=c_space )
        WrapAMap.__init__(self, amap, amap_dual)
        
class PlusValueRcompDP(WrapAMap):
    def __init__(self,  c_value):
        amap = PlusValueRcompMap(c_value)
#         setattr(amap, '__name__', '+ {}'.format(c_value)) 
        amap_dual = MinusValueRcompMap(c_value)
#         setattr(amap, '__name__', '- {}'.format(c_value))
        WrapAMap.__init__(self, amap, amap_dual)
        
class PlusValueNatDP(WrapAMap):
    def __init__(self,  c_value):
        amap = PlusValueNatMap(c_value)
        amap_dual = MinusValueNatMap(c_value)
        WrapAMap.__init__(self, amap, amap_dual)