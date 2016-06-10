# -*- coding: utf-8 -*-
from .primitive import PrimitiveDP
from contracts import contract
from mcdp_posets import Poset  # @UnusedImport
from mcdp_posets import PosetProduct


__all__ = [
    'Constant',
]


class Constant(PrimitiveDP):

    @contract(R='$Poset|str|code_spec')
    def __init__(self, R, value):
        from mocdp import get_conftools_posets
        _, R = get_conftools_posets().instance_smarter(R)
        F = PosetProduct(())
        self.c = value
        M = PosetProduct(())
        PrimitiveDP.__init__(self, F=F, R=R, M=M)

    def solve(self, _):
        return self.R.U(self.c)

    def __repr__(self):
        return 'Constant(%s:%r)' % (self.R, self.c)


