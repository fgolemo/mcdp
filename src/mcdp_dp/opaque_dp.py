# -*- coding: utf-8 -*-
from .primitive import PrimitiveDP
from contracts import contract
from contracts.utils import check_isinstance, indent
from mocdp import ATTRIBUTE_NDP_RECURSIVE_NAME

__all__ = [
    'OpaqueDP',
]


class OpaqueDP(PrimitiveDP):

    @contract(dp=PrimitiveDP)
    def __init__(self, dp):
        check_isinstance(dp, PrimitiveDP)
        if isinstance(dp, OpaqueDP):
            raise ValueError(dp)
        self.dp = dp
        F = dp.F
        R = dp.R
        I = dp.I
        PrimitiveDP.__init__(self, F, R, I)

    def solve(self, f):
        return self.dp.solve(f)

    def evaluate(self, i):
        return self.dp.evaluate(i)

    def get_implementations_f_r(self, f, r):
        return self.dp.get_implementations_f_r(f, r)

    def repr_long(self):
        r1 = self.dp.repr_long()
        s = 'OpaqueDP'
        s+= '\n' + indent(r1, '. ', first='\ ')
        if hasattr(self.dp, ATTRIBUTE_NDP_RECURSIVE_NAME):
            a = getattr(self.dp, ATTRIBUTE_NDP_RECURSIVE_NAME)
            s += '\n (labeled as %s)' % a.__str__()
        return s
