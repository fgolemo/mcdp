from mocdp.unittests.generation import for_all_dps
from comptests.registrar import comptest
from nose.tools import assert_equal
from mocdp.posets.rcomp import R_dimensionless, R_Time, R_Weight, R_Energy
from mocdp.posets.space_product import SpaceProduct
from mocdp.lang.syntax import parse_ndp
import itertools
from mocdp.dp.dp_series import get_product_compact
from mocdp.posets.poset_product import PosetProduct



@for_all_dps
def check_evaluate_f_m1(id_dp, dp):
    print('Testing %s: %s' % (id_dp, dp))
    F = dp.get_fun_space()
    R = dp.get_res_space()
    M = dp.get_imp_space_mod_res()
    
    f0 = F.get_bottom()
    m0 = M.witness()
    r = dp.evaluate_f_m(f0, m0)
    R.belongs(r)

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
    print('F: %s' % F)
    M, pack, unpack = get_product_compact(F1, F2, F3)

    print('M: %s' % M)
    element = (F1.get_top(), F2.get_bottom(), F3.get_top())
    print('elements: %s' % F.format(element))
    s = pack(*element)
    print('packed: %s' % str(s))
    u = unpack(s)
    print('depacked: %s' % str(u))
    assert_equal(u, element)


    F1 = PosetProduct(())
    M, pack, unpack = get_product_compact(F1)

    print('M: %s' % M)
    element = ((),)
    print('elements: %s' % F.format(*element))
    s = pack(*element)
    print('packed: %s' % str(s))
    u = unpack(s)
    print('depacked: %s' % str(u))
    assert_equal(u, element)


@comptest
def check_evaluation():
    ndp = parse_ndp("""
    cdp {  
          f =  cdp {
            provides a [R]
            provides b [R]
            #    
            requires c [R]
            # c >= 0.3 [R] * (a * b)  
            c >= (a * b) + 0.42 [R]
          }

      f.a >= f.c
      f.b >= f.c
  }
    """)
    dp = ndp.get_dp()
    print(dp.repr_long())
    M = dp.get_imp_space_mod_res()
    
    assert_equal(M, SpaceProduct((R_dimensionless, R_dimensionless)))
    assert_equal(dp.get_res_space(), SpaceProduct(()))
    assert_equal(dp.get_fun_space(), SpaceProduct(()))

    bf = dp.is_feasible((), (0.0, 0.0), ())
    print('bf: %s ' % bf)

    import numpy as np
    xs = np.linspace(0, 1, 50)
    ys = np.linspace(0, 1, 50)
    
    for y in reversed(ys):

        res = []
        for x in xs:
            f = ()
            r = ()
            m = (x, y)
            feasible = dp.is_feasible(f, m, r)
            res.append(str(int(feasible)))

        line = 'y = %.3s  ' % y + "".join(res)
        print(line)

