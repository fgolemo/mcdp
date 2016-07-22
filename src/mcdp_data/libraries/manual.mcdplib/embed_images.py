#!/usr/bin/env python

from mcdp_report.gg_utils import embed_images

import sys, os

filename = sys.argv[1]
dirname = os.path.dirname(filename)

html2 = embed_images(open(filename).read(), dirname)

with open(filename, 'w') as f:
    f.write(html2)
