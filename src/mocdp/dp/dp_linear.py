# -*- coding: utf-8 -*-
from .primitive import PrimitiveDP
from contracts import contract
from mocdp.posets import Rcomp
from mocdp.posets.poset_product import PosetProduct


__all__ = [
    'Linear',
]

class Linear(PrimitiveDP):

    @contract(a='float|int', F='$Rcomp|str|None', R='$Rcomp|str|None')
    def __init__(self, a, F=None, R=None):
        from mocdp import get_conftools_posets

        if F is None:
            F = Rcomp()
        if R is None:
            R = Rcomp()
        library = get_conftools_posets()
        _, F = library.instance_smarter(F)
        _, R = library.instance_smarter(R)
        self.a = float(a)

        M = PosetProduct(())
        PrimitiveDP.__init__(self, F=F, R=R, M=M)

    def solve(self, func):
        self.F.belongs(func)

        r = self.F.multiply(func, self.a)

        return self.R.U(r)

    def __repr__(self):
        return 'Linear(%r)' % self.F.format(self.a)


