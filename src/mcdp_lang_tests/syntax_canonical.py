from comptests.registrar import comptest
from mcdp_lang import parse_ndp
from .utils import assert_parsable_to_connected_ndp


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
def check_canonical2(): # change
    ndp = parse_ndp("""
 mcdp {
    A = instance catalogue  {
        provides f1 [g]
        requires r1 [J]
        
        a1 | 10 g | 10 J 
        a2 | 15 g | 15 J
    }

    B = instance catalogue  {
        provides f2 [J]
        requires r2 [W]
        
        b1 | 10 J | 10 W 
        b2 | 15 J | 15 W
    }

    provides f <= A.f1
    A.r1 <= B.f2
    requires r >= B.r2
}
""")
    dp = ndp.get_dp()
    print(dp.repr_long())
    I = dp.get_imp_space()
    print('I: %s' % I)



@comptest
def check_canonical3():
    pass


@comptest
def check_canonical4():
    pass

@comptest
def check_canonical5():
    pass
