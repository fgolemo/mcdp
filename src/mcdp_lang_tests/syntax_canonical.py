from mcdp_lang_tests.utils import assert_parsable_to_connected_ndp
from comptests.registrar import comptest

@comptest
def check_canonical1():
    ndp = assert_parsable_to_connected_ndp("""
        canonical mcdp { } 
""")



@comptest
def check_canonical2():
    pass


@comptest
def check_canonical3():
    pass


@comptest
def check_canonical4():
    pass

@comptest
def check_canonical5():
    pass
