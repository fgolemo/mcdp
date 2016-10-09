# -*- coding: utf-8 -*-
from comptests.registrar import comptest_fails
from mcdp_dp import Max
from .utils import assert_parsable_to_connected_ndp


@comptest_fails
def check_simplification():
    """
        Simplification for commutative stuff
        
        SimpleWrap
         provides          y (R[s]) 
         provides          x (R[s]) 
         requires          z (R[s]) 
        | Series:   R[s]×R[s] -> R[s]
        | S1 Mux(R[s]×R[s] → R[s]×R[s], [1, 0])
        | S2 Max(R[s])
    
    """
    m1 = assert_parsable_to_connected_ndp("""
    mcdp {
        provides x  [s]
        provides y  [s]
        requires z  [s]
                
        z >= max(x, y)
    }
""")
    dp1 = m1.get_dp()

    m2 = assert_parsable_to_connected_ndp("""
    mcdp {
        provides x  [s]
        provides y  [s]
        requires z  [s]
                
        z >= max(y, x)
    }
""")
    dp2 = m2.get_dp()
    assert isinstance(dp1, Max)
    assert isinstance(dp2, Max)
