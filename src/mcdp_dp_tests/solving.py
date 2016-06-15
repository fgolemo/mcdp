from comptests.registrar import comptest
from mcdp_dp.solver import (ConvergedToEmpty, ConvergedToFinite,
    ConvergedToInfinite, generic_solve)
from mcdp_lang import parse_ndp
from numpy.ma.testutils import assert_equal

def get_problem(gamma, add_mass_limit=None):
    prob = """
    mcdp {  
    provides T [s] 
    provides W0 [kg]
    provides P0 [W]

    sub battery = instance abstract mcdp {
        provides capacity [J] 
        provides one_over_alpha [kg/J]
        requires mass     [kg] 

        mass >= capacity * one_over_alpha
    }

    provides one_over_alpha using battery

    sub actuation = instance abstract mcdp {
        provides lift      [N]
        requires power [W]
        gamma = GAMMA
        power >= square(lift) * gamma 
    }

    energy = (actuation.power + P0) * T
    battery.capacity >= energy

    g = 9.81 m/s^2
     weight = (battery.mass + W0) * g
    actuation.lift >= weight

    requires mass for battery
 
    OTHER 
    }
    """

    if add_mass_limit:
        prob = prob.replace('OTHER', ' battery.mass <= %s' % add_mass_limit)
    else:
        prob = prob.replace('OTHER', '')
    prob = prob.replace('GAMMA', gamma)
    return prob

def get_trace_solution(T, W0, P0, one_over_alpha, gamma, add_mass_limit):
    prob = get_problem(gamma=gamma, add_mass_limit=add_mass_limit)
    ndp = parse_ndp(prob)
    dp = ndp.get_dp()
    f = (T, W0, P0, one_over_alpha)
    trace = generic_solve(dp, f, max_steps=None)
    return trace

@comptest
def check_prob_feasibility_1():
    T = 1.0
    W0 = 1.0
    P0 = 0.0
    one_over_alpha = 1.0  # kg/J
    add_mass_limit = None
    gamma = '1.0 W/N'
    trace = get_trace_solution(T=T, W0=W0, P0=P0, one_over_alpha=one_over_alpha,
                               gamma=gamma, add_mass_limit=add_mass_limit)
    assert_equal(trace.result, ConvergedToInfinite)

@comptest
def check_prob_feasibility_2():
    T = 1.0
    W0 = 1.0
    P0 = 1.0
    one_over_alpha = 1.0  # kg/J
    add_mass_limit = '86 kg'
    gamma = '1.0 W/N'
    trace = get_trace_solution(T=T, W0=W0, P0=P0, one_over_alpha=one_over_alpha,
                               gamma=gamma, add_mass_limit=add_mass_limit)
    assert_equal(trace.result, ConvergedToEmpty)


@comptest
def check_prob_feasibility_3():
    T = 1.0
    W0 = 0.002
    P0 = 0.0001
    one_over_alpha = 1.0  # kg/J
    add_mass_limit = None
    gamma = '1.0 W/N'
    # 0.0009212503585203743
    trace = get_trace_solution(T=T, W0=W0, P0=P0, one_over_alpha=one_over_alpha,
                               gamma=gamma, add_mass_limit=add_mass_limit)

    assert_equal(trace.result, ConvergedToFinite)

    ur = trace.get_r_sequence()[-1]
    print ur.minimals



@comptest
def check_prob_feasibility_4():
    T = 1.0
    W0 = 0.002
    P0 = 0.0001
    one_over_alpha = 1.0  # kg/J
#     add_mass_limit = None
    add_mass_limit = '0.00092 kg'
    gamma = '1.0 W/N'
    # 0.0009212503585203743
    trace = get_trace_solution(T=T, W0=W0, P0=P0, one_over_alpha=one_over_alpha,
                               gamma=gamma, add_mass_limit=add_mass_limit)

    assert_equal(trace.result, ConvergedToEmpty)






