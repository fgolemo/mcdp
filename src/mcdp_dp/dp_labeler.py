# -*- coding: utf-8 -*-
import copy

from contracts import contract
from contracts.utils import indent
from mcdp_dp.primitive import PrimitiveDP
from mocdp import ATTRIBUTE_NDP_RECURSIVE_NAME


__all__ = [
    'LabelerDP',
]

class LabelerDP(PrimitiveDP):
    
    @contract(dp=PrimitiveDP, recname='tuple,seq(str)')
    def __init__(self, dp, recname):
        self.dp = dp
        F = dp.get_fun_space()
        R = dp.get_res_space()
        I0 = dp.get_imp_space()
        Imarked = copy.copy(I0)
        setattr(Imarked, ATTRIBUTE_NDP_RECURSIVE_NAME, recname)
        PrimitiveDP.__init__(self, F=F, R=R, I=Imarked)
        self.recname = recname

    def repr_long(self):
        s = 'LabelerDP({})'.format(self.recname)
        s += '\n' + indent(self.dp.repr_long(), ' ')
        return s

    def solve(self, f):
        return self.dp.solve(f)

    def evaluate(self, i):
        return self.dp.evaluate(i)

    def get_implementations_f_r(self, f, r):
        return self.dp.get_implementations_f_r(f, r)
