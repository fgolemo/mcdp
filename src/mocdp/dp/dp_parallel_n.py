# -*- coding: utf-8 -*-
from .primitive import PrimitiveDP
from contracts.utils import indent
from mocdp.dp.dp_series import get_product_compact
from mocdp.dp.primitive import NormalForm
from mocdp.exceptions import do_extra_checks
from mocdp.posets import Map, PosetProduct, UpperSet, UpperSets, poset_minima
from contracts import contract
import warnings
import itertools


__all__ = [
    'ParallelN',
]


class ParallelN(PrimitiveDP):
    """ Generalization to N problems """

    @contract(dps='list($PrimitiveDP)')
    def __init__(self, dps):
        warnings.warn('None of the following is implemented')
        Fs = [_.get_fun_space() for _ in dps]
        F = PosetProduct(tuple(Fs))
        Rs = [_.get_res_space() for _ in dps]
        R = PosetProduct(tuple(Rs))
        Ms = [_.get_imp_space_mod_res() for _ in dps]

        self.dps = dps
        self.M, self.pack, self.unpack = get_product_compact(*tuple(Ms))

        PrimitiveDP.__init__(self, F=F, R=R, M=self.M)

    def evaluate_f_m(self, f, m):
        raise NotImplementedError()
#
#         """ Returns the resources needed
#             by the particular implementation m """
#         _, _, unpack = get_product_compact(self.M1, self.M2)
#         f1, f2 = f
#         m1, m2 = unpack(m)
#         r1 = self.dp1.evaluate_f_m(f1, m1)
#         r2 = self.dp2.evaluate_f_m(f2, m2)
#         return (r1, r2)

    def solve(self, f):
        if do_extra_checks():
            F = self.get_fun_space()
            F.belongs(f)

        res = []
        for i, dp in enumerate(self.dps):
            fi = f[i]
            ri = dp.solve(fi)
            res.append(ri)
            
        minimals = [_.minimals for _ in res]
        s = []
        for comb in itertools.product(*tuple(minimals)):
            s.append(comb)

        R = self.get_res_space()
        res = R.Us(set(s))

        if do_extra_checks():
            tres = self.get_tradeoff_space()
            tres.belongs(res)

        return res

    def get_implementations_f_r(self, f, r):
        all_imps = []
        for i, dp in enumerate(self.dps):
            fi = f[i]
            ri = r[i]
            imps = dp. get_implementations_f_r(f=fi, r=ri)
            all_imps.append(imps)
        options = set()
        for comb in itertools.product(*tuple(all_imps)):
            m = self.pack(*comb)
            options.add(m)
        if do_extra_checks():
            for _ in options:
                self.M.belongs(_)

        return options

#         f1, f2 = f
#         r1, r2 = r
#         _, pack, _ = get_product_compact(self.M1, self.M2)
#
#         m1s = self.dp1.get_implementations_f_r(f1, r1)
#         m2s = self.dp2.get_implementations_f_r(f2, r2)
#
#         options = set()
#         for m1 in m1s:
#             for m2 in m2s:
#                 m = pack(m1, m2)
#                 options.add(m)
#
#         if do_extra_checks():
#             for _ in options:
#                 self.M.belongs(_)
#
#         return options



    def __repr__(self):
        return 'ParallelN(%s)' % ",".join(_.__repr__() for _ in self.dps)
#
#     def repr_long(self):
#         r1 = self.dp1.repr_long()
#         r2 = self.dp2.repr_long()
#         s = 'Parallel  %% %s -> %s' % (self.get_fun_space(), self.get_res_space())
#         s += '\n' + indent(r1, '. ', first='\ ')
#         s += '\n' + indent(r2, '. ', first='\ ')
#         return s

    def get_normal_form(self):
        raise NotImplementedError()


