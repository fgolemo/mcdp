# -*- coding: utf-8 -*-
from .primitive import PrimitiveDP
from contracts.utils import indent, raise_desc, raise_wrapped
from mocdp.dp.primitive import NormalForm, NotFeasible
from mocdp.posets import Map, PosetProduct, UpperSets
from mocdp.exceptions import DPInternalError
from mocdp.posets.space_product import SpaceProduct
from mocdp.posets.poset import Poset
from contracts import contract
from mocdp.posets.space import Space  # @UnusedImport


__all__ = [
    'Series',
    'Series0',
]



class Series0(PrimitiveDP):

    def __init__(self, dp1, dp2):
        from mocdp import get_conftools_dps
        library = get_conftools_dps()
        _, self.dp1 = library.instance_smarter(dp1)
        _, self.dp2 = library.instance_smarter(dp2)

        # if equiv_to_identity(self.dp1) or equiv_to_identity(self.dp2):
        #    raise ValueError('should not happen series\n- %s\n -%s' % (self.dp1, self.dp2))

        R1 = self.dp1.get_res_space()
        F2 = self.dp2.get_fun_space()

        if not R1 == F2:
            msg = 'Cannot connect different spaces.'
            raise_desc(DPInternalError, msg, dp1=dp1.repr_long(), dp2=dp2.repr_long(), R1=R1, F2=F2)

        F1 = self.dp1.get_fun_space()
        R2 = self.dp2.get_res_space()

        self.M1 = self.dp1.get_imp_space_mod_res()
        self.M2 = self.dp2.get_imp_space_mod_res()

        M, _, _ = get_product_compact(self.M1, R1, self.M2)
        PrimitiveDP.__init__(self, F=F1, R=R2, M=M)
        
    def evaluate_f_m(self, f1, m):
        """ Returns the resources needed
            by the particular implementation m """
        F1 = self.dp1.get_fun_space()
        R1 = self.dp1.get_res_space()
        F1.belongs(f1)
        M, _, unpack = get_product_compact(self.M1, R1, self.M2)
        M.belongs(m)
        m1, f2, m2 = unpack(m)
        r1 = self.dp1.evaluate_f_m(f1, m1)
#         f2 = r1  # could be another element of M
        r2 = self.dp2.evaluate_f_m(f2, m2)
        return r2


    def check_feasible(self, f1, m, r):
        # print('Feasible for %s' % type(self))
        R1 = self.dp1.get_res_space()
        M, _, unpack = get_product_compact(self.M1, R1, self.M2)
        M.belongs(m)
        m1, f2, m2 = unpack(m)
        try:
            self.dp1.check_feasible(f1, m1, f2)
        except NotFeasible as e:
            msg = 'First one not feasible'
            raise_wrapped(NotFeasible, e, msg, compact=True)

        # R1 = self.dp1.get_res_space()
        # print('r1 = %s' % R1.format(r1))
#         f2 = r1  # could be another element of M
        try:
            self.dp2.check_feasible(f2, m2, r)
#             r2 = self.dp2.evaluate_f_m(f2, m2)
        except NotFeasible as e:
            msg = 'Second one not feasible'
            raise_wrapped(NotFeasible, e, msg, compact=True)

#
#         R2 = self.R
#         # print('evaluated to r2 = %s' % R2.format(r2))
#         ok2 = R2.leq(r2, r)
#         print('%s <= %s is %s' % (R2.format(r2), R2.format(r), ok2))
#         return ok2


    def solve(self, func):
        from mocdp.posets import UpperSet, poset_minima

        u1 = self.dp1.solve(func)
        ressp1 = self.dp1.get_res_space()
        tr1 = UpperSets(ressp1)
        tr1.belongs(u1)

        mins = set([])
        for u in u1.minimals:
            v = self.dp2.solve(u)
            mins.update(v.minimals)
            

        ressp = self.get_res_space()
        minimals = poset_minima(mins, ressp.leq)
        # now mins is a set of UpperSets
        tres = self.get_tradeoff_space()

        us = UpperSet(minimals, ressp)
        tres.belongs(us)

        return us

    def __repr__(self):
        return 'Series(%r, %r)' % (self.dp1, self.dp2)

    def repr_long(self):
        r1 = self.dp1.repr_long()
        r2 = self.dp2.repr_long()
        s1 = 'Series:'
        s2 = ' %s -> %s' % (self.get_fun_space(), self.get_res_space())
        s = s1 + ' % ' + s2
        s += '\n' + indent(r1, '. ', first='\ ')
        s += '\n' + indent(r2, '. ', first='\ ')
        return s

    def get_normal_form(self):
        """
            
            alpha1: U(F1) x S1 -> U(R1)
            beta1:  U(F1) x S1 -> S1
            
            alpha2: U(R1) x S2 -> U(R2)
            beta2:  U(R1) x S2 -> S2
             
        """

        S1, alpha1, beta1 = self.dp1.get_normal_form()
        S2, alpha2, beta2 = self.dp2.get_normal_form()

        F1 = self.dp1.get_fun_space()
        # R1 = self.dp1.get_res_space()
        R2 = self.dp2.get_res_space()

        UR2 = UpperSets(R2)

        UF1 = UpperSets(F1)
        """
        S = S1 x S2 is a Poset
        alpha: UF1 x S -> UR1
        beta: UF1 x S -> S
"""     
        S, pack, unpack = get_product_compact(S1, S2)


        D = PosetProduct((UF1, S))
                         
        class SeriesAlpha(Map):
            def __init__(self, dp):
                self.dp = dp
                dom = D
                cod = UR2
                Map.__init__(self, dom, cod)

            def _call(self, x):
                (F, s) = x
                (s1, s2) = unpack(s)
                a = alpha1((F, s1))
                return alpha2((a, s2))

        class SeriesBeta(Map):
            def __init__(self, dp):
                self.dp = dp
                dom = D
                cod = S
                Map.__init__(self, dom, cod)

            def _call(self, x):

                (F, s) = x
                (s1, s2) = unpack(s)
                r_1 = beta1((F, s1))
                a = alpha1((F, s1))
                r_2 = beta2((a, s2))
                
                return pack(r_1, r_2)

        return NormalForm(S, SeriesAlpha(self), SeriesBeta(self))


Series = Series0

if False:
    # Huge product spaces
    def prod_make(S1, S2):
        S = PosetProduct((S1, S2))
        return S

    def prod_get_state(S1, S2, s):  # @UnusedVariable
        (s1, s2) = s
        return (s1, s2)
else:
    @contract(returns='tuple($Space, *, *)')
    def get_product_compact(*spaces):
        """
            S, pack, unpack = get_product_compact(S1, S2)
        """

        S = _prod_make(spaces)
        def pack(*elements):
            return _prod_make_state(elements, spaces)
        def unpack(s):
            return _prod_get_state(s, spaces)
#         pack = lambda s1, s2: _prod_make_state(s1, s2, spaces=spaces)
#         unpack = lambda s: _prod_get_state(s, spaces=spaces)
        return S, pack, unpack

    def _prod_make(spaces):
        def get_subs(x):
            if isinstance(x, SpaceProduct):
                return x.subs
            else:
                return (x,)

        subs = ()
        for space in spaces:
            subs = subs + get_subs(space)

        if all(isinstance(x, Poset) for x in subs):
            S = PosetProduct(subs)
        else:
            S = SpaceProduct(subs)

        return S

    def _prod_make_state(elements, spaces):

        def get_state(X, x):
            if isinstance(X, SpaceProduct):
                return x
            else:
                return (x,)
            
        s = ()
        for space, e in zip(spaces, elements):
            s = s + get_state(space, e)
        return s

    def _prod_get_state(s, spaces):
        assert isinstance(s, tuple)
        S = _prod_make(spaces)
        # print('S = %s %s s =%s' % (S, type(S), s))
        S.belongs(s)
        res = []
        for Si in spaces:
            if isinstance(Si, SpaceProduct):
                n = len(Si)
                si = s[:n]
                s = s[n:]
            else:
                si = s[0]
                s = s[1:]
            res.append(si)

        return tuple(res)

# def fit_into(s1, s2, cols):
#     n = cols - len(s1) - len(s2)
#     return s1 + ' ' * n + s2

