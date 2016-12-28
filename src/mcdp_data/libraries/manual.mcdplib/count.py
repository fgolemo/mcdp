#!/usr/bin/env python

from mcdp_web.renderdoc.latex_inside_equation_abbrevs import count_possible_replacements
import sys
if len(sys.argv) != 2:
    raise Exception('expected 1 argument')
fn = sys.argv[1]
count_possible_replacements(fn)
    