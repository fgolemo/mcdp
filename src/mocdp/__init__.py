# -*- coding: utf-8 -*-
__version__ = '2.0.10'

import logging
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
    raise Exception('PIL not available')

try:
    import matplotlib
except ImportError as e:
    logger.error(e)
    suggest_package('python-matplotlib')
    raise Exception('Matplotlib not available')

try:
    import yaml
except ImportError as e:
    logger.error(e)
    suggest_package('python-yaml')
    raise Exception('YAML not available')

# command dot -> graphviz

import conf_tools
import decent_params
import decent_logs
import quickapp
