# -*- coding: utf-8 -*-
__version__ = '1.2.0'

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from .configuration import *
import mcdp_posets
# from . import dp

import numpy
numpy.seterr('raise')
