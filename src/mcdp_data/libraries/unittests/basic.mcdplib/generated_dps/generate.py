# -*- coding: utf-8 -*-
import re
from mcdp_library.library import MCDPLibrary

fn = '../primitivedps.py'

contents = open(fn).read()

lines = contents.split('\n')
# throw away comments
lines = [_ for _ in lines if not '#' in _]
contents = '\n'.join(lines)

r = re.compile('def\s+([\w]+)')

for func in r.findall(contents):
    ext = MCDPLibrary.ext_primitivedps

    fn = '%s.%s' % (func, ext)
    contents = """
code primitivedps.%s  
""" % func

    with open(fn, 'w') as f:
        f.write(contents)

    print('Created %r.' % fn)
