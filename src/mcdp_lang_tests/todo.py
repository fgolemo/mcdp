from comptests.registrar import comptest, run_module_tests
from mcdp_lang_tests.utils2 import eval_rvalue_as_constant_same_exactly
from mcdp_lang.parse_interface import parse_ndp, parse_poset
from mocdp.exceptions import DPSemanticError
from contracts.utils import raise_wrapped
from mcdp_lang.syntax import Syntax
from mcdp_lang_tests.utils import parse_wrap_check

@comptest
def check_nat_power():
    eval_rvalue_as_constant_same_exactly('3 ^ 2', 'Nat: 9')
    

@comptest
def check_nat_power_frac():
    eval_rvalue_as_constant_same_exactly('9 ^ (1/2)', 'Rcomp: 3.0')

@comptest
def check_comments_show_up():
    s = """
    # comment1
    mcdp {
        requires x [Nat]
        # comment2
        requires x [Nat]
    }
    """
    try:
        parse_ndp(s)
    except DPSemanticError as e:
        st = str(e)
        if not 'comment2' in st:
            msg = 'Comments are not preserved'
            raise_wrapped(Exception, e, msg)
        

@comptest
def check_add_bottom():
    s = """
    add_bottom poset {
      v1_5 v5 v6_6 
    }
    """
    
    P = parse_poset(s)
    print P.elements
    

@comptest
def check_poset_geq():
    
    parse_wrap_check('a>=b>=c', Syntax.finite_poset_chain_geq)
    parse_wrap_check('a<=b<=c', Syntax.finite_poset_chain_leq)
    
    s = """
    poset {
      a >= b >= c 
    }
    """
    
    P = parse_poset(s)
    print P.elements
    print P.relations



@comptest
def check_poset_bottom_two():
    
    s = """
    add_bottom add_bottom poset {
      a 
    }
    """
    try:
        parse_poset(s)
    except DPSemanticError as e:
        assert 'Poset already has the' in str(e)
        return
    
    assert False


if __name__ == '__main__': 
    run_module_tests()
    
    
    
