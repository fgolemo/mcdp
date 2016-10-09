from contracts import contract
from mcdp_dp.dp_loop import DPLoop0
from mcdp_posets.uppersets import UpperSet, UpperSets
from mocdp.exceptions import do_extra_checks


MaxStepsReached = 'MaxStepsReached'
ConvergedToFinite = 'ConvergedToFinite'
ConvergedToInfinite = 'ConvergedToTop'
ConvergedToEmpty = 'ConvergedToEmpty'

Allowed = [MaxStepsReached, ConvergedToFinite, ConvergedToInfinite, ConvergedToEmpty]

class SolverTrace():
    
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
        # sequence in UR
        return list(self.rtrace)

    @contract(returns=str)
    def get_result(self):
        return self.result

@contract(returns=SolverTrace)
def generic_solve_by_loop(dp, f, max_steps=None):
    assert isinstance(dp, DPLoop0)

    F = dp.get_fun_space()
    if do_extra_checks():
        F.belongs(f)
    uf = F.U(f)
    R = dp.get_res_space()
    S = UpperSets(R)
    s0 = S.get_bottom()
    print('s0: %s' % str(s0))
    ss = [s0]
    sr = [dp.solveU(s0)]

    print('sr0: %s' % str(sr[0]))

    result = None

    print('Iterating in the space %s' % S)
    for i in range(100000):
        if max_steps:
            if i >= max_steps:
                result = MaxStepsReached
                break

        s_last = ss[-1]
        s_next = beta((uf, s_last))

        print('%d: si  = %s' % (i, S.format(s_next)))

        if S.equal(ss[-1], s_next):
            print('%d: breaking because converged' % i)
            result = ConvergedToFinite
            break

        rn = alpha((uf, s_next))
        # print('%d: rn  = %s' % (i, UR.format(rn)))

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

    if result != MaxStepsReached:
        if sr:
            if not sr[-1].minimals:
                result = ConvergedToEmpty


    return SolverTrace(dp=dp, f=f, strace=ss, rtrace=sr, result=result)


@contract(returns=SolverTrace)
def generic_solve(dp, f, max_steps=None):
    F = dp.get_fun_space()
    if do_extra_checks():
        F.belongs(f)
    uf = F.U(f)
    # UR = UpperSets(dp.get_res_space())

    S, alpha, beta = dp.get_normal_form()

    s0 = S.get_bottom()
    print('s0: %s' % str(s0))
    ss = [s0]
    sr = [alpha((uf, s0))]

    print('sr0: %s' % str(sr[0]))

    result = None

    print('Iterating in the space %s' % S)
    for i in range(100000):
        if max_steps:
            if i >= max_steps:
                result = MaxStepsReached
                break
                 
        s_last = ss[-1]
        s_next = beta((uf, s_last))

        print('%d: si  = %s' % (i, S.format(s_next)))

        if S.equal(ss[-1], s_next):
            print('%d: breaking because converged' % i)
            result = ConvergedToFinite
            break

        rn = alpha((uf, s_next))
        # print('%d: rn  = %s' % (i, UR.format(rn)))
        
        ss.append(s_next)
        sr.append(rn)

        if isinstance(s_next, UpperSet):
            if not s_next.minimals:
                result = ConvergedToEmpty
                break

            if len(s_next.minimals) == 1:
                m1 = list(s_next.minimals)[0]
                if S.P.equal(S.P.get_top(), m1):
                    result = ConvergedToInfinite
                    print('%d: converged to infinite' % i)
                    break

    if result != MaxStepsReached:
        if sr:
            if not sr[-1].minimals:
                result = ConvergedToEmpty

    return SolverTrace(dp=dp, f=f, strace=ss, rtrace=sr, result=result)


