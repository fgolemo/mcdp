from mocdp.unittests.generation import for_all_dps
from mocdp.posets.poset_product import PosetProduct
from mocdp.posets.rcomp import Rcomp, R_Weight
from comptests.registrar import comptest
from mocdp.dp.dp_series import get_product_compact
from nose.tools import assert_equal



@for_all_dps
def check_dp1(id_dp, dp):
    print('Testing %s: %s' % (id_dp, dp))
    funsp = dp.get_fun_space()
    ressp = dp.get_res_space()
    trsp = dp.get_tradeoff_space()
    print('F: %s' % funsp)
    print('R: %s' % ressp)

    I = dp.get_imp_space()
    M = dp.get_imp_space_mod_res()
    print('I: %s' % I)
    print('M: %s' % M)

    f_top = funsp.get_top()
    f_bot = funsp.get_bottom()

#     if isinstance(dp, DPLoop0):
#         return

    u0 = dp.solve(f_bot)
    u1 = dp.solve(f_top)

    print('u0', u0)
    print('u1', u1)

    trsp.check_leq(u0, u1)


@for_all_dps
def check_dp2(_id_dp, dp):
    from mocdp.posets.utils import poset_check_chain

    funsp = dp.get_fun_space()

    chain = funsp.get_test_chain(n=5)
    poset_check_chain(funsp, chain)

#     if isinstance(dp, DPLoop):
#         return

    trchain = map(dp.solve, chain)

    trsp = dp.get_tradeoff_space()
    poset_check_chain(trsp, trchain)

    print trchain

@comptest
def check_products1():
    def check_product(S1, S2, expected):
        S, pack, unpack = get_product_compact(S1, S2)
        print('product(%s, %s) = %s  expected %s' % (S1, S2, S, expected))
        assert_equal(S, expected)

        a = S1.witness()
        b = S2.witness()
        S1.belongs(a)
        S2.belongs(b)
        c = pack(a, b)
        a2, b2 = unpack(c)
        S1.check_equal(a, a2)
        S2.check_equal(b, b2)

        print('a = %s  b = %s' % (a, b))
        print('c = %s ' % S.format(c))
        print('a2 = %s  b2 = %s' % (a2, b2))


    R = Rcomp()
    E = R_Weight
    check_product(PosetProduct((R, E)), R, PosetProduct((R, E, R)))
    check_product(PosetProduct((R, R)), E, PosetProduct((R, R, E)))
    check_product(PosetProduct((R, E)), PosetProduct((R, E)), PosetProduct((R, E, R, E)))

    check_product(PosetProduct(()), R, R)
    check_product(PosetProduct(()), PosetProduct((R,)), R)
    check_product(R, PosetProduct(()), R)
    check_product(PosetProduct((R,)), PosetProduct(()), R)


