# -*- coding: utf-8 -*-
__version__ = '2.0.9'

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
    raise SystemExit(1)

try:
    from PIL import Image
except ImportError as e:
    logger.error(e)
    suggest_package('python-pil')
    raise SystemExit(1)

try:
    import matplotlib
except ImportError as e:
    logger.error(e)
    suggest_package('python-matplotlib')
    raise SystemExit(1)

try:
    import yaml
except ImportError as e:
    logger.error(e)
    suggest_package('python-yaml')
    raise SystemExit(1)

import conf_tools
import decent_params
import decent_logs
import quickapp
