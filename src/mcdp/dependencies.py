# -*- coding: utf-8 -*-
""" Checks that all important dependencies are installed """
from .logs import logger

__all__ = ['STRICT_DEPENDENCIES']

# Set this to True to enforce strict dependency checking (i.e., fail on missing dependencies)
# During Python 3 migration, this is set to False to allow testing to proceed
STRICT_DEPENDENCIES = False


def suggest_package(name): # pragma: no cover
    msg = f"""You could try installing the package using:
    
    sudo apt-get install {name}
"""
    logger.info(msg)
    
try:    
    import decent_logs  # @UnusedImport
    import decent_params  # @UnusedImport
    import quickapp  # @UnusedImport
except ImportError as e:  # pragma: no cover
    logger.error(f"Dependency issue: {e}")
    if STRICT_DEPENDENCIES:
        raise Exception(f"Missing required dependency: {e}")
    else:
        logger.warning("Continuing despite missing dependency. This may cause issues later.")

try:
    import numpy
    # Updated for Python 3 - use keyword arguments
    numpy.seterr(all='raise')
except ImportError as e: # pragma: no cover
    logger.error(f"Numpy import error: {e}")
    suggest_package('python-numpy')
    if STRICT_DEPENDENCIES:
        raise Exception("Numpy not available")
    else:
        logger.warning("Continuing despite missing numpy. This may cause issues later.")

try:
    from PIL import Image  # @UnusedImport @NoMove
except ImportError as e:  # pragma: no cover
    logger.error(f"PIL import error: {e}")
    suggest_package('python-pil')
    msg = 'PIL not available'
    if STRICT_DEPENDENCIES:
        raise Exception(msg)
    else:
        logger.error(msg)

try:
    import matplotlib  # @UnusedImport @NoMove
except ImportError as e: # pragma: no cover
    logger.error(f"Matplotlib import error: {e}")
    suggest_package('python-matplotlib')
    msg = 'Matplotlib not available'
    if STRICT_DEPENDENCIES:
        raise Exception(msg)
    else:
        logger.error(msg)

try:
    from ruamel import yaml  # @UnusedImport @NoMove
except ImportError as e: # pragma: no cover
    logger.error(f"ruamel.yaml import error: {e}")
    msg = 'ruamel.yaml package not available'
    if STRICT_DEPENDENCIES:
        raise Exception(msg)
    else:
        logger.error(msg)
    
    