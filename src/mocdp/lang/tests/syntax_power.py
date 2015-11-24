from .utils import ok, sem, syn
from mocdp.lang.parts import CDPLanguage
from mocdp.lang.syntax import Syntax
from comptests.registrar import comptest
from mocdp.lang.parse_actions import parse_ndp
from mocdp.lang.tests.utils import assert_parsable_to_connected_ndp, \
    assert_semantic_error, parse_wrap_check

L = CDPLanguage


ok(Syntax.integer_fraction, '1/2', L.IntegerFraction(num=1, den=2))
syn(Syntax.integer_fraction, '1/2.0')
sem(Syntax.integer_fraction, '1/0')
syn(Syntax.integer_fraction, '1/')

ok(Syntax.power_expr, 'pow(x,1/2)',
    L.Power(op1=L.VariableRef('x'),
            exponent=L.IntegerFraction(num=1, den=2)))

ok(Syntax.power_expr, 'x ^ 1/2',
    L.Power(op1=L.VariableRef('x'),
            exponent=L.IntegerFraction(num=1, den=2)))

ok(Syntax.power_expr, 'x ^ 2',
    L.Power(op1=L.VariableRef('x'),
            exponent=int(2)))

ok(Syntax.power_expr, 'pow(x, 2)',
    L.Power(op1=L.VariableRef('x'),
            exponent=int(2)))


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
def check_power8():
    pass
