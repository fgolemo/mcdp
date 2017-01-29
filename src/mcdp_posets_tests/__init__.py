# -*- coding: utf-8 -*-
import os

if 'raise_if_test_included' in os.environ:
    raise Exception()

from .basic import *
from .joins import *
from .coproducts import *
from .advanced_embedding import *
from .test_find_poset_minima import *
