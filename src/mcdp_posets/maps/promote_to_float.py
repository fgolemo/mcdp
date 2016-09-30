from contracts import contract
from mcdp_posets import Map, Space


__all__ = ['PromoteToFloat']

class PromoteToFloat(Map):

    @contract(cod=Space, dom=Space)
    def __init__(self, cod, dom):
        # todo: check dom is Rcomp or Rcompunits
        Map.__init__(self, cod, dom)

    def _call(self, x):
        return float(x)
