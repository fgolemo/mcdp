# -*- coding: utf-8 -*-
from .primitive import PrimitiveDP
from contracts import contract
from mocdp import get_conftools_posets
from mocdp.posets import PosetProduct, SpaceProduct
from mocdp.posets.rcomp_units import RcompUnits
import functools


__all__ = [
    'Sum',
    'SumN',
    'Product',
    'ProductN',
    'SumUnitsNotCompatible',
    'check_sum_units_compatible',
]

class Sum(PrimitiveDP):

    def __init__(self, F):
        library = get_conftools_posets()
        _, F0 = library.instance_smarter(F)

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


class SumN(PrimitiveDP):

    @contract(Fs='tuple, seq[>=2]($RcompUnits)', R=RcompUnits)
    def __init__(self, Fs, R):

        self.Fs = Fs

        # todo: check dimensionality
        F = PosetProduct(self.Fs)
        R = R

        M = SpaceProduct(())
        PrimitiveDP.__init__(self, F=F, R=R, M=M)

    def solve(self, func):
        self.F.belongs(func)
        
        res = 0.0
        for Fi, x in zip(self.Fs, func):
            # reasonably sure this is correct...
            factor = 1.0 / float(self.R.units / Fi.units)
            res += factor * x

        return self.R.U(res)

    def __repr__(self):
        return 'SumN(%s -> %s)' % (self.F, self.R)

class SumUnitsNotCompatible(Exception):
    pass

@contract(Fs='tuple, seq[>=2]($RcompUnits)')
def check_sum_units_compatible(Fs):
    """
    
        raises SumUnitsNotCompatible
    """
    F0 = Fs[0]
    errors = []
    for i, F in enumerate(Fs):
        
        try: 
            F.units + F0.units
        except ValueError as e:
            errors.append(e)
        except BaseException as e:
            print(e)
            
    if errors:
        msg = "Units not compatible: "
        msg += '\n' + "\n".join(str(e) for e in errors)
        raise SumUnitsNotCompatible(msg)




class Product(PrimitiveDP):

    def __init__(self, F1, F2, R):
        library = get_conftools_posets()
        _, self.F1 = library.instance_smarter(F1)
        _, self.F2 = library.instance_smarter(F2)
        _, R = library.instance_smarter(R)

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

    @contract(Fs='tuple')
    def __init__(self, Fs, R):
        F = PosetProduct(Fs)
        M = SpaceProduct(())
        PrimitiveDP.__init__(self, F=F, R=R, M=M)

    def solve(self, f):
        self.F.belongs(f)
        # print self.F, f

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
        return self.R.U(r)

    def __repr__(self):
        return 'ProductN(%s -> %s)' % (self.F, self.R)


