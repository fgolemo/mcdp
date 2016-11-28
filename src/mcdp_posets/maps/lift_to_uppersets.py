# -*- coding: utf-8 -*-
from mcdp_posets import Map
from contracts import contract

__all__ = ['LiftToUpperSets']

class LiftToUpperSets(Map):
    """ Lift the map f to uppersets """
    @contract(f=Map)
    def __init__(self, f):
        from mcdp_posets.uppersets import UpperSets
        dom = UpperSets(f.get_domain())
        cod = UpperSets(f.get_codomain())
        self.f = f
        Map.__init__(self, dom=dom, cod=cod)

    def _call(self, x):
        minimals = x.minimals
        elements2 = set(self.f(_) for _ in minimals)
        from mcdp_posets.uppersets import UpperSet
        return UpperSet(elements2, self.cod.P)
