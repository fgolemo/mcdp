# -*- coding: utf-8 -*-
from comptests.registrar import comptest, run_module_tests
from mcdp_lang.parse_actions import parse_wrap
from mcdp_lang.parse_interface import parse_ndp
from mcdp_lang.syntax import Syntax


@comptest
def sum01():
    s = """
    mcdp {
        
        a = instance mcdp {
            requires mass = 10 g
        }

        b = instance mcdp {
            requires mass = 10 g
        }
    
        requires mass = sum mass required by *  
    }
    
    """
    parse_ndp(s)

@comptest
def sum02():
    s = """
    mcdp {
        
        a = instance mcdp {
            provides capacity = 10 g
        }

        b = instance mcdp {
            provides capacity = 10 g
        }
    
        provides capacity = sum capacity provided by *  
    }
    
    """
    parse_ndp(s)

@comptest
def sum03():
#     sum_over_resources = sp(SUM + rname + REQUIRED_BY + ASTERISK,
#                             lambda t: CDP.SumResources(t[0],t[1],t[2],t[3]))
#     sum_over_functions = sp(SUM + fname + PROVIDED_BY + ASTERISK,
#                             lambda t: CDP.SumResources(t[0],t[1],t[2],t[3]))
    sor = Syntax.rvalue_sum_over_resources
    sof = Syntax.fvalue_sum_over_functions
    parse_wrap(sor, "sum r required by *")
    parse_wrap(sor, "∑ r required by *")
    parse_wrap(sof, "sum f provided by *")
    parse_wrap(sof, "∑ f provided by *")

if __name__ == '__main__':
    run_module_tests()
    