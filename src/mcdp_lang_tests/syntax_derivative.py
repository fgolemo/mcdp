from comptests.registrar import comptest, comptest_fails
from mcdp_lang.parse_interface import parse_template, parse_ndp
from mcdp_lang.parts import CDPLanguage
from mcdp_lang_tests.utils import parse_wrap_check, parse_wrap_semantic_error,\
    assert_parse_ndp_semantic_error
from mcdp_lang.syntax import Syntax

@comptest_fails
def check_deriv01():
    s = """
    deriv(battery, mcdp {
        battery = instance mcdp {
            requires mass [g]
            provides energy [J]
            specific_energy = 0.1 J / g
            provided energy <= required mass * specific_energy
        }
        mass   required by battery <= 2 g
        energy provided by battery >= 5 J 
    })
    
    """
    ndp = parse_template(s)
    

@comptest
def check_deriv02():
    parse_wrap_check('deriv(a, `b)', Syntax.template_deriv)


@comptest
def check_deriv03():
    s = """
    eversion(battery, mcdp {
        battery = instance mcdp {
            requires mass [g]
            provides energy [J]
            specific_energy = 0.1 J / g
            provided energy <= required mass * specific_energy
        }
        mass   required by battery <= 2 g
        energy provided by battery >= 5 J 
    })
    
    """
    ndp = parse_ndp(s)
    


@comptest
def check_deriv04():
    s = """
    eversion(not_existent, mcdp {
        battery = instance mcdp {
            requires mass [g]
            provides energy [J]
            specific_energy = 0.1 J / g
            provided energy <= required mass * specific_energy
        }
        mass   required by battery <= 2 g
        energy provided by battery >= 5 J 
    })
    
    """
    
    ex = "Could not find 'not_existent' as a sub model"
    
    assert_parse_ndp_semantic_error(s, ex)
    

@comptest
def check_deriv05():
    # Problem with names
    s = """
    eversion(battery, mcdp {
        provides r = Nat: 5 
        battery = instance mcdp {
            requires r = Nat :2
        }
        r required by battery <= Nat: 3
    })
    
    """
    
    ex = "Function 'r' already exists in the big ndp"
    assert_parse_ndp_semantic_error(s, ex)
    
    s = """
    eversion(battery, mcdp {
        requires r = Nat: 5 
        battery = instance mcdp {
            provides r = Nat :2
        }
        r provided by battery >= Nat: 3
    })
    
    """
    ex = "Resource 'r' already exists in the big ndp"
    assert_parse_ndp_semantic_error(s, ex)
    


@comptest
def check_deriv06():
    pass


@comptest
def check_deriv07():
    pass


@comptest
def check_deriv08():
    pass


@comptest
def check_deriv09():
    pass


@comptest
def check_deriv10():
    pass

