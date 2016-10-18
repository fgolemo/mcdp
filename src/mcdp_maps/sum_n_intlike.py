# -*- coding: utf-8 -*-
from contracts import contract
from mcdp_posets import Int, Map, Poset, PosetProduct, Space, get_types_universe


_ = Space

__all__ = [
    'SumNInt',
]

class SumNInt(Map):
    """ Sum of many spaces that can be cast to Int. """
    @contract(Fs='tuple, seq[>=2]($Space)', R=Poset)
    def __init__(self, Fs, R):
        dom = PosetProduct(Fs)
        cod = R
        Map.__init__(self, dom=dom, cod=cod)

        tu = get_types_universe()
        self.subs = []
        target = Int()
        for F in Fs:
            # need F to be cast to Int
            F_to_Int, _ = tu.get_embedding(F, target)
            self.subs.append(F_to_Int)

        self.to_R, _ = tu.get_embedding(target, R)

    def _call(self, x):
        res = 0
        target = Int()
        for xe, s in zip(x, self.subs):
            xe_int = s(xe)
            res = target.add(res, xe_int)
        r = self.to_R(res)
        return r
