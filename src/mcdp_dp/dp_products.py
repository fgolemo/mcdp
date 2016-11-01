# -*- coding: utf-8 -*-
from contracts import contract
from mcdp_maps import ProductNMap, ProductNNatMap

from .dp_generic_unary import WrapAMap
from mcdp_posets.rcomp import Rcomp


__all__ = [
    'ProductNDP',
    'ProductNNatDP',
    'ProductNRcompDP',
]

class ProductNDP(WrapAMap):
    @contract(Fs='tuple[>=2]')
    def __init__(self, Fs, R):
        amap = ProductNMap(Fs, R)
#         if len(Fs) == 2:
#             from mcdp_dp.dp_inv_mult import InvMult2
#             amap_dual = InvMult2(R, Fs)
#         else:
        amap_dual = None

        WrapAMap.__init__(self, amap, amap_dual)

class ProductNRcompDP(WrapAMap):
    
    def __init__(self, n):
        R = Rcomp()
        Fs = (R,)*n
        amap = ProductNMap(Fs, R)
        amap_dual = None
        WrapAMap.__init__(self, amap, amap_dual)

class ProductNNatDP(WrapAMap):
    def __init__(self, n):
        amap = ProductNNatMap(n)
        amap_dual = None
        WrapAMap.__init__(self, amap, amap_dual)

