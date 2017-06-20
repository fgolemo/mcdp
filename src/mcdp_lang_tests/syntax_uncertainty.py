# -*- coding: utf-8 -*-
from comptests.registrar import comptest, run_module_tests, comptest_fails
from contracts.utils import raise_desc
from mcdp_dp.dp_transformations import get_dp_bounds
from mcdp_dp.primitive import WrongUseOfUncertain
from mcdp_lang import parse_ndp
from mcdp_posets import UpperSet, UpperSets
from mcdp_lang.parse_actions import parse_wrap
from mcdp_lang.syntax import Syntax
from mcdp_lang.namedtuple_tricks import recursive_print


@comptest
def check_uncertainty1():
    ndp = parse_ndp("""
        mcdp {
            requires r1 [USD]
            r1 >= Uncertain(1 USD, 2USD)
        }
    """)
    dp = ndp.get_dp()
    dpl, dpu = get_dp_bounds(dp, 1, 1)
    UR = UpperSets(dp.get_res_space())
    f = ()
    sl = dpl.solve(f)
    su = dpu.solve(f)
    UR.check_leq(sl, su)

@comptest
def check_uncertainty2():
    ndp = parse_ndp("""
        mcdp {
            provides f1 [N]
            f1 <= Uncertain(1 N, 2 N)
        }
    """)
    
    dp = ndp.get_dp()
    dpl, dpu = get_dp_bounds(dp, 1, 1)

    R = dp.get_res_space()
    UR = UpperSets(R)
    f0 = 0.0  # N
    sl = dpl.solve(f0)
    su = dpu.solve(f0)
    UR.check_leq(sl, su)
    print sl
    print su

    f0 = 1.5  # N
    sl = dpl.solve(f0)
    su = dpu.solve(f0)
    UR.check_leq(sl, su)
    print sl
    print su
    feasible = UpperSet(set([()]), R)
    infeasible = UpperSet(set([]), R)
    sl_expected = feasible
    su_expected = infeasible
    print sl_expected
    print su_expected
    UR.check_equal(sl, sl_expected)
    UR.check_equal(su, su_expected)



@comptest
def check_uncertainty4():
    """ This will give an error somewhere """
    ndp = parse_ndp("""
mcdp {
    requires r1 [USD]
    r1 >= Uncertain(2 USD, 1 USD)
}

"""
 )
    # > DPSemanticError: Run-time check failed; wrong use of "Uncertain" operator.
    # > l: Instance of <type 'float'>.
    # >    2.0
    # > u: Instance of <type 'float'>.
    # >    1.0
    dp = ndp.get_dp()
    dpl, dpu = get_dp_bounds(dp, 1, 1)

    f = ()
    try:
        dpl.solve(f)
    except WrongUseOfUncertain:
        pass
    else: # pragma: no cover
        msg = 'Expected WrongUseOfUncertain.'
        raise_desc(Exception, msg)

    try:
        dpu.solve(f)
    except WrongUseOfUncertain:
        pass
    else: # pragma: no cover
        msg = 'Expected WrongUseOfUncertain.'
        raise_desc(Exception, msg)


@comptest
def check_uncertainty3():

    s = """
mcdp {
  provides capacity [J]
  requires mass     [kg]

  required mass * Uncertain(2 J/kg, 3 J/kg) >= provided capacity
}
"""
    ndp = parse_ndp(s)
    dp = ndp.get_dp()
    R = dp.get_res_space()
    UR = UpperSets(R)
    dpl, dpu = get_dp_bounds(dp, 100, 100)
    f0 = 1.0  # J
    sl = dpl.solve(f0)
    su = dpu.solve(f0)
    print sl
    print su
    UR.check_leq(sl, su)

    real_lb = UpperSet(set([0.333333]), R)
    real_ub = UpperSet(set([0.500000]), R)

    # now dpl will provide a lower bound from below
    UR.check_leq(sl, real_lb)
    # and dpu will provide the upper bound from above
    UR.check_leq(real_ub, su)


@comptest
def check_uncertainty5():

    s = """
mcdp {
  provides capacity [Wh]
  requires mass     [kg]

  required mass * Uncertain(100 Wh/kg, 120 Wh/kg) >= provided capacity

}"""
    ndp = parse_ndp(s)
    dp = ndp.get_dp()
    R = dp.get_res_space()
    UR = UpperSets(R)
    dpl, dpu = get_dp_bounds(dp, 1000, 1000)
    f0 = 1.0  # J
    sl = dpl.solve(f0)
    su = dpu.solve(f0)
    UR.check_leq(sl, su)
#     print sl
#     print su


from mcdp_tests import logger

@comptest
def check_uncertainty7_uncertain():
    string = "energy_density = between 1 and 2"
    parse_wrap(Syntax.setname_constant_uncertain, string)
    expr = parse_wrap(Syntax.line_expr, string)[0]
    logger.debug('TMP:\n'+ recursive_print(expr))
    
    s = """
    mcdp {
        provides capacity [m]
        requires mass [m]
        energy_density = between 1 and 2
        required mass * energy_density >= provided capacity 
    }
    """
    parse_ndp(s)
    
@comptest
def check_uncertainty7():
    s = """
    mcdp {
        provides capacity [m]
        requires mass [m]
        energy_density = 1 # nat
        required mass * energy_density >= provided capacity 
    }
    """
    parse_ndp(s)
    
    
@comptest
def check_uncertainty8():
    s = """
    mcdp {
        provides capacity [m]
        requires mass [m]
        energy_density = between 1 and 2
        required mass  >= provided capacity * energy_density 
    }
    """
    parse_ndp(s)
    
    
@comptest 
def check_uncertainty6():
    s = """
    mcdp {
        provides capacity [kWh]
        requires mass [g]
        requires cost [$]
        energy_density = between 140 kWh/kg and 160 kWh/kg
        required mass * energy_density >= provided capacity 
    }
    """
    parse_ndp(s)
    
#     s = """
# mcdp {
#   provides capacity [J]
#   requires mass     [kg]
#
#   required mass * Uncertain(100 J/kg, 120 J/kg) >= provided capacity
#
# }"""
#     ndp = parse_ndp(s)
#     dp = ndp.get_dp()
#     dpl, dpu = get_dp_bounds(dp, 100, 100)
#     f0 = 1.0  # J
#     sl = dpl.solve(f0)
#     su = dpu.solve(f0)
#     print sl
#     print su

if __name__ == '__main__':
    run_module_tests()
