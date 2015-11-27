from mocdp.posets.space import Map, Space
from contracts import contract

class IdentityMap(Map):

    @contract(cod=Space, dom=Space)
    def __init__(self, cod, dom):
        Map.__init__(self, cod, dom)

    def _call(self, x):
        return x
