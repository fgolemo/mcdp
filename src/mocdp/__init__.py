# -*- coding: utf-8 -*-
__version__ = '2.0.1'

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

import numpy
numpy.seterr('raise')
