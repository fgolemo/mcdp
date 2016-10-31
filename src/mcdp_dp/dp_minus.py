from mcdp_dp.dp_generic_unary import WrapAMap
from contracts.utils import check_isinstance
from mcdp_maps.plus_value_map import MinusValueRcompMap, PlusValueRcompMap
from mcdp_posets.rcomp_units import RcompUnits
from mcdp_maps.plus_value_map import PlusValueMap, MinusValueMap
from mcdp_posets.rcomp import Rcomp
from mcdp_maps.plus_nat import MinusValueNatMap, PlusValueNatMap

__all__ = [
    'MinusValueDP',
    'MinusValueRcompDP',
    'MinusValueNatDP',
]

class MinusValueDP(WrapAMap):
    """ Give a positive constant here """
    def __init__(self, F, c_value, c_space):
        check_isinstance(F, RcompUnits)
        check_isinstance(c_space, RcompUnits)
        c_space.belongs(c_value)
        amap = MinusValueMap(P=F, c_value=c_value, c_space=c_space)
        amap_dual = PlusValueMap(F=F, c_value=c_value, c_space=c_space, R=F)
        WrapAMap.__init__(self, amap, amap_dual)
        
class MinusValueRcompDP(WrapAMap):
    """ Give a positive constant here """
    def __init__(self, c_value):
        Rcomp().belongs(c_value)
        amap = MinusValueRcompMap(c_value)
        amap_dual = PlusValueRcompMap(c_value=c_value)
        WrapAMap.__init__(self, amap, amap_dual)
        
class MinusValueNatDP(WrapAMap):
    """ Give a positive constant here """
    def __init__(self, c_value):
        assert c_value >= 0, c_value
        amap = MinusValueNatMap(c_value)
        amap_dual = PlusValueNatMap(c_value)
        WrapAMap.__init__(self, amap, amap_dual)
