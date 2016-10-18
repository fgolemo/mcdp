# -*- coding: utf-8 -*-
from mcdp_posets.uppersets import UpperSets
from contracts import contract
from mcdp_dp.solver import MaxStepsReached

class SolverApproxTrace():

    def __init__(self, dp, f, strace, rtrace, result):
        assert result in Allowed
        R = dp.get_res_space()
        F = dp.get_fun_space()
        F.belongs(f)
        UR = UpperSets(R)
        S, _, _ = dp.get_normal_form()
        for s in strace:
            S.belongs(s)
        for r in rtrace:
            UR.belongs(r)
        self.S = S
        self.dp = dp
        self.f = f
        self.strace = strace
        self.rtrace = rtrace
        self.result = result


    def get_s_sequence(self):
        return list(self.strace)

    def get_r_sequence(self):
        return list(self.rtrace)

@contract(returns=SolverApproxTrace)
def generic_solve_approx(dp, f, max_steps=None):
    F = dp.get_fun_space()
    F.belongs(f)
    uf = F.U(f)
    UR = UpperSets(dp.get_res_space())

    S, gamma, delta = dp.get_normal_form()

    s0 = S.get_bottom()

    ss_l = [s0]
    ss_u = [s0]
    nl = 0
    nu = 0
    x, y = gamma((uf, s0, nl, nu))
    sr_l = [x]
    sr_u = [y]

    result = None

    for i in range(100000):
        if max_steps:
            if i >= max_steps:
                result = MaxStepsReached
                break

        s_l_last = ss[-1]
        print('Computing step')
        s_l_next, s_u_next = beta((uf, s_last))

        print('%d: si  = %s' % (i, S.format(s_next)))

        if S.equal(ss[-1], s_next):
            print('%d: breaking because converged' % i)
            result = ConvergedToFinite
            break

        rn = alpha((uf, s_next))
        print('%d: rn  = %s' % (i, UR.format(rn)))

        ss.append(s_next)
        sr.append(rn)

        if not s_next.minimals:
            result = ConvergedToEmpty
            break

        if len(s_next.minimals) == 1:
            m1 = list(s_next.minimals)[0]
            if S.P.equal(S.P.get_top(), m1):
                result = ConvergedToInfinite
                break

    if sr:
        if not sr[-1].minimals:
            result = ConvergedToEmpty


    return SolverTrace(dp=dp, f=f, strace=ss, rtrace=sr, result=result)






