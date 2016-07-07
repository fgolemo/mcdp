# -*- coding: utf-8 -*-
from comptests.registrar import comptest
from mcdp_lang.parse_actions import parse_wrap
from mcdp_lang.syntax import Syntax, SyntaxIdentifiers
from mcdp_lang.syntax_codespec import SyntaxCodeSpec
from  .utils import (assert_parsable_to_connected_ndp,
    assert_semantic_error, parse_wrap_check)
from nose.tools import assert_equal
from pyparsing import Literal

@comptest
def check_lang():
    idn = SyntaxIdentifiers.get_idn()
    parse_wrap(idn, 'battery')
    parse_wrap(idn + Syntax.ow, 'battery ')
    parse_wrap(idn + Syntax.ow + Literal('='), 'battery=')
    parse_wrap(Syntax.ndpt_load, 'load battery')

@comptest
def check_lang3_times():
    parse_wrap(Syntax.rvalue, 'mission_time')


@comptest
def check_lang4_composition():
    parse_wrap(Syntax.rvalue, 'mission_time')

    s = """
dp {
    provides current [A]
    provides capacity [J]
    requires weight [g]
    
    implemented-by load times
}
    """
    parse_wrap(Syntax.ndpt_simple_dp_model, s)[0]


@comptest
def check_lang5_composition():
    parse_wrap(Syntax.rvalue, 'mission_time')

    parse_wrap(SyntaxCodeSpec.funcname, 'mocdp.example_battery.Mobility')
    parse_wrap(SyntaxCodeSpec.code_spec, 'code mocdp.example_battery.Mobility')


@comptest
def check_lang6_composition():
    parse_wrap(Syntax.rvalue, 'mission_time')

    parse_wrap(SyntaxCodeSpec.funcname, 'mocdp.example_battery.Mobility')
    parse_wrap(SyntaxCodeSpec.code_spec, 'code mocdp.example_battery.Mobility')

    parse_wrap(SyntaxCodeSpec.code_spec_with_args, 'code mocdp.example_battery.Mobility(a=1)')


@comptest
def check_lang8_addition():
    # x of b  == x required by b
    p = assert_parsable_to_connected_ndp("""
    mcdp {
        provides mission_time  [s]
        provides extra_payload [g]
        requires total_weight [g]
        
        sub battery = instance mcdp {
            provides capacity [J]
            requires weight   [kg]
            
            specific_weight = 1 J/kg
            weight >= capacity / specific_weight
        }
        
        sub actuation = instance mcdp {
            provides payload [g]
            requires power   [W]
            
            c = 1 W/g
            power >= c * payload
        }
                
        capacity provided by battery >= mission_time * (power required by actuation)    
        payload provided by actuation >= (weight required by battery) + extra_payload
        
        total_weight >= weight required by battery
    }
    """)
    assert_equal(p.get_rnames(), ['total_weight'])
    assert_equal(p.get_fnames(), ['mission_time', 'extra_payload'])




@comptest
def check_lang9_max():
    parse_wrap_check("""provides x [R]""",
                     Syntax.fun_statement)
    parse_wrap_check("""
            provides x [R]
            requires r [R]
        """,
    Syntax.simple_dp_model_stats)
   
    parse_wrap_check("""dp {
            provides x [R]
            requires r [R]
            
            implemented-by load SimpleNonlinearity1
        }""",
        Syntax.ndpt_simple_dp_model)
    
    parse_wrap(Syntax.rvalue_binary, 'max(f, g)')
    parse_wrap(Syntax.rvalue, 'max(f, g)')
    parse_wrap(Syntax.constraint_expr_geq, 'hnlin.x >= max(f, g)')

#     p = assert_parsable_to_connected_ndp("""
#     mcdp {
#         provides f [R]
#
#         sub hnlin = instance dp {
#             provides x [R]
#             requires r [R]
#
#             implemented-by load SimpleNonlinearity1
#         }
#
#         hnlin.x >= max(f, hnlin.r)
#     }
#     """)
#
#     assert_equal(p.get_rnames(), [])
#     assert_equal(p.get_fnames(), ['f'])


@comptest
def check_lang10_comments():
    p = assert_parsable_to_connected_ndp("""
    mcdp {
        provides f [R]
        
        sub hnlin = instance mcdp {
            provides x [R]
            requires r [R]
            
            r >= pow(x, 2)
        }
        
        hnlin.x >= max(f, hnlin.r)        
    }
    """)
    assert_equal(p.get_rnames(), [])
    assert_equal(p.get_fnames(), ['f'])




@comptest
def check_lang11_resources():
    p = assert_parsable_to_connected_ndp("""
    mcdp {
        provides f [R]
        requires z [R]
        
       sub hnlin = instance mcdp {
            provides x [R]
            requires r [R]
            
            r >= pow(x, 2)
        }
        
        hnlin.x >= max(f, hnlin.r)
        z >= hnlin.r        
    }
    """)

    assert_equal(p.get_rnames(), ['z'])
    assert_equal(p.get_fnames(), ['f'])




@comptest
def check_lang12_addition_as_resources():
    assert_parsable_to_connected_ndp("""
    mcdp {
        provides a [R]
        provides b [R]
        requires c [R]
        requires d [R]
         
        c + d >= a + b
        }
    """)


@comptest
def check_lang15():
    assert_semantic_error("""
mcdp {
    provides g [s]
    provides f [s]

    f >= g
}""", "the name 'f' can't be used as a function")





# TODO:
#     assert_parsable_to_unconnected_ndp("""
# cdp {
#   motor = abstract cdp {
#     provides torque [R]
#     requires weight [R]
#
#     weight >= 1.0 [R]
#     torque <= 1.0 [R]
#   }
# }
# """)











@comptest
def check_lang49():
    """ Shortcuts "for" """
    parse_wrap(Syntax.res_shortcut3, "requires cost, weight for motor")



@comptest
def check_lang51():
    """ Shortcuts "using" """
    print parse_wrap(Syntax.space_pint_unit, 'R')
    print parse_wrap(Syntax.unitst, '[R]')



    parse_wrap(Syntax.number_with_unit, '4.0 [R]')

    parse_wrap(Syntax.space_pint_unit, "N")
    parse_wrap(Syntax.space_pint_unit, "m")
    parse_wrap(Syntax.space_pint_unit, "N*m")
    parse_wrap(Syntax.space_pint_unit, "m / s^2")
    parse_wrap(Syntax.space_pint_unit, "m/s^2")
    
    parse_wrap(Syntax.number_with_unit, '1 m')
    parse_wrap(Syntax.number_with_unit, '1 m/s')
    parse_wrap(Syntax.number_with_unit, '1 m/s^2')



@comptest
def check_lang_invplus():
    assert_parsable_to_connected_ndp("""
mcdp {
    provides a [s]
    
    requires x [s]
    requires y [s]
    
    x + y >= a
}""")



@comptest
def check_lang52():
    pass



@comptest
def check_lang53():
    assert_parsable_to_connected_ndp("""
    approx_lower(10, mcdp {
    provides a [s]
    
    requires x [s]
    requires y [s]
    
    x + y >= a
})""")
    pass
