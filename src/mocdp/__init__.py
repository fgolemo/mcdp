# -*- coding: utf-8 -*-
__version__ = '2.9.7'

import logging

import decent_logs

from contracts.utils import raise_wrapped
import decent_params
import quickapp


logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def suggest_package(name):
    msg = """You could try installing the package using:
    
    sudo apt-get install %s
""" % name
    logger.info(msg)
    
try:
    import numpy
    numpy.seterr('raise')
except ImportError as e:
    logger.error(e)
    suggest_package('python-numpy')
    raise Exception('Numpy not available')

try:
    from PIL import Image
except ImportError as e:
    logger.error(e)
    suggest_package('python-pil')
    msg = 'PIL not available'
    # raise Exception('PIL not available')
    logger.error(msg)
    # raise_wrapped(Exception, e, msg)

try:
    import matplotlib
except ImportError as e:
    logger.error(e)
    suggest_package('python-matplotlib')
    msg = 'Matplotlib not available'
    logger.error(msg)
    # raise_wrapped(Exception, e, 'Matplotlib not available')

try:
    import yaml
except ImportError as e:
    logger.error(e)
    suggest_package('python-yaml')
    msg = 'YAML package not available'
    logger.error(msg)
#     raise Exception('YAML not available')

# command dot -> graphviz

# import conf_tools

# some constants

# deprecated, used as attr for implementation spaces
ATTRIBUTE_NDP_RECURSIVE_NAME = 'ndp_recursive_name'

# added to NamedDPs
ATTRIBUTE_NDP_MAKE_FUNCTION = 'make'

# added 
ATTR_LOAD_NAME = '__mcdplibrary_load_name'
ATTR_LOAD_LIBNAME = '__mcdplibrary_load_libname'
ATTR_LOAD_REALPATH = '__mcdplibrary_load_realpath'


class MCDPConstants():
    """ Some system-wide constants """
    
    # source
    
    indent = 4
    tabsize = 4
        
    
    #
    # Compilation stage
    #
    
    # only compile to graphs using two-factor multiplication for functions
    force_mult_two_functions = True
    # only compile to graphs using two-factor multiplication for resources
    force_mult_two_resources = True
    
    force_plus_two_resources = True
    
    # force_plus_two_functions = True # currently unused (InvPlus2 -> InvPlusN)
    
    # TODO: make algo configurable for invplus, etc. see also: InvMult2.ARGO 
    
    #
    # Testing
    #
    
    Nat_chain_include_maxint = False
    Rcomp_chain_include_tiny = False
    Rcomp_chain_include_eps = False
    Rcomp_chain_include_max = False
    
    # test the correspondence between h and h* (currently failing)
    test_dual01_chain = False
    
    # Ignore graphviz errors in unit tests
    test_ignore_graphviz_errors = True
    
    # Ignore the known failures
    test_include_primitivedps_knownfailures = False
    
    # only draw 1/20th of pictures
    test_fraction_of_allreports = 0.025
     
    test_insist_correct_html_from_ast_to_html = False
    #
    # UI
    #
    
    # Affects things like Nat
    use_unicode_symbols = False
    
    # Any time we need to solve a relation like (r1*r2==f),
    # we will bound r1 and r2 in the interval [eps, 1/eps].
    inv_relations_eps = numpy.finfo(float).eps # ~1e-16
    # TODO: think whether this makes us optimistic or pessimistic, and where
    
    # threshold above which we output a warning
    parsing_too_slow_threshold = 0.5

    log_cache_writes = False
    
    InvPlus2Nat_max_antichain_size=  100000
    InvMult2Nat_memory_limit   = 10000
    
    # Actually write to disk the reports
    test_allformats_report_write = False
    
    # this can be changed by customer. The other configuration switches
    # are all relative.
    diagrams_fontsize = 14

    diagrams_smallimagesize_rel = 0.4
    diagrams_leqimagesize_rel = 0.3
    diagrams_bigimagesize_rel = 60  
    
    # how much to scale the produced svg from dots
    # if diagrams_fontsize = 14 and you want the font to be 10,
    # use 10.0
    svg_apparent_fontsize = 10.0 
    scale_svg = svg_apparent_fontsize / float(diagrams_fontsize)
    
    # useful for debugging css
    # for (1) manual and (2) mcdp-render
    manual_link_css_instead_of_including = True
    
    
#     pdf_to_png_dpi = 300 # dots per inch
    pdf_to_png_dpi = 100 # dots per inch
    
    
def get_mcdp_tmp_dir():
    from tempfile import gettempdir
    import os
    d0 = gettempdir()
    d = os.path.join(d0, 'mcdp_tmp_dir')
    from mcdp_report.utils import safe_makedirs
    if not os.path.exists(d):
        os.makedirs(d)
    return d
