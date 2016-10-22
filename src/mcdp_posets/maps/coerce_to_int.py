# -*- coding: utf-8 -*-
from contracts import contract
from mcdp_posets import Map, Space
from mcdp_posets.poset import is_top


__all__ = ['CoerceToInt']

class CoerceToInt(Map):

    @contract(cod=Space, dom=Space)
    def __init__(self, dom, cod):
        # todo: check dom is Nat or Int
        Map.__init__(self, dom, cod)

    def _call(self, x):
        if is_top(self.dom, x):
            return self.cod.get_top()
        return int(x)
