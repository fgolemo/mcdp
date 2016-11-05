from comptests.registrar import comptest
from mcdp_lang.parse_actions import parse_wrap
from mcdp_lang.syntax import Syntax
from mcdp_lang.parse_interface import parse_ndp
from mcdp_lang_tests.utils import assert_parse_ndp_semantic_error

@comptest
def check_variables01():
    some = [
        'variable x [m]',
        'variable x [Nat]',
        'variable x [R]',
    ]
    expr = Syntax.var_statement
    for s in some:
        parse_wrap(expr, s)
    

@comptest
def check_variables02():
    s = """
    mcdp {
        provides f [Nat]
        requires r [Nat]
        
        variable x [Nat]

        provided f <= x
        x <= required r
    }
    """        
    parse_ndp(s)


@comptest
def check_variables03():
    # This causes an error because the variable x is not used.
    s = """
    mcdp {
        provides f [Nat]
        requires r [Nat]
        
        variable x [Nat] # declared but not used

        provided f <= required r
    }
    """
    assert_parse_ndp_semantic_error(s)


@comptest
def check_variables04():
    pass

@comptest
def check_variables05():
    pass

@comptest
def check_variables06():
    pass

@comptest
def check_variables07():
    pass

@comptest
def check_variables08():
    pass

@comptest
def check_variables09():
    pass

@comptest
def check_variables10():
    pass

@comptest
def check_variables11():
    pass

@comptest
def check_variables12():
    pass

@comptest
def check_variables13():
    pass

@comptest
def check_variables14():
    pass

@comptest
def check_variables15():
    pass

