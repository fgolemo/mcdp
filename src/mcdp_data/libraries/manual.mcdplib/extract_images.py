#!/usr/bin/env python

from mcdp_report.gg_utils import extract_assets

import sys, os

filename = sys.argv[1]
dirname = sys.argv[2]

extract_assets(open(filename).read(), dirname)