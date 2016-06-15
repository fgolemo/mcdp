# -*- coding: utf-8 -*-
from .primitive import PrimitiveDP
from contracts import contract
from contracts.utils import check_isinstance, raise_wrapped
from mcdp_posets import (Int, Map, Nat, Poset, PosetProduct, Rcomp, RcompUnits,
    Space)  # @UnusedImport
from mcdp_posets import SpaceProduct, get_types_universe
# from mocdp import get_conftools_posets
import functools
import numpy as np



__all__ = [
    'Sum',
    'SumN',
    'SumNNat',
    'SumNInt',
    'Product',
    'ProductN',
#     'ProductNNat',
    'SumUnitsNotCompatible',
    'check_sum_units_compatible',
]

class Sum(PrimitiveDP):

    def __init__(self, F):
        F0 = F
#         library = get_conftools_posets()
#         _, F0 = library.instance_smarter(F)

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


class SumNNat(PrimitiveDP):
    @contract(Fs='tuple, seq[>=2]($Nat)', R=Nat)
    def __init__(self, Fs, R):
        for _ in Fs:
            check_isinstance(_, Nat)
        check_isinstance(R, Nat)
        self.Fs = Fs

        # todo: check dimensionality
        F = PosetProduct(self.Fs)
        R = R

        M = SpaceProduct(())
        PrimitiveDP.__init__(self, F=F, R=R, M=M)

    def solve(self, func):
        res = sum_nats(self.Fs, func, self.R)
        return self.R.U(res)

    def __repr__(self):
        return 'SumNNat(%s -> %s)' % (self.F, self.R)

class SumNInt(Map):
    """ Sum of many spaces that can be cast to Int, and  """
    @contract(Fs='tuple, seq[>=2]($Space)', R=Poset)
    def __init__(self, Fs, R):
        dom = PosetProduct(Fs)
        cod = R
        Map.__init__(self, dom=dom, cod=cod)
        
        tu = get_types_universe()
        self.subs = []
        target = Int()
        for F in Fs:
            # need F to be cast to Int
            F_to_Int, _ = tu.get_embedding(F, target)
            self.subs.append(F_to_Int)

        self.to_R, _ = tu.get_embedding(target, R)
        
    def _call(self, x):
        res = 0
        target = Int()
        for xe, s in zip(x, self.subs):
            xe_int = s(xe)
            res = target.add(res, xe_int)
        r = self.to_R(res)
        return r
    

class SumN(PrimitiveDP):
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

        M = SpaceProduct(())
        PrimitiveDP.__init__(self, F=F, R=R, M=M)


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
            return  R.get_top()

        # reasonably sure this is correct...
        try:
            factor = 1.0 / float(R.units / Fi.units)
        except Exception as e:  # DimensionalityError
            raise_wrapped(Exception, e, 'some error', Fs=Fs, R=R)

        res += factor * x

    if np.isinf(res):
        return R.get_top()

    return res


# Fs: sequence of Rcompunits
def sum_nats(Fs, values, R):
    for _ in Fs:
        assert isinstance(_, Nat)
    assert isinstance(R, Nat)
    res = 0
    for Fi, x in zip(Fs, values):
        if Fi.equal(x, Fi.get_top()):
            return R.get_top()
        assert isinstance(x, int), x
    
        # reasonably sure this is correct...
        # factor = 1.0 / float(R.units / Fi.units)
        factor = 1
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
#         library = get_conftools_posets()
        self.F1 = F1
        self.F2 = F2
#         _, self.F1 = library.instance_smarter(F1)
#         _, self.F2 = library.instance_smarter(F2)
#         _, R = library.instance_smarter(R)

        F = PosetProduct((F1, F2))

        M = SpaceProduct(())
        PrimitiveDP.__init__(self, F=F, R=R, M=M)

    def solve(self, func):
        f1, f2 = func

        r = self.F1.multiply(f1, f2)

        return self.R.U(r)

    def __repr__(self):
        return 'Product(%r×%r→%r)' % (self.F1, self.F2, self.R)

class ProductN(PrimitiveDP):

    @contract(Fs='tuple[>=2]')
    def __init__(self, Fs, R):
        for _ in Fs:
            check_isinstance(_, RcompUnits)
        check_isinstance(R, RcompUnits)
        F = PosetProduct(Fs)
        M = SpaceProduct(())
        PrimitiveDP.__init__(self, F=F, R=R, M=M)

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
        r = functools.reduce(mult, f)
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


