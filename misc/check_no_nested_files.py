import os
from conf_tools.utils import locate_files

extensions = ['mcdp', 'mcdp_poset', 'mcdp_template', 'mcdp_primitivedp', 'mcdp_value']

for ext in extensions:
    filenames = locate_files('src', '*' + ext)
    for f in filenames:
        dirname = os.path.dirname(f)
        if 'shelf' in dirname and  not dirname.endswith('mcdplib') and not 'old' in dirname:
            print f
