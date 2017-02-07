# -*- coding: utf-8 -*-
from nose.tools import assert_almost_equal

from comptests.registrar import run_module_tests, comptest, comptest_fails
from mcdp_dp.dp_transformations import get_dp_bounds
from mcdp_lang import parse_ndp
from mcdp_lang.parse_actions import parse_wrap
from mcdp_lang.syntax import Syntax
from mcdp_lang_tests.utils2 import parse_as_rvalue, parse_as_fvalue
from mcdp_posets import UpperSets, UpperSet


@comptest
def new_uncertainty00():
    s = "10 kg +- 50 g"
    parse_as_rvalue(s)
    

@comptest
def new_uncertainty01():
    s = "10 kg ± 5%"
    parse_as_rvalue(s)
    
@comptest
def new_uncertainty01use():
    s = """mcdp {
        requires r1 = 10 kg ± 50 g
    }
    """
    ndp = parse_ndp(s)
    dp = ndp.get_dp()
    
    dpl, dpu = get_dp_bounds(dp, 1, 1)
    rl = dpl.solve(())
    ru = dpu.solve(())
    
    R = dp.get_res_space()
    UR = UpperSets(R)
    UR.check_equal(rl, UpperSet([9.95], R))
    UR.check_equal(ru, UpperSet([10.05], R))


@comptest
def new_uncertainty01usef():
    s = """mcdp {
        provides f1 = 10 kg ± 50 g
    }
    """
    ndp = parse_ndp(s)
    dp = ndp.get_dp()
    
    dpl, dpu = get_dp_bounds(dp, 1, 1)
    fl = dpl.solve_r(())
    fu = dpu.solve_r(())
    
    assert_almost_equal(list(fl.maximals)[0], 9.95)
    assert_almost_equal(list(fu.maximals)[0], 10.05)


@comptest
def new_uncertainty01buse():
    s = """mcdp {
        requires r1 = 10 kg ± 0.5%
    }
    """
    ndp = parse_ndp(s)
    dp = ndp.get_dp()
    
    dpl, dpu = get_dp_bounds(dp, 1, 1)
    rl = dpl.solve(())
    ru = dpu.solve(())
    assert_almost_equal(list(rl.minimals)[0], 9.95)
    assert_almost_equal(list(ru.minimals)[0], 10.05)

@comptest
def new_uncertainty01b():
    s = "10 kg +- 5%"
    parse_as_rvalue(s)
    
@comptest
def new_uncertainty02():
    s = "between 9.95 kg and 10.05 kg"
    parse_as_rvalue(s)

@comptest
def new_uncertainty03():
    s = "100 $/kWh ± 5%"
    parse_as_rvalue(s)

@comptest
def new_uncertainty04():
    s = "10 kg +- 50 g"
    parse_as_fvalue(s)
    
@comptest
def new_uncertainty05():
    s = "10 kg ± 5%"
    parse_as_fvalue(s)
    
@comptest
def new_uncertainty06():
    s = "between 9.95 kg and 10.05 kg"
    parse_as_fvalue(s)

@comptest
def new_uncertainty07():
    s = "100 $/kWh ± 5%"
    parse_as_fvalue(s)
    
@comptest
def new_uncertainty08():
    s = """mcdp {
        c = 10 kg
        δ = 50 g
        requires r = between c-δ and c+δ
    } """
    parse_ndp(s)
    

@comptest
def new_uncertainty09():
    s = """mcdp {
        c = 10 kg
        δ = 50 g
        provides f = between c-δ and c+δ
    } """
    parse_ndp(s)


@comptest
def new_uncertainty11():
    s = """mcdp {
        c = 10 kg
        δ = 50 g
        requires x = between c-δ and c+δ
    } """
    parse_ndp(s)


@comptest_fails
def new_uncertainty12():
    s = """
    catalogue {
        provides length [m]
        requires weight [g]
        1 m <--| imp |--> 10 kg 
    }
    """
    parse_ndp(s)
    
    parse_wrap(Syntax.catalogue_entry_constant_uncertain, '10 kg +- 50 g')

    s = """
    catalogue {
        provides length [m]
        requires weight [g]
        1 m <--| imp |--> 10 kg +- 50 g
    }
    """
    parse_ndp(s)
    

if __name__ == '__main__': 
    
    run_module_tests()