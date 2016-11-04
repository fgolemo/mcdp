# -*- coding: utf-8 -*-
from contracts.utils import raise_desc
from mcdp_dp import NotSolvableNeedsApprox, ApproximableDP
from mcdp_maps import SumNIntMap, SumNNatsMap, SumNMap, SumNRcompMap
from mcdp_posets import Int
from mcdp_posets import is_top
from mocdp.exceptions import DPNotImplementedError, mcdp_dev_warning

from .dp_generic_unary import WrapAMap
from .sequences_invplus import sample_sum_upperbound, \
    sample_sum_lowersets
from mcdp_dp.repr_strings import invplus2_repr_h_map


__all__ = [
    'SumNDP',
    'SumNNatDP',
    'SumNRcompDP',
    'SumNIntDP',
    'SumNLDP',
    'SumNUDP',
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
    
    def repr_hd_map(self):
        return repr_hd_map_sumn(len(self.Fs))

 
class SumNNatDP(WrapAMap, ApproximableDP):
    
    def __init__(self, n):
        self.n = n
        amap = SumNNatsMap(n)
        amap_dual = None
        WrapAMap.__init__(self, amap, amap_dual)
    
    def __repr__(self):
        return 'SumNNatDP(%s)' % self.n
    
    def solve_r(self, r):  # @UnusedVariable
        
        # Max { (f1, f2): f1 + f2 <= r }
        if self.n > 2:
            msg = 'SumNNatDP(%s).solve_r not implemented yet' % self.n
            raise_desc(DPNotImplementedError, msg)
        
        mcdp_dev_warning('move away')    
        if is_top(self.R, r):
            top = self.F[0].get_top()
            s = set([(top, top)])
            return self.F.Ls(s)

        assert isinstance(r, int)

        if r >= 100000:
            msg = 'This would create an antichain of %s items.' % r
            raise NotSolvableNeedsApprox(msg)
        
        s = set()        
        for o in range(r + 1):
            s.add((o, r - o))

        return self.F.Ls(s)
    
    def get_lower_bound(self, nl):  # @UnusedVariable
        msg = 'SumNNatDP(%s).get_lower_bound() not implemented yet' % self.n
        raise_desc(DPNotImplementedError, msg)

    def get_upper_bound(self, nu):  # @UnusedVariable
        msg = 'SumNNatDP(%s).get_upper_bound() not implemented yet' % self.n
        raise_desc(DPNotImplementedError, msg)
        
    def repr_hd_map(self):
        return repr_hd_map_sumn(len(self.Fs))

    
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
    
    def repr_hd_map(self):
        return repr_hd_map_sumn(len(self.Fs), 'U', self.n)

    
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
            msg = 'SumNLDP:solve_r: Cannot invert more than two terms.'
            raise_desc(NotImplementedError, msg)
            
        options = sample_sum_lowersets(self.R, self.F, r, self.n)
        return self.F.Ls(options)

    def repr_hd_map(self):
        return repr_hd_map_sumn(len(self.Fs), 'L', self.n)

class SumNRcompDP(WrapAMap, ApproximableDP):
    
    def __init__(self, n):
        amap = SumNRcompMap(n)
        amap_dual = None
        self.n = n
        WrapAMap.__init__(self, amap, amap_dual)

    def solve_r(self, r):  # @UnusedVariable
        raise NotSolvableNeedsApprox()
    
    def get_lower_bound(self, nl):
        return SumNRcompLDP(self.n, nl)

    def get_upper_bound(self, nu): 
        return SumNRcompUDP(self.n, nu)
    
    def repr_hd_map(self):
        return repr_hd_map_sumn(len(self.Fs))

    
class SumNRcompUDP(WrapAMap):
    """
        f1, f2, f3 -> f1 + f2 +f3
        r -> ((a,b) | a + b = r}
        
        This is an upper approximation, which is always pessimistic.
        So the points are exactly on the line, because that means 
        that we are being pessimistic.
        
    """
    def __init__(self, n, nu):
        self.n = n
        self.nu = nu
        amap = SumNRcompMap(n)
        WrapAMap.__init__(self, amap)
        
    def solve_r(self, r):
        if self.n > 2:
            msg = 'SumNRcompUDP: Cannot invert more than two terms.'
            raise_desc(NotImplementedError, msg)

        mcdp_dev_warning('not sure')
        options = sample_sum_upperbound(self.R, self.F, r, self.nu)
        return self.F.Ls(options)
    
    
    def repr_hd_map(self):
        return repr_hd_map_sumn(self.n, 'U', self.nu)

    
    
class SumNRcompLDP(WrapAMap):
    """
        f1, f2, f3 -> f1 + f2 +f3
        r -> ((a,b) | a + b = r}
        
        This is a lower approximation, which is always optimistic.
        
    """
    def __init__(self, n, nl):
        self.n = n
        self.nl = nl
        amap = SumNRcompMap(n)
        WrapAMap.__init__(self, amap)
        
    def solve_r(self, r):
        if self.n > 2:
            msg = 'SumNRcompLDP:solve_r: Cannot invert more than two terms.'
            raise_desc(NotImplementedError, msg)
            
        mcdp_dev_warning('not sure')
        options = sample_sum_lowersets(self.R, self.F, r, self.nl)
        return self.F.Ls(options)

    def repr_hd_map(self):
        return repr_hd_map_sumn(self.n, 'L', self.nl)


class SumNIntDP(WrapAMap):

    def __init__(self, n):
        Fs = (Int(),) * n
        R = Int()
        self.n = n

        amap = SumNIntMap(Fs, R)
        WrapAMap.__init__(self, amap)
        
    def __repr__(self):
        return 'SumNIntDP(%s)' % (self.n)
    

    def repr_hd_map(self):
        return repr_hd_map_sumn(self.n)

