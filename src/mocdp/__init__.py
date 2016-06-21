# -*- coding: utf-8 -*-
__version__ = '2.0.0'

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

import numpy
numpy.seterr('raise')


def add_vendor():
    import os
    import sys

    # Add vendor directory to module search path
    parent_dir = os.path.abspath(os.path.dirname(__file__))
    vendor_dir = os.path.join(parent_dir, 'vendor')

    assert os.path.exists(vendor_dir)

    sys.path.insert(0, vendor_dir)


add_vendor()
