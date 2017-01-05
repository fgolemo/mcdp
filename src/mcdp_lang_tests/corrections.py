# -*- coding: utf-8 -*-
from nose.tools import assert_equal

from comptests.registrar import comptest, run_module_tests
from mcdp_lang.parse_actions import parse_wrap
from mcdp_lang.parse_interface import parse_ndp_refine
from mcdp_lang.parts import CDPLanguage
from mcdp_lang.suggestions import get_suggestions, apply_suggestions,\
    get_suggestion_identifier
from mcdp_lang.syntax import Syntax
from mcdp_report.out_mcdpl import ast_to_mcdpl
from mocdp.comp.context import Context
from contracts.utils import indent
from mcdp_lang.dealing_with_special_letters import ends_with_divider,\
    starts_with_divider


CDP = CDPLanguage

# @comptest
def check_correction():
    s = """
    mcdp {  
 provides endurance [s] 
 provides payload   [kg]
 battery = instance template 
  mcdp {
    provides capacity [J]
    requires mass     [kg]
  }
 actuation = instance template 
  mcdp {
    provides lift  [N]
    requires power [W]
  }
 capacity provided by battery >= 
    endurance * (actuation.power)
a = power required by actuation
b = lift provided by actuation
 g = 9.81 m/s^2
 actuation.lift  >=
    (mass required by battery + payload) * g
}"""
    try_corrections2(s)
    
#     try_corrections(s)
# 
# def style_correction_transform(x, parents):  # @UnusedVariable
#     if isinstance(x, CDP.leq):
#         return CDP.leq('≤', where=x.where)
#     if isinstance(x, CDP.geq):
#         return CDP.geq('≥', where=x.where)
#         
#     if isinstance(x, CDP.NewFunction) and x.keyword is None:
#         w0 = x.where
#         w = Where(w0.string, w0.character, w0.character)
#         keyword = CDP.ProvidedKeyword('provided', w)
#         x2 = CDP.NewFunction(keyword=keyword, name=x.name, where=w0)
#         return x2
# #     
# #     if isinstance(x, CDP.Resource) and isinstance(x.keyword, CDP.DotPrep):
# # #         w0 = x.where
# #         s = '%s required by %s' % (x.s.value, x.dp.value)
# #         print s.__repr__()
# #         x2 = parse_wrap(Syntax.rvalue_resource_fancy, s)[0]
# #         
# # #         w = Where(w0.string, w0.character, w0.character)
# # #         keyword = CDP.ProvidedKeyword('provided', w)
# # #         x2 = CDP.Resource(dp=x.dp, s=x., where=w0)
# #         return x2
#     
# 
#     return x
# 
# def try_corrections(s):
#     x = parse_wrap(Syntax.ndpt_dp_rvalue, s)[0]
# #     print recursive_print(x)
#     context = Context()
#     xr = parse_ndp_refine(x, context)
# #     print recursive_print(xr)
#     t = namedtuple_visitor_ext(xr, style_correction_transform)
#     print recursive_print(t)
#     ts = ast_to_mcdpl(t)
#     print ts
#     
#     x2 = parse_wrap(Syntax.ndpt_dp_rvalue, ts)[0]
# #     print recursive_print(x2)

        
def try_corrections2(s):
    x = parse_wrap(Syntax.ndpt_dp_rvalue, s)[0]
    context = Context()
    xr = parse_ndp_refine(x, context)
    suggestions = get_suggestions(xr)
   
    for orig_where, sub in suggestions:
        orig_1 = orig_where.string[orig_where.character:orig_where.character_end]
        
        print 'Change %r in %r' % (orig_1, sub)
        
    s2 = apply_suggestions(s, suggestions)
    #print s2
    _x2 = parse_wrap(Syntax.ndpt_dp_rvalue, s2)[0]
    return s2
#     print recursive_print(t)
#     ts = ast_to_mcdpl(t)
#     print ts
#      
#     x2 = parse_wrap(Syntax.ndpt_dp_rvalue, ts)[0]
# #     print recursive_print(x2)
CDP = CDPLanguage

# @comptest
def check_print():
    s = """ mcdp {
#     provides f [m]
    f <= 10 m
    } """
    x = parse_wrap(Syntax.ndpt_dp_rvalue, s)[0]
    s2 = ast_to_mcdpl(x) 
    assert_equal(s.strip(), s2.strip())
    
    


@comptest
def check_suggestions_greek1():
    s = """ mcdp {
     provides eta [m]
     provides rho [m]
     provides rho_1 [m]
     provides alpha [m]
     provides alphabet [m]
    } """
 
    s2 = try_corrections2(s)
    print indent(s, 's : ')
    print indent(s2, 's2: ')
    
    assert 'eta' not in s2
    assert 'alpha ' not in s2
    assert 'α' in s2
    assert 'η' in s2
    assert 'alphabet' in s2
    assert 'ρ₁' in s2
    
@comptest
def check_get_suggestion_identifier1():
    assert ends_with_divider('rho₁')
    assert starts_with_divider('₁a')
    assert ends_with_divider('rho_')
    assert starts_with_divider('_a')
    assert_equal(get_suggestion_identifier('eta'), ('eta', 'η'))
    assert_equal(get_suggestion_identifier('alpha'), ('alpha', 'α'))
    assert_equal(get_suggestion_identifier('alphabet'), None)
    assert_equal(get_suggestion_identifier('rho'), ('rho', 'ρ'))
    assert_equal(get_suggestion_identifier('a_1'), ('_1', '₁'))
    assert_equal(get_suggestion_identifier('rho_1'), ('rho_1', 'ρ₁'))
    assert_equal(get_suggestion_identifier('alpha_rho_1'), ('alpha_rho_1', 'α_ρ₁'))
    assert_equal(get_suggestion_identifier('rho_rho_1'), ('rho_rho_1', 'ρ_ρ₁'))
    
    
if __name__ == '__main__': 
    
    run_module_tests()
    
    
    
    