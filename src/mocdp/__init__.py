# -*- coding: utf-8 -*-
__version__ = '2.0.4'

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

import numpy
numpy.seterr('raise')
