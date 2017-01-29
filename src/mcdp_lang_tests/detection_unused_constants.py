from nose.tools import assert_equal

from comptests.registrar import comptest, run_module_tests, comptest_fails
from mcdp_lang.eval_warnings import MCDPWarnings
from mcdp_lang.parse_interface import parse_ndp
from mocdp.comp.context import ModelBuildingContext


@comptest_fails
def warning_unused_variable1(): # TODO: rename
    s = """
    mcdp {
        c = 42
    }
    """ 
    context = ModelBuildingContext()
    ndp = parse_ndp(s, context)
    w = context.warnings
    print ndp.repr_long()
    assert_equal(len(w), 1)
    assert_equal(w[0].which, MCDPWarnings.LANGUAGE_UNUSED_CONSTANT)



if __name__ == '__main__': 
    run_module_tests()
    
    
    