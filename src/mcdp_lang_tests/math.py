# -*- coding: utf-8 -*-
from comptests.registrar import comptest, comptest_fails
from mcdp_lang import parse_constant, parse_ndp, parse_poset
from mcdp_posets import get_types_universe

from .utils2 import eval_rvalue_as_constant, eval_rvalue_as_constant_same_exactly


@comptest
def check_subtraction1():
    s = """
    mcdp {
            v1 = 10 g
            v2 = 2 g
            v3 = 1 g
            v = v1 - v2 - v3 
            
            requires x >= v
        }
    """
    print parse_ndp(s)
    
    s = """
    mcdp {
     t = instance mcdp {
            v1 = 10 g
            v2 = 2 g
            v3 = 1 g
            v = v1 - v2 - v3 
            
            requires x >= v
        }
    }
    """
    print parse_ndp(s)
    
    parse_constant("""
    assert_equal(
        solve(<>, mcdp {
            v1 = 10 g
            v2 = 2 g
            v3 = 1 g
            v = v1 - v2 - v3 
            
            requires x >= v
        }),
        upperclosure { 7 g }
    )
    """)
    
@comptest
def check_subtraction2_contexts(): 

    s = """
    mcdp {
      v2 = 2 g
      t = instance mcdp {
          v1 = 10 g
            v = v1 - v2        
            requires x >= v
        }
    }
    """
    print parse_ndp(s)
    
    s = """
    mcdp {
          v1 = 10 g
        mcdp {
      v2 = 2 g
      t = instance mcdp {
            v = v1 - v2        
            requires x >= v
        }
        }
    }
    """
    print parse_ndp(s)
    

# @comptest
# def check_subtraction2():
#     """ Underflow in constants """
#     try:
#         parse_constant("""
#         solve(<>, mcdp {
#             v1 = 10 g
#             v2 = 2 g
#             v3 = 9 g
#             v = v1 - v2 - v3 
#             
#             requires x >= v
#         })
#     
#     """)
#     except DPSemanticError as e:
#         print e
#     else:
#         raise Exception()


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
#     def check(s, value,):
#         ndp = parse_ndp(s)
#         dp = ndp.get_dp()
#         return dp
    tu = get_types_universe()

    dimensionless = parse_poset('R')
    Nat = parse_poset('Nat')
    # m * s
    ndp = parse_ndp(""" 
    mcdp {
        provides a [m]
        provides b [s]
        requires x >= a * b
    }
    """)
    M = ndp.get_rtype('x')
    tu.check_equal(M, parse_poset('m*s'))

    # Nat * Nat
    ndp = parse_ndp(""" 
    mcdp {
        provides a [Nat]
        provides b [Nat]
        requires x >= a * b
    }
    """)
    M = ndp.get_rtype('x')
    tu.check_equal(M, Nat)


    # Nat * []
    ndp = parse_ndp(""" 
    mcdp {
        provides a [Nat]
        provides b [R]
        requires x >= a * b
    }
    """)
    M = ndp.get_rtype('x')
    tu.check_equal(M, dimensionless)





@comptest
def check_mult_mixed3():
    pass


@comptest
def check_mult_mixed4():
    pass


@comptest
def check_mult_mixed5():
    pass


@comptest
def check_mult_mixed6():
    pass


@comptest
def check_mult_mixed7():
    pass


@comptest
def check_mult_mixed8():
    pass

