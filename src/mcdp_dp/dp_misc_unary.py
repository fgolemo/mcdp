# -*- coding: utf-8 -*-
from mcdp_dp.dp_generic_unary import WrapAMap
from mcdp_dp.dp_series_simplification import wrap_series
from mcdp_maps.map_composition import MapComposition
from mcdp_maps.misc_imp import (SquareNatMap, SqrtMap, FloorMap, SquareMap,
    Floor0Map, CeilMap)
from mcdp_posets import Nat, Rcomp
from mcdp_posets.maps.coerce_to_int import CoerceToInt
from mcdp_posets.maps.promote_to_float import PromoteToFloat
from mcdp_posets.rcomp_units import RCompUnitsPowerMap


__all__ = [
    'SquareNatDP',
    'PromoteToFloatDP',    
    'CoerceToIntDP',
    'CeilSqrtNatDP',
    'SquareDP',
    'Floor0DP',
    'CeilDP',
    'SqrtRDP',
    'RcompUnitsPowerDP',
]



class RcompUnitsPowerDP(WrapAMap): # TODO: move
    def __init__(self, F, num, den):
        amap = RCompUnitsPowerMap(F, num=num, den=den)
        amap_dual = RCompUnitsPowerMap(amap.get_codomain(), num=den, den=num) # swap
        WrapAMap.__init__(self, amap, amap_dual)


class SquareNatDP(WrapAMap):
    def __init__(self):
        amap = SquareNatMap()
        
        N = Nat()
        R = Rcomp()
        
        maps = (
            PromoteToFloat(N, R),
            SqrtMap(R),
            FloorMap(R),
            CoerceToInt(R, N))
        
        amap_dual = MapComposition(maps)
         
        WrapAMap.__init__(self, amap, amap_dual)
        
    def diagram_label(self):
        return self.amap.diagram_label()

class PromoteToFloatDP(WrapAMap):
    def __init__(self, F, R):
        amap = PromoteToFloat(F, R)
        amap_dual = CoerceToInt(R, F)
        WrapAMap.__init__(self, amap, amap_dual)
    
class CoerceToIntDP(WrapAMap):
    def __init__(self, F, R):
        amap = CoerceToInt(F, R)
        amap_dual = PromoteToFloat(R, F)
        WrapAMap.__init__(self, amap, amap_dual)
        
def CeilSqrtNatDP():
    # promote to float
    # take sqrt
    # make ceil
    # coerce
    R = Rcomp()
    N = Nat()
    dps = (
        PromoteToFloatDP(N, R),
        SqrtRDP(R),
        CeilDP(R),
        CoerceToIntDP(R, N),
    )
    return wrap_series(N, dps)
        
    
class SquareDP(WrapAMap):
    def __init__(self, F):
        amap = SquareMap(F)
        amap_dual = SqrtMap(F)
        WrapAMap.__init__(self, amap, amap_dual)
    
    def diagram_label(self):
        return '^ 2'
    
        
class SqrtRDP(WrapAMap):
    """ r >= sqrt(f) for rcomp or rcompunits """
    def __init__(self, F):
        amap = SqrtMap(F)
        amap_dual = SquareMap(F)
        WrapAMap.__init__(self, amap, amap_dual)
    
    def diagram_label(self):
        return 'sqrt'
        
class Floor0DP(WrapAMap):
    """
        Note that floor() is not S-C.
        
        This is floor0:
        
        floor0(f) = { 0 for f = 0
                      ceil(f-1) for f > 0
    """
    def __init__(self, F):
        amap = Floor0Map(F)
        amap_dual = CeilMap(F)
        WrapAMap.__init__(self, amap, amap_dual)

    def diagram_label(self):  
        return 'floor0'

class CeilDP(WrapAMap):
    def __init__(self, F):
        amap = CeilMap(F)
        amap_dual = FloorMap(F)
        WrapAMap.__init__(self, amap, amap_dual)
    def diagram_label(self):  
        return 'ceil'

    