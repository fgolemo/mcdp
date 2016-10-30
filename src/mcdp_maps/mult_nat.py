# -*- coding: utf-8 -*-
from contracts import contract
from mcdp_posets import Map, Nat
from mcdp_posets.nat import Nat_mult_uppersets_continuous


__all__ = ['MultNat']

class MultNat(Map):

    @contract(value=int)
    def __init__(self, value):
        self.value = value
        self.N = Nat()
        Map.__init__(self, dom=self.N, cod=self.N)

    def _call(self, x):
        return Nat_mult_uppersets_continuous(self.value, x)
#         if self.N.equal(self.N.get_top(), x):
#             return x
#         # TODO: check
#         res = x * self.value
#         assert isinstance(res, int), res
#         return res
