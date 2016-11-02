# -*- coding: utf-8 -*-
from contracts import contract
from contracts.utils import raise_desc, check_isinstance
from mcdp_dp.dp_inv_mult import Nat_mult_antichain_Max
from mcdp_dp.primitive import NotSolvableNeedsApprox, ApproximableDP
from mcdp_maps import ProductNMap, ProductNNatMap
from mcdp_posets import Rcomp, RcompUnits
from mcdp_posets.rcomp_units import check_mult_units_consistency_seq
from mocdp.exceptions import mcdp_dev_warning

from .dp_generic_unary import WrapAMap
from mcdp_dp.dp_inv_plus import sample_sum_upperbound


__all__ = [
    'ProductNDP',
    'ProductNNatDP',
    'ProductNRcompDP',
    'Product2DP_U',
    'Product2DP_L',
]

class ProductNDP(WrapAMap, ApproximableDP):
    
    @contract(Fs='tuple[>=2]')
    def __init__(self, Fs, R):
        if isinstance(R, Rcomp):
            for F in Fs:
                check_isinstance(F, Rcomp)
        elif isinstance(R, RcompUnits):
            for F in Fs:
                check_isinstance(F, RcompUnits)
            check_mult_units_consistency_seq(Fs, R)
        self.Fs = Fs
        amap = ProductNMap(Fs, R)
        WrapAMap.__init__(self, amap, None)

    def solve_r(self, f):
        raise NotSolvableNeedsApprox(type(self))
    
    def get_lower_bound(self, n):
#         if len(self.Fs) != 2:
#             msg = ('ProductNDP:get_lower_bound(): Not implemented yet '
#                   'for %d components.' % len(self.Fs))
#             raise_desc(NotImplementedError, msg)
        if len(self.Fs) == 2:
            return Product2DP_L(self.Fs, self.R, n)
        else:
            return ProductNDP_L(self.Fs, self.R, n)

    def get_upper_bound(self, n):
        if len(self.Fs) == 2:
            return Product2DP_U(self.Fs, self.R, n)
        else:
            return ProductNDP_U(self.Fs, self.R, n)
#             msg = ('ProductNDP:get_upper_bound(): Not implemented yet '
#                   'for %d components.' % len(self.Fs))
#             raise_desc(NotImplementedError, msg)
         


class ProductNDP_L(WrapAMap):
    
    def __init__(self, Fs, R, nl):
        amap = ProductNMap(Fs, R)
        WrapAMap.__init__(self, amap, None)
        self.nl = nl
        
    def solve_r(self, r):
        raise NotImplementedError

class ProductNDP_U(WrapAMap):
    
    def __init__(self, Fs, R, nl):
        amap = ProductNMap(Fs, R)
        WrapAMap.__init__(self, amap, None)
        self.nl = nl
        
    def solve_r(self, r):
        raise NotImplementedError


class Product2DP_L(WrapAMap):
    
    @contract(Fs='tuple[2]')
    def __init__(self, Fs, R, nl):
        amap = ProductNMap(Fs, R)
        WrapAMap.__init__(self, amap, None)
        self.nl = nl
        
    def solve_r(self, r):  # @UnusedVariable
        msg = 'Product2DP_L:solve_r() not implemented'
        raise_desc(NotImplementedError, msg)

class Product2DP_U(WrapAMap):
    
    @contract(Fs='tuple[2]')
    def __init__(self, Fs, R, nu):
        amap = ProductNMap(Fs, R)
        WrapAMap.__init__(self, amap, None)
        self.nu = nu
        
    def solve_r(self, r):  
        # we want this to be pessimistic
        options = sample_sum_upperbound(self.R, self.F, r, self.nu)
        return self.L.Us(options)

class ProductNRcompDP(WrapAMap, ApproximableDP):
    
    def __init__(self, n):
        R = Rcomp()
        Fs = (R,) * n
        amap = ProductNMap(Fs, R)
        self.Fs = Fs
        WrapAMap.__init__(self, amap, None)

    def solve_r(self, f):
        raise NotSolvableNeedsApprox(type(self))
    
    def get_lower_bound(self, n):
        if len(self.Fs) != 2:
            msg = ('ProductNRcompDP:get_lower_bound(): Not implemented yet '
                  'for %d components.' % len(self.Fs))
            raise_desc(NotImplementedError, msg)
        return Product2RcompDP_L(n) 

    def get_upper_bound(self, n):
        if len(self.Fs) != 2:
            msg = ('ProductNRcompDP:get_upper_bound(): Not implemented yet '
                  'for %d components.' % len(self.Fs))
            raise_desc(NotImplementedError, msg)
        return Product2RcompDP_U(n) 
    
class Product2RcompDP_L(WrapAMap):
    
    def __init__(self, nl):
        R = Rcomp()
        Fs = (R,) * nl
        self.nl = nl
        mcdp_dev_warning('This is not even true - it is the complicated function')
        amap = ProductNMap(Fs, R)
        WrapAMap.__init__(self, amap, None)
        
    def solve_r(self, r):
        raise NotImplementedError

class Product2RcompDP_U(WrapAMap):
    
    def __init__(self, nu):
        R = Rcomp()
        Fs = (R,) * nu
        self.nl = nu
        mcdp_dev_warning('This is not even true - it is the complicated function')
        amap = ProductNMap(Fs, R)
        WrapAMap.__init__(self, amap, None)
        
    def solve_r(self, r):
        raise NotImplementedError
    
    
class ProductNNatDP(WrapAMap):
    """
        r >= f1 * f2 * ... * fn
    """
    def __init__(self, n):
        amap = ProductNNatMap(n)
        WrapAMap.__init__(self, amap, None)
        self.n = n

    def solve_r(self, r):
        if self.n > 2:
            msg = 'ProductNNatDP not implemented for n = %s.' % self.n
            raise_desc(NotImplementedError, msg, n=self.n)

        assert self.n == 2
        options = Nat_mult_antichain_Max(r)
        return self.F.Ls(options)
