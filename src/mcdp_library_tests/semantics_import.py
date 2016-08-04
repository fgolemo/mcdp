from comptests.registrar import comptest
from mcdp_lang.parse_interface import parse_ndp

@comptest
def feat_import1():

    s = """
        mcdp {
            from lib1 import s
        }
    """
    parse_ndp(s)


@comptest
def feat_import2():
    pass

@comptest
def feat_import3():
    pass

@comptest
def feat_import4():
    pass

@comptest
def feat_import5():
    pass

@comptest
def feat_import6():
    pass

@comptest
def feat_import7():
    pass

@comptest
def feat_import8():
    pass

@comptest
def feat_import9():
    pass
