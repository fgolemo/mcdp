# -*- coding: utf-8 -*-
from .primitive import PrimitiveDP
from mocdp import get_conftools_posets
from mocdp.posets import PosetProduct, SpaceProduct
from contracts import contract
import functools


__all__ = [
    'Sum', 'SumN',
    'Product',
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

    @contract(n='int,>=1')
    def __init__(self, F, n):

        library = get_conftools_posets()
        _, F0 = library.instance_smarter(F)

        self.F0 = F0
        self.n = n

        F = PosetProduct((F0,) * n)
        R = F0

        M = SpaceProduct(())
        PrimitiveDP.__init__(self, F=F, R=R, M=M)

    def solve(self, func):
        self.F.belongs(func)

        r = functools.reduce(self.F0.add, func)

        return self.R.U(r)

    def __repr__(self):
        return 'Sum(%s, %r)' % (self.n, self.F0)


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
        mult = lambda x, y: x * y
        r = functools.reduce(mult, f)
        return self.R.U(r)

    def __repr__(self):
        return 'ProductN(%s -> %s)' % (self.F, self.R)


