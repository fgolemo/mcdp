# -*- coding: utf-8 -*-
from comptests.registrar import comptest
from contracts.utils import raise_desc
from mcdp_lang import parse_constant
from mcdp.exceptions import DPUserAssertion


def expect(exc, f, *args):
    """ exc: Exception or tuple of Exceptions """
    try:
        res = f(*args)
    except exc:
        pass
    else: # pragma: no cover
        msg = 'Expected {}'.format(exc)
        raise_desc(Exception, msg, f=f, res=res)

def exp_ass(s):
    expect(DPUserAssertion, parse_constant, s)

@comptest
def check_asserts1():
    parse_constant('assert_leq(0g, 1g)')
    exp_ass('assert_leq(1g, 0g)')
    
@comptest
def check_asserts2():
    parse_constant('assert_lt(0g, 1g)')
    exp_ass('assert_lt(0g, 0g)')
    

@comptest
def check_asserts3():
    parse_constant('assert_gt(1g, 0g)')
    exp_ass('assert_gt(0g, 0g)')

@comptest
def check_asserts4():
    parse_constant('assert_equal(0g, 0g)')
    parse_constant('assert_equal(1kg, 1000g)')
    exp_ass('assert_equal(0g, 1g)')

@comptest
def check_asserts5():
    parse_constant('assert_nonempty({0g})')
    exp_ass('assert_empty({0g})')

@comptest
def check_asserts6():

    parse_constant('assert_nonempty(solve(<>, mcdp{}))')
    pass

