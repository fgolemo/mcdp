# -*- coding: utf-8 -*-
import functools

from contracts import contract
from contracts.utils import check_isinstance, raise_wrapped
from mcdp_posets import Map, Nat, PosetProduct, Rcomp, RcompUnits
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
        return self.R.U(res)
    
    def __repr__(self):
        return 'SumNMap(%s -> %s)' % (self.dom, self.cod)
    
    
class SumNDP(WrapAMap):
    
    def __init__(self, Fs, R):
        amap = SumNMap(Fs, R)
        WrapAMap.__init__(self, amap)
#         
#     
# class SumN_old(EmptyDP):
#     """ Sum of real values with units. """
#     @contract(Fs='tuple, seq[>=2]($RcompUnits)', R=RcompUnits)
#     def __init__(self, Fs, R):
#         for _ in Fs:
#             check_isinstance(_, RcompUnits)
#         check_isinstance(R, RcompUnits)
#         self.Fs = Fs
# 
#         # todo: check dimensionality
#         F = PosetProduct(self.Fs)
#         R = R
# 
#         EmptyDP.__init__(self, F=F, R=R)
#         sum_dimensionality_works(Fs, R)
# 
#     def solve(self, func):
#         # self.F.belongs(func)
#         res = sum_units(self.Fs, func, self.R)
#         return self.R.U(res)
# 
#     def __repr__(self):
#         return 'SumN(%s -> %s)' % (self.F, self.R)

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
                if Fi.leq(Fi.get_top(), fi):
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
        WrapAMap.__init__(self, amap)
        
#         
# class ProductN_old(EmptyDP):
# 
#     @contract(Fs='tuple[>=2]')
#     def __init__(self, Fs, R):
#         if do_extra_checks():
#             for _ in Fs:
#                 check_isinstance(_, RcompUnits)
#             check_isinstance(R, RcompUnits)
# 
#         F = PosetProduct(Fs)
#         EmptyDP.__init__(self, F=F, R=R)
# 
#     def solve(self, f):
#         # first, find out if there are any tops
#         def is_there_a_top():
#             for Fi, fi in zip(self.F, f):
#                 if Fi.leq(Fi.get_top(), fi):
#                     return True
#             return False
#         
#         if is_there_a_top():
#             return self.R.U(self.R.get_top())
# 
#         mult = lambda x, y: x * y
#         try:
#             r = functools.reduce(mult, f)
#         except FloatingPointError as e:
#             # assuming this is overflow
#             assert 'overflow' in str(e)
#             r = np.inf
#         if np.isinf(r):
#             r = self.R.get_top()
#         return self.R.U(r)
# 
#     def __repr__(self):
#         return 'ProductN(%s -> %s)' % (self.F, self.R)



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
            return self.R.U(self.R.get_top())
        
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
        if self.dom.equal(x, self.dom.get_top()):
            return self.cod.get_top()

        res = x * self.value

        if bool(np.isfinite(res)):
            return res
        else:
            return self.cod.get_top() 
