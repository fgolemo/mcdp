# -*- coding: utf-8 -*-
import os

def safe_makedirs(dirname):
    if not os.path.exists(dirname):
        os.makedirs(dirname)
