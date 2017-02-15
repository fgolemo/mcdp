# -*- coding: utf-8 -*-

import getpass

import warnings

import decent_logs

from contracts.enabling import all_disabled
from contracts.utils import raise_wrapped
import decent_params
import quickapp


#     raise Exception('YAML not available')

# command dot -> graphviz

# some constants


        
def get_mcdp_tmp_dir():
    from tempfile import gettempdir
    import os
    d0 = gettempdir()
    d = os.path.join(d0, 'mcdp_tmp_dir')
    from mcdp_report.utils import safe_makedirs
    if not os.path.exists(d):
        os.makedirs(d)
    return d
