# -*- coding: utf-8 -*-
from .dp_flatten import Mux
from .dp_identity import Identity
from .primitive import PrimitiveDP
from contracts.utils import indent, raise_desc, raise_wrapped
from mocdp.dp.primitive import Feasible, NormalForm, NotFeasible
from mocdp.exceptions import DPInternalError, do_extra_checks
from mcdp_posets import (Map, PosetProduct, SpaceProduct, UpperSets,
    get_product_compact)
from mocdp.dp.tracer import Tracer


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
            raise_desc(DPInternalError, msg, dp1=self.dp1.repr_long(),
                       dp2=self.dp2.repr_long(), R1=R1, F2=F2)

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

        self._solve_cache = {}
        PrimitiveDP.__init__(self, F=F1, R=R2, M=M)

    def _unpack_m(self, m):
        _M, _, unpack = get_product_compact(self.M1, self.extraM, self.M2)
        # M.belongs(m)
        m1, m_extra, m2 = unpack(m)
        return m1, m_extra, m2

    def evaluate_f_m(self, f1, m):
        """ Returns the resources needed
            by the particular implementation m """
        m1, m_extra, m2 = self._unpack_m(m)

        if isinstance(self.dp1, (Mux, Identity)):
            f2 = self.dp1.evaluate_f_m(f1, m1)
        elif self._is_equiv_to_terminator(self.dp2):
            F2 = self.dp2.get_fun_space()
            f2 = F2.get_top()
        else:
            f2 = m_extra

        r2 = self.dp2.evaluate_f_m(f2, m2)
        return r2

    def get_implementations_f_r(self, f, r):
        f1 = f
        _M, pack, _unpack = get_product_compact(self.M1, self.extraM, self.M2)
        R2 = self.dp2.get_res_space()
        res = set()
        # First let's solve again for r1
        r1s = self.dp1.solve(f)
        for r1 in r1s.minimals:
            m1s = self.dp1.get_implementations_f_r(f1, r1)
            assert m1s, (self.dp1, f1, r1)
            
            f2 = r1
            r2s = self.dp2.solve(f2)
            
            if isinstance(self.dp1, (Mux, Identity)):
                # print('equivalent to identity')
                m_extra = ()  # XXX
            elif self._is_equiv_to_terminator(self.dp2):
                # print('equivalent to _is_equiv_to_terminator')
                m_extra = ()  # XXX
            else:
                m_extra = f2

            for r2 in r2s.minimals:
                if not R2.leq(r2, r):
                    continue
                m2s = self.dp2.get_implementations_f_r(f2, r2)
                # print('Found f1=%s r1=%s r2=%s' % (f1, r1, r2))
                for m1 in m1s:
                    for m2 in m2s:
                        m = pack(m1, m_extra, m2)
                        res.add(m)
        if not res:
            msg = 'The (f,r) pair was not feasible.'
            raise_desc(NotFeasible, msg, f=f, r=r, self=self)


        if do_extra_checks():
            M = self.get_imp_space_mod_res()
            for _ in res:
                M.belongs(_)
        assert res
        return res


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
        trace = Tracer()
        return self.solve_trace(func, trace)

    def solve_trace(self, func, trace):
        if func in self._solve_cache:
            # trace.log('using cache for %s' % str(func))
            return trace.result(self._solve_cache[func])
        trace.values(type='series')
        from mcdp_posets import UpperSet, poset_minima

        with trace.child('dp1') as t:
            u1 = self.dp1.solve_trace(func, t)
        # ressp1 = self.dp1.get_res_space()
        # tr1 = UpperSets(ressp1)
        # tr1.belongs(u1)

        mins = set([])
        for u in u1.minimals:
            with trace.child('dp2') as t:
                v = self.dp2.solve_trace(u, t)
            mins.update(v.minimals)

        ressp = self.get_res_space()
        minimals = poset_minima(mins, ressp.leq)
        # now mins is a set of UpperSets
        # tres = self.get_tradeoff_space()

        us = UpperSet(minimals, ressp)
        # tres.belongs(us)

        # print('solving for %s' % str(func))
        # return us
        self._solve_cache[func] = us
        return trace.result(us)

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

