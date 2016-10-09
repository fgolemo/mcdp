# -*- coding: utf-8 -*-
from comptests.registrar import comptest
from contracts.utils import raise_desc
from mcdp_lang import parse_constant
from mocdp.exceptions import DPUserAssertion


def expect(exc, f, *args):
    """ exc: Exception or tuple of Exceptions """
    try:
        res = f(*args)
    except exc:
        pass
    else:
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

@comptest
def check_asserts7():
    pass

@comptest
def check_asserts8():
    pass

@comptest
def check_asserts9():
    pass

@comptest
def check_asserts10():
    pass

@comptest
def check_asserts11():
    pass

@comptest
def check_asserts12():
    pass

@comptest
def check_asserts13():
    pass

@comptest
def check_asserts14():
    pass

@comptest
def check_asserts15():
    pass

@comptest
def check_asserts16():
    pass

@comptest
def check_asserts17():
    pass

@comptest
def check_asserts18():
    pass

@comptest
def check_asserts19():
    pass

@comptest
def check_asserts20():
    pass

