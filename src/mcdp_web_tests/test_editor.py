from contracts.utils import check_isinstance, raise_desc
from mcdp_library_tests.tests import get_test_library
from mcdp_tests.generation import for_all_source_mcdp
from mcdp_web.editor_fancy.app_editor_fancy_generic import spec_models, \
    process_parse_request


@for_all_source_mcdp
def check_editor_response(filename, source, libname):  # @UnusedVariable
    if libname in ['loading_python', 'making']:
        # mcdplib-loading_python-source_mcdp-load1.mcdp-check_editor_response
        # mcdplib-making-source_mcdp-test1.mcdp-check_editor_response
        return 
    library = get_test_library(libname)
    string = source
    spec = spec_models
    key = ()
    cache = {}
    res = process_parse_request(library, string, spec, key, cache)
    
    if res['ok']:
        
        
        if 'highlight' in res:
            check_isinstance(res['highlight'], unicode) 
            
    else:
    
        if 'DPNotImplementedError' in res['error']:
            pass
        else:
            msg = 'Failed'
            raise_desc(ValueError, msg, source=source, res=res)
