from contracts.utils import indent, raise_desc, raise_wrapped
from mcdp_dp.primitive import Feasible, NotFeasible, PrimitiveDP
from mcdp_dp.tracer import Tracer
from mcdp_posets.poset import NotLeq
from mcdp_posets.poset_product import PosetProduct
from mcdp_posets.space import NotEqual
from mcdp_posets.types_universe import get_types_universe
from mocdp.exceptions import do_extra_checks
from mcdp_posets.uppersets import UpperSets, UpperSet
from mcdp_dp.dp_loop import Iteration
from mcdp_posets.find_poset_minima.baseline_n2 import poset_minima

class DPLoop2(PrimitiveDP):
    """
                  ______
           f1 -> |  dp  |--->r1
           f2 -> |______|---. r2
              `-----[>=]----/
    """
    def __init__(self, dp1):
        self.dp1 = dp1

        F0 = self.dp1.get_fun_space()
        R0 = self.dp1.get_res_space()
        M0 = self.dp1.get_imp_space_mod_res()

        if not isinstance(F0, PosetProduct) or len(F0.subs) != 2:
            msg = 'The function space must be a product of length 2.'
            raise_desc(ValueError, msg, F0=F0)

        if not isinstance(R0, PosetProduct) or len(R0.subs) != 2:
            msg = 'The resource space must be a product of length 2.'
            raise_desc(ValueError, msg, R0=R0)
            
        F1, F2 = F0[0], F0[1]
        R1, R2 = R0[0], R0[1]
        
        tu = get_types_universe()
        
        try:
            tu.check_equal(F2, R2)
        except NotEqual as e:
            msg = ('The second component of function and resource space '
                   'must be equal.')
            raise_wrapped(ValueError, e, msg, F2=F2, R2=R2)

        F = F1
        R = R1
        # M = M0
        # from mcdp_dp.dp_series import prod_make
        from mcdp_dp.dp_series import get_product_compact
        M, _, _ = get_product_compact(M0, F2)
        self.M0 = M0
        self.F1 = F1
        self.F2 = F2
        self.R1 = R1
        self.R2 = R2

        self._solve_cache = {}
        PrimitiveDP.__init__(self, F=F, R=R, M=M)

    def get_implementations_f_r(self, f1, r):
        raise NotImplementedError
        f2 = r
        f = (f1, f2)
        m0s = self.dp1.get_implementations_f_r(f, r)
        options = set()
        from mcdp_dp.dp_series import get_product_compact

        M, M_pack, _ = get_product_compact(self.M0, self.F2)


        for m0 in m0s:
            m = M_pack(m0, r)
            options.add(m)

        if do_extra_checks():
            for _ in options:
                M.belongs(_)

        return options

    def _unpack_m(self, m):
        from mcdp_dp.dp_series import get_product_compact
        _, _, unpack = get_product_compact(self.M0, self.F2)
        m0, f2 = unpack(m)
        return m0, f2

    def evaluate_f_m(self, f1, m):
        """ Returns the resources needed
            by the particular implementation.
            raises NotFeasible 
        """
        raise NotImplementedError
        F2 = self.F2
        F1 = self.F
        m0, f2 = self._unpack_m(m)
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
        raise NotImplementedError
        from mcdp_dp.dp_series import get_product_compact
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
        raise NotImplementedError
        from mcdp_dp.dp_series import get_product_compact
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


    def __repr__(self):
        return 'DPLoop2(%r)' % self.dp1

    def repr_long(self):
        s = 'DPLoop2:   %s -> %s\n' % (self.get_fun_space(), self.get_res_space())
        return s + indent(self.dp1.repr_long(), 'L ')


    def solve(self, f1):
        t = Tracer()
        res = self.solve_trace(f1, t)
        return res

    def solve_trace(self, f1, trace):
        if f1 in self._solve_cache:
            # trace.log('using cache for %s' % str(func))
            return trace.result(self._solve_cache[f1])

        F1 = self.F1
        R1 = self.R1
        R2 = self.R2
        R = self.dp1.R
        dp0 = self.dp1

        if do_extra_checks():
            F1.belongs(f1)


        UR = UpperSets(R)

        trace.values(type='loop2', UR=UR, R=R, dp=self)

        # we consider a set of iterates
        # we start from the bottom
        zero = R2.get_bottom()
        s0 = dp0.solve_trace((f1, zero), trace)
        UR.belongs(s0)
        trace.log('Iterating in UR = %s' % UR)
        trace.log('Starting from %s' % UR.format(s0))

        S = [Iteration(s=s0, converged=set())]
        for i in range(1000000):  # XXX
            with trace.iteration(i) as t:
                si = S[-1].s

                sip, converged = dploop2_iterate(dp0, f1, R, si, t)

                t.values(sip=sip, converged=converged)
                t.log('it %d: sip = %s' % (i, UR.format(sip)))
                t.log('it %d: converged = %s' % (i, UR.format(converged)))

                if do_extra_checks():
                    try:
                        UR.check_leq(si, sip)
                    except NotLeq as e:
                        msg = 'Loop iteration invariant not satisfied.'
                        raise_wrapped(Exception, e, msg, si=si, sip=sip, dp=self.dp1)

                S.append(Iteration(s=sip, converged=converged))

                if UR.leq(sip, si):
                    t.log('Breaking because converged (iteration %s) ' % i)
                    t.log(' solution is %s' % (UR.format(sip)))
                    break


        res = S[-1].s

        trace.log('res: %s' % UR.format(res))
        res = R1.Us(poset_minima([r1 for (r1, _) in res.minimals], leq=R1.leq))

        # Now we have the minimal R2
#         # but the result should be in A(R1)
#
#         r1_res = set()
#         for r2 in r2_res.minimals:
#             hr = dp0.solve_trace((f1, r2), trace)
#             for (r1, r2b) in hr.minimals:
#                 if R2.leq(r2, r2b):
#                     r1_res.add(r1)
#
#         r1_res = poset_minima(r1_res, R1.leq)
#

#         res = R1.Us(r1_res)
#         res = trace.result(solutions_r1)
#         assert isinstance(res, UpperSet)

        self._solve_cache[f1] = res
        return res

def dploop2_iterate(dp0, f1, R, S, trace):
    """ Returns the next iteration  si \in UR 
    
    
        Min ( h(f1, r20) \cup  !r20 ) 
        
    """
    UR = UpperSets(R)
    if do_extra_checks():
        UR.belongs(S)
    R1 = R[0]
    R2 = R[1]
    converged = set()  # subset of solutions for which they converged
    nextit = set()
    # find the set of all r2s
#     r2s = set([r2 for (r1, r2) in S.minimals])

    for (r1, r2) in S.minimals:
        # what are the results of solve(f1, f2)?
        hr = dp0.solve_trace((f1, r2), trace)

        for (r1b, r2b) in hr.minimals:
            valid = R1.leq(r1, r1b)

            if valid:
                nextit.add((r1b, r2b))

                feasible = R2.leq(r2, r2b)
                if feasible:
                    converged.add((r1b, r2b))

    nextit = R.Us(poset_minima(nextit, R.leq))
    converged = R.Us(poset_minima(converged, R.leq))
    # print('iterations: %s' % UR.format(res))
    return nextit, converged

