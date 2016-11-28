from comptests.registrar import comptest, run_module_tests
from mcdp_lang_tests.utils import parse_wrap_check
from mcdp_lang.syntax import Syntax
from mcdp_lang.utils_lists import unwrap_list, get_odd_ops
from nose.tools import assert_equal
from mcdp_lang.parse_interface import parse_ndp


@comptest
def check_shortcut1():
    x = parse_wrap_check('requires x, y, z [Nat] "comment"', Syntax.res_shortcut5)
    rnames = [_.value for _ in get_odd_ops(unwrap_list(x.rnames))]
    assert_equal(rnames, ['x','y','z'])

    s = parse_wrap_check('provides x, y, z [Nat] "comment"', Syntax.fun_shortcut5)
    rnames = [_.value for _ in get_odd_ops(unwrap_list(s.fnames))]
    assert_equal(rnames, ['x','y','z'])
    

@comptest
def check_shortcut5_context():
    s = """
    mcdp {
        provides f1,f2 [Nat]
        requires r1,r2 [Nat]
    }
    """
    ndp = parse_ndp(s)
    assert_equal(['r1','r2'], ndp.get_rnames())
    assert_equal(['f1','f2'], ndp.get_fnames())
    
#     # 
#     FunShortcut5 = namedtuplewhere('FunShortcut5', 'keyword fnames lbracket unit rbracket comment')
#     # requires x, y, z [Nat] 'comment'
#     ResShortcut5 = namedtuplewhere('ResShortcut5', 'keyword rnames lbracket unit rbracket comment')
    
    
if __name__ == '__main__': 
    run_module_tests()
    
    
    
