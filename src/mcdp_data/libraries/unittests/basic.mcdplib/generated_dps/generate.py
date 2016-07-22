import re
from mcdp_library.library import MCDPLibrary

fn = '../primitivedps.py'

contents = open(fn).read()

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
