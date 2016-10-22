# -*- coding: utf-8 -*-
from contracts import contract
from mcdp_posets import Map, Space
from mcdp_posets.poset import is_top


__all__ = [
    'PromoteToFloat',
]

class PromoteToFloat(Map):
    """ Applies float() to argument, or returns dom.top if top. """
    
    @contract(cod=Space, dom=Space)
    def __init__(self, cod, dom):
        # todo: check dom is Rcomp or Rcompunits
        Map.__init__(self, cod, dom)

    def _call(self, x):
        if is_top(self.dom, x):
            return self.cod.get_top() 
        return float(x)
