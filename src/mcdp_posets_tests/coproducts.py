from comptests.registrar import comptest
from mcdp_posets.poset_product import PosetProduct
from mcdp_posets.category_coproduct import Coproduct1
from mcdp_posets.rcomp_units import R_Weight, R_Energy, R_Time
from mcdp_posets.poset_coproduct import PosetCoproduct
from mcdp_posets.types_universe import express_value_in_isomorphic_space

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


@comptest
def check_coproduct_embedding1():
    from mcdp_posets.finite_poset import FinitePoset
    A = FinitePoset(set(['a1', 'a2', 'a3']), [])
    B = FinitePoset(set(['b1', 'b2']), [])

    P = PosetCoproduct((A, B))

    a = 'a1'
    A.belongs(a)
    p = express_value_in_isomorphic_space(A, a, P)

    # a2 = express_value_in_isomorphic_space(P, p, A)
    # A.belongs(a2)

    print p

@comptest
def check_coproduct_embedding2():
    pass

@comptest
def check_coproduct_embedding3():
    pass

@comptest
def check_coproduct_embedding4():
    pass

@comptest
def check_coproduct_embedding5():
    pass

@comptest
def check_coproduct_embedding6():
    pass
