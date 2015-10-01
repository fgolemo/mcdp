# -*- coding: utf-8 -*-
from .primitive import PrimitiveDP
from contracts import contract
from mocdp.posets import Poset  # @UnusedImport


__all__ = [
    'Identity',
]

class Identity(PrimitiveDP):

    @contract(F='$Poset|str|code_spec')
    def __init__(self, F):
        from mocdp import get_conftools_posets
        _, F = get_conftools_posets().instance_smarter(F)
        R = F
        PrimitiveDP.__init__(self, F=F, R=R)


    def solve(self, f):
        self.F.belongs(f)
        return self.R.U(f)

    def __repr__(self):
        return 'Id(%r)' % self.F


