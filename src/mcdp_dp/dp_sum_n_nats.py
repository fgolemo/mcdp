# -*- coding: utf-8 -*-
from contracts import contract
from contracts.utils import check_isinstance
from mcdp_maps import SumNatsN
from mcdp_posets import Nat

from .dp_generic_unary import WrapAMap


__all__ = [
    'SumNNat',
]


class SumNNat(WrapAMap):

    @contract(Fs='tuple, seq[>=2]($Nat)', R=Nat)
    def __init__(self, Fs, R):
        for _ in Fs:
            check_isinstance(_, Nat)
        check_isinstance(R, Nat)

        self.n = len(Fs)
        amap = SumNatsN(self.n)
        WrapAMap.__init__(self, amap)

#     def solve_r(self, r):
#         
#         
        
    def __repr__(self):
        return 'SumNNat(%s)' % (self.n)
