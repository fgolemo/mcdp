# -*- coding: utf-8 -*-
import functools

from contracts import contract
from contracts.utils import check_isinstance, raise_wrapped, raise_desc
from mcdp_dp.primitive import NotSolvableNeedsApprox, ApproximableDP,\
    PrimitiveDP
from mcdp_posets import Map, Nat, PosetProduct, Rcomp, RcompUnits
from mcdp_posets.poset import is_top
from mocdp.exceptions import mcdp_dev_warning
import numpy as np

from .dp_generic_unary import WrapAMap


#
# __all__ = [
#     'Sum',
#     'SumN',
#     'SumNNat',
#     'SumNInt',
#     'Product',
#     'ProductN',
#     'SumUnitsNotCompatible',
#     'check_sum_units_compatible',
# ]
class SumNMap(Map):
    
    @contract(Fs='tuple, seq[>=2]($RcompUnits)', R=RcompUnits)
    def __init__(self, Fs, R):
        for _ in Fs:
            check_isinstance(_, RcompUnits)
        check_isinstance(R, RcompUnits)
        self.Fs = Fs
        self.R = R
        
        sum_dimensionality_works(Fs, R)
        
        dom = PosetProduct(self.Fs)
        cod = R

        Map.__init__(self, dom=dom, cod=cod)
        
    def _call(self, x):
        res = sum_units(self.Fs, x, self.R)
        return res
    
    def __repr__(self):
        return 'SumNMap(%s → %s)' % (self.dom, self.cod)
    
    
class SumNDP(WrapAMap, ApproximableDP):
    """
        f1, f2, f3 -> f1 + f2 +f3
    """
    def __init__(self, Fs, R):
        amap = SumNMap(Fs, R)
        
#         if len(Fs) == 2:
#             from mcdp_dp.dp_inv_plus import InvPlus2
#             amap_dual = InvPlus2(R, Fs)
#         else:
#         
        amap_dual = None
        WrapAMap.__init__(self, amap, amap_dual)
        self.Fs = Fs
        self.R = R
    
    def solve_r(self, r):  # @UnusedVariable
        if len(self.Fs) > 2:
            msg = 'Cannot invert more than two terms.'
            raise_desc(NotImplementedError, msg) 
        raise NotSolvableNeedsApprox()
    
    def get_lower_bound(self, n):
        return Sum2LDP(self.Fs, self.R, n)

    def get_upper_bound(self, n):
        return Sum2UDP(self.Fs, self.R, n)


class Sum2LDP():
    """
        f1, f2, f3 -> f1 + f2 +f3
        r -> ((a,b) | a + b = r}
    """
    def __init__(self, Fs, R, n):
        assert len(Fs) == 2
        self.n = n
        
        F = PosetProduct(Fs)
        M = PosetProduct((F, R))
        PrimitiveDP.__init__(self, F=F, R=R, I=M)
        
    def solve(self, f):
        from mcdp_dp.dp_inv_plus import InvPlus2
        from mcdp_dp.dp_inv_plus import van_der_corput_sequence
        
        if is_top(self.F, f):
            # +infinity
            top1 = self.R[0].get_top()
            top2 = self.R[1].get_top()
            s = set([(top1, 0.0), (0.0, top2)])
            return self.R.Us(s)

        n = self.n
        
        if InvPlus2.ALGO == InvPlus2.ALGO_VAN_DER_CORPUT:
            options = van_der_corput_sequence(n)
        elif InvPlus2.ALGO == InvPlus2.ALGO_UNIFORM:
            options = np.linspace(0.0, 1.0, n)
        else:
            assert False, InvPlus2.ALGO

        s = set()
        for o in options:
            s.add((f * o, f * (1 - o)))
        return self.R.Us(s)

    def solve_f(self, f):
        f1, f2 = f
        minr = self.F.add(f1, f2)
        return self.R.U(minr)


class SumNRcompMap(Map):
    """ Sum of Rcomp. """
    
    @contract(n='int,>=0')
    def __init__(self, n):
        P = Rcomp()
        dom = PosetProduct((P,)*n)
        cod = P
        self.n = n
        Map.__init__(self, dom, cod)
        
    def _call(self, x):
        res = sum(x)
        mcdp_dev_warning('overflow, underflow')
        return res

    def __repr__(self):
        return 'SumNRcompMap(%s)' % self.n

def sum_dimensionality_works(Fs, R):
    """ Raises ValueError if it is not possible to sum Fs to get R. """
    for Fi in Fs:
        check_isinstance(Fi, RcompUnits)
    check_isinstance(R, RcompUnits)

    for Fi in Fs:
        ratio = R.units / Fi.units
        try:
            float(ratio)
        except Exception as e: # pragma: no cover
            raise_wrapped(ValueError, e, 'Could not convert.', Fs=Fs, R=R)


# Fs: sequence of Rcompunits
def sum_units(Fs, values, R):
    for Fi in Fs:
        check_isinstance(Fi, RcompUnits)
    res = 0.0
    for Fi, x in zip(Fs, values):
        if Fi.equal(x, Fi.get_top()):
            return R.get_top()

        # reasonably sure this is correct...
        try:
            factor = 1.0 / float(R.units / Fi.units)
        except Exception as e:  # pragma: no cover (DimensionalityError)
            raise_wrapped(Exception, e, 'some error', Fs=Fs, R=R)

        res += factor * x

    if np.isinf(res):
        return R.get_top()

    return res

class ProductNMap(Map):

    @contract(Fs='tuple[>=2]')
    def __init__(self, Fs, R):
        for _ in Fs:
            check_isinstance(_, RcompUnits)
        check_isinstance(R, RcompUnits)

        self.F = dom = PosetProduct(Fs)
        self.R = cod = R
        Map.__init__(self, dom=dom, cod=cod)

    def _call(self, f):
        
        # first, find out if there are any tops
        def is_there_a_top():
            for Fi, fi in zip(self.F, f):
                if is_top(Fi, fi):
                    return True
            return False
        
        if is_there_a_top():
            return self.R.get_top()

        mult = lambda x, y: x * y
        try:
            r = functools.reduce(mult, f)
        except FloatingPointError as e:
            # assuming this is overflow
            assert 'overflow' in str(e)
            r = np.inf
        if np.isinf(r):
            r = self.R.get_top()
        return r

class ProductN(WrapAMap):

    @contract(Fs='tuple[>=2]')
    def __init__(self, Fs, R):
        amap = ProductNMap(Fs, R)
#         if len(Fs) == 2:
#             from mcdp_dp.dp_inv_mult import InvMult2
#             amap_dual = InvMult2(R, Fs)
#         else:
        amap_dual = None

        WrapAMap.__init__(self, amap, amap_dual)
        
    


class ProductNatN(Map):

    """ Multiplies several Nats together """

    @contract(n='int,>=2')
    def __init__(self, n):
        self.P = Nat()
        dom = PosetProduct( (self.P,) * n)
        cod = self.P
        Map.__init__(self, dom=dom, cod=cod)
        self.n = n
                     
    def _call(self, x):
        def is_there_a_top():
            for xi in x:
                if self.P.equal(self.P.get_top(), xi):
                    return True
            return False

        if is_there_a_top():
            return self.R.get_top()
        
        mult = lambda a, b : a * b
        r = functools.reduce(mult, x)
        mcdp_dev_warning('lacks overflow')
        return r

    def __repr__(self):
        return 'ProductNatN(%s)' % (self.n)


class MultValueMap(Map):
    """ multiplies by <value> """
    """ Implements _ -> _ * x on RCompUnits """
    def __init__(self, F, R, value):
        check_isinstance(F, RcompUnits)
        check_isinstance(R, RcompUnits)
        dom = F
        cod = R
        self.value = value
        Map.__init__(self, dom=dom, cod=cod)

    def _call(self, x):
        if is_top(self.dom, x):
            return self.cod.get_top()

        res = x * self.value

        if bool(np.isfinite(res)):
            return res
        else:
            return self.cod.get_top() 
