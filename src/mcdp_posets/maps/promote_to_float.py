# -*- coding: utf-8 -*-
from contracts import contract
from mcdp_posets import Map, Space
from mcdp_posets.poset import is_top
from mocdp.exceptions import DPInternalError
from contracts.utils import raise_wrapped


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
        try: 
            return float(x)
        except BaseException as e:
            msg = 'Internal error in PromoteToFloat.'
            raise_wrapped(DPInternalError, e, msg, x=x)
            

    def repr_map(self, letter):
        return "%s ⟼ (float) %s" % (letter, letter)