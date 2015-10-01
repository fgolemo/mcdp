# -*- coding: utf-8 -*-
from .primitive import PrimitiveDP
from mocdp import get_conftools_posets
from mocdp.posets import PosetProduct
from contracts.utils import check_isinstance
from contracts import contract


__all__ = [
    'Flatten', 'Mux',
]


class Mux(PrimitiveDP):

    @contract(coords='seq(int|tuple|list)')
    def __init__(self, F, coords):
        library = get_conftools_posets()
        _, F = library.instance_smarter(F)
        R = get_R_from_F_coords(F, coords)

        self.coords = coords
        

        PrimitiveDP.__init__(self, F=F, R=R)

    def solve(self, func):
        self.F.belongs(func)

        r = get_it(func, self.coords, reduce_list=tuple)

        return self.R.U(r)

    def __repr__(self):
        return 'Mux(%r -> %r, %s)' % (self.F, self.R, self.coords)

def get_R_from_F_coords(F, coords):
    return get_it(F, coords, reduce_list=PosetProduct)

def get_flatten_muxmap(F0):
    check_isinstance(F0, PosetProduct)
    coords = []
#     rs = []
    for i, f in enumerate(F0.subs):
        if isinstance(f, PosetProduct):
            for j, x in enumerate(f.subs):
#                 rs.append(x)
                coords.append((i, j))
        else:
#             rs.append(f)
            coords.append(i)

#     R_ = PosetProduct(tuple(rs))
    

#     assert (R == R_), (R, R_)
    
#     return R, coords
    return coords


def show(f):

    def ff(seq, coords, reduce_list):
#         print('get_it(%s, %s)' % (seq, coords))
        r = f(seq, coords, reduce_list)
#         print(' =>  %s' % r.__repr__())
        return r
    return ff

@show
@contract(coords='tuple|int|list')
def get_it(seq, coords, reduce_list):
    """
        ['a', ['b', 'c']]
        
        () => ['a', ['b', 'c']]
        [(), ()] => reduce([['a', ['b', 'c']], ['a', ['b', 'c']]])
        [0, (1, 1)] => ['a', 'c']
    
    """



    if coords == ():
        return seq
    if isinstance(coords, list):
        subs = [get_it(seq, c, reduce_list=reduce_list) for c in coords]
        R = reduce_list(subs)
        return R

    if isinstance(coords, int):
        return seq[coords]

    assert isinstance(coords, tuple) and len(coords) >= 1, coords
    a = coords[0]
    r = coords[1:]
    assert isinstance(a, int)
    if r:
        s = seq[a]
        assert isinstance(r, tuple)
        return get_it(s, r, reduce_list=reduce_list)
    else:
        assert isinstance(a, int)
        return seq[a]
    



class Flatten(Mux):
    def __init__(self, F):
        library = get_conftools_posets()
        _, F0 = library.instance_smarter(F)
        coords = get_flatten_muxmap(F0)
        Mux.__init__(self, F0, coords)

    def __repr__(self):
        return 'Flatten(%r -> %r, %s)' % (self.F, self.R, self.coords)
