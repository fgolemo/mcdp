# -*- coding: utf-8 -*-
from .primitive import PrimitiveDP
from contracts.utils import indent, raise_desc, raise_wrapped
from mocdp.dp.primitive import NormalForm, NotFeasible, Feasible
from mocdp.posets import Map, PosetProduct, UpperSets
from mocdp.exceptions import DPInternalError
from mocdp.posets.space_product import SpaceProduct
from mocdp.dp.dp_identity import Identity
from mocdp.dp.dp_flatten import Mux
from mocdp.posets import get_product_compact


__all__ = [
    'Series',
    'Series0',
]
#
# def only_one_r_from_f():
#     """ This is the test that makes sure we
#  if isinstance(self.dp1, (Mux, Identity)):
#
# def do_not_create_intermediate_M(dp1):
#     from mocdp.lang.parts import GenericNonlinearity
#     if isinstance(dp1, (Mux, Identity, GenericNonlinearity)):
#         return True
#     if isinstance(dp1, Parallel0):
#         return do
#
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


        if isinstance(self.dp1, (Mux, Identity)):
            self.extraM = SpaceProduct(())
        elif self._is_equiv_to_terminator(self.dp2):
            self.extraM = SpaceProduct(())
        else:
            self.extraM = R1
        M, _, _ = get_product_compact(self.M1, self.extraM, self.M2)


        PrimitiveDP.__init__(self, F=F1, R=R2, M=M)
        
    def evaluate_f_m(self, f1, m):
        """ Returns the resources needed
            by the particular implementation m """
        F1 = self.dp1.get_fun_space() 
        F1.belongs(f1)
        M, _, unpack = get_product_compact(self.M1, self.extraM, self.M2)
        M.belongs(m)
        m1, m_extra, m2 = unpack(m)

        if isinstance(self.dp1, (Mux, Identity)):
            f2 = self.dp1.evaluate_f_m(f1, m1)
        elif self._is_equiv_to_terminator(self.dp2):
            F2 = self.dp2.get_fun_space()
            f2 = F2.get_top()
        else:
            f2 = m_extra
                
        r2 = self.dp2.evaluate_f_m(f2, m2)
        return r2

    def _is_equiv_to_terminator(self, dp):
        from mocdp.dp.dp_terminator import Terminator
        if isinstance(dp, Terminator):
            return True
        if isinstance(dp, Mux) and dp.coords == []:
            return True
        return False

    def check_feasible(self, f1, m, r):
        # print('series:check_feasible(%s,%s,%s)' % (f1, m, r))
        M, _, unpack = get_product_compact(self.M1, self.extraM, self.M2)
        M.belongs(m)
        m1, m_extra, m2 = unpack(m)

        comments = ''
        try:
            if isinstance(self.dp1, (Mux, Identity)):
                f2 = self.dp1.evaluate_f_m(f1, m1)
            elif self._is_equiv_to_terminator(self.dp2):
                comments += 'dp2 is terminator'
                # f2 = self.dp1.evaluate_f_m(f1, m1)
                F2 = self.dp2.get_fun_space()
                f2 = F2.get_top()
            else:
                comments += 'Using extra.'
                f2 = m_extra
        except NotFeasible as e:
            msg = 'series: Asking for feasible(f1=%s, m=%s, r=%s)' % (f1, m, r)
            msg += 'First evaluation not feasible.'
            raise_wrapped(NotFeasible, e, msg, comments=comments,
                          dp1=self.dp1.repr_long(), dp2=self.dp2.repr_long())
            
        try:
            self.dp1.check_feasible(f1, m1, f2)
        except NotFeasible as e:
            msg = 'series: Asking for feasible(f1=%s, m=%s, r=%s)' % (f1, m, r)
            msg += '\nFirst one not feasible:'
            msg += '\n  f1 = %s -> [dp1(%s)] <~= f2 = %s ' % (f1, m1, f2)
            raise_wrapped(NotFeasible, e, msg, compact=True, comments=comments,
                          dp1=self.dp1.repr_long(), dp2=self.dp2.repr_long())
 
        if not self._is_equiv_to_terminator(self.dp2):
            try:
                self.dp2.check_feasible(f2, m2, r)
            except NotFeasible as e:
                msg = 'series: Asking for feasible(f1=%s, m=%s, r=%s)' % (f1, m, r)
                msg += '\nFirst one is feasible:'
                msg += '\n  f1 = %s -> [dp1(%s)] <= f2 = %s ' % (f1, m1, f2)
                msg += '\nbut dp2 is *not* feasible:'
                msg += '\n  f2 = %s -> [dp2(%s)] <~= r = %s ' % (f2, m2, r)
                raise_wrapped(NotFeasible, e, msg, compact=True, dp2=self.dp2.repr_long(),
                              dp1=self.dp1.repr_long(), comments=comments)

    def check_unfeasible(self, f1, m, r):
        M, _, unpack = get_product_compact(self.M1, self.extraM, self.M2)
        M.belongs(m)
        m1, m_extra, m2 = unpack(m)
        try:
            if isinstance(self.dp1, (Mux, Identity)):
                r1 = self.dp1.evaluate_f_m(f1, m1)
            elif self._is_equiv_to_terminator(self.dp2):
                F2 = self.dp2.get_fun_space()
                r1 = F2.get_top()
            else:
                r1 = m_extra
        except NotFeasible:
            return  # ok

        try:
            self.dp1.check_unfeasible(f1, m1, r1)
        except Feasible as e1:
            try:
                f2 = r1
                self.dp2.check_unfeasible(f2, m2, r)
            except Feasible as e2:
                msg = 'series: Asking to show unfeasible(f1=%s, m=%s, r=%s)' % (f1, m, r)

                msg += '\nBut! one is feasible:'
                msg += '\n  f1 = %s -> [ m1 = %s ] <= r1 = %s ' % (f1, m1, r1)
                msg += '\n' + indent(self.dp1.repr_long(), '  dp1: ')
                msg += '\n' + indent(str(e1).strip(), ' 1| ')
#                 msg += '\n Then f2 evaluated to f2 = %s. ' % str(f2)
                msg += '\nand two is feasible:'
                msg += '\n  f2 = %s -> [ m2 = %s ] <= r = %s ' % (f2, m2, r)
                msg += '\n' + indent(self.dp2.repr_long(), '  dp2: ')
                msg += '\n' + indent(str(e2).strip(), ' 2| ')
                raise_desc(Feasible, msg)


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

