# -*- coding: utf-8 -*-
from nose.tools import assert_equal

from comptests.registrar import comptest, comptest_fails
from contracts.utils import raise_desc
from mcdp_dp import CatalogueDP, CoProductDP, NotFeasible, Template
from mcdp_lang.parse_actions import parse_wrap
from mcdp_lang.parse_interface import parse_ndp, parse_poset
from mcdp_lang.pyparsing_bundled import Literal
from mcdp_lang.syntax import Syntax, SyntaxIdentifiers
from mcdp_lang.syntax_codespec import SyntaxCodeSpec
from mcdp_lang_tests.utils import assert_parse_ndp_semantic_error
from mcdp_posets import LowerSets, Rcomp, UpperSet, UpperSets, PosetProduct, get_product_compact
from mocdp import ATTRIBUTE_NDP_RECURSIVE_NAME
from mocdp.comp.recursive_name_labeling import get_names_used
from mocdp.exceptions import DPNotImplementedError, DPSemanticError
import numpy as np

from .utils import (assert_parsable_to_connected_ndp, assert_semantic_error,
    parse_wrap_check)


@comptest
def check_lang():
    idn = SyntaxIdentifiers.get_idn()
    parse_wrap(idn, 'battery')
    parse_wrap(idn, 'battery ')
    expr = idn + Literal('=')
    parse_wrap(expr, 'battery=')
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
    parse_wrap_check("""requires x [R]""",
                     Syntax.res_statement)

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


@comptest
def check_lang49():
    """ Shortcuts "for" """
    parse_wrap(Syntax.res_shortcut3, "requires cost, weight for motor")



@comptest
def check_lang51():
    """ Shortcuts "using" """
    print parse_wrap(Syntax.space_pint_unit, 'R')
    print parse_wrap(Syntax.unitst, '[R]')



    parse_wrap(Syntax.valuewithunit, '4.0 [R]')

    parse_wrap(Syntax.space_pint_unit, "N")
    parse_wrap(Syntax.space_pint_unit, "m")
    parse_wrap(Syntax.space_pint_unit, "N*m")
    parse_wrap(Syntax.space_pint_unit, "m / s^2")
    parse_wrap(Syntax.space_pint_unit, "m/s^2")
    
    parse_wrap(Syntax.valuewithunit, '1 m')
    parse_wrap(Syntax.valuewithunit, '1 m/s')
    parse_wrap(Syntax.valuewithunit, '1 m/s^2')



@comptest
def check_lang_invplus():
    assert_parsable_to_connected_ndp("""
mcdp {
    provides a [s]
    
    requires x [s]
    requires y [s]
    
    x + y >= a
}""")

    s = """
    mcdp {
        provides a [s]
        
        requires x [s]
        requires y [s]
        requires z [s]
        
        x + y * z >= a
    }"""
    try:
        parse_ndp(s)
    except DPSemanticError as e:
        if 'Inconsistent units' in str(e):
            pass
        else:
            msg = 'Expected inconsistent unit error.'
            raise_desc(Exception, msg)
    else:
        msg = 'Expected exception'
        raise_desc(Exception, msg)

    s = """
    mcdp {
        provides a [s]
        
        requires x [s]
        requires y [hour]
        
        x + y >= a
    }"""
    try:
        parse_ndp(s)
    except DPNotImplementedError as e:
        pass
    else:
        msg = 'Expected DPNotImplementedError'
        raise_desc(Exception, msg)


@comptest
def check_lang53():
    assert_parsable_to_connected_ndp("""
    approx_lower(10, mcdp {
    provides a [s]
    
    requires x [s]
    requires y [s]
    
    x + y >= a
})""")

def add_def_poset(l, name, data):
    fn = '%s.mcdp_poset' % name
    l.file_to_contents[fn] = dict(realpath='#', data=data)

@comptest
def check_join_not_existence():
    """ A test for finite posets where the join might not exist. """
    from mcdp_library.library import MCDPLibrary
    l = MCDPLibrary()

    add_def_poset(l, 'P', """
    finite_poset {
        a <= b <= c
        A <= B <= C
    }
    """)


#     parse_wrap(Syntax.LOAD, '`')
#     parse_wrap(Syntax.posetname, 'P')
#     print Syntax.load_poset
#     parse_wrap(Syntax.load_poset, '`P')
#     parse_wrap(Syntax.space_operand, '`P')
#     parse_wrap(Syntax.fun_statement, "provides x [`P]")

    ndp = l.parse_ndp("""
        mcdp {
            provides x [`P]
            provides y [`P]
            requires z [`P]
            
            z >= x
            z >= y
        }
    """)
    dp = ndp.get_dp()

    res1 = dp.solve(('a', 'b'))

    P = l.load_poset('P')
    UR = UpperSets(P)
    UR.check_equal(res1, UpperSet(['b'], P))

    res2 = dp.solve(('a', 'A'))

    UR.check_equal(res2, UpperSet([], P))



@comptest
def check_ignore1():  # TODO: rename
    assert_parsable_to_connected_ndp("""
        mcdp {
            a = instance mcdp {
                provides f [s]
                f <= 10 s
            }
            ignore f provided by a
        }
    """)


    assert_parsable_to_connected_ndp("""
        mcdp {
            a = instance mcdp {
                requires r [s]
                r >= 10 s
            }
            ignore r required by a
        }
    """)

def f():
    pass

@comptest
def check_addmake1():
    parse_wrap_check(""" addmake(root: code mcdp_lang_tests.syntax_misc.f) mcdp {} """,
                     Syntax.ndpt_addmake)

    ndp = parse_ndp(""" addmake(root: code mcdp_lang_tests.syntax_misc.f) mcdp {} """)

    assert len(ndp.make) == 1
    assert ndp.make[0][0] == 'root'
    from mcdp_lang.eval_ndp_imp import ImportedFunction
    assert isinstance(ndp.make[0][1], ImportedFunction)
    # assert ndp.make == [('root', f)], ndp.make

@comptest
def check_get_names_used1():  
    
# . L . . . . . . . \ Parallel2  % R[kg]×(R[N]×R[N]) -> R[kg]×R[W] I = PosetProduct(R[kg],PosetProduct(R[N],R[N]){actuati
# on/_prod1},R[N²]) names: [('actuation', '_prod1')]
# . L . . . . . . . . \ Id(R[kg]) I = R[kg]
# . L . . . . . . . . \ Series: %  R[N]×R[N] -> R[W] I = PosetProduct(PosetProduct(R[N],R[N]){actuation/_prod1},R[N²]) nam
# es: [('actuation', '_prod1'), ('actuation', '_mult1')]
# . L . . . . . . . . . \ ProductN(R[N]×R[N] -> R[N²]) named: ('actuation', '_prod1') I = PosetProduct(R[N],R[N])
# . L . . . . . . . . . \ GenericUnary(<mcdp_lang.misc_math.MultValue instance at 0x10d8dcbd8>) named: ('actuation', '_mult1
# ') I = R[N²]

    S1 = parse_poset('N')
    setattr(S1, ATTRIBUTE_NDP_RECURSIVE_NAME, ('S1',))
    S2 = parse_poset('kg')
    setattr(S2, ATTRIBUTE_NDP_RECURSIVE_NAME, ('S2',))
    S12 = PosetProduct((S1, S2))
    names = get_names_used(S12)
    assert names == [('S1',), ('S2',)], names
    P = parse_poset('J x W')
    setattr(P, ATTRIBUTE_NDP_RECURSIVE_NAME, ('prod',))

    S, _pack, _unpack = get_product_compact(P, S12)
    print S.__repr__()
    assert get_names_used(S) == [('prod',), ('S1',), ('S2',)]
    
    

@comptest
def check_namedproduct1():   
    parse_wrap_check("required in", Syntax.fvalue_new_resource2)
    parse_wrap_check("required in", Syntax.fvalue_operand)
    parse_wrap_check("required in", Syntax.fvalue)
    parse_wrap_check("(required in).dc", Syntax.fvalue_label_indexing3)
    parse_wrap_check("((required in).dc).connector", Syntax.fvalue_label_indexing3)

    parse_wrap_check("((required in).dc).connector >= `USB_connectors: USB_Std_A",
                     Syntax.line_expr)

@comptest
def check_ignore_resources1():
    ndp = parse_ndp("""
        ignore_resources(total_cost)
        mcdp {
            requires mass [g]
            requires total_cost [USD]
        }
    
    """)
    rnames = ndp.get_rnames()
    print rnames
    assert rnames == ['mass']

@comptest
def check_coproductdp_error1():  
    
    # check error if types are different
    F1 = parse_poset('g')
    F2 = parse_poset('kg')
    R1 = parse_poset('J')
    R2 = parse_poset('V')
    # Same R, different F
    dp1 = Template(F1, R1)
    dp2 = Template(F2, R1)
    try:
        CoProductDP((dp1, dp2))
    except ValueError as e:
        assert 'Cannot form' in str(e)
    else: 
        raise Exception()
    
    # Same F, different R
    dp1 = Template(F1, R1)
    dp2 = Template(F1, R2)
    try:
        CoProductDP((dp1, dp2))
    except ValueError as e:
        assert 'Cannot form' in str(e)
    else: 
        raise Exception()
    

@comptest
def check_coproductdp2(): 
    F = parse_poset('g')
    R = parse_poset('J')
    I = parse_poset('finite_poset{a b c}')
    entries = [('a', 1.0, 2.0), ('b', 2.0, 4.0)]
    dp1 = CatalogueDP(F=F,R=R,I=I,entries=entries)
    
    # This will not be feasible for dp1
    f= 3.0
    r = 1000.0
    try:
        ms = dp1.get_implementations_f_r(f,r)
    except NotFeasible:
        pass
    else:
        assert False, ms
    
    # and not for dp as well
    dp = CoProductDP((dp1,))
    try:
        ms = dp.get_implementations_f_r(f,r)
    except NotFeasible:
        pass
    else:
        assert False, ms
    
#### 
# Check all 4

    
@comptest
def check_lang76(): # TODO: rename
    s = '[[ identifier ]]'
    parse_wrap(Syntax.constant_placeholder, s)
    parse_wrap(Syntax.rvalue_placeholder, s)
    parse_wrap(Syntax.fvalue_placeholder, s)
    parse_wrap(Syntax.space_placeholder, s)
    parse_wrap(Syntax.ndpt_placeholder, s)
    parse_wrap(Syntax.template_placeholder, s)
    parse_wrap(Syntax.primitivedp_placeholder, s)
    parse_wrap(Syntax.collection_placeholder, s)

    parse_wrap(Syntax.constant_value, s)
    parse_wrap(Syntax.rvalue, s)
    parse_wrap(Syntax.fvalue, s)
    parse_wrap(Syntax.space, s)
    parse_wrap(Syntax.ndpt_dp_rvalue, s)
    parse_wrap(Syntax.template, s)
    
    parse_wrap(Syntax.upper_set_from_collection, 'upperclosure [[ set ]]')
    parse_wrap(Syntax.ndpt_dp_rvalue, 'abstract [[ model ]]')
    
@comptest
def check_lang77(): # TODO: rename
    s = 'EmptySet Nat x Nat'
    parse_wrap(Syntax.constant_emptyset, s)
    parse_wrap(Syntax.constant_value, s)
    
@comptest
def check_lang78(): # TODO: rename
    pass

@comptest_fails
def check_lang79b(): # TODO: rename
    pass
# 
#     s = 'provided f - 1 dimensionless'
#     
#     print parse_wrap(Syntax.rvalue_minus_constant, s)
#     x = parse_wrap(Syntax.rvalue, s)[0]
#     check_isinstance(x, CDPLanguage.RvalueMinusConstant)
#     s = '(provided f) - 1 dimensionless'
#     print parse_wrap(Syntax.rvalue_minus_constant, s)
#     x = parse_wrap(Syntax.rvalue, s)[0]
    
    
@comptest
def check_lang79(): # TODO: rename
    pass
# 
#     s = 'rvalue_minus_constant(provided f, 1 dimensionless)'
#     
#     print parse_wrap(Syntax.rvalue_minus_constant, s)
#     x = parse_wrap(Syntax.rvalue, s)[0]
#     check_isinstance(x, CDPLanguage.RvalueMinusConstant)
    
@comptest
def check_lang80b(): # TODO: rename
    s = """
mcdp {
    provides f [R]
    requires r [R]
    x = provided f
    required r >= x  + (0 dimensionless - 1 dimensionless)
}
    """
    ndp = parse_ndp(s)
    dp = ndp.get_dp()
    print dp.repr_long()


@comptest
def check_lang80(): # TODO: rename
    s = """
mcdp {
    provides f [R]
    requires r [R]
    x = provided f
    required r >= x - 1 dimensionless
}
    """
    ndp = parse_ndp(s)
    dp = ndp.get_dp()
    print dp.repr_long()
    s = 'provided f'
    print parse_wrap(Syntax.rvalue, s)
    
    s = 'x - Nat:1'
    print parse_wrap(Syntax.rvalue, s)
    
    s = 'provided f - Nat:1'
    print parse_wrap(Syntax.rvalue, s)
    

@comptest
def check_lang81(): # TODO: rename
    
    print parse_wrap(Syntax.rvalue_power_base, '(provided f)')
    print parse_wrap(Syntax.rvalue_power_expr_2, '(provided f) ^ 5')
    

    pass

@comptest
def check_lang82(): # TODO: rename
    print parse_wrap(Syntax.rvalue_unary_expr, " ceilsqrt(f.x) ")

    s = """
mcdp {
    provides f [Nat]
    requires r [Nat]
    x = provided f
    required r >= ceilsqrt(x)
}
    """
    ndp = parse_ndp(s)
    dp = ndp.get_dp()
    for f in range(20):
        ur = dp.solve(f)
        r = list(ur.minimals)[0]
        assert_equal(r, np.ceil(np.sqrt(f))) 
    


@comptest
def check_lang83(): # TODO: rename
    """ Loss of monotonicty. """ 
    s = """
mcdp {
    provides f1 [R]
    provides f2 [R]
    requires r [R]
    required r >= f1 - f2
}
    """
    assert_parse_ndp_semantic_error(s)

@comptest
def check_lang84(): # TODO: rename to LF
    
    # In LF,
    F = parse_poset('m')
    LF = LowerSets(F)
    
    
    lf0 = F.Ls(set([]))
    lf1 = F.L(0.0)
    lf2 = F.L(5.0)
    lf3 = F.L(F.get_top())
    
    # the bottom is lf3
    LF.check_leq(lf3, lf2)
    LF.check_leq(lf3, lf1)
    LF.check_leq(lf3, lf0)
    
    LF.check_leq(lf2, lf1)
    LF.check_leq(lf2, lf0)
    
    LF.check_leq(lf1, lf0)
    
    pass

@comptest
def check_lang85(): # TODO: rename
    a = Rcomp()
    b = Rcomp()
    assert a.__eq__(b)
    assert a == b

@comptest
def check_lang86(): # TODO: rename
    pass

@comptest
def check_lang87(): # TODO: rename
    pass

@comptest
def check_lang88(): # TODO: rename
    pass

@comptest
def check_lang89(): # TODO: rename
    pass 
    

