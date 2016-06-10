from comptests.registrar import comptest
from mcdp_posets.poset_product import PosetProduct
from mcdp_posets.category_coproduct import Coproduct1
from mcdp_posets.rcomp_units import R_Weight, R_Energy, R_Time

@comptest
def check_coproduct1():
    S1 = R_Weight
    S2 = PosetProduct((R_Time, R_Energy))

    C = Coproduct1((S1, S2))

    x = C.witness()
    C.belongs(x)
    print C.format(x)

    
    i, xi = C.unpack(x)
    
    if i == 0:
        S1.belongs(xi)
    elif i == 1:
        S2.belongs(xi)
    else:
        assert False

    r = C.pack(i, xi)
    C.check_equal(r, x)
