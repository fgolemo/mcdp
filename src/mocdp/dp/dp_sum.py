# -*- coding: utf-8 -*-
from .primitive import PrimitiveDP
from mocdp import get_conftools_posets
from mocdp.posets import PosetProduct


__all__ = [
    'Sum',
    'Product',
]

class Sum(PrimitiveDP):

    def __init__(self, F):
        library = get_conftools_posets()
        _, F0 = library.instance_smarter(F)

        self.F = PosetProduct((F0, F0))
        self.R = F0
        self.F0 = F0

    def get_fun_space(self):
        return self.F

    def get_res_space(self):
        return self.R

    def solve(self, func):
        self.F.belongs(func)

        f1, f2 = func

        r = self.F0.add(f1, f2)

        return self.R.U(r)

    def __repr__(self):
        return 'Sum(%r)' % self.F0



class Product(PrimitiveDP):

    def __init__(self, F1, F2, R):
        library = get_conftools_posets()
        _, self.F1 = library.instance_smarter(F1)
        _, self.F2 = library.instance_smarter(F2)
        _, self.R = library.instance_smarter(R)

        self.F = PosetProduct((F1, F2))

    def get_fun_space(self):
        return self.F

    def get_res_space(self):
        return self.R

    def solve(self, func):
        self.F.belongs(func)

        f1, f2 = func

        r = self.F1.multiply(f1, f2)

        return self.R.U(r)

    def __repr__(self):
        return 'Multiply(%rx%r->%r)' % (self.F1, self.F2, self.R)


