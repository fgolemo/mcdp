# -*- coding: utf-8 -*-

from nose.tools import assert_equal
from numpy.testing.utils import assert_allclose

from comptests.registrar import comptest, comptest_fails
from mcdp_lang import parse_ndp
from mcdp_lang.parts import CDPLanguage
from mcdp_lang.syntax import Syntax, SyntaxBasics
from mcdp_posets.rcomp_units import make_rcompunit
from mcdp_posets.types_universe import get_types_universe

from .utils import (TestFailed, assert_parsable_to_connected_ndp,
    assert_semantic_error, assert_syntax_error, parse_wrap_check,
    parse_wrap_syntax_error)
from .utils2 import (eval_rvalue_as_constant,
    eval_rvalue_as_constant_same_exactly)


CDP = CDPLanguage

@comptest
def check_numbers1():
    parse_wrap_check('1.0', SyntaxBasics.floatnumber, 1.0)
    assert_syntax_error('1', SyntaxBasics.floatnumber)
    parse_wrap_check('1', SyntaxBasics.integer, 1)
    parse_wrap_check('1', SyntaxBasics.integer_or_float, CDP.ValueExpr(1))
    parse_wrap_check('1.0', SyntaxBasics.integer_or_float, CDP.ValueExpr(1.0))


@comptest
def check_top1():
    eval_rvalue_as_constant('Top Nat')

@comptest
def check_top2():
    eval_rvalue_as_constant('⊤ ℕ')

@comptest
def check_tuples():
    eval_rvalue_as_constant('<1 g, 2J>')
    eval_rvalue_as_constant('⟨1g, 2J⟩')

@comptest
def check_numbers2():
    parse_wrap_check('1.0 [g]', Syntax.valuewithunit,
                     CDP.SimpleValue(CDP.ValueExpr(1.0), CDP.RcompUnit('g')))
    assert_syntax_error('1', Syntax.valuewithunit)
    # automatic conversion to float
    parse_wrap_check('1 [g]', Syntax.valuewithunit,
                      CDP.SimpleValue(CDP.ValueExpr(1.0), CDP.RcompUnit('g')))

@comptest_fails
def check_sum_nat():
    eval_rvalue_as_constant_same_exactly('nat:1 + nat:1', 'nat:2')

@comptest_fails
def check_sum_int():
    eval_rvalue_as_constant_same_exactly('int:1 + int:1', 'int:2')

@comptest_fails
def check_sum_nat_int():
    eval_rvalue_as_constant_same_exactly('int:1 + nat:1', 'int:2')

@comptest
def check_division():
    parse_wrap_check('(5 g)', Syntax.rvalue)
    parse_wrap_check('1.0 [g] / 5 [l]', Syntax.rvalue)
    parse_wrap_check('(5 g) / 5 l', Syntax.rvalue)

    eval_rvalue_as_constant('1.0 [g] / 5 [l]')

@comptest
def check_unit1():

    # parsing as unit_simple
    parse_wrap_syntax_error('N*m', Syntax.pint_unit_simple)
    # parsing as pint_unit:
    parse_wrap_check('N*m', Syntax.space_pint_unit)
    parse_wrap_check('y', Syntax.pint_unit_simple)
    parse_wrap_syntax_error('x', Syntax.pint_unit_simple)
    # unit_base
    parse_wrap_syntax_error('V x m', Syntax.pint_unit_simple)

    nu = Syntax.valuewithunit_number_with_units

    parse_wrap_check('12 W', nu)
    parse_wrap_check('12 Wh', nu)
    parse_wrap_syntax_error('12 W\n h', nu)

    parse_wrap_check('1 / s', Syntax.space_pint_unit)

    
    # print('unit_simple:')
    parse_wrap_syntax_error('V x m', Syntax.pint_unit_simple)

    # print('pint_unit:')
    parse_wrap_syntax_error('V x m', Syntax.space_pint_unit)

    parse_wrap_syntax_error('*', Syntax.space_pint_unit)
    parse_wrap_syntax_error('/', Syntax.space_pint_unit)
    parse_wrap_syntax_error('^2', Syntax.space_pint_unit)
    good = ['g', 'g^2', 'g^ 2', 'g ^ 2', 'm/g ^2',
            'm^2/g^2', 'N*m', '$', 'V', 'A', 'm/s',
            'any', '1/s',
            ]
    results = []
    for g in good:
        try:
            r = parse_wrap_check(g, Syntax.space_pint_unit)
        except TestFailed as e: # pragma: no cover
            results.append((g, False, e, None))
        else:
            results.append((g, True, None, r))

    exceptions = []
    for g, ok, e, r in results:
        if ok:
            print('%20s: OK   %s' % (g, r))
            pass
        if not ok:  # pragma: no cover
            print('%20s: FAIL ' % g)
            
            exceptions.append(e)

    if exceptions:  # pragma: no cover
        msg = "\n".join(str(e) for e in exceptions)
        raise TestFailed(msg)

@comptest
def check_numbers3():

    assert_parsable_to_connected_ndp("""    
    mcdp  {
        provides a [1/s]
        provides b [s]
        
        a * b <= 1 dimensionless
    }
    """)

@comptest
def check_numbers3b():
    # Need connections: don't know the value of a

    assert_parsable_to_connected_ndp("""    
    mcdp  {
        requires a [g]
        
        a >= 2 [g]
    }
    """)

@comptest
def check_numbers3_neg():
    assert_semantic_error("""    
    mcdp  {
        provides f [g]
        requires r [g]
        
        r >= f * -2 dimensionless
    }
    """)

ONE_MPH_IN_M_S = 0.44704

@comptest
def check_unit_conversions():
    ndp = parse_ndp("""
    # test connected
mcdp {  
      
        requires a [m/s] 
        provides b [m/s]

        sub motor = instance mcdp { 
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
mcdp {  
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

@comptest
def check_conversion1():
    ndp = parse_ndp("""
    mcdp {
           provides capacity [J]
           requires mass [kg] # note kg, below is g
    
           a = 1 kg / J
           m0 = 5 g
           mass >= a * capacity + m0
    }""")

    dp = ndp.get_dp()
    print(dp.repr_long())
    print(dp)
    r = dp.solve(0.0)
    print(r)
    assert_equal(r.minimals, set([0.005]))



@comptest
def check_conversion2():
    ndp = parse_ndp("""
    mcdp {
           provides capacity [J]
           requires mass [g] # note grams, above is kg
    
           a = 1 kg / J
           m0 = 5 g
           mass >= a * capacity + m0
    }""")

    dp = ndp.get_dp()
    print(dp.repr_long())
    r = dp.solve(0.0)
    print(r)
    assert_equal(r.minimals, set([5.0]))

@comptest
def check_conversion3():
    #print("How does it work with negative numbers?")

    string = """
    mcdp {
        provides f [g]
        requires r [g]
    
        c = -0.1 kg
        required r >= provided f + c
    }"""

    ndp = parse_ndp(string)

    # same as:
    #  r + 0.1 kg >= f 

    dp = ndp.get_dp()
    #print dp.repr_long()
    r = dp.solve(0.0)
    assert r.minimals == set([0.0]), r
    # one solution for 100 g
    r = dp.solve(100.0)
    assert r.minimals == set([0.0]), r
    r = dp.solve(200.0)
    assert r.minimals == set([100.0]), r



@comptest
def check_conversion3b():
    ndp = parse_ndp("""
    mcdp {
           provides capacity [J]
           requires mass [kg] # note kg, below is g
    
           a = 1 kg / J
           m0 = 0.005 kg
           mass >= a * capacity + m0
    }""")

    dp = ndp.get_dp()
    #print(dp.repr_long())
    r = dp.solve(0.0)
    #print(r)
    assert_equal(r.minimals, set([0.005]))


@comptest
def check_conversion4():
    ndp = parse_ndp("""
    mcdp {
           provides capacity [J]
           requires mass [g] # note grams, above is kg
    
           a = 1 kg / J
           m0 = 0.005 kg # note now in kg
           mass >= a * capacity + m0
    }""")

    dp = ndp.get_dp()
    #print(dp.repr_long())
    r = dp.solve(0.0)
    #print(r)
    assert_equal(r.minimals, set([5.0]))

@comptest
def check_tables():

    parse_wrap_check("duracella | 1.5 V | 5 $ | 0.20 g ",
                     Syntax.catalogue_row)
    parse_wrap_check("duracella | 1.5 V | 5 $ | 0.20 g | 1.5 [mA] * 10 [V]",
                     Syntax.catalogue_row)

@comptest
def alternatives():
    parse_ndp("""
mcdp {
    # two linear response
    # 0J => 0, 0
    # two slutions for 12.5 g
    # 100J =>
    mcdp battery1 = mcdp {
        provides capacity [J]
        requires mass [kg]

        m0 = 5 g
        specific_energy = 1 J / kg 

        mass >=  capacity / specific_energy + m0
    }
    
    mcdp battery2 = mcdp {
        provides capacity [J]
        requires mass [kg]

        m0 = 10 g 
        specific_energy = 0.6 J / kg

        mass >= capacity / specific_energy + m0
    }
    
    sub battery = instance choose(b1: battery1, b2: battery2)

    requires mass for battery
    provides capacity using battery
    
}
""")
