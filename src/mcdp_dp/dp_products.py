# -*- coding: utf-8 -*-
from contracts import contract
from contracts.utils import raise_desc, check_isinstance
from mcdp_dp.dp_inv_mult import invmultU_solve_options, invmultL_solve_options
from mcdp_dp.repr_strings import repr_hd_map_productn
from mcdp_dp.sequences_invplus import Nat_mult_antichain_Max
from mcdp_maps import ProductNMap, ProductNNatMap
from mcdp_posets import Rcomp, RcompUnits
from mcdp_posets.rcomp_units import check_mult_units_consistency_seq
from mcdp.exceptions import mcdp_dev_warning

from .dp_generic_unary import WrapAMap
from .dp_inv_mult import  InvMult2
from .primitive import NotSolvableNeedsApprox, ApproximableDP


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
        if len(self.Fs) == 2:
            return Product2DP_L(self.Fs, self.R, n)
        else: 
#             msg = 'Lower bound for n>=2 not implemented.'
#             raise_desc(DPNotImplementedError, msg, Fs=self.Fs) 
            # note 'N' not 2
            return ProductNDP_L(self.Fs, self.R, n)

    def get_upper_bound(self, n):
        if len(self.Fs) == 2:
            return Product2DP_U(self.Fs, self.R, n)
        else:
#             msg = 'Upper bound for n>=2 not implemented.'
#             raise_desc(DPNotImplementedError, msg, Fs=self.Fs)

            # note 'N' not 2 
            return ProductNDP_U(self.Fs, self.R, n) 
         
    def repr_hd_map(self):
        n = len(self.Fs)
        return repr_hd_map_productn(n)


class ProductNDP_L(WrapAMap):
    
    def __init__(self, Fs, R, nl):
        amap = ProductNMap(Fs, R)
        WrapAMap.__init__(self, amap, None)
        self.nl = nl
        
    def solve_r(self, r):  # @UnusedVariable
        msg = 'ProductNDP_L(%s, %s):solve_r()' % (self.F, self.nl)
        raise_desc(NotImplementedError, msg)
        
    def repr_hd_map(self):
        return repr_hd_map_productn(2, 'L', self.nl)

class ProductNDP_U(WrapAMap):
    
    def __init__(self, Fs, R, nl):
        amap = ProductNMap(Fs, R)
        WrapAMap.__init__(self, amap, None)
        self.nl = nl #XXX
        
    def solve_r(self, r):  # @UnusedVariable
        msg = 'ProductNDP_U(%s, %s):solve_r()' % (self.F, self.nl)
        raise_desc(NotImplementedError, msg)

    def repr_hd_map(self):
        return repr_hd_map_productn(2, 'U', self.nl)

class Product2DP_L(WrapAMap):
    
    @contract(Fs='tuple[2]')
    def __init__(self, Fs, R, nl):
        amap = ProductNMap(Fs, R)
        WrapAMap.__init__(self, amap, None)
        self.nl = nl
        
    def solve_r(self, r):  # @UnusedVariable
        algo = InvMult2.ALGO
        mcdp_dev_warning('Not sure about this: is it L or U?')
        options = invmultU_solve_options(F=self.R, R=self.F, f=r, n=self.nl, algo=algo)
        return self.F.Ls(options)
    
    def repr_hd_map(self):
        return repr_hd_map_productn(2, 'L')

class Product2DP_U(WrapAMap):
    
    @contract(Fs='tuple[2]')
    def __init__(self, Fs, R, nu):
        amap = ProductNMap(Fs, R)
        WrapAMap.__init__(self, amap, None)
        self.nu = nu
        
    def solve_r(self, r):  
        # we want this to be pessimistic
        mcdp_dev_warning('Not sure about this: is it L or U?')
        algo = InvMult2.ALGO
        options = invmultL_solve_options(F=self.R, R=self.F, f=r, n=self.nu, algo=algo)
        return self.F.Ls(options)
    
    
    def repr_hd_map(self):
        return repr_hd_map_productn(2, 'U')

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
        if len(self.Fs) == 2:
            return Product2RcompDP_L(n)
        else:
            return ProductNRcompDP_L(len(self.Fs), nl=n)

    def get_upper_bound(self, n):
        if len(self.Fs) == 2:
            return Product2RcompDP_U(n)
        else:
            return ProductNRcompDP_U(len(self.Fs), nu=n) 
        
    
    def repr_hd_map(self):
        return repr_hd_map_productn(len(self.F))
    
class ProductNRcompDP_L(WrapAMap):
    
    def __init__(self, n, nl):
        R = Rcomp()
        Fs = (R,) * n
        amap = ProductNMap(Fs, R)
        self.Fs = Fs
        WrapAMap.__init__(self, amap, None)
        self.nl = nl

    def solve_r(self, f):  # @UnusedVariable
        msg = 'ProductNRcompDP_L(%s, %s):solve_r()' % (self.Fs, self.nl)
        raise_desc(NotImplementedError, msg)
        
    def repr_hd_map(self):
        return repr_hd_map_productn(len(self.F), 'L', self.nl)

class ProductNRcompDP_U(WrapAMap):
    
    def __init__(self, n, nu):
        R = Rcomp()
        Fs = (R,) * n
        amap = ProductNMap(Fs, R)
        self.Fs = Fs
        WrapAMap.__init__(self, amap, None)
        self.nu = nu

    def solve_r(self, f):  # @UnusedVariable
        msg = 'ProductNRcompDP_U(%s, %s):solve_r()' % (self.Fs, self.nl)
        raise_desc(NotImplementedError, msg)
        
    def repr_hd_map(self):
        return repr_hd_map_productn(len(self.F), 'U', self.nu)
    
class Product2RcompDP_L(WrapAMap):
    
    def __init__(self, nl):
        R = Rcomp()
        Fs = (R, R)
        self.nl = nl
        mcdp_dev_warning('This is not even true - it is the complicated function')
        amap = ProductNMap(Fs, R)
        WrapAMap.__init__(self, amap, None)
        
    def solve_r(self, r):  # @UnusedVariable
        mcdp_dev_warning('Not sure about this')
        algo = InvMult2.ALGO
        options = invmultU_solve_options(F=self.R, R=self.F, f=r, n=self.nl, algo=algo)
        return self.F.Ls(options)

    def repr_hd_map(self):
        return repr_hd_map_productn(2, 'L', self.nl)
    
class Product2RcompDP_U(WrapAMap):
    
    def __init__(self, nu):
        R = Rcomp()
        Fs = (R, R)
        self.nl = nu
        mcdp_dev_warning('This is not even true - it is the complicated function')
        amap = ProductNMap(Fs, R)
        WrapAMap.__init__(self, amap, None)
        
    def solve_r(self, r):  # @UnusedVariable
        mcdp_dev_warning('Not sure about this')
        algo = InvMult2.ALGO
        options = invmultL_solve_options(F=self.R, R=self.F, f=r, n=self.nl, algo=algo)
        return self.F.Ls(options)

    def repr_hd_map(self):
        return repr_hd_map_productn(2, 'U', self.nl)

    
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
    
    def repr_hd_map(self):
        return repr_hd_map_productn(self.n)

