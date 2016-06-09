# -*- coding: utf-8 -*-
from .utils import (assert_parsable_to_connected_ndp, assert_semantic_error,
    assert_syntax_error)
from comptests.registrar import comptest
from mocdp.comp.context import Context
from mocdp.lang.eval_constant_imp import eval_constant
from mocdp.lang.parse_actions import parse_wrap
from mocdp.lang.parts import CDPLanguage
from mocdp.lang.syntax import Syntax, parse_ndp
from mocdp.lang.tests.utils import (TestFailed, parse_wrap_check,
    parse_wrap_syntax_error)
from mocdp.posets.rcomp_units import make_rcompunit
from mocdp.posets.types_universe import get_types_universe
from nose.tools import assert_equal
from numpy.testing.utils import assert_allclose

def valid_constant(s):
    """ Evaluates as a constant value (= constant resource) """
    parsed = parse_wrap(Syntax.rvalue, s)[0]
    context = Context()
    return eval_constant(parsed, context)

CDP = CDPLanguage

@comptest
def check_numbers1():
    parse_wrap_check('1.0', Syntax.floatnumber, 1.0)
    assert_syntax_error('1', Syntax.floatnumber)
    parse_wrap_check('1', Syntax.integer, 1)
    parse_wrap_check('1', Syntax.integer_or_float, CDP.ValueExpr(1))
    parse_wrap_check('1.0', Syntax.integer_or_float, CDP.ValueExpr(1.0))


    print valid_constant('5 W')
    print valid_constant('Top Nat')
    print valid_constant('⊤ ℕ')

    print valid_constant('<1 g, 2J>')
    print valid_constant('⟨1g, 2J⟩')



@comptest
def check_numbers2():
    parse_wrap_check('1.0 [g]', Syntax.number_with_unit,
                     CDP.SimpleValue(CDP.ValueExpr(1.0), CDP.RcompUnit('g')))
    assert_syntax_error('1', Syntax.number_with_unit)
    # automatic conversion to float
    parse_wrap_check('1 [g]', Syntax.number_with_unit,
                      CDP.SimpleValue(CDP.ValueExpr(1.0), CDP.RcompUnit('g')))

@comptest
def check_division():
    print parse_wrap_check('(5 g)', Syntax.rvalue)
    c = parse_wrap_check('1.0 [g] / 5 [l]', Syntax.rvalue)
    print parse_wrap_check('(5 g) / 5 l', Syntax.rvalue)

    context = Context()
    r = eval_constant(c, context)
    print r


@comptest
def check_unit1():

    print('parsing as unit_simple:')
    print parse_wrap_syntax_error('N*m', Syntax.pint_unit_simple)
    print('parsing as pint_unit:')
    print parse_wrap_check('N*m', Syntax.pint_unit)
    parse_wrap_check('y', Syntax.pint_unit_simple)
    parse_wrap_syntax_error('x', Syntax.pint_unit_simple)
    parse_wrap_check('x', Syntax.disallowed)
    print('unit_base:')
    parse_wrap_syntax_error('V x m', Syntax.pint_unit_simple)

    nu = Syntax.number_with_unit3
#     Syntax.space_expr.setWhiteSpaceChars(' \t')
    print('skip: %r white: %r copydef: %r' % (nu.skipWhitespace, nu.whiteChars,
            nu.copyDefaultWhiteChars))
    parse_wrap_check('12 W', nu)
    parse_wrap_check('12 Wh', nu)
    parse_wrap_syntax_error('12 W\n h', nu)




    
    if True:
        print('unit_simple:')
        parse_wrap_syntax_error('V x m', Syntax.pint_unit_simple)

        print('pint_unit:')
        parse_wrap_syntax_error('V x m', Syntax.pint_unit)

        parse_wrap_syntax_error('*', Syntax.pint_unit)
        parse_wrap_syntax_error('/', Syntax.pint_unit)
        parse_wrap_syntax_error('^2', Syntax.pint_unit)
        good = ['g', 'g^2', 'g^ 2', 'g ^ 2', 'm/g ^2',
                'm^2/g^2', 'N*m', '$', 'V', 'A', 'm/s',
                'any',
                ]
        results = []
        for g in good:
            try:
                r = parse_wrap_check(g, Syntax.pint_unit)
            except TestFailed as e:
                results.append((g, False, e, None))
            else:
                results.append((g, True, None, r))

        exceptions = []
        for g, ok, e, r in results:
            if ok:
                print('%20s: OK   %s' % (g, r))
            if not ok:
                print('%20s: FAIL ' % g)
                exceptions.append(e)

        if exceptions:
            msg = "\n".join(str(e) for e in exceptions)
            raise TestFailed(msg)



@comptest
def check_numbers3():
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
        
        r >= f * -2 [R]
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
    ndp = parse_ndp("""
    mcdp {
           provides capacity [J]
           requires mass [kg] # note kg, below is g
    
           a = 1 kg / J
           m0 = 0.005 kg
           mass >= a * capacity + m0
    }""")

    dp = ndp.get_dp()
    print(dp.repr_long())
    r = dp.solve(0.0)
    print(r)
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
    print(dp.repr_long())
    r = dp.solve(0.0)
    print(r)
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
    
    sub battery = instance (battery1 ^ battery2)

    requires mass for battery
    provides capacity using battery
    
}
""")


@comptest
def check_sums1():
    valid_constant('int:2 + int:2 ')

@comptest
def check_sums2():
    valid_constant('nat:2 + int:2')

