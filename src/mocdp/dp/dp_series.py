# -*- coding: utf-8 -*-
from .primitive import PrimitiveDP
from mocdp.posets.uppersets import UpperSets
from mocdp.posets.poset_product import PosetProduct
from mocdp.posets.space import Map
from mocdp.dp.primitive import NormalForm
from contracts.utils import raise_desc, raise_wrapped

__all__ = [
    'make_series',
    'Series',
]


def make_series(dp1, dp2):
    """ Creates a Series if needed.
        Simplifies the identity and muxes """
    # first, check that the series would be created correctly
    from mocdp.dp.dp_identity import Identity
    a = Series0(dp1, dp2)
    if isinstance(dp1, Identity):
        return dp2
    if isinstance(dp2, Identity):
        return dp1

    from mocdp.dp.dp_flatten import Mux
    if isinstance(dp1, Mux) and isinstance(dp2, Mux):
        return mux_composition(dp1, dp2)
    return a

def mux_composition(dp1, dp2):
    try:
        dp0 = Series(dp1, dp2)
        from mocdp.dp.dp_flatten import Mux
        assert isinstance(dp1, Mux)
        assert isinstance(dp2, Mux)
        F = dp1.get_fun_space()
    #     assert isinstance(F, PosetProduct),

        c1 = dp1.coords
        c2 = dp2.coords
        from multi_index.get_it_test import compose_indices
        coords = compose_indices(F, c1, c2, list)
        res = Mux(F, coords)

        print('res: %s' % str(res))

        assert res.get_res_space() == dp0.get_res_space()

        return res
    except Exception as e:
        msg = 'Cannot create shortcut.'
        raise_wrapped(Exception , e , msg, dp1=dp1, dp2=dp2,)




class Series0(PrimitiveDP):

    def __init__(self, dp1, dp2):
        from mocdp import get_conftools_dps
        library = get_conftools_dps()
        _, self.dp1 = library.instance_smarter(dp1)
        _, self.dp2 = library.instance_smarter(dp2)


        R1 = self.dp1.get_res_space()
        F2 = self.dp2.get_fun_space()

        if not R1 == F2:
            msg = 'Cannot connect different spaces.'
            raise_desc(ValueError, msg, dp1=dp1, dp2=dp2, R1=R1, F2=F2)


        F1 = self.dp1.get_fun_space()
        R2 = self.dp2.get_res_space()

        PrimitiveDP.__init__(self, F=F1, R=R2)
        
    def solve(self, func):
        from mocdp.posets import UpperSet, poset_minima

#         self.info('func: %s' % self.F.format(func))

        u1 = self.dp1.solve(func)
        ressp1 = self.dp1.get_res_space()
        tr1 = UpperSets(ressp1)
        tr1.belongs(u1)

#         self.info('u1: %s' % tr1.format(u1))

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

#         self.info('us: %s' % tres.format(us))

        return us

    def __repr__(self):
        return 'Series(%r, %r)' % (self.dp1, self.dp2)

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
        S = PosetProduct((S1, S2))
        D = PosetProduct((UF1, S))
                         
        class SeriesAlpha(Map):
            def __init__(self, dp):
                self.dp = dp
                dom = D
                cod = UR2
                Map.__init__(self, dom, cod)

            def _call(self, x):
                (F, (s1, s2)) = x
                a = alpha1((F, s1))
                return alpha2((a, s2))

        class SeriesBeta(Map):
            def __init__(self, dp):
                self.dp = dp
                dom = D
                cod = S
                Map.__init__(self, dom, cod)

            def _call(self, x):

                (F, (s1, s2)) = x

                r_1 = beta1((F, s1))
                a = alpha1((F, s1))
                r_2 = beta2((a, s2))
                
                return r_1, r_2

        return NormalForm(S, SeriesAlpha(self), SeriesBeta(self))


Series = Series0

