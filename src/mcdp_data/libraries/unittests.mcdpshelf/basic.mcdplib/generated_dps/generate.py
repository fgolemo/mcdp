# -*- coding: utf-8 -*-
import re
from mcdp_library import MCDPLibrary
from mcdp import MCDPConstants
from mcdp_dp_tests.primitivedps import all_primitivedps_tests

fn = '../primitivedps.py'

# contents = open(fn).read()

# lines = contents.split('\n')
# # throw away comments
# lines = [_ for _ in lines if not '#' in _]
# contents = '\n'.join(lines)

# r = re.compile('def\s+([\w]+)')

# for func in r.findall(contents):
for func0 in all_primitivedps_tests:
    ext = MCDPConstants.ext_primitivedps
    func = func0.__name__
    fn = '%s.%s' % (func, ext)
    contents = """
code mcdp_dp_tests.primitivedps.%s
""" % func

    with open(fn, 'w') as f:
        f.write(contents)

    #print('Created %r.' % fn)
