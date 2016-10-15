# -*- coding: utf-8 -*-
from mcdp_maps import JoinNMap, Max1Map, MeetNMap
from mcdp_maps.max1map import Max1dualMap
from mcdp_posets import Poset

from .dp_flatten import Mux
from .dp_generic_unary import WrapAMap


__all__ = [
    'Max',
    'Max1',
    'Min',
    'JoinNDP',
    'MeetNDual',
]


class Max1(WrapAMap):
    """
        f ⟼ { max(value, f) }
        r ⟼  {r} if r >= value
               {} otherwise 
    """
    def __init__(self, F, value):
        assert isinstance(F, Poset)
        m = Max1Map(F, value)
        md = Max1dualMap(R=F, value=value)
        WrapAMap.__init__(self, m, md)
        self.value = value
    
    def __repr__(self):
        return 'Max1(%r, %s)' % (self.F, self.value)


class Min(WrapAMap):
    """ 
        Meet on a poset  
        
        f1, f2 ⟼ { min(f1, f2) }
        
        r ⟼  {r} if r >= value
               {} otherwise 
    """

    def __init__(self, F):  #
        assert isinstance(F, Poset)
        amap = MeetNMap(2, F)
        WrapAMap.__init__(self, amap)
        
        self.F0 = F

    def diagram_label(self):  # XXX
        return 'Min'
    
    def __repr__(self):
        return 'Min(%r)' % self.F0
    
    

class JoinNDP(WrapAMap):
    def __init__(self, n, P):
        amap = JoinNMap(n, P)
        WrapAMap.__init__(self, amap)


class MeetNDual(Mux):
    """ This is just a Mux 
    
        f ⟼ {(f, f, ..., f)} 
        
        r1, ..., rn ⟼ {min(r1, ..., rn)}
        
    """
    def __init__(self, n, P):
        coords = [()] * n
        Mux.__init__(self, P, coords)
    
        self._set_map_dual(MeetNMap(n, P)) 
        
# SplitMap = MeetNDual
        
class Max(WrapAMap):
    """ This is the same as JoinNDP but it is its own class for visualization """    
    def __init__(self, F0):
        amap = JoinNMap(2, F0)
        from mcdp_dp.dp_flatten import MuxMap
        
        amap_dual = MuxMap(F0, [(), ()])
        WrapAMap.__init__(self, amap, amap_dual)

        self.F0 = F0

    def diagram_label(self):
        return 'Max'
    
    def __repr__(self):
        return 'Max(%r)' % self.F0

