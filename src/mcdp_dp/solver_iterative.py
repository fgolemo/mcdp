from contracts import contract
from mcdp_dp.solver import SolverTrace
from mocdp.exceptions import do_extra_checks
from mcdp_dp.dp_transformations import get_dp_bounds
from mcdp_posets.uppersets import UpperSets

def solver_iterative(dp, f, tracer):
    F = dp.get_fun_space()
    R = dp.get_res_space()
    UR = UpperSets(R)
    if do_extra_checks():
        F.belongs(f)
    uf = F.U(f)

    r0 = R.U(R.get_bottom())
    for i in range(10):
        with tracer.child('it%d' % i) as ti:
            n = i + 1
            nl = n
            nu = n
            dpL, dpU = get_dp_bounds(dp, nl, nu)

            with ti.child('dpL') as t:
                rL = dpL.solve_trace(f, t)
            with ti.child('dpU') as t:
                rU = dpU.solve_trace(f, t)

            ti.log('rL: %s' % UR.format(rL))
            ti.log('rU: %s' % UR.format(rU))


    return res
