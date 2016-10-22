# -*- coding: utf-8 -*-
from contracts import contract
from mcdp_posets import Map, Nat
from mcdp_posets.space import MapNotDefinedHere
from mcdp_posets.poset import is_top
from contracts.utils import check_isinstance


__all__ = [
    'PlusValueNatMap',
    'MinusValueNatMap',
]

class PlusValueNatMap(Map):

    @contract(value=int)
    def __init__(self, value):
        self.value = value
        self.N = Nat()
        Map.__init__(self, dom=self.N, cod=self.N)

    def _call(self, x):
        if self.N.equal(self.N.get_top(), x):
            return x
        # TODO: check overflow
        res = x + self.value
        assert isinstance(res, int), res
        return res

    def __repr__(self):
        return '+ %s' % self.value


class MinusValueNatMap(Map):

    @contract(value=int)
    def __init__(self, value):
        self.c = value
        N = Nat()
        Map.__init__(self, dom=N, cod=N)
        self.top  = self.dom.get_top()
        
    def _call(self, x):
        P = self.dom
        
        if P.equal(x, self.c):
            return 0
        else:
            if P.leq(x, self.c):
                msg = '%s < %s' % (P.format(x), P.format(self.c))
                raise MapNotDefinedHere(msg)
            else:
                if is_top(P, x):
                    return self.top
                else:
                    check_isinstance(x, int)
                    res = x - self.c
                    assert res >= 0
                    # todo: check underflow
                    return res
                
    def __repr__(self):
        return '- %s' % self.c
