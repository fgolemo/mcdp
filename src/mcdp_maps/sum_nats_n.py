from mcdp_posets import Map, Nat, PosetProduct
import numpy as np


__all__ = ['SumNatsN']


class SumNatsN(Map):

    """ sums together N natural numbers """
    def __init__(self, n):
        self.n = n
        N = Nat()
        dom = PosetProduct((N,) * n)
        cod = N
        Map.__init__(self, dom=dom, cod=cod)
        self.top = cod.get_top()
        self.n = n

    def _call(self, x):
        assert isinstance(x, tuple) and len(x) == self.n
        N = self.cod
        top = self.top
        res = 0
        for xi in x:
            if N.equal(x, top):
                return top
            res += xi
        if np.isinf(res):
            return top

        return res

