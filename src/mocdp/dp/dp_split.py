# -*- coding: utf-8 -*-
from .primitive import PrimitiveDP
from mocdp import get_conftools_posets
from mocdp.exceptions import mcdp_dev_warning
from mocdp.posets import PosetProduct
from mocdp.posets.space_product import SpaceProduct


__all__ = [
    'Split',
]

class Split(PrimitiveDP):

    def __init__(self, F):
        mcdp_dev_warning('Replace by Mux')
        library = get_conftools_posets()
        _, F0 = library.instance_smarter(F)

        R = PosetProduct((F0, F0))
        F = F0

        M = SpaceProduct(())
        PrimitiveDP.__init__(self, F=F, R=R, M=M)

    def solve(self, func):
        r = (func, func)
        return self.R.U(r)

    def __repr__(self):
        return 'Split(%r)' % self.F


