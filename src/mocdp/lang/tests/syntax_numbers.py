# -*- coding: utf-8 -*-
from .utils import (assert_parsable_to_connected_ndp, assert_semantic_error,
    assert_syntax_error)
from comptests.registrar import comptest
from mocdp.lang.parts import CDPLanguage
from mocdp.lang.syntax import Syntax, parse_ndp
from mocdp.lang.tests.utils import parse_wrap_check
from mocdp.posets import R_Weight
from mocdp.posets.rcomp_units import make_rcompunit
from mocdp.posets.types_universe import get_types_universe
from numpy.testing.utils import assert_allclose

CDP = CDPLanguage

@comptest
def check_numbers1():
    parse_wrap_check('1.0', Syntax.floatnumber, 1.0)
    assert_syntax_error('1', Syntax.floatnumber)
    parse_wrap_check('1', Syntax.integer, 1)
    parse_wrap_check('1', Syntax.integer_or_float, CDP.ValueExpr(1))
    parse_wrap_check('1.0', Syntax.integer_or_float, CDP.ValueExpr(1.0))

@comptest
def check_numbers2():
    parse_wrap_check('1.0 [g]', Syntax.number_with_unit, CDP.SimpleValue(CDP.ValueExpr(1.0),
                                                                         CDP.UnitExpr(R_Weight)))
    assert_syntax_error('1', Syntax.number_with_unit)
    # automatic conversion to float
    parse_wrap_check('1 [g]', Syntax.number_with_unit, CDP.SimpleValue(CDP.ValueExpr(1.0),
                                                                        CDP.UnitExpr(R_Weight)))

@comptest
def check_numbers3():
    # Need connections: don't know the value of a

    assert_parsable_to_connected_ndp("""    
    cdp  {
        requires a [g]
        
        a >= 2 [g]
    }
    """)

@comptest
def check_numbers3_neg():
    assert_semantic_error("""    
    cdp  {
        provides f [g]
        requires r [g]
        
        r >= f * -2 [R]
    }
    """)

ONE_MPH_IN_M_S = 0.44704

@comptest
def check_unit_conversions():
    ndp = parse_ndp("""
    # test connected
cdp {  
      
        requires a [m/s] 
        provides b [m/s]


        sub motor = cdp { 
          provides vel [mph]
          requires vel2 [mph]

          vel2 >= vel + 1 mph
        }


        a >= motor.vel2
        b <= motor.vel
 
}
    
    """)

    dp = ndp.get_dp()

    r = dp.solve(0.0)
    print r
    limit = list(r.minimals)[0]

    # 1 MPH = 0.44704 m / s
    assert_allclose(limit, ONE_MPH_IN_M_S)



@comptest
def check_unit_conversions2():


    tu = get_types_universe()

    A = make_rcompunit('mph')
    B = make_rcompunit('m/s')
    assert not A == B

    tu.check_leq(A, B)
    tu.check_leq(B, A)
    assert not tu.equal(A, B)

    B_from_A, A_from_B = tu.get_embedding(A, B)
    print('B_from_A: %s' % B_from_A)
    print('A_from_B: %s' % A_from_B)

    tu.check_equal(B_from_A.dom, A)
    tu.check_equal(B_from_A.cod, B)
    tu.check_equal(A_from_B.dom, B)
    tu.check_equal(A_from_B.cod, A)

    print('B_from_A: %s  a=1.0 B_from_A(1.0) = %s' % (B_from_A, B_from_A(1.0)))
    assert_allclose(B_from_A(1.0), ONE_MPH_IN_M_S)
    assert_allclose(A_from_B(ONE_MPH_IN_M_S), 1.0)


    ndp = parse_ndp("""
cdp {  
    provides a [m/s] 
    provides b [mph]

    requires c [m/s]
    requires d [mph]

    c >= a + b
    d >= a + b
}
    """)
    print ndp.repr_long()
    dp = ndp.get_dp()
    print dp.repr_long()
    cases = (
      ((0.0, 1.0), (ONE_MPH_IN_M_S, 1.0)),
      ((1.0, 0.0), (1.0, 1.0 / ONE_MPH_IN_M_S)),
    )

    for func, expected in cases:
        print('func: %s   F = %s' % (str(func), dp.get_fun_space()))
        print('expected: %s' % str(expected))
        r = dp.solve(func)
        print('obtained: %s %s' % (str(r), dp.get_res_space()))
        limit = list(r.minimals)[0]
        assert_allclose(limit, expected)

# @comptest
# def check_numbers3_emptyunit():
#     parse_wrap_check('[]', empty_unit, dict(unit=R_dimensionless))
#     parse_wrap_check('1 []', number_with_unit, ValueWithUnits(1, R_dimensionless))


@comptest
def check_type_universe1():

    tu = get_types_universe()

    R1 = make_rcompunit('R')
    R2 = make_rcompunit('R')
    assert R1 == R2

    tu.check_equal(R1, R2)
    tu.check_leq(R1, R2)
    _embed1, _embed2 = tu.get_embedding(R1, R2)


