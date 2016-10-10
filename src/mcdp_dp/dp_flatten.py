# -*- coding: utf-8 -*-
from contracts import contract
from contracts.utils import raise_wrapped
from mcdp_posets import Map, PosetProduct
from mocdp.exceptions import DPInternalError
from multi_index import get_it

from .dp_generic_unary import WrapAMap


__all__ = [
    'Mux',
    'MuxMap',
    'TakeFun',
    'TakeRes',
]

class MuxMap(Map):
    def __init__(self, F, coords):
        try:
            R = get_R_from_F_coords(F, coords)
        except ValueError as e: # pragma: no cover
            msg = 'Cannot create Mux'
            raise_wrapped(DPInternalError, e, msg, F=F, coords=coords)

        self.coords = coords
        Map.__init__(self, F, R)

    def _call(self, x):
        r = get_it(x, self.coords, reduce_list=tuple)
        return r


class Mux(WrapAMap):

    @contract(coords='seq(int|tuple|list)|int')
    def __init__(self, F, coords):

        self.amap = MuxMap(F, coords)

        WrapAMap.__init__(self, self.amap)

        # This is used by many things (e.g. series simplification)
        self.coords = coords

    def __repr__(self):
        return 'Mux(%r → %r, %s)' % (self.F, self.R, self.coords)

    def repr_long(self):
        s = 'Mux(%r -> %r, %s)    I = %s' % (self.F, self.R,
                                             self.amap.coords.__repr__(), self.get_imp_space())
        return s

class TakeFun(WrapAMap):
    """ used by Context.ires_get_index 
    
        Only used for having an appropriate icon (one red, many green)
    """
    def __init__(self, F, coords):
        amap = MuxMap(F, coords)
        WrapAMap.__init__(self, amap)


class TakeRes(WrapAMap):
    """ Used by Context.ifun_get_index.
        Only used for having an appropriate icon (one green, many red). """
    def __init__(self, F, coords):
        amap = MuxMap(F, coords)
        WrapAMap.__init__(self, amap)


def get_R_from_F_coords(F, coords):
    return get_it(F, coords, reduce_list=PosetProduct)

# def get_flatten_muxmap(F0):
#     check_isinstance(F0, PosetProduct)
#     coords = []
#     for i, f in enumerate(F0.subs):
#         if isinstance(f, PosetProduct):
#             for j, _ in enumerate(f.subs):
#                 coords.append((i, j))
#         else:
#             coords.append(i)
#     return coords
