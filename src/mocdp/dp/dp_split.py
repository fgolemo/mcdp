# -*- coding: utf-8 -*-
from .primitive import PrimitiveDP
from mocdp import get_conftools_posets
from mocdp.posets import PosetProduct


__all__ = [
    'Split',
]

class Split(PrimitiveDP):

    def __init__(self, F):
        library = get_conftools_posets()
        _, F0 = library.instance_smarter(F)

        self.R = PosetProduct((F0, F0))
        self.F = F0

    def get_fun_space(self):
        return self.F

    def get_res_space(self):
        return self.R

    def solve(self, func):
        self.F.belongs(func)

        r = (func, func)

        return self.R.U(r)

    def __repr__(self):
        return 'Split(%r)' % self.F


