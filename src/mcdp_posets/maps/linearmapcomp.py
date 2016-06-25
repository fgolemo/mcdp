from mcdp_posets import Map
import numpy as np

class LinearMapComp(Map):
    """ Linear multiplication on R + top """

    def __init__(self, A, B, factor):
        Map.__init__(self, A, B)
        self.A = A
        self.B = B
        self.factor = factor

    def _call(self, x):
        if self.A.equal(x, self.A.get_top()):
            return self.B.get_top()
        res = x * self.factor
        if np.isinf(res):
            return self.B.get_top()
        return res
