# -*- coding: utf-8 -*-
from .primitive import PrimitiveDP
from mocdp.posets import PosetProduct
import itertools

__all__ = [
    'Parallel',
    'make_parallel',
]

def make_parallel(dp1, dp2):
    from mocdp.dp.dp_flatten import Mux
    from mocdp.dp.dp_identity import Identity

    # if none is a mux, we cannot do anything
    if not isinstance(dp1, Mux) and not isinstance(dp2, Mux):
        return Parallel(dp1, dp2)
#
#     def identity_as_mux(x):
#         if isinstance(x, Identity):
#             F = x.get_fun_space()
#             return Mux(F, ())
#         return x
#
#     dp1 = identity_as_mux(dp1)
#     dp2 = identity_as_mux(dp2)

    a = Parallel(dp1, dp2)

    from mocdp.dp.dp_series import equiv_to_identity
    if equiv_to_identity(dp1) and equiv_to_identity(dp2):
            return Identity(a.get_fun_space())

    # change identity to Mux


    return a


class Parallel(PrimitiveDP):

    def __init__(self, dp1, dp2):
        from mocdp import get_conftools_dps
        library = get_conftools_dps()
        _, self.dp1 = library.instance_smarter(dp1)
        _, self.dp2 = library.instance_smarter(dp2)

        F1 = self.dp1.get_fun_space()
        F2 = self.dp2.get_fun_space()
        F = PosetProduct((F1, F2))
        R1 = self.dp1.get_res_space()
        R2 = self.dp2.get_res_space()
        R = PosetProduct((R1, R2))

        PrimitiveDP.__init__(self, F=F, R=R)
        
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


