import os

from contracts.utils import check_isinstance, raise_desc

from mcdp_library_tests.tests import get_test_library
from mcdp_tests.generation import for_all_source_all
from mcdp_web.editor_fancy.app_editor_fancy_generic import process_parse_request, specs
from mcdp_web.visualization.app_visualization import generate_view_syntax
from mcdp_library.specs_def import SPEC_POSETS, SPEC_VALUES,\
    SPEC_TEMPLATES, SPEC_MODELS


def filename2spec(filename): # TODO: move to specs
    """ returns the corresponding spec based on filename """
    
    _, dot_extension = os.path.splitext(filename)
    extension = dot_extension[1:]
    extension2spec= {
        'mcdp': specs[SPEC_MODELS],
        'mcdp_template': specs[SPEC_TEMPLATES],
        'mcdp_value': specs[SPEC_VALUES],
        'mcdp_poset': specs[SPEC_POSETS],
    }
    spec = extension2spec[extension]
    return spec

@for_all_source_all
def check_editor_response(filename, source, libname):  # @UnusedVariable
    if libname in ['loading_python', 'making']:
        # mcdplib-loading_python-source_mcdp-load1.mcdp-check_editor_response
        # mcdplib-making-source_mcdp-test1.mcdp-check_editor_response
        return 
    library = get_test_library(libname)
    string = source
    spec = filename2spec(filename)
   
    key = ()
    cache = {}
    make_relative = lambda x: x
    res = process_parse_request(library, string, spec, key, cache, make_relative)
    
    if res['ok']:
        
        if 'highlight' in res:
            check_isinstance(res['highlight'], unicode) 
            
    else:
        forgive = ['Could not find file', 'DPNotImplementedError']
    
        if any(_ in  res['error'] for _ in forgive):
            pass
        else:
            msg = 'Failed'
            raise_desc(ValueError, msg, source=source, res=res)


@for_all_source_all
def check_generate_view_syntax(filename, source, libname):  # @UnusedVariable
    library = get_test_library(libname)
    spec = filename2spec(filename)
    
    name, _ext = os.path.splitext(os.path.basename(filename))
    make_relative = lambda x: x
    _res = generate_view_syntax(libname, library, name,  spec, make_relative)
