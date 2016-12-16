# -*- coding: utf-8 -*-
from nose.tools import assert_equal, assert_raises

from comptests.registrar import comptest, run_module_tests, comptest_fails
from mcdp_lang import parse_ndp
from mcdp_lang.dealing_with_special_letters import greek_letters, subscripts
from mcdp_lang.eval_space_imp import eval_space
from mcdp_lang.parse_actions import parse_wrap
from mcdp_lang.parse_interface import parse_ndp_refine
from mcdp_lang.suggestions import get_suggestions, apply_suggestions
from mcdp_lang.syntax import Syntax
from mcdp_lang_tests.utils import parse_wrap_check, TestFailed
from mcdp_lang_tests.utils2 import eval_rvalue_as_constant
from mcdp_report.out_mcdpl import extract_ws
from mocdp.comp.context import Context
from mocdp.exceptions import DPSemanticError
from contracts.utils import indent
from mocdp import MCDPConstants


@comptest
def check_spaces1():
    def p(s):
        c = Context()
        r = parse_wrap_check(s, Syntax.space)
        _x = eval_space(r, c)
        
    p('V')
    p("V x m")
    p("V × m")
    p("V × m × J")
    p("m × m × m")
    p("m × (m × m)")

@comptest
def check_spaces2():
    _ndp = parse_ndp("""
    mcdp {
         
        a = catalogue {

        provides voltage [set-of(V)]
        provides capacity [J]

        requires cost [$]
        requires mass [kg]

        model1 | {1.5 V} | 1 J | 5 $ | 0.20 kg 
        model2 | {1.5 V} | 1 J | 5 $ | 0.20 kg 
        model3 | {5.0 V} | 1 J | 5 $ | 0.30 kg

    }
    }
    """)
    #print ndp

@comptest
def check_spaces3():  # changename
    parse_wrap_check('instance simple_cell', Syntax.dpinstance_from_type)
    parse_wrap_check('sub cell = instance simple_cell', Syntax.setname_ndp_instance1)

@comptest
def check_spaces4():
    parse_wrap_check('<5mm, 5mm, 5mm>', Syntax.tuple_of_constants)
    parse_wrap_check('step_up1 | {5 V}        | {1.5 V} |  5 $ | 20 g | <5mm, 5mm, 5mm>', Syntax.catalogue_row)
    parse_ndp("""
catalogue {
    provides voltage    [℘(V)]
    requires v_in       [℘(V)]
    requires cost       [$]
    requires mass       [g]
    requires shape      [m x m x m]
    
    step_up1 | {5 V}        | {1.5 V} |  5 $ | 20 g | <5mm, 5mm, 5mm>
    step_up2 |       {12 V} | {1.5 V} | 10 $ | 20 g | <5mm, 5mm, 5mm>
    step_up2 | {5 V,  12 V} | {1.5 V} | 10 $ | 20 g | <5mm, 5mm, 5mm>
}
""")
         
@comptest
def undefined_x():
    source = """
    mcdp {
        provides x
        provided x ≼ 9.8 m/s^2
    }
    """
    assert_raises(DPSemanticError, parse_ndp, source)
####################

def check_suggestions_result(s, s2_expected):
    suggestions = get_suggestions_ndp(s)
    s2 = apply_suggestions(s, suggestions)
    if s2 != s2_expected:
        msg = 'Expected:\n\n'
        msg += '\n\n'+indent(make_chars_visible(s), '   original |')
        msg += '\n\n'+indent(make_chars_visible(s2), 'transformed |')
        msg += '\n\n'+indent(make_chars_visible(s2_expected), '   expected |')
        raise ValueError(msg)
  
def make_chars_visible(x):
    """ Replaces whitespaces ' ' and '\t' with '␣' and '⇥' """
    x = x.replace(' ', '␣')
    if MCDPConstants.tabsize == 4:
        tab = '├──┤'
    else:
        tab = '⇥'
        
    x = x.replace('\t', tab)
#     nl = '␤\n'
    nl = '⏎\n'
    x = x.replace('\n', nl)
    return x

@comptest
def check_spaces7():
    source = """
    mcdp {
        provides x
        provided x ≼ 9.8 m/s^2
    }
    """
    suggestions = get_suggestions_ndp(source)
    
    assert_equal(1, len(suggestions))
    assert_equal('m/s\xc2\xb2', suggestions[0][1])
    
    _s2 = apply_suggestions(source, suggestions)
#     if suggestions:
#         print s2
        

@comptest
def check_spaces_superscript1():
    parse_wrap_check('m^2', Syntax.space_pint_unit)
    # ¹²³⁴⁵⁶⁷⁸⁹
    parse_wrap_check('m¹', Syntax.space_pint_unit)
    parse_wrap_check('m²', Syntax.space_pint_unit)
    parse_wrap_check('m³', Syntax.space_pint_unit)
    parse_wrap_check('m⁴', Syntax.space_pint_unit)
    parse_wrap_check('m⁵', Syntax.space_pint_unit)
    parse_wrap_check('m⁶', Syntax.space_pint_unit)
    parse_wrap_check('m⁷', Syntax.space_pint_unit)
    parse_wrap_check('m⁸', Syntax.space_pint_unit)
    parse_wrap_check('m⁹', Syntax.space_pint_unit)

    eval_rvalue_as_constant('9.81 m/s²')

@comptest
def no_newlines_before_unit():
    s = '1\nm'

    with assert_raises(TestFailed): # does not work
        parse_wrap_check(s,  Syntax.pint_unit_simple)
        
    with assert_raises(TestFailed):
        parse_wrap_check(s,  Syntax.valuewithunit_number_with_units)
    
@comptest
def power1():
    parse_wrap_check('x^2', Syntax.rvalue_power_expr)
    parse_wrap_check('²', Syntax.superscripts)
    parse_wrap_check('x²', Syntax.rvalue_power_expr)
    parse_ndp("""
    mcdp {
        provides f [dimensionless]
        requires r [dimensionless]
        
        (provided f)²  <= required r
    }
    """)
    

@comptest
def suggestions_exponent():
    source = """
mcdp {
    provides f [dimensionless]
    requires r [dimensionless]
    (provided f)^2 ≼ required r
}
    """
    suggestions = get_suggestions_ndp(source) 
    assert_equal(1, len(suggestions))
    w, sub = suggestions[0]
    ws = w.string[w.character:w.character_end]
    assert_equal(ws, '^2')
    assert_equal('\xc2\xb2', sub)
    
    s2 = apply_suggestions(source, suggestions)
    parse_ndp(s2)


@comptest
def suggestions_exponent2():
    s = """
mcdp {
    variable a, c [dimensionless] 
    c ≽ a^2 + 1
}"""
#     x = parse_wrap(Syntax.ndpt_dp_rvalue, s)[0]
#     xr = parse_ndp_refine(x, Context())
    
    suggestions = get_suggestions_ndp(s)
#     print suggestions
    assert_equal(1, len(suggestions))
    assert_equal('\xc2\xb2', suggestions[0][1])
    
    s2 = apply_suggestions(s, suggestions)
    parse_ndp(s2)
    # print s2

@comptest
def suggestions_subscript():
    s = """
mcdp {  
    variable a_1 [dimensionless]
}"""
    s2_exp = u"""
mcdp {  
    variable a₁ [dimensionless]
}""".encode('utf8')
# 
#     x = parse_wrap(Syntax.ndpt_dp_rvalue, s)[0]
#     xr = parse_ndp_refine(x, Context())
    
    suggestions = get_suggestions_ndp(s)
    assert_equal(1, len(suggestions))
    assert_equal('\xe2\x82\x81', suggestions[0][1])
    
    s2 = apply_suggestions(s, suggestions)
    parse_ndp(s2)
    #print s2
    s2 = apply_suggestions(s, suggestions)
    assert_equal(s2_exp, s2)


@comptest
def suggestions_subscript_no_inside():
    s = """
mcdp {  
    variable a_1_last [dimensionless]
}"""
    suggestions = get_suggestions_ndp(s)
    if suggestions: print suggestions
    assert_equal(0, len(suggestions)) 
    
@comptest
def dont_suggest_weird_places():
    s = """
mcdp {  
    # this might look like "nu"
    variable num_stuff [dimensionless]
    num_replacements = 0
}"""
    suggestions = get_suggestions_ndp(s)
    if suggestions: print suggestions
    assert_equal(0, len(suggestions)) 

@comptest
def suggestions_greek():
    s = """
mcdp {  
    variable a_alpha_last [dimensionless]
}"""
    s2_exp = u"""
mcdp {  
    variable a_α_last [dimensionless]
}""".encode('utf8')

#     x = parse_wrap(Syntax.ndpt_dp_rvalue, s)[0]
#     assert_equal(x.where.string, s)
#     xr = parse_ndp_refine(x, Context())
#     suggestions = get_suggestions(xr)
    suggestions = get_suggestions_ndp(s)
    #if suggestions: print suggestions
    assert_equal(1, len(suggestions)) 
    s2 = apply_suggestions(s, suggestions)
    assert_equal(s2_exp, s2)
    

@comptest
def dont_suggest_if_already_done():
    s = """
mcdp {  
    # this is already done
    variable a₁ [dimensionless]
    variable alpha [dimensionless]
}"""
    suggestions = get_suggestions_ndp(s)
    if suggestions: print suggestions
    assert_equal(0, len(suggestions))
    
def get_suggestions_ndp(s):
    x = parse_wrap(Syntax.ndpt_dp_rvalue, s)[0]
    assert_equal(x.where.string, s)
    
#     print ('get_suggestions_ndp s = %r' % s)
#     print ('get_suggestions_ndp x = %s' % recursive_print(x))
#     print ('get_suggestions_ndp x string = %r' % x.where.string)
    xr = parse_ndp_refine(x, Context())
    suggestions = get_suggestions(xr)
    return suggestions

@comptest
def just_list():
    s = sorted(greek_letters, key=lambda t: t.lower() + t[0])
    print(" ".join(greek_letters[_] for _ in s))   
    print("\n".join('%s %s' % (greek_letters[k], k) for k in s))
    print(" ".join(subscripts.values()))

@comptest
def space_suggestions():
    s = """
 mcdp {
        a = 2
 } 
"""
    suggestions = get_suggestions_ndp(s)
#     print suggestions
    assert_equal(1, len(suggestions))

@comptest
def space_suggestions1():
    # 3 spaces
    s = """
mcdp {
   a = 2
} 
"""
    s2expected = """
mcdp {
    a = 2
} 
"""
    suggestions = get_suggestions_ndp(s)
#     print suggestions
    assert_equal(1, len(suggestions))
    assert_equal(suggestions[0][0].character, suggestions[0][0].character_end) 
    s2 = apply_suggestions(s, suggestions)
    assert_equal(s2, s2expected)


@comptest
def space_suggestions_brace():
    # 3 spaces
    s = """
 mcdp {
     a = 2
} 
"""
    s2expected = """
 mcdp {
     a = 2
 } 
"""
    suggestions = get_suggestions_ndp(s)
#     print suggestions
    assert_equal(1, len(suggestions))
    assert_equal(suggestions[0][0].character, suggestions[0][0].character_end) 
    s2 = apply_suggestions(s, suggestions)
    assert_equal(s2, s2expected)
    
@comptest
def spaces():
    assert_equal(extract_ws(''), ('','',''))
    assert_equal(extract_ws('x'), ('','x',''))
    assert_equal(extract_ws(' x'), (' ','x',''))
    assert_equal(extract_ws(' x '), (' ','x',' '))
    assert_equal(extract_ws(' '), (' ','',''))
    assert_equal(extract_ws('  '), ('  ','',''))
    
    
@comptest
def check_spaces_right_position():
    s = """
mcdp {
a = 2
}"""
    suggestions = get_suggestions_ndp(s)
    s2 = apply_suggestions(s, suggestions)
    suggestions2 = get_suggestions_ndp(s2)
    assert_equal(0, len(suggestions2))


@comptest
def check_spaces_right_position2():
    s = """
mcdp {
    a = 2
#
}"""
    suggestions = get_suggestions_ndp(s)
    s2 = apply_suggestions(s, suggestions)
    suggestions2 = get_suggestions_ndp(s2)
    assert_equal(0, len(suggestions2))
    
    


@comptest
def recursive1():
    s = """
mcdp {
    a = instance mcdp { }
}"""
    suggestions = get_suggestions_ndp(s)
    assert_equal(0, len(suggestions))

@comptest
def nochanges():
    s = """
mcdp {
    a = mcdp { 
            b = mcdp {
                } 
        }
}"""
    suggestions = get_suggestions_ndp(s)
    assert_equal(0, len(suggestions))

@comptest
def recursive2():
    s = """
mcdp {
    a = instance mcdp { 
}
}"""
    s2expected = """
mcdp {
    a = instance mcdp { 
                 }
}"""
    suggestions = get_suggestions_ndp(s)
    assert_equal(1, len(suggestions))
    s2 = apply_suggestions(s, suggestions)
    assert_equal(s2, s2expected)
    
@comptest
def recursive3():
    s = """
mcdp {
     a = instance mcdp { 
                 }
}"""
    s2_expected = """
mcdp {
    a = instance mcdp { 
                  }
}"""
    s3_expected = """
mcdp {
    a = instance mcdp { 
                 }
}"""
    suggestions = get_suggestions_ndp(s)
    s2 = apply_suggestions(s, suggestions)
    assert_equal(2, len(suggestions))
    print s2
    assert_equal(s2, s2_expected)
    
    # this one there will be a further adjustment
    suggestions2 = get_suggestions_ndp(s2)
    assert_equal(1, len(suggestions2))
    s3 = apply_suggestions(s2, suggestions2)
    assert_equal(s3, s3_expected)

@comptest
def tabs1():
    s = 'mcdp {\n\t# this is equivalent to a mux\n\tprovides fa [g]\n\tprovides fb [J]\n\n\trequires r [g x J]\n\n\tr >= <provided fa, fb>\n}'
    suggestions = get_suggestions_ndp(s)
    print s.__repr__()
    s2 = apply_suggestions(s, suggestions)


@comptest
def tabs2():
    s = 'template mcdp {\n\ta = 1\n}'
    suggestions = get_suggestions_ndp(s)
    print s.__repr__()
    s2 = apply_suggestions(s, suggestions)

@comptest
def overlapping():
    s = 'mcdp {\n # this is equivalent to a mux\n provides fa [g]\n provides fb [J]\n\n requires r [g x J]\n\n r >= <provided fa, fb>\n}'
    suggestions = get_suggestions_ndp(s)
    s2 = apply_suggestions(s, suggestions)

@comptest_fails
def suggestion_problem1():
    s=""" 
 mcdp {
     a = mcdp { 
             b = mcdp {} 
} 
 }"""    
    suggestions = get_suggestions_ndp(s)
    s2 = apply_suggestions(s, suggestions)
    s2_expected = """
 mcdp {
    a = mcdp { 
             b = mcdp {}
         } 
 }"""
    assert_equal(s2, s2_expected)
    
    
@comptest 
def nested():  
    s="""
mcdp {
\ta = mcdp { 
        
    }
m = 4
}"""
    s2_expected = """
mcdp {
\ta = mcdp { 
        
    }
    m = 4
}"""
    check_suggestions_result(s, s2_expected)
    
@comptest 
def first():
    s = "mcdp {}"
    s2_expected = "mcdp {\n}"
    check_suggestions_result(s, s2_expected)
    
if __name__ == '__main__': 
#     overlapping()
    run_module_tests()
    