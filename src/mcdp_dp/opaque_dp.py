# -*- coding: utf-8 -*-
from .primitive import PrimitiveDP
from contracts import contract
from contracts.utils import check_isinstance, indent, raise_desc
from mocdp.exceptions import DPInternalError

__all__ = [
    'OpaqueDP',
]


class OpaqueDP(PrimitiveDP):

    @contract(dp=PrimitiveDP)
    def __init__(self, dp):
        check_isinstance(dp, PrimitiveDP)
        if isinstance(dp, OpaqueDP):
            msg = 'OpaqueDP inside OpaqueDP? this should not happen.'
            raise_desc(DPInternalError, msg)
        self.dp = dp
        F = dp.F
        R = dp.R
        I = dp.I
        PrimitiveDP.__init__(self, F, R, I)

    def solve(self, f):
        return self.dp.solve(f)

    def solve_r(self, r):
        return self.dp.solve_r(r)

    def evaluate(self, i):
        return self.dp.evaluate(i)

    def get_implementations_f_r(self, f, r):
        return self.dp.get_implementations_f_r(f, r)

    def repr_h_map(self):
        return self.dp.repr_h_map() + ' (opaque)'
    
    def repr_hd_map(self):
        return self.dp.repr_hd_map() + ' (opaque)'

    def repr_long(self):
        r1 = self.dp.repr_long()
        s = 'OpaqueDP'
        s+= '\n' + indent(r1, '. ', first='\ ')
        return s
