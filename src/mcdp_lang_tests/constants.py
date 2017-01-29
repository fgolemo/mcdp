# -*- coding: utf-8 -*-
from comptests.registrar import comptest_fails
from mcdp_lang.parse_interface import parse_constant

@comptest_fails
def math_constants1():
    parse_constant('pi')

@comptest_fails
def math_constants2():
    parse_constant('π')

@comptest_fails
def math_constants3():
    parse_constant('3^2')

@comptest_fails
def math_constants4():
    parse_constant('pi^2')
    
@comptest_fails
def math_constants5():
    parse_constant('π^2')

@comptest_fails
def math_constants6():
    parse_constant('pow(π, 2)')
    
@comptest_fails
def math_constants7():
    parse_constant('e')
 
@comptest_fails
def math_constants9():
    parse_constant('e^2')

@comptest_fails
def math_constants10():
    parse_constant('pow(e, 2)')

@comptest_fails
def math_constants11():
    parse_constant('e + π')

@comptest_fails
def math_constants12():
    parse_constant('e * π')
