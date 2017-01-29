# -*- coding: utf-8 -*-
import os

if 'raise_if_test_included' in os.environ:
    raise Exception()

from .test0 import *
from .test1 import *
