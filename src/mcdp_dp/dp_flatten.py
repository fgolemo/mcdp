# -*- coding: utf-8 -*-
from contracts import contract
from contracts.utils import raise_wrapped
from mcdp_posets import Map, PosetProduct
from mocdp.exceptions import DPInternalError
from multi_index import get_it

from .dp_generic_unary import WrapAMap
from multi_index.inversion import transform_pretty_print,\
    transform_right_inverse, get_letter_proxy
from multi_index.get_it_test import is_iterable


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

    def repr_map(self, letter):
        if letter == 'f':
            start = 'a'
        else:
            start = 'A'
#                     
#         def transform_pretty_print2(P, coords, start_letter='a'):
#             proxy, _ = get_letter_proxy(P, start_letter)
#             transformed = get_it(proxy, coords, list)
#             def pretty(x):
#                 if is_iterable(x):
#                     m = [pretty(_) for _ in x]
#                     return '⟨' + ', '.join(m) + '⟩'
#                 else:
#                     return str(x)
#             t1 = pretty(proxy)
#             t2 = pretty(transformed)
#             s = 'here %s ⟼ %s' % (t1, t2)
#             return s

        return transform_pretty_print(self.dom, self.coords, start)
    
            
class Mux(WrapAMap):

    @contract(coords='seq(int|tuple|list)|int')
    def __init__(self, F, coords):
        self.amap_pretty = transform_pretty_print(F, coords)
        amap = MuxMap(F, coords)
        try:
            R, coords2 = transform_right_inverse(F, coords, PosetProduct)
        except:
            print('cannot invert {}'.format(self.amap_pretty))
            raise

#         print 'R', R
#         print 'coords2', coords2
        amap_dual = MuxMap(R, coords2)
        WrapAMap.__init__(self, amap, amap_dual)

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
        # Note that these always correspond to the identity!
        # Let's check
        n = len(coords)
        assert list(range(n)) == coords, coords
        
        amap = MuxMap(F, coords)
        amap_dual = MuxMap(F, coords)
        
        WrapAMap.__init__(self, amap, amap_dual)


class TakeRes(WrapAMap):
    """ Used by Context.ifun_get_index.
        Only used for having an appropriate icon (one green, many red). """
    def __init__(self, F, coords):
        # Note that these always correspond to the identity!
        # Let's check
        n = len(coords)
        assert list(range(n)) == coords, coords
        
        amap = MuxMap(F, coords)
        amap_dual = MuxMap(F, coords)
        
        WrapAMap.__init__(self, amap, amap_dual)


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
