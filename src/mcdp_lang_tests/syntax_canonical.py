from mcdp_lang_tests.utils import assert_parsable_to_connected_ndp
from comptests.registrar import comptest

@comptest
def check_canonical1():
    assert_parsable_to_connected_ndp("""
canonical mcdp {
    f = instance mcdp  {
        provides a [Nat]
        
        requires x [Nat]
        requires y [Nat]
        
        x + y >= a
    }

    provides z [Nat]

    f.a >= f.x + f.y + z 

    requires x, y for f
}
"""
 )



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
