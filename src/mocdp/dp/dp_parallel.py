# -*- coding: utf-8 -*-
from .primitive import PrimitiveDP
from mocdp.posets import PosetProduct
import itertools

__all__ = [
    'Parallel',
]

class Parallel(PrimitiveDP):

    def __init__(self, dp1, dp2):
        from mocdp import get_conftools_dps
        library = get_conftools_dps()
        _, self.dp1 = library.instance_smarter(dp1)
        _, self.dp2 = library.instance_smarter(dp2)

    def get_fun_space(self):
        F1 = self.dp1.get_fun_space()
        F2 = self.dp2.get_fun_space()
        return PosetProduct((F1, F2))

    def get_res_space(self):
        R1 = self.dp1.get_res_space()
        R2 = self.dp2.get_res_space()
        return PosetProduct((R1, R2))

    def solve(self, f):
        F = self.get_fun_space()
        F.belongs(f)

        f1, f2 = f

        r1 = self.dp1.solve(f1)
        r2 = self.dp2.solve(f2)
        
        R = self.get_res_space()
        s = []
        for m1, m2 in itertools.product(r1.minimals, r2.minimals):
            s.append((m1, m2))

        res = R.Us(set(s))

        tres = self.get_tradeoff_space()
        tres.belongs(res)

        return res

    def __repr__(self):
        return 'Parallel(%r, %r)' % (self.dp1, self.dp2)


