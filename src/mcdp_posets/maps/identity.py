from contracts import contract
from mcdp_posets import Map, Space

__all__ = [
    'IdentityMap',
]

class IdentityMap(Map):

    @contract(cod=Space, dom=Space)
    def __init__(self, cod, dom):
        Map.__init__(self, cod, dom)

        self.__name__ = 'Identity'

    def _call(self, x):
        return x
