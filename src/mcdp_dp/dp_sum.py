# -*- coding: utf-8 -*-
from .primitive import PrimitiveDP
from contracts import contract
from contracts.utils import check_isinstance, raise_wrapped
from mcdp_dp.primitive import EmptyDP
from mcdp_posets import Map, Nat, PosetProduct, Rcomp, RcompUnits, SpaceProduct
from mocdp.exceptions import do_extra_checks
import functools
import numpy as np

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

class Sum(PrimitiveDP):

    def __init__(self, F):
        F0 = F
        F = PosetProduct((F0, F0))
        R = F0
        self.F0 = F0

        M = SpaceProduct(())
        PrimitiveDP.__init__(self, F=F, R=R, M=M)

    def solve(self, func):
        self.F.belongs(func)

        f1, f2 = func

        r = self.F0.add(f1, f2)

        return self.R.U(r)

    def __repr__(self):
        return 'Sum(%r)' % self.F0


class SumN(EmptyDP):
    """ Sum of real values with units. """
    @contract(Fs='tuple, seq[>=2]($RcompUnits)', R=RcompUnits)
    def __init__(self, Fs, R):
        for _ in Fs:
            check_isinstance(_, RcompUnits)
        check_isinstance(R, RcompUnits)
        self.Fs = Fs

        # todo: check dimensionality
        F = PosetProduct(self.Fs)
        R = R


        EmptyDP.__init__(self, F=F, R=R)
        sum_dimensionality_works(Fs, R)

    def solve(self, func):
        # self.F.belongs(func)
        res = sum_units(self.Fs, func, self.R)
        return self.R.U(res)

    def __repr__(self):
        return 'SumN(%s -> %s)' % (self.F, self.R)

def sum_dimensionality_works(Fs, R):
    """ Raises ValueError if it is not possible to sum Fs to get R. """
    for Fi in Fs:
        check_isinstance(Fi, RcompUnits)
    check_isinstance(R, RcompUnits)

    for Fi in Fs:
        ratio = R.units / Fi.units
        try:
            float(ratio)
        except Exception as e:
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
        except Exception as e:  # DimensionalityError
            raise_wrapped(Exception, e, 'some error', Fs=Fs, R=R)

        res += factor * x

    if np.isinf(res):
        return R.get_top()

    return res


class SumUnitsNotCompatible(Exception):
    pass

@contract(Fs='tuple, seq[>=2]($RcompUnits)')
def check_sum_units_compatible(Fs):
    """
    
        raises SumUnitsNotCompatible
    """
    F0 = Fs[0]
    errors = []
    for F in Fs:
        
        try: 
            F.units + F0.units
        except ValueError as e:
            errors.append(e)
        except BaseException as e:
            raise
            
    if errors:
        msg = "Units not compatible: "
        msg += '\n' + "\n".join(str(e) for e in errors)
        raise SumUnitsNotCompatible(msg)


class Product(PrimitiveDP):

    def __init__(self, F1, F2, R):
        self.F1 = F1
        self.F2 = F2

        F = PosetProduct((F1, F2))

        M = SpaceProduct(())
        PrimitiveDP.__init__(self, F=F, R=R, M=M)

    def solve(self, func):
        f1, f2 = func

        r = self.F1.multiply(f1, f2)

        return self.R.U(r)

    def __repr__(self):
        return 'Product(%r×%r→%r)' % (self.F1, self.F2, self.R)

class ProductN(EmptyDP):

    @contract(Fs='tuple[>=2]')
    def __init__(self, Fs, R):
        if do_extra_checks():
            for _ in Fs:
                check_isinstance(_, RcompUnits)
            check_isinstance(R, RcompUnits)

        F = PosetProduct(Fs)
        EmptyDP.__init__(self, F=F, R=R)

    def solve(self, f):
        # first, find out if there are any tops
        def is_there_a_top():
            for Fi, fi in zip(self.F, f):
                if Fi.leq(Fi.get_top(), fi):
                    return True
            return False
        if is_there_a_top():
            return self.R.U(self.R.get_top())

        mult = lambda x, y: x * y
        try:
            r = functools.reduce(mult, f)
        except FloatingPointError as e:
            # assuming this is overflow
            assert 'overflow' in str(e)
            r = np.inf
        if np.isinf(r):
            r = self.R.get_top()
        return self.R.U(r)

    def __repr__(self):
        return 'ProductN(%s -> %s)' % (self.F, self.R)


class ProductMap(Map):
    
    def __init__(self, Fs, R):
        for _ in Fs:
            check_isinstance(_, (Nat, Rcomp))
        check_isinstance(R, (Nat, Rcomp))
        self.Fs = Fs
        self.R = R

        dom = PosetProduct(Fs)
        cod = PosetProduct(R)
        Map.__init__(self, dom=dom, cod=cod)

    def _call(self, x):
        def is_there_a_top():
            for Fi, fi in zip(self.Fs, x):
                if Fi.equal(Fi.get_top(), fi):
                    return True
            return False
        if is_there_a_top():
            return self.R.U(self.R.get_top())
        # float
        res = 1.0
        for fi in x:  # Fi, fi in zip(self.Fs, x):
            res = res * fi
        finite = bool(np.isfinite(res))
        if isinstance(self.R, Nat):
            if finite:
                return int(np.ceil(res))
            else:
                return self.R.top()
        if isinstance(self.R, Rcomp):
            if finite:
                return res
            else:
                return self.R.top()


