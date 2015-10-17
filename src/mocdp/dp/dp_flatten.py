# -*- coding: utf-8 -*-
from .primitive import PrimitiveDP
from contracts import contract
from contracts.utils import check_isinstance
from mocdp import get_conftools_posets
from mocdp.posets import PosetProduct
from multi_index import get_it


__all__ = [
    'Flatten', 'Mux',
]


class Mux(PrimitiveDP):

    @contract(coords='seq(int|tuple|list)|int')
    def __init__(self, F, coords):
        library = get_conftools_posets()
        _, F = library.instance_smarter(F)
        R = get_R_from_F_coords(F, coords)

        self.coords = coords
        
        M = PosetProduct(())
        PrimitiveDP.__init__(self, F=F, R=R, M=M)

    def solve(self, func):
        self.F.belongs(func)

        r = get_it(func, self.coords, reduce_list=tuple)

        return self.R.U(r)

    def __repr__(self):
        return 'Mux(%r → %r, %s)' % (self.F, self.R, self.coords)

def get_R_from_F_coords(F, coords):
    return get_it(F, coords, reduce_list=PosetProduct)

def get_flatten_muxmap(F0):
    check_isinstance(F0, PosetProduct)
    coords = []
    for i, f in enumerate(F0.subs):
        if isinstance(f, PosetProduct):
            for j, x in enumerate(f.subs):
                coords.append((i, j))
        else:
            coords.append(i)
    return coords

class Flatten(Mux):
    def __init__(self, F):
        library = get_conftools_posets()
        _, F0 = library.instance_smarter(F)
        coords = get_flatten_muxmap(F0)
        Mux.__init__(self, F0, coords)

    def __repr__(self):
        return 'Flatten(%r→%r, %s)' % (self.F, self.R, self.coords)
