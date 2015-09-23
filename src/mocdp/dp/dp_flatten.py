# -*- coding: utf-8 -*-
from .primitive import PrimitiveDP
from mocdp import get_conftools_posets
from mocdp.posets import PosetProduct
from contracts.utils import check_isinstance
from contracts import contract


__all__ = [
    'Flatten',
]


class Mux(PrimitiveDP):

    @contract(coords='seq(int|tuple(int,int))')
    def __init__(self, F, R, coords):
        self.F = F
        self.R = R
        self.coords = coords
        
    def get_fun_space(self):
        return self.F

    def get_res_space(self):
        return self.R

    def solve(self, func):
        self.F.belongs(func)
        def extract(c):
            if isinstance(c, tuple):
                return func[c[0]][c[1]]
            else:
                return func[c]

        r = tuple(map(extract, self.coords))

        return self.R.U(r)

    def __repr__(self):
        return 'Mux(%r -> %r, %s)' % (self.F, self.R, self.coords)


def get_flatten_muxmap(F0):
    check_isinstance(F0, PosetProduct)
    coords = []
    rs = []
    for i, f in enumerate(F0.subs):
        if isinstance(f, PosetProduct):
            for j, x in enumerate(f.subs):
                rs.append(x)
                coords.append((i, j))
        else:
            rs.append(f)
            coords.append(i)

    R = PosetProduct(tuple(rs))
    coords = tuple(coords)
    return R, coords

class Flatten(Mux):
    def __init__(self, F):
        library = get_conftools_posets()
        _, F0 = library.instance_smarter(F)
        R, coords = get_flatten_muxmap(F0)
        Mux.__init__(self, F0, R, coords)

    def __repr__(self):
        return 'Flatten(%r -> %r, %s)' % (self.F, self.R, self.coords)
