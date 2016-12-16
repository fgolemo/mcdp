from mcdp_lang.parse_actions import parse_wrap
from mcdp_lang.parse_interface import parse_ndp_refine
from mcdp_lang.suggestions import apply_suggestions, get_suggestions
from mcdp_lang.syntax import Syntax
from mcdp_tests.generation import for_all_source_mcdp
from mocdp.comp.context import Context
from contracts.utils import raise_desc


@for_all_source_mcdp
def check_suggestions(filename, source):  # @UnusedVariable
    
    # skip generated files (hack)
    if 'drone_unc2_' in filename:
        return
    
    # print filename
    source = open(filename).read()
    
    x = parse_wrap(Syntax.ndpt_dp_rvalue, source)[0]
    xr = parse_ndp_refine(x, Context())
    suggestions = get_suggestions(xr)
    for w, r in suggestions:  # @UnusedVariable
        #print('"%s" -> "%s"' % (w.string[w.character:w.character_end], r))
        pass
    print source.__repr__()
    s2 = apply_suggestions(source, suggestions)
    if suggestions:
        print(s2)
        
    # do it a second time
    x = parse_wrap(Syntax.ndpt_dp_rvalue, s2)[0]
    xr = parse_ndp_refine(x, Context())
    suggestions2 = get_suggestions(xr)
    s3 = apply_suggestions(s2, suggestions2)
    
    # the third time, there should not be any more suggestions
    x = parse_wrap(Syntax.ndpt_dp_rvalue, s3)[0]
    xr = parse_ndp_refine(x, Context())
    suggestions3 = get_suggestions(xr)
    
    if suggestions3:
        msg = 'I expected that there are at most 2 rounds of suggestions.'
        raise_desc(ValueError, msg, s=source, s2=s2,s3=s3,suggestions=suggestions,
                   suggestions2=suggestions2, suggestions3=suggestions3)
        
        

        
        