# -*- coding: utf-8 -*-
from comptests.registrar import run_module_tests, comptest
from mcdp_lang_tests.utils2 import parse_as_rvalue, parse_as_fvalue
from mcdp_lang.parse_interface import parse_ndp
from mcdp_lang.syntax import Syntax
from mcdp_lang.parse_actions import parse_wrap

@comptest
def new_uncertainty00():
    s = "10 kg +- 50 g"
    parse_as_rvalue(s)
    
@comptest
def new_uncertainty01():
    s = "10 kg ± 5%"
    parse_as_rvalue(s)

@comptest
def new_uncertainty01b():
    s = "10 kg +- 5%"
    parse_as_rvalue(s)
    
@comptest
def new_uncertainty02():
    s = "between 9.95 kg and 10.05 kg"
    parse_as_rvalue(s)

@comptest
def new_uncertainty03():
    s = "100 $/kWh ± 5%"
    parse_as_rvalue(s)

@comptest
def new_uncertainty04():
    s = "10 kg +- 50 g"
    parse_as_fvalue(s)
    
@comptest
def new_uncertainty05():
    s = "10 kg ± 5%"
    parse_as_fvalue(s)
    
@comptest
def new_uncertainty06():
    s = "between 9.95 kg and 10.05 kg"
    parse_as_fvalue(s)

@comptest
def new_uncertainty07():
    s = "100 $/kWh ± 5%"
    parse_as_fvalue(s)
    
@comptest
def new_uncertainty08():
    s = """mcdp {
        c = 10 kg
        δ = 50 g
        x = between c-δ and c+δ
        requires x
    } """
    parse_ndp(s)
    

@comptest
def new_uncertainty09():
    s = """mcdp {
        c = 10 kg
        δ = 50 g
        x = between c-δ and c+δ
        provides x
    } """
    parse_ndp(s)

@comptest
def new_uncertainty10():
    s = """mcdp {
        c = 10 kg
        δ = 50 g
        provides x = between c-δ and c+δ
    } """
    parse_ndp(s)
    

@comptest
def new_uncertainty11():
    s = """mcdp {
        c = 10 kg
        δ = 50 g
        requires x = between c-δ and c+δ
    } """
    parse_ndp(s)


@comptest
def new_uncertainty12():
    s = """
    catalogue {
        provides length [m]
        requires weight [g]
        1 m <--| imp |--> 10 kg 
    }
    """
    parse_ndp(s)
    
    parse_wrap(Syntax.catalogue_entry_constant_uncertain, '10 kg +- 50 g')

    s = """
    catalogue {
        provides length [m]
        requires weight [g]
        1 m <--| imp |--> 10 kg +- 50 g
    }
    """
    parse_ndp(s)
    

if __name__ == '__main__': 
    
    run_module_tests()