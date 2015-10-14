# -*- coding: utf-8 -*-
from .primitive import PrimitiveDP
from mocdp.posets import PosetProduct
import itertools
from contracts.utils import indent

__all__ = [
    'Parallel',
    'make_parallel',
]

def make_parallel(dp1, dp2):
    from mocdp.dp.dp_flatten import Mux
    from mocdp.dp.dp_identity import Identity
    from mocdp.dp.dp_series import make_series
    from mocdp.dp.dp_series import is_equiv_to_terminator

#     # if none is a mux, we cannot do anything
#     if not isinstance(dp1, Mux) and not isinstance(dp2, Mux):
#         return Parallel(dp1, dp2)
#
#     def identity_as_mux(x):
#         if isinstance(x, Identity):
#             F = x.get_fun_space()
#             return Mux(F, ())
#         return x
#
#     dp1 = identity_as_mux(dp1)
#     dp2 = identity_as_mux(dp2)


    from mocdp.dp.dp_series import equiv_to_identity
    # change identity to Mux
    a = Parallel(dp1, dp2)
    if equiv_to_identity(dp1) and equiv_to_identity(dp2):
        F = PosetProduct((dp1.get_fun_space(), dp2.get_fun_space()))
        assert F == a.get_fun_space()
        return Identity(F)

    # Parallel(X, Terminator) => Series(Mux([0]), X, Mux([0, ()]))
    if is_equiv_to_terminator(dp2):
        F = a.get_fun_space()  # PosetProduct((dp1.get_fun_space(),))
        m1 = Mux(F, coords=0)
        m2 = dp1
        m3 = Mux(m2.get_res_space(), [(), []])
        res = make_series(make_series(m1, m2), m3)

        assert res.get_res_space() == a.get_res_space()
        assert res.get_fun_space() == a.get_fun_space()
        return res

    if is_equiv_to_terminator(dp1):
        F = a.get_fun_space()  # PosetProduct((dp1.get_fun_space(),))
        m1 = Mux(F, coords=1)
        m2 = dp2
        m3 = Mux(m2.get_res_space(), [[], ()])
        return make_series(make_series(m1, m2), m3)


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

    def repr_long(self):
        r1 = self.dp1.repr_long()
        r2 = self.dp2.repr_long()
        s = 'Parallel:   %s -> %s' % (self.get_fun_space(), self.get_res_space())
        s += '\n' + indent(r1, 'P1 ')
        s += '\n' + indent(r2, 'P2 ')
        return s
