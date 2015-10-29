# -*- coding: utf-8 -*-
from .primitive import PrimitiveDP
from mocdp.exceptions import mcdp_dev_warning
from mocdp.posets import PosetProduct
import numpy as np


__all__ = [
    'GenericUnary',
]

class GenericUnary(PrimitiveDP):

    def __init__(self, F, R, function):
        M = PosetProduct(())
        PrimitiveDP.__init__(self, F=F, R=R, M=M)
        self.function = function

    def solve(self, func):
        if self.F.equal(func, self.F.get_top()):
            r = self.R.get_top()
        else:
            r = self.function(func)

            mcdp_dev_warning('give much more thoguth')
            if isinstance(r, float) and np.isinf(r):
                r = self.R.get_top()
            
        return self.R.U(r)

    def __repr__(self):
        return self.function.__name__


