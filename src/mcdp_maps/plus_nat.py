# -*- coding: utf-8 -*-
from contracts import contract
from mcdp_posets import Map, Nat
from mcdp_posets.space import MapNotDefinedHere
from mcdp_posets.poset import is_top
from contracts.utils import check_isinstance
from mcdp_posets.nat import Nat_add


__all__ = [
    'PlusValueNatMap',
    'MinusValueNatMap',
]

class PlusValueNatMap(Map):

    def __init__(self, value):
        self.value = value
        self.N = Nat()
        self.N.belongs(value)
        Map.__init__(self, dom=self.N, cod=self.N)

    def _call(self, x):
        return Nat_add(x, self.value)
#         if self.N.equal(self.N.get_top(), x):
#             return x
#         # TODO: check overflow
#         res = x + self.value
#         assert isinstance(res, int), res
#         return res

    def __repr__(self):
        return '+ %s' % self.N.format(self.value)


class MinusValueNatMap(Map):
    
    """
        if value is Top:
        
            r |->   MapNotDefinedHere   if r != Top
                    Top  if r == Top  
        
        otherwise:
        
            r |->   MapNotDefinedHere   if r < value:
                    r - value  if r >= value 
        f - Top <= r 
    
    """
    @contract(value=int)
    def __init__(self, value):
        self.c = value
        N = Nat()
        Map.__init__(self, dom=N, cod=N)
        self.top  = self.dom.get_top()
        
    def _call(self, x):
        P = self.dom
        
        if is_top(self.dom, self.c):
            #  r = 0 -> f empty
            #  r = 1 -> f empty
            #  r = Top -> f <= Top
            if is_top(self.dom, x):
                return self.top
            else:
                raise MapNotDefinedHere()
        
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
