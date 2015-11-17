# -*- coding: utf-8 -*-
from .primitive import PrimitiveDP
from contracts.utils import indent, raise_desc, raise_wrapped
from mocdp.dp.primitive import Feasible, NotFeasible
from mocdp.posets import Map, NotLeq, PosetProduct, UpperSet, UpperSets
from mocdp.posets.utils import poset_minima
import itertools
from collections import namedtuple


__all__ = [
    'DPLoop0',
    'make_loop',
]

def make_loop(dp):
    from mocdp.dp.dp_series_simplification import unwrap_series
    from mocdp.dp.dp_series_simplification import wrap_series
    from mocdp.dp.dp_flatten import Mux
    from mocdp.dp.dp_series_simplification import make_series
    from mocdp.dp.dp_identity import Identity
    from mocdp.dp.dp_parallel_simplification import make_parallel

    dps = unwrap_series(dp)

    if len(dps) > 1 and isinstance(dps[-1], Mux):
        # Loop( Series(S, mux) ) = Series(Loop( Series(Parallel(Id, mux), S) ), mux)
        F1 = dp.get_fun_space()[0]
        first = make_parallel(Identity(F1), dps[-1])
        x = wrap_series(first.get_fun_space(), [first] + dps[:-1])
        return make_series(make_loop(x), dps[-1])
    
    return DPLoop0(dp)


class DPLoop0(PrimitiveDP):
    """
        This is the version in the papers
                  ______
           f1 -> |  dp  |--->r
           f2 -> |______| |
              `-----------/
    """
    def __init__(self, dp1):
        from mocdp import get_conftools_dps

        library = get_conftools_dps()
        _, self.dp1 = library.instance_smarter(dp1)

        F0 = self.dp1.get_fun_space()
        R0 = self.dp1.get_res_space()
        M0 = self.dp1.get_imp_space_mod_res()

        if not isinstance(F0, PosetProduct):
            raise ValueError('Funsp is not a product: %r' % F0)

        if len(F0) != 2:
            raise ValueError('funsp needs to be length 2: %s' % F0)

        F1 = F0[0]
        F2 = F0[1]

        if not(F2 == R0):
            raise_desc(ValueError, "Spaces incompatible for loop",
                       funsp=F0, ressp=R0)

        F = F1
        R = R0
        # M = M0
        # from mocdp.dp.dp_series import prod_make
        from mocdp.dp.dp_series import get_product_compact
        M, _, _ = get_product_compact(M0, F2)
        PrimitiveDP.__init__(self, F=F, R=R, M=M)
        self.M0 = M0
        self.F2 = F2

    def evaluate_f_m(self, f1, m):
        """ Returns the resources needed
            by the particular implementation.
            raises NotFeasible 
        """
        from mocdp.dp.dp_series import get_product_compact
        F2 = self.F2
        F1 = self.F

        _, _, unpack = get_product_compact(self.M0, self.F2)
        m0, f2 = unpack(m)
        f = (f1, f2)
        r = self.dp1.evaluate_f_m(f, m0)
        try:
            F2.check_leq(r, f2)
        except NotLeq as e:
            msg = 'Loop constraint not satisfied %s <= %s not satisfied.' % (F2.format(r), F2.format(f2))
            msg += "\n f1 = %10s -->| ->[ %s ] --> %s " % (F1.format(f1), self.dp1, F2.format(r))
            msg += "\n f2 = %10s -->|" % F2.format(f2)
            raise_wrapped(NotFeasible, e, msg, compact=True)

        self.R.belongs(r)
        return r

    def check_unfeasible(self, f1, m, r):
        from mocdp.dp.dp_series import get_product_compact
        F2 = self.F2
        F1 = self.F

        M, _, unpack = get_product_compact(self.M0, F2)
        M.belongs(m)
        m0, f2 = unpack(m)
        f = (f1, f2)

        try:
            self.dp1.check_unfeasible(f, m0, r)
        except Feasible as e:
            used = self.dp1.evaluate_f_m(f, m0)
            if F2.leq(used, f2):
                msg = 'loop: asking to show it is unfeasible (%s, %s, %s)' % (f1, m, r)
                msg += '\nBut inner is feasible and loop constraint *is* satisfied.'
                msg += "\n f1 = %10s -->| ->[ m0= %s ] --> %s <= %s" % (F1.format(f1), self.M0.format(m0),
                                                                    F2.format(used), F2.format(r))
                msg += "\n f2 = %10s -->|" % F2.format(f2)
                raise_wrapped(Feasible, e, msg, compact=True, dp1=self.dp1.repr_long())

    def check_feasible(self, f1, m, r):
        from mocdp.dp.dp_series import get_product_compact
        F2 = self.F2
        F1 = self.F

        M, _, unpack = get_product_compact(self.M0, F2)
        M.belongs(m)
        m0, f2 = unpack(m)
        f = (f1, f2)

        try:
            self.dp1.check_feasible(f, m0, r)
        except NotFeasible as e:
            msg = 'loop: Asking loop if feasible (f1=%s, m=%s, r=%s)' % (f1, m, r)
            msg += '\nInternal was not feasible when asked for (f=%s, m0=%s, r=%r)' % (f, m0, r)
            raise_wrapped(NotFeasible, e, msg, dp1=self.dp1.repr_long(), compact=True)

        used = self.dp1.evaluate_f_m(f, m0)
        if F2.leq(used, f2):
            pass
        else:
            msg = 'loop: Asking loop to show feasible (f1=%s, m=%s, r=%s)' % (f1, m, r)
            msg += '\nbut loop constraint is *not* satisfied.'
            msg += "\n f1 = %10s -->| ->[ %s ] --> used = %s <= r = %s" % (F1.format(f1), self.dp1,
                                                                F2.format(used), F2.format(r))
            msg += "\n f2 = %10s -->|" % F2.format(f2)
            raise_desc(NotFeasible, msg)

#
#     def is_feasible(self, f1, m, r):
#         from mocdp.dp.dp_series import get_product_compact
#         _, _, unpack = get_product_compact(self.M0, self.F2)
#         m0, f2 = unpack(m)
#         f = (f1, f2)
#         print('checking feasilbility for loop')
#         print('f = %s' % str(f))
#         print('m0 = %s, f2 = %s' % (m0, f2))
#
#         if not self.dp1.is_feasible(f, m0, r):
#             print('The internal one is not feasibile with (%s, %s, %s)' % (f, m0, r))
#             return False
#         used = self.evaluate_f_m(f, m0)
#         print('used = %s' % str(used))
#         ok1 = self.R.leq(used, r)
#         ok2 = self.R.leq(r, f2)
#         print('ok1 = %s' % ok1)
#         print('ok2 = %s' % ok2)
#         return ok1 and ok2

    def get_normal_form(self):
        """
            S0 is a Poset
            alpha0: U(F0) x S0 -> UR
            beta0:  U(F0) x S0 -> S0
        """

        S0, alpha0, beta0 = self.dp1.get_normal_form()

        F = self.dp1.get_fun_space()
        R = self.dp1.get_res_space()
        F1 = F[0]
        UR = UpperSets(R)

#         S = PosetProduct((S0, UR))

        # from mocdp.dp.dp_series import prod_make
        # S = prod_make(S0, UR)
        from mocdp.dp.dp_series import get_product_compact
        S, pack, unpack = get_product_compact(S0, UR)

        UF1 = UpperSets(F1)
#         UR1 = UpperSets(self.R1)
        F1R = PosetProduct((F1, R))
        UF1R = UpperSets(F1R)

#         UR1R2 = UpperSets(PosetProduct((self.R1, R2)))
#         from mocdp.dp.dp_series import prod_get_state

        """
        S = S0 x UR is a Poset
        alpha: UF1 x S -> UR
        beta: UF1 x (S0 x UR) -> (S0 x UR)
"""
        class DPAlpha(Map):
            def __init__(self, dp):
                self.dp = dp

                dom = PosetProduct((UF1, S))
                cod = UR
                Map.__init__(self, dom, cod)

            def _call(self, x):
                (fs, s) = x
                (s0, rs) = unpack(s)

                # fs is an upper set of F1
                UF1.belongs(fs)
                # rs is an upper set of R2
                UR.belongs(rs)

                # alpha0: U(F0) x S0 -> U(R0)
                # alpha0: U(F1xR2) x S0 -> U(R1xR2)
                #print('rs: %s' % rs)
                #print('fs: %s' % fs)
                # make the dot product
                #print set(itertools.product(fs.minimals, rs.minimals))

                solutions = set()
                # for each r
                for f2 in rs.minimals:
                    # take the product

                    x = UpperSet(set((_, f2) for _ in fs.minimals), F1R)
                    # this is an elment of U(F1xR)
                    UF1R.belongs(x)

                    # set(itertools.product(fs.minimals, rs.minimals)), F1R)
                    # get what alpha0 says
                    y0 = alpha0((x, s0))
                    # this is in UR
                    UR.belongs(y0)
                    
                    # now check which ones are ok
                    for r in y0.minimals:
                        if R.leq(r, f2):
                            solutions.add(r)
                 
                u = poset_minima(solutions, R.leq)
                a1 = UpperSet(u, R)
                return a1


        class DPBeta(Map):
            def __init__(self, dp):
                self.dp = dp

                dom = PosetProduct((UF1, S))
                cod = S
                Map.__init__(self, dom, cod)

            def _call(self, x):
                # beta0: U(F0) x S0 -> S0
                # beta0: U(F1xR1) x S0 -> S0

                # beta: UF1 x S -> S
                # beta: UF1 x (S0 x UR) -> (S0 x UR)
                fs, s = x
                # (s0, rs) = prod_get_state(S0, UR, s)
                (s0, rs) = unpack(s)

                # fs is an upper set of F1
                UF1.belongs(fs)
                # rs is an upper set of R2
                UR.belongs(rs)

                # print('loop-beta: product of %s and %s' % (fs, rs))
                # make the dot product
                x = UpperSet(set(itertools.product(fs.minimals, rs.minimals)), F1R)
                # this is an elment of U(F1xR2)
                UF1R.belongs(x)

                # get what beta0 says
                s0p = beta0((x, s0))

                # get what alpha0 says
                y0 = alpha0((x, s0))
                # this is in UR1R2
                UR.belongs(y0)

                res = pack(s0p, y0)
                # beta: UF1 x (S0 x UR)  -> (S0 x UR)
                #       <fs , <s0, rs>> |->
#
#                 alls = set()
#                 for f1 in fs.minimals:
#                     rs2 = iterate(self.dp, f1, R, rs)
#                     UR.belongs(rs2)
#                     alls.extend(rs2.minimals)
#                 u = poset_minima(alls, R.leq)

                    # F1 x UR -> UR

                return res

        return S, DPAlpha(self), DPBeta(self)

    def __repr__(self):
        return 'DPLoop0(%s)' % self.dp1

    def repr_long(self):
        s = 'DPLoop0:   %s -> %s\n' % (self.get_fun_space(), self.get_res_space())
        return s + indent(self.dp1.repr_long(), 'L ')


    def solve(self, f1):
        trace = self.solve_trace(f1)
        return trace[-1].s

    def solve_trace(self, f1):
        F = self.dp1.get_fun_space()
        F1 = F[0]
        F1.belongs(f1)
        R = self.dp1.get_res_space()

        UR = UpperSets(R)

        # we consider a set of iterates
        # we start from the bottom
        s0 = UR.get_bottom()

        print('Iterating in UR = %s' % UR)
        print('Starting from %s' % UR.format(s0))

        S = [Iteration(s=s0, converged=set())]
        for i in range(100):  # XXX
            si = S[-1].s
            sip, converged = iterate(self.dp1, f1, R, si)
            print('it %d: %s' % (i, UR.format(sip)))
            try:
                UR.check_leq(si, sip)
            except NotLeq as e:
                msg = 'Loop iteration invariant not satisfied.'
                raise_wrapped(Exception, e, msg, si=si, sip=sip, dp=self.dp1)

            S.append(Iteration(s=sip, converged=converged))

            if UR.leq(sip, si):
                print('Breaking because converged (iteration %s) ' % i)
                print(' solution is %s' % (UR.format(sip)))
                break

        return S

def iterate(dp0, f1, R, si):
    """ Returns the next iteration  si \in UR 
    
        ?: F1 x UR -> UR
    """
    # compute the product
    UR = UpperSets(R)
    UR.belongs(si)

    solutions = set()
    converged = set()  # subset of solutions for which they converged
    # for each f2 in si
    for f2 in si.minimals:
        # what are the results of solve(f1, f2)?
        result = _solve1(R, f1, f2, dp0=dp0)
        # print('f2 = %s -> %s' % (f2, UR.format(result)))
        solutions.update(result.minimals)
        if f2 in result.minimals:
            converged.add(f2)

    if not solutions:
        print('No viable solutions asking f1 = %s and si = %s' % (f1, si))
    u = poset_minima(solutions, R.leq)

    res = R.Us(u)
    # print('iterations: %s' % UR.format(res))
    return res, converged


def _solve1(R, f1, f2, dp0):
    result = set()
    res = dp0.solve((f1, f2))
    for r in res.minimals:
        if R.leq(f2, r):
            # f1  ->|    | r
            #       | dp1|----->
            # f2 |->|____|   |
            #     `----(>=)--/
            result.add(r)
    return R.Us(result)
Iteration = namedtuple('Iteration', 's converged')
                        
