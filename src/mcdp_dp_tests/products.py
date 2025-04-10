# -*- coding: utf-8 -*-
from comptests.registrar import comptest
from mcdp_dp.dp_series import get_product_compact
from mcdp_posets import PosetProduct, R_Energy, R_Time, R_Weight, Rcomp
from nose.tools import assert_equal



@comptest
def check_products1():
    def check_product(S1, S2, expected):
        S, pack, unpack = get_product_compact(S1, S2)
        print(f"product({S1}, {S2}) = {S}  expected {expected}")
        assert_equal(S, expected)

        a = S1.witness()
        b = S2.witness()
        S1.belongs(a)
        S2.belongs(b)
        c = pack(a, b)
        a2, b2 = unpack(c)
        S1.check_equal(a, a2)
        S2.check_equal(b, b2)

        print(f"a = {a}  b = {b}")
        print(f"c = {S} ".format(c))
        print(f"a2 = {a2}  b2 = {b2}")


    R = Rcomp()
    E = R_Weight
    check_product(PosetProduct((R, E)), R, PosetProduct((R, E, R)))
    check_product(PosetProduct((R, R)), E, PosetProduct((R, R, E)))
    check_product(PosetProduct((R, E)), PosetProduct((R, E)), PosetProduct((R, E, R, E)))

    check_product(PosetProduct(()), R, R)
    check_product(PosetProduct(()), PosetProduct((R,)), R)
    check_product(R, PosetProduct(()), R)
    check_product(PosetProduct((R,)), PosetProduct(()), R)




@comptest
def check_products():
    F1 = R_Weight
    F2 = R_Time
    F3 = R_Energy
    M, pack, unpack = get_product_compact(F1, F2, F3)

    print(M)
    s = pack(F1.get_top(), F2.get_bottom(), F3.get_top())
    print(s)
    u = unpack(s)
    assert_equal(u, s)

    F1 = R_Time
    F2 = PosetProduct(())
    F3 = R_Energy
    F = PosetProduct((F1, F2, F3))
    print(f"F: {F}")
    M, pack, unpack = get_product_compact(F1, F2, F3)

    print(f"M: {M}")
    element = (F1.get_top(), F2.get_bottom(), F3.get_top())
    print(f"elements: {F}".format(element))
    s = pack(*element)
    print(f"packed: {str}"(s))
    u = unpack(s)
    print(f"depacked: {str}"(u))
    assert_equal(u, element)

    # NOte now this is different
     
@comptest
def check_products2():
    print('------')
    F1 = PosetProduct(())
    M, pack, unpack = get_product_compact(F1)

    print(f"M: {M}")
    element = ()
    F1.belongs(element)
    print(f"elements: {F}"1.format(element))
    
    s = pack(*(element,))
    print(f"packed: {str}"(s))
    u,  = unpack(s)
    print(f"depacked: {str}"(u))
    assert_equal(u, element)

