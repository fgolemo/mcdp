from contracts import contract
from mcdp_posets import Map, Nat


__all__ = [
    'PlusNat',
]

class PlusNat(Map):

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
