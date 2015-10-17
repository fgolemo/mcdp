# -*- coding: utf-8 -*-
from .primitive import PrimitiveDP
from contracts.utils import indent, raise_desc
from mocdp.dp.primitive import NormalForm
from mocdp.posets import Map, PosetProduct, UpperSets
from mocdp.exceptions import DPInternalError
from mocdp.posets.space_product import SpaceProduct


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

        M1 = self.dp1.get_imp_space_mod_res()
        M2 = self.dp2.get_imp_space_mod_res()
        M = SpaceProduct((M1, M2))

        PrimitiveDP.__init__(self, F=F1, R=R2, M=M)
        
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
        s = 'Series:   %s -> %s' % (self.get_fun_space(), self.get_res_space())
        s += '\n' + indent(r1, 'S1 ')
        s += '\n' + indent(r2, 'S2 ')
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
        S = prod_make(S1, S2)


        D = PosetProduct((UF1, S))
                         
        class SeriesAlpha(Map):
            def __init__(self, dp):
                self.dp = dp
                dom = D
                cod = UR2
                Map.__init__(self, dom, cod)

            def _call(self, x):
                (F, s) = x
                (s1, s2) = prod_get_state(S1, S2, s)
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
                (s1, s2) = prod_get_state(S1, S2, s)
                r_1 = beta1((F, s1))
                a = alpha1((F, s1))
                r_2 = beta2((a, s2))
                
                return prod_make_state(S1, S2, r_1, r_2)

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

    def prod_make(S1, S2):
        assert isinstance(S1, PosetProduct), S1
        if isinstance(S2, PosetProduct):
            S = PosetProduct(S1.subs + S2.subs)
        else:
            S = PosetProduct(S1.subs + (S2,))

        return S

    def prod_make_state(S1, S2, s1, s2):
        assert isinstance(S1, PosetProduct), S1
        assert isinstance(s1, tuple)
        if isinstance(S2, PosetProduct):
            assert isinstance(s2, tuple)
            return s1 + s2
        else:
            return s1 + (s2,)

    def prod_get_state(S1, S2, s):
        assert isinstance(S1, PosetProduct)
        assert isinstance(s, tuple)
        n1 = len(S1)

        s1 = s[:n1]
        s2 = s[n1:]
        if isinstance(S2, PosetProduct):
            pass
        else:
            assert len(s2) == 1
            s2 = s2[0]

        return (s1, s2)


