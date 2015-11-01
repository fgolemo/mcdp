# -*- coding: utf-8 -*-
from .primitive import PrimitiveDP
from contracts.utils import indent, raise_desc
from mocdp.posets import poset_minima

from contracts import contract
from mocdp.posets.types_universe import get_types_universe
from mocdp.posets.space import NotEqual
from mocdp.posets.category_coproduct import Coproduct1
from mocdp.dp.primitive import NotFeasible


__all__ = [
    'CoProductDP',
]


class CoProductDP(PrimitiveDP):
    """ Returns the co-product of 1+ dps. """

    @contract(dps='tuple,seq[>=1]($PrimitiveDP)')
    def __init__(self, dps):
        from mocdp import get_conftools_dps
        library = get_conftools_dps()
        dps = [library.instance_smarter(_)[1] for _ in dps]
        tu = get_types_universe()

        F1 = dps[0].get_fun_space()
        R1 = dps[0].get_res_space()

        for dp in dps:
            Fj = dp.get_fun_space()
            Rj = dp.get_res_space()

            try:
                tu.check_equal(F1, Fj)
                tu.check_equal(R1, Rj)
            except NotEqual:
                msg = 'Cannot form the co-product.'
                raise_desc(ValueError, msg, dps=dps)

        F = F1
        R = R1
        Ms = [dp.get_imp_space_mod_res() for dp in dps]

        self.dps = dps
        M = Coproduct1(tuple(Ms))
        PrimitiveDP.__init__(self, F=F, R=R, M=M)

    def evaluate_f_m(self, f, m):
        """ Returns the resources needed
            by the particular implementation m """

        i, xi = self.M.unpack(m)
        return self.dps[i].evaluate_f_m(f, xi)

    def get_implementations_f_r(self, f, r):
        """ Returns a nonempty set of thinks in self.M.
            Might raise NotFeasible() """
        res = set()
        es = []
        for j, dp in enumerate(self.dps):
            try:
                ms = dp.get_implementations_f_r(f, r)
                print('%s: dp.get_implementations_f_r(f, r) = %s ' % (j, ms))
                assert len(ms) > 0, dp
                for m in ms:
                    res.add(self.M.pack(j, m))
            except NotFeasible as e:
                es.append(e)
        if not ms:
            # no one was feasible
            msg = 'None was feasible'
            msg += '\n\n' + '\n\n'.join(str(e) for e in es)
            raise_desc(NotFeasible, msg, f=f, r=r, self=self)
        return res

    def solve(self, f):
        R = self.get_res_space()

        s = []

        for dp in self.dps:
            rs = dp.solve(f)
            s.extend(rs.minimals)

        res = R.Us(poset_minima(s, R.leq))

        return res

    def __repr__(self):
        s = "^".join('%s' % x for x in self.dps)
        return 'CoProduct(%s)' % s

    def repr_long(self):
        s = 'CoProduct  %% %s -> %s' % (self.get_fun_space(), self.get_res_space())
        for dp in self.dps:
            r1 = dp.repr_long()
            s += '\n' + indent(r1, '. ', first='^ ')
        return s
#
#     def get_normal_form(self):
#         """
#
#             alpha1: U(F1) x S1 -> U(R1)
#             beta1:  U(F1) x S1 -> S1
#
#             alpha2: U(F2) x S2 -> U(R2)
#             beta2:  U(R2) x S2 -> S2
#
#         """
#
#         S1, alpha1, beta1 = self.dp1.get_normal_form()
#         S2, alpha2, beta2 = self.dp2.get_normal_form()
#
#         S, pack, unpack = get_product_compact(S1, S2)
#
#         F = self.get_fun_space()
#         R = self.get_res_space()
#         F1 = F[0]
#         # R1 = R[0]
#         F2 = F[1]
#         # R2 = R[1]
#         UF = UpperSets(F)
#         UR = UpperSets(R)
#
#         D = PosetProduct((UF, S))
#         """
#             alpha: U(F1xF2) x (S1xS2) -> U(R1xR2)
#             beta : U(F1xF2) x (S1xS2) -> (S1xS2)
#         """
#         class SeriesAlpha(Map):
#             def __init__(self, dp):
#                 self.dp = dp
#                 dom = D
#                 cod = UR
#                 Map.__init__(self, dom, cod)
#
#             def _call(self, x):
#                 (uf, s) = x
#                 (s1, s2) = unpack(s)
#
#                 res = set()
#                 for f1, f2 in uf.minimals:
#
#                     uf1 = UpperSet(set([f1]), F1)
#                     ur1 = alpha1((uf1, s1))
#
#                     uf2 = UpperSet(set([f2]), F2)
#                     ur2 = alpha2((uf2, s2))
#
#                     # now I need to take all combinations
#                     for a, b in itertools.product(ur1.minimals, ur2.minimals):
#                         res.add((a, b))
#                 # now take the minimal
#                 resm = poset_minima(res, R.leq)
#                 r = UpperSet(resm, R)
#                 return r
#
#         """
#             alpha: U(F1xF2) x (S1xS2) -> U(R1xR2)
#             beta : U(F1xF2) x (S1xS2) -> (S1xS2)
#         """
#         class SeriesBeta(Map):
#             def __init__(self, dp):
#                 self.dp = dp
#                 dom = D
#                 cod = S
#                 Map.__init__(self, dom, cod)
#
#             def _call(self, x):
#                 (uf, s) = x
#                 (s1, s2) = unpack(s)
#
#                 # now need to project down
#                 uf1, uf2 = upperset_project_two(F, uf)
#
#                 s1p = beta1((uf1, s1))
#                 s2p = beta2((uf2, s2))
#                 return pack(s1p, s2p)
#
#         return NormalForm(S, SeriesAlpha(self), SeriesBeta(self))
