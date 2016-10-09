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
]


class IdentityDP(WrapAMap):

    @contract(F=Poset)
    def __init__(self, F):
        amap = IdentityMap(F, F)
        WrapAMap.__init__(self, amap)

    def __repr__(self):
        return 'Id(%r)' % self.F



class ResourceNode(IdentityDP):
    pass

class FunctionNode(IdentityDP):
    pass

#     class ResourceNode(OpaqueIdentity):
#         pass
#
#     class FunctionNode(OpaqueIdentity):
#         pass


Identity = IdentityDP
