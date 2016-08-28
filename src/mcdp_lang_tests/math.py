# -*- coding: utf-8 -*-
from .utils2 import eval_rvalue_as_constant
from comptests.registrar import comptest, comptest_fails
from mcdp_lang.parse_interface import parse_constant, parse_ndp
from mocdp.exceptions import DPSemanticError


@comptest
def check_subtraction1():
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
def check_subtraction2():
    """ Underflow in constants """
    try:
        parse_constant("""
        solve(<>, mcdp {
            v1 = 10 g
            v2 = 2 g
            v3 = 9 g
            v = v1 - v2 - v3 
            
            requires x >= v
        })
    
    """)
    except DPSemanticError as e:
        print e
    else:
        raise Exception()


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

