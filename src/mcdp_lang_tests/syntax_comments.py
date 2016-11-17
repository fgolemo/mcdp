from comptests.registrar import comptest, comptest_fails
from mcdp_lang.parse_interface import parse_ndp
from mcdp_lang_tests.utils import parse_wrap_check, assert_syntax_error
from mcdp_lang.syntax import Syntax
from mcdp_lang.parts import CDPLanguage
from mcdp_lang.syntax_utils import sp


@comptest
def check_comments01():
    " Single quotes "
    parse_wrap_check("""'ciao'""", Syntax.comment_string_simple)
    parse_wrap_check(""" "ciao" """, Syntax.comment_string_simple)
    
    parse_wrap_check("""'ciao'""", Syntax.comment_fun)
    parse_wrap_check("""'ciao'""", Syntax.comment_res)
    parse_wrap_check("""'ciao'""", Syntax.comment_var)

@comptest_fails    
def check_comments02():
    """ Triple quotes """
    parse_wrap_check(""" '''ciao\n''' """, Syntax.comment_string_complex)
    parse_wrap_check(''' """ciao""" ''', Syntax.comment_string_complex)

    parse_wrap_check(""" '''ciao\n''' """, Syntax.comment_model)
    parse_wrap_check(''' """ciao""" ''', Syntax.comment_model)
    assert_syntax_error(""" '''ciao\n''' """, Syntax.comment_fun)
    assert_syntax_error(""" '''ciao\n''' """, Syntax.comment_var)
    assert_syntax_error(""" '''ciao\n''' """, Syntax.comment_res)
    

@comptest
def check_comments03():    
    s = """ mcdp { 'Doc' } """
    parse_ndp(s)
    s = """ mcdp { "Doc" } """
    parse_ndp(s)

@comptest
def check_comments03b():
    """ Double comments """
    s = """ mcdp { '''Doc''' } """
    parse_ndp(s)
    s = ''' mcdp { """Doc""" } '''
    parse_ndp(s)

@comptest
def check_comments04():
    s = """ mcdp { 
        provides f [m] "fun comment"
    } """
    parse_ndp(s)

    s = """ mcdp { 
        requires r [m] "res comment"
    } """
    parse_ndp(s)

@comptest
def check_comments05():
    s = """ mcdp { 
        c = 10V "constant comment"
    } """
    parse_ndp(s)
    pass

@comptest
def check_comments06():
    pass

@comptest
def check_comments07():
    pass

@comptest
def check_comments08():
    pass

@comptest
def check_comments09():
    pass

@comptest
def check_comments10():
    pass

@comptest
def check_comments11():
    pass

@comptest
def check_comments12():
    pass

@comptest
def check_comments13():
    pass

@comptest
def check_comments14():
    pass

@comptest
def check_comments15():
    s = "gravity = 9.8 m/s^2 'Gravity on Earth'"
    parse_wrap_check(s, Syntax.setname_constant)
    
    # We don't think that division is allowed 
    # in definitely_constant_value
    s = '(9.8 m/s^2) / 6 dimensionless'
    assert_syntax_error(s, Syntax.definitely_constant_value)
    s = "constant gravity = (9.8 m/s^2) / 6 dimensionless 'Gravity on Earth'"
    parse_wrap_check(s, Syntax.setname_constant)
    
    pass

@comptest
def check_comments16():
    parse_wrap_check('1 g', Syntax.definitely_constant_value)
    parse_wrap_check("'Number of constants'", Syntax.comment_con)
    
    parse_wrap_check("axx = 1.2 g", Syntax.setname_rvalue)
    parse_wrap_check("axx", Syntax.constant_name)
    expr=Syntax.constant_name + Syntax.EQ + Syntax.definitely_constant_value
    parse_wrap_check("axx = 1.2 g", expr)
    def parse(tokens):
        print 'here', tokens
        t = tokens
        return CDPLanguage.SetNameConstant(t[0], t[1], t[2])
    expr2 = sp(expr, parse)
    parse_wrap_check("axx = 1.2 g", expr2)
    parse_wrap_check("axx = 1.2 g", Syntax.setname_constant)
    parse_wrap_check("a = 1 g", Syntax.setname_constant)
    parse_wrap_check("a = 1 g  'Number of constants'", Syntax.setname_constant)
    parse_wrap_check("constant a = 1 g  'Number of constants'", Syntax.setname_constant)
    parse_wrap_check(
        "constant gravity = (9.8 m/s^2) / 6 dimensionless 'Gravity on Earth'",
        Syntax.setname_constant)
    s = """
     mcdp {
    ' One example of documentation for the entire MCDP.'

    requires     mass [kg]   'The mass that must be transported.'
    provides capacity [kWh]  'The capacity of the battery.'

    constant a = 1 g  'Number of constants'
  
    constant gravity = (9.8 m/s^2) / 6 dimensionless 'Gravity on Earth'

    variable x, y [Nat] 'constant '
  }"""
    parse_ndp(s)

