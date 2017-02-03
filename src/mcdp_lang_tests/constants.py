# -*- coding: utf-8 -*-
from comptests.registrar import comptest_fails, comptest, run_module_tests
from mcdp_lang.parse_interface import parse_constant, parse_ndp
from mcdp_lang.parse_actions import parse_wrap
from mcdp_lang.syntax import Syntax


@comptest_fails
def math_constants3():
    parse_constant('3^2')

@comptest_fails
def math_constants4():
    parse_constant('pi^2')
    
@comptest_fails
def math_constants5():
    parse_constant('π^2')

@comptest
def math_constants5a():
    parse_ndp('''mcdp {
        requires x = π
    }''')

@comptest
def math_constants5b():
    parse_ndp('''mcdp {
        provides x = π
    }''')

@comptest_fails
def math_constants6():
    parse_constant('pow(π, 2)')
    
@comptest_fails
def math_constants9():
    parse_constant('e^2')

@comptest_fails
def math_constants10():
    parse_constant('pow(e, 2)')


@comptest
def math_constants7():
    parse_constant('e')
 
@comptest
def math_constants11():
    parse_constant('e + π')

@comptest
def math_constants12():
    parse_constant('e * π')


@comptest
def math_constants2():
    parse_constant('π')


@comptest
def math_constants1():
    parse_constant('pi')

@comptest
def math_constants13():
    parse_wrap(Syntax.constant_e, 'e')
    parse_wrap(Syntax.constant_pi, 'pi')
    parse_wrap(Syntax.constant_pi, 'π')
    
if __name__ == '__main__': 
    
    run_module_tests()
    
    