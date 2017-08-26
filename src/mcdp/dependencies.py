# -*- coding: utf-8 -*-
""" Checks that all important dependencies are installed """
from .logs import logger
import traceback

__all__ = []


def suggest_package(name): # pragma: no cover
    msg = """You could try installing the package using:
    
    sudo apt-get install %s
""" % name
    logger.info(msg)
    
try:    
    import decent_logs  # @UnusedImport
    import decent_params  # @UnusedImport
    import quickapp  # @UnusedImport
except ImportError as e:  # pragma: no cover
    logger.error(e)
    suggest_package('quickapp')
    raise Exception('quickapp not available: %s' % traceback.format_exc(e))

try:
    import numpy
    numpy.seterr('raise')
except ImportError as e: # pragma: no cover
    logger.error(e)
    suggest_package('python-numpy')
    raise Exception('Numpy not available')

try:
    from PIL import Image  # @UnusedImport @NoMove
except ImportError as e:  # pragma: no cover
    logger.error(e)
    suggest_package('python-pil')
    msg = 'PIL not available'
    # raise Exception('PIL not available')
    logger.error(msg)
    # raise_wrapped(Exception, e, msg)

try:
    import matplotlib  # @UnusedImport @NoMove
except ImportError as e: # pragma: no cover
    logger.error(e)
    suggest_package('python-matplotlib')
    msg = 'Matplotlib not available'
    logger.error(msg)
    # raise_wrapped(Exception, e, 'Matplotlib not available')

try:
    from ruamel import yaml  # @UnusedImport @NoMove
except ImportError as e: # pragma: no cover
    logger.error(e)
    msg = 'rueml.yaml package not available'
    logger.error(msg)
    
    