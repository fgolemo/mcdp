# -*- coding: utf-8 -*-
from contracts.utils import raise_desc
from mcdp_dp import NotSolvableNeedsApprox, ApproximableDP
from mcdp_dp.dp_inv_plus import sample_sum_upperbound, sample_sum_lowersets
from mcdp_maps import SumNIntMap, SumNNatsMap, SumNMap, SumNRcompMap
from mcdp_posets import Int

from .dp_generic_unary import WrapAMap


__all__ = [
    'SumNDP',
    'SumNNatDP',
    'SumNRcompDP',
    'SumNIntDP',
]

class SumNDP(WrapAMap, ApproximableDP):
    """
        f1, f2, f3 -> f1 + f2 +f3
    """
    def __init__(self, Fs, R):
        amap = SumNMap(Fs, R)
        amap_dual = None
        WrapAMap.__init__(self, amap, amap_dual)
        self.Fs = Fs
        self.R = R
    
    def solve_r(self, r):  # @UnusedVariable
        raise NotSolvableNeedsApprox()
    
    def get_lower_bound(self, n):
        return SumNLDP(self.Fs, self.R, n)

    def get_upper_bound(self, n): 
        return SumNUDP(self.Fs, self.R, n)
 
class SumNNatDP(WrapAMap):
    def __init__(self, n):
        self.n = n
        amap = SumNNatsMap(n)
        amap_dual = None
        WrapAMap.__init__(self, amap, amap_dual)
    
    def __repr__(self):
        return 'SumNNatDP(%s)' % self.n
    
    def solve_r(self, r):  # @UnusedVariable
        raise NotImplementedError()
#     
#     def get_lower_bound(self, n):
#         return SumNLDP(self.Fs, self.R, n)
# 
#     def get_upper_bound(self, n): 
#         return SumNUDP(self.Fs, self.R, n)
    
class SumNUDP(WrapAMap):
    """
        f1, f2, f3 -> f1 + f2 +f3
        r -> ((a,b) | a + b = r}
        
        This is an upper approximation, which is always pessimistic.
        So the points are exactly on the line, because that means 
        that we are being pessimistic.
        
    """
    def __init__(self, Fs, R, n):
        self.n = n
        amap = SumNMap(Fs, R)
        self.Fs = Fs 
        WrapAMap.__init__(self, amap)
        
    def solve_r(self, r):
         
        if len(self.Fs) > 2:
            msg = 'Cannot invert more than two terms.'
            raise_desc(NotImplementedError, msg)

        options = sample_sum_upperbound(self.R, self.F, r, self.n)
        return self.F.Ls(options)
    
    
class SumNLDP(WrapAMap):
    """
        f1, f2, f3 -> f1 + f2 +f3
        r -> ((a,b) | a + b = r}
        
        This is a lower approximation, which is always optimistic.
        
    """
    def __init__(self, Fs, R, n):
        self.n = n
        self.Fs = Fs
        amap = SumNMap(Fs, R)
        WrapAMap.__init__(self, amap)
        
    def solve_r(self, r):
        if len(self.Fs) > 2:
            msg = 'Cannot invert more than two terms.'
            raise_desc(NotImplementedError, msg)
            
        options = sample_sum_lowersets(self.R, self.F, r, self.n)
        return self.F.Ls(options)

class SumNRcompDP(WrapAMap):
    def __init__(self, n):
        amap = SumNRcompMap(n)
        amap_dual = None
        WrapAMap.__init__(self, amap, amap_dual)


class SumNIntDP(WrapAMap):

    def __init__(self, n):
        Fs = (Int(),) * n
        R = Int()
        self.n = n

        amap = SumNIntMap(Fs, R)
        WrapAMap.__init__(self, amap)
        
    def __repr__(self):
        return 'SumNIntDP(%s)' % (self.n)
    


