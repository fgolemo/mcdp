# -*- coding: utf-8 -*-
__version__ = '2.1.3'

import logging
from contracts.utils import raise_wrapped
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
import decent_params
import decent_logs
import quickapp

# some constants

# deprecated, used as attr for implementation spaces
ATTRIBUTE_NDP_RECURSIVE_NAME = 'ndp_recursive_name'

# added to NamedDPs
ATTRIBUTE_NDP_MAKE_FUNCTION = 'make'

# added 
ATTR_LOAD_NAME = '__mcdplibrary_load_name'
ATTR_LOAD_LIBNAME = '__mcdplibrary_load_libname'


class MCDPConstants:
    
    
    # only compile to graphs using two-factor multiplication for functions
    force_mult_two_functions = True
    # only compile to graphs using two-factor multiplication for resources
    force_mult_two_resources = True
    
    force_plus_two_resources = True
    
    
    # see also: InvMult2.ARGO
    # see also: the other thing
    
    # testing
    Nat_chain_include_maxint = False
    Rcomp_chain_include_tiny = False
    Rcomp_chain_include_eps = False
    Rcomp_chain_include_max = False
    
    # test the correspondence between h and h*
    test_dual01_chain = False
    
