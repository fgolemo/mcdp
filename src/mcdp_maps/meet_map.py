# -*- coding: utf-8 -*-
from contracts import contract
from contracts.utils import raise_wrapped
from mcdp_posets import Poset, NotJoinable, PosetProduct, Map, MapNotDefinedHere
from mcdp_maps.repr_map import repr_map_meetn


__all__ = [
    'MeetNMap',
]

class MeetNMap(Map):
    """ 
    
        A map that computes the meet of n arguments. 
    
        Raises MapNotDefinedHere if the elements are not joinable.
    """

    @contract(n='int,>=1', P=Poset)
    def __init__(self, n, P):
        dom = PosetProduct((P,) * n)
        cod = P
        Map.__init__(self, dom, cod)
        self.P = P

    def _call(self, xs):
        try:
            res = xs[0]
            for x in xs[1:]:
                res = self.P.meet(res, x)
            return res
        except NotJoinable as e:
            msg = 'Cannot meet all elements.'
            raise_wrapped(MapNotDefinedHere, e, msg, res=res, x=x)

    def repr_map(self, letter):
        n = len(self.dom)
        return repr_map_meetn(letter, n)
    
