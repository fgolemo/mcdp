from comptests.registrar import comptest
from mcdp_lang.namedtuple_tricks import recursive_print
from mcdp_lang.parse_interface import parse_constant, parse_ndp, parse_poset
from mcdp_lang.parts import CDPLanguage
from mcdp_lang.syntax import Syntax
from mcdp_lang_tests.utils import parse_wrap_check
from mcdp_posets.finite_poset import FinitePoset
from mcdp_posets.uppersets import UpperSets

CDP = CDPLanguage

@comptest
def check_lang_singlespace1():
#      SingleElementPosetKeyword = namedtuplewhere('SingleElementPosetKeyword', 'keyword')
#     SingleElementPosetTag = namedtuplewhere('SingleElementPosetTag', 'value')
#     SingleElementPoset = namedtuplewhere('SingleElementPoset', 'keyword tag')

    p = parse_wrap_check('S(singleton)', Syntax.space_single_element_poset,
                     CDP.SingleElementPoset(CDP.SingleElementPosetKeyword('S'),
                                            CDP.SingleElementPosetTag(value='singleton')))

    print recursive_print(p)

@comptest
def check_lang_singlespace2():
    P = parse_poset('S(singleton)')
    assert P == FinitePoset(set(['singleton']), [])
    c = parse_constant('S(singleton):*')
    assert c.value == 'singleton'

@comptest
def check_lang_singlespace3():
    ndp1 = parse_ndp("""
    mcdp {
        provides power [ S(electric_power) x W ] 
    
        requires heat  [ S(heat) x W ]
    
        efficiency = 0.9 []
        
        r_heat = take(required heat, 1)
        f_power = take(provided power, 1)
        
        
        r_heat >= f_power / efficiency 
    }
    
    """)

    ndp2 = parse_ndp("""
    mcdp {
        provides power [ S(electric_power) x W ] 
    
        requires heat  [ S(heat) x W ]
    
        efficiency = 0.9 []
        
        f_power = take(provided power, 1)
        
        
        heat >= <S(heat):*, f_power / efficiency> 
    }
    
    """)
    dp1 = ndp1.get_dp()
    dp2 = ndp2.get_dp()
    R = dp1.get_res_space()
    print type(R), R
    UR = UpperSets(R)
    res1 = dp1.solve(('electric_power', 10.0))
    res2 = dp2.solve(('electric_power', 10.0))
    print UR.format(res1)
    print UR.format(res2)

@comptest
def check_lang_singlespace4():
    pass


@comptest
def check_lang_singlespace5() :pass
@comptest
def check_lang_singlespace6() :pass
@comptest
def check_lang_singlespace7() :pass
@comptest
def check_lang_singlespace8() :pass
@comptest
def check_lang_singlespace9() :pass
@comptest
def check_lang_singlespace10() :pass
