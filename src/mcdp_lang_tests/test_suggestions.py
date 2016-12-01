from mcdp_tests.generation import for_all_source_mcdp
from mocdp.comp.context import Context
from mcdp_lang.parse_interface import parse_ndp_refine
from mcdp_lang.parse_actions import parse_wrap
from mcdp_lang.syntax import Syntax
from mcdp_lang.suggestions import apply_suggestions, get_suggestions

@for_all_source_mcdp
def check_suggestions(filename, source):  # @UnusedVariable
    # print filename
    source = open(filename).read()
    
    x = parse_wrap(Syntax.ndpt_dp_rvalue, source)[0]
    xr = parse_ndp_refine(x, Context())
    suggestions = get_suggestions(xr)     
    s2 = apply_suggestions(source, suggestions)
    if suggestions:
        print s2