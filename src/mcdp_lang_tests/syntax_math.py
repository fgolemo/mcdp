# -*- coding: utf-8 -*-
from nose.tools import assert_equal, assert_raises

from comptests.registrar import comptest, comptest_fails, run_module_tests
from mcdp.exceptions import DPSemanticError
from mcdp_lang import parse_constant, parse_ndp, parse_poset
from mcdp_lang.syntax import Syntax, SyntaxBasics
from mcdp_lang_tests.utils import parse_wrap_check
from mcdp_lang_tests.utils2 import eval_rvalue_as_constant, eval_rvalue_as_constant_same_exactly, \
    eval_constant_same_exactly
from mcdp_posets import get_types_universe, Nat, Rcomp


@comptest
def check_subtraction1():
    s = """
    mcdp {
            v1 = 10 g
            v2 = 2 g
            v3 = 1 g
            v = v1 - v2 - v3

            requires x = v
        }
    """
    parse_ndp(s)

    s = """
    mcdp {
     t = instance mcdp {
            v1 = 10 g
            v2 = 2 g
            v3 = 1 g
            v = v1 - v2 - v3

            requires x = v
        }
    }
    """
    parse_ndp(s)

    parse_constant("""
    assert_equal(
        solve(<>, mcdp {
            v1 = 10 g
            v2 = 2 g
            v3 = 1 g
            v = v1 - v2 - v3

            requires x = v
        }),
        upperclosure { 7 g }
    )
    """)

@comptest_fails
def check_subtraction2_contexts_a():
    """ We cannot do propagation of constants inside contexts """
    s = """
    mcdp {
      v2 = 2 g
      t = instance mcdp {
          v1 = 10 g
            v = v1 - v2
            requires x = v
        }
    }
    """
    parse_ndp(s)

@comptest_fails
def check_subtraction2_contexts_b():
    s = """
    mcdp {
          v1 = 10 g
        mcdp {
      v2 = 2 g
      t = instance mcdp {
            v = v1 - v2
            requires x = v
        }
        }
    }
    """
    parse_ndp(s)


@comptest_fails
def check_sums3():
    eval_rvalue_as_constant('int:2 + nat:3')


@comptest_fails
def check_sums4():
    eval_rvalue_as_constant('int:2 + int:4 ')


@comptest_fails
def check_sums5():
    eval_rvalue_as_constant('nat:3 + int:2')


@comptest_fails
def check_sums6():
    eval_rvalue_as_constant('int:2 + nat:3')


@comptest
def check_mult_mixed1():
    eval_rvalue_as_constant_same_exactly('Nat:3 * Nat:2', 'Nat:6')
    eval_rvalue_as_constant_same_exactly('Nat:3 * 2 []', '6 []')
    eval_rvalue_as_constant_same_exactly('Nat:3 * 2 g', '6 g')
    eval_rvalue_as_constant_same_exactly('3 [] * 2 g', '6 g')
    eval_rvalue_as_constant_same_exactly('3 [] * 2 []', '6 []')
    eval_rvalue_as_constant_same_exactly('Nat:3 * 10 []', '30 []')
    eval_rvalue_as_constant_same_exactly('Nat:3 * 10 kg', '30 kg')


@comptest
def check_mult_mixed2():
    tu = get_types_universe()

    dimensionless = parse_poset('dimensionless')
    Nat = parse_poset('Nat')
    # m * s
    ndp = parse_ndp("""
    mcdp {
        provides a [m]
        provides b [s]
        requires x = provided a * provided b
    }
    """)
    M = ndp.get_rtype('x')
    tu.check_equal(M, parse_poset('m*s'))

    # Nat * Nat
    ndp = parse_ndp("""
    mcdp {
        provides a [Nat]
        provides b [Nat]
        requires x = provided a * provided b
    }
    """)
    M = ndp.get_rtype('x')
    tu.check_equal(M, Nat)


    # Nat * []
    ndp = parse_ndp("""
    mcdp {
        provides a [Nat]
        provides b [dimensionless]
        requires x = provided a * provided b
    }
    """)
    M = ndp.get_rtype('x')
    tu.check_equal(M, dimensionless)



@comptest
def check_rcomp1():
    parse_wrap_check('1.05', SyntaxBasics.floatnumber)
    parse_wrap_check('2.05', Syntax.rcomp_constant)
    parse_wrap_check('3.05', Syntax.definitely_constant_value)
    parse_wrap_check('4.05', Syntax.constant_value)

    eval_constant_same_exactly('5.05', 'Rcomp:5.05')


@comptest
def check_nat1():
    parse_wrap_check('1', Syntax.integer_or_float)
    parse_wrap_check('2', Syntax.nat_constant2)
    parse_wrap_check('3', Syntax.definitely_constant_value)
    parse_wrap_check('4', Syntax.constant_value)

    eval_constant_same_exactly('5', 'Nat:5')

@comptest
def check_nat2():
    s = """
    mcdp {
        requires x = 1
    }
    """
    ndp = parse_ndp(s)
    assert_equal(Nat(), ndp.get_rtype('x'))

@comptest
def check_nat3():
    s = """
    mcdp {
        provides x = 1
    }
    """
    ndp = parse_ndp(s)
    assert_equal(Nat(), ndp.get_ftype('x'))

@comptest
def check_rcomp2():
    s = """
    mcdp {
        requires x = 1.0
    }
    """
    ndp = parse_ndp(s)
    assert_equal(Rcomp(), ndp.get_rtype('x'))

@comptest
def check_rcomp3():
    s = """
    mcdp {
        provides x = 1.0
    }
    """
    ndp = parse_ndp(s)
    assert_equal(Rcomp(), ndp.get_ftype('x'))


@comptest
def check_add_mixed_new_syntax():
    eval_rvalue_as_constant_same_exactly('3 + 2', 'Nat: 5')
    eval_rvalue_as_constant_same_exactly('3 + 2.0', 'Rcomp: 5.0')

@comptest
def check_mult_mixed_new_syntax():
    eval_rvalue_as_constant_same_exactly('3 * 2', 'Nat: 6')
    eval_rvalue_as_constant_same_exactly('3 * 2.0', 'Rcomp: 6.0')
    eval_rvalue_as_constant_same_exactly('3 * 2 g', '6 g')
    eval_rvalue_as_constant_same_exactly('3.0 * 2 g', '6 g')
    eval_rvalue_as_constant_same_exactly('3.0 * 2.0', 'Rcomp: 6.0')
    eval_rvalue_as_constant_same_exactly('3 * 10.0', 'Rcomp: 30.0')
    eval_rvalue_as_constant_same_exactly('3 * 10.0 * 1 g', '30 g')

@comptest
def check_misc():
    parse_constant('100 m + 100 km')
    assert_raises(DPSemanticError, parse_constant, '100 m + 100 g')

if __name__ == '__main__':
    run_module_tests()
