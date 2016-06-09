# -*- coding: utf-8 -*-
from .utils import ok, sem, syn
from comptests.registrar import comptest
from mocdp.dp.dp_transformations import get_dp_bounds
from mocdp.lang.parse_actions import parse_ndp
from mocdp.lang.parts import CDPLanguage
from mocdp.lang.syntax import Syntax
from mocdp.lang.tests.utils import (assert_parsable_to_connected_ndp,
    assert_semantic_error, parse_wrap_check)
from mocdp.posets.uppersets import UpperSets
from nose.tools import assert_equal

L = CDPLanguage


ok(Syntax.integer_fraction, '1/2', L.IntegerFraction(num=1, den=2))
syn(Syntax.integer_fraction, '1/2.0')
sem(Syntax.integer_fraction, '1/0')
syn(Syntax.integer_fraction, '1/')

exponent = L.exponent('^')

ok(Syntax.power_expr, 'pow(x,1/2)',
    L.Power(op1=L.VariableRef('x'),
            glyph=None,
            exponent=L.IntegerFraction(num=1, den=2)))

ok(Syntax.power_expr, 'x ^ 1/2',
    L.Power(op1=L.VariableRef('x'),
            glyph=exponent,
            exponent=L.IntegerFraction(num=1, den=2)))

ok(Syntax.power_expr, 'x ^ 2',
    L.Power(op1=L.VariableRef('x'),
            glyph=exponent,
            exponent=L.IntegerFraction(num=2, den=1)))

ok(Syntax.power_expr, 'pow(x, 2)',
    L.Power(op1=L.VariableRef('x'),
            glyph=None,
            exponent=L.IntegerFraction(num=2, den=1)))


@comptest
def check_power1():
    assert_parsable_to_connected_ndp("""
    mcdp {
        provides lift [N]
        requires power [W]

        c = 1.0 W / N^2
        power >= (lift ^ 2) * c
    }""")


@comptest
def check_power2():
    assert_parsable_to_connected_ndp("""
    mcdp {
        provides lift [N]
        requires power [W]

        c = 2.0 W / N^2
        power >= pow(lift, 2) * c
    }""")

@comptest
def check_power3():
    assert_parsable_to_connected_ndp("""
    mcdp {
        provides lift [N]
        requires power [W]

        c = 1.0 W / N^2
        power >= (lift ^ 2/1) * c
    }""")

@comptest
def check_power4():
    assert_parsable_to_connected_ndp("""
    mcdp {
        provides lift [N]
        requires power [W]

        c = 2.0 W / N^2
        power >= pow(lift, 2/1) * c
    }""")

@comptest
def check_power5():
    print parse_wrap_check("pow(lift, 2/1)", Syntax.power_expr)
    print parse_wrap_check("pow(lift, 2/1)", Syntax.rvalue)
    print parse_wrap_check("power >= pow(lift, 2/1)", Syntax.constraint_expr_geq)


    assert_semantic_error("""
    mcdp {
        provides lift [N]
        requires power [W]

        power >= pow(lift, 2/1)
    }""")

@comptest
def check_power6():
    pass

@comptest
def check_power7():
    pass

@comptest
def check_power8():  # TODO: move to ther files

    ndp = parse_ndp("""
    mcdp {
      requires a [R]
      requires b [R]
      
      provides c [R]
      
      a + b >= c
    }
    """)
    dp = ndp.get_dp()
    print(dp.repr_long())
    nl = 5
    nu = 5
    dpL, dpU = get_dp_bounds(dp, nl, nu)

    print(dpL.repr_long())
    print(dpU.repr_long())
    f = 10.0
    UR = UpperSets(dp.get_res_space())
    Rl = dpL.solve(f)
    Ru = dpU.solve(f)
    assert_equal(len(Rl.minimals), nl)
    assert_equal(len(Ru.minimals), nu)
    print('Rl: %s' % UR.format(Rl))
    print('Ru: %s' % UR.format(Ru))
    UR.check_leq(Rl, Ru)
    
    import numpy as np
    for x in np.linspace(0, f, 100):
        y = f - x
        p = (x, y)

        Rl.belongs(p)





