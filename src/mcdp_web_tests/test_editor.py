from nose.tools import assert_equal

from contracts.utils import check_isinstance
from mcdp_library_tests.tests import get_test_library
from mcdp_tests.generation import for_all_source_mcdp
from mcdp_web.editor_fancy.app_editor_fancy_generic import spec_models, \
    process_parse_request


@for_all_source_mcdp
def check_editor_response(filename, source, libname):  # @UnusedVariable 
    library = get_test_library(libname)
    string = source
    spec = spec_models
    key = ()
    cache = {}
    res = process_parse_request(library, string, spec, key, cache)
    
    assert_equal(res['ok'], True)
    
    if 'highlight' in res:
        check_isinstance(res['highlight'], unicode) 