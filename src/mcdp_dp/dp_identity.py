# -*- coding: utf-8 -*-
from contracts import contract
from mcdp_posets import Poset
from mcdp_posets.maps import IdentityMap

from .dp_generic_unary import WrapAMap


__all__ = [
    'Identity',
    'IdentityDP',
    'FunctionNode',
    'ResourceNode',
    'VariableNode',
]


class IdentityDP(WrapAMap):

    @contract(F=Poset)
    def __init__(self, F):
        amap = IdentityMap(F, F)
        amap_dual = IdentityMap(F, F)
        WrapAMap.__init__(self, amap, amap_dual)

    def __repr__(self):
        return 'Id(%r)' % self.F


class VariableNode(IdentityDP):
    def __init__(self, P, vname):
        IdentityDP.__init__(self, P)
        self.vname = vname
    def diagram_label(self):
        return self.vname

class ResourceNode(IdentityDP):
    pass

class FunctionNode(IdentityDP):
    pass

Identity = IdentityDP
