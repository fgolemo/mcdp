# -*- coding: utf-8 -*-
import itertools

from contracts import contract
from contracts.utils import indent
from mcdp_posets import PosetProduct
from mcdp_posets.uppersets import lowerset_product_multi, upperset_product_multi
from mocdp import ATTRIBUTE_NDP_RECURSIVE_NAME
from mocdp.exceptions import do_extra_checks

from .dp_series import get_product_compact
from .primitive import PrimitiveDP


__all__ = [
    'ParallelN',
]


class ParallelN(PrimitiveDP):
    """ Generalization to N problems """

    @contract(dps='tuple,seq($PrimitiveDP)')
    def __init__(self, dps):
        Fs = [_.get_fun_space() for _ in dps]
        Rs = [_.get_res_space() for _ in dps]
        Ms = [_.get_imp_space() for _ in dps]

        F = PosetProduct(tuple(Fs))
        R = PosetProduct(tuple(Rs))

        self.Ms = Ms
        self.dps = tuple(dps)
        self.M, _, _ = self._get_product()
        PrimitiveDP.__init__(self, F=F, R=R, I=self.M)

    def __getstate__(self):
        state = dict(**self.__dict__)
        state.pop('prod', None)
        return state

    def _get_product(self):
        if not hasattr(self, 'prod'):
            self.prod = _, _, _ = get_product_compact(*tuple(self.Ms))
        return self.prod

#     def evaluate_f_m(self, f, m):
#         raise NotImplementedError()
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
            ri = dp.solve(f[i])
            res.append(ri)
            
        return upperset_product_multi(tuple(res))
        
    def solve_r(self, r):
        res = []
        for i, dp in enumerate(self.dps):
            fi = dp.solve_r(r[i])
            res.append(fi)
        return lowerset_product_multi(tuple(res))    

    def evaluate(self, m):
        _, _, unpack = self._get_product()

        ms = unpack(m)
        LFs = []
        URs = []
        for i, dp in enumerate(self.dps):
            mi = ms[i]
            LFi, URi = dp.evaluate(mi)
            LFs.append(LFi)
            URs.append(URi)

        UR = upperset_product_multi(URs)
        LF = lowerset_product_multi(LFs)
        return LF, UR

    def get_implementations_f_r(self, f, r):
        _, pack, _ = self._get_product()
        
        all_imps = []
        for i, dp in enumerate(self.dps):
            fi = f[i]
            ri = r[i]
            imps = dp. get_implementations_f_r(f=fi, r=ri)
            all_imps.append(imps)
        options = set()
        for comb in itertools.product(*tuple(all_imps)):
            m = pack(*comb)
            options.add(m)
        if do_extra_checks():
            for _ in options:
                self.M.belongs(_)

        return options

    def __repr__(self):
        return 'ParallelN(%s)' % ",".join(_.__repr__() for _ in self.dps)

    def repr_long(self):
        s = 'ParallelN  %% %s -> %s' % (self.get_fun_space(), self.get_res_space())
        for dp in self.dps:
            r = dp.repr_long()
            s += '\n' + indent(r, '. ', first='\ ')

        if hasattr(dp, ATTRIBUTE_NDP_RECURSIVE_NAME):
            a = getattr(dp, ATTRIBUTE_NDP_RECURSIVE_NAME)
            s += '\n (labeled as %s)' % a.__str__()

        return s

    def get_normal_form(self):
        raise NotImplementedError()


