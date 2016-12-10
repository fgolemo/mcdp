# -*- coding: utf-8 -*-
from comptests.registrar import comptest, run_module_tests
from mcdp_lang.parse_interface import parse_ndp
from mcdp_lang.dealing_with_special_letters import greek_letters, subscripts
from mcdp_lang.syntax import SyntaxIdentifiers
from mcdp_lang_tests.utils import parse_wrap_check
from nose.tools import assert_equal


@comptest
def special_letters1():
    s = """
    mcdp {
        provides lift [N]
        requires power [W]
        
        requires budget [USD]
        required budget ≥ 1000 USD
        requires mass = 1 kg
        l = provided lift
        #01234
        p₀ = 1 W
        p₁ = 1 W / N
        p₂ = 1 W / N²
        α₁ = 10
        # xₘₐₓ
        required power ≥ p₀ + p₁·l + p₂·l²
    }
"""
    parse_ndp(s)
    
@comptest
def subscript_only_end():
    # these are not valid
    invalid = [u'₁x', u'a₁b', u'x₁₁']
    
@comptest
def special_letters_identifiers():
    examples = [] # ustring, 
    
    for name, letter in greek_letters.items(): 
        identifier = name.encode('utf8')
        appears = letter
        example = (identifier, appears)
        examples.append(example)
    
    for num, subscript in subscripts.items():
        identifier = 'x_%d' % num
        appears = 'x' + subscript
        example = (identifier, appears)  
        examples.append(example)
    
    idn = SyntaxIdentifiers.get_idn()
    
    for identifier, appears in examples:
        appears = appears.encode('utf-8')
        
        res = parse_wrap_check(appears, idn)
        #print('- %r %r -> %r' % (identifier, appears, res))
#         x = '  %s %s -> %s' % (identifier.decode('utf8'), 
#                                appears.decode('utf8'), 
#                                res.decode('utf8'))
        #print(x)
        assert_equal(res, identifier)


@comptest
def check_subs():
    for _num, subscript in subscripts.items():
        subscript = subscript.encode('utf8')
        assert subscript in SyntaxIdentifiers.last_letter
        assert subscript not in SyntaxIdentifiers.mid_letter
        assert subscript not in SyntaxIdentifiers.first_letter


if __name__ == '__main__': 
    run_module_tests()
    
    
    