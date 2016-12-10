from mcdp_tests.generation import for_all_source_mcdp
from mcdp_library.library import MCDPLibrary
from mcdp_web.editor_fancy.app_editor_fancy_generic import spec_models,\
    process_parse_request
from nose.tools import assert_equal



@for_all_source_mcdp
def check_editor_response(filename, source):  # @UnusedVariable 
    
    library = MCDPLibrary()
    string = source
    spec = spec_models
    key = ()
    cache = {}
    res = process_parse_request(library, string, spec, key, cache)
    
    assert_equal(res['ok'], True) 