# -*- coding: utf-8 -*-
from comptests.registrar import comptest
from mcdp_dp.dp_series import get_product_compact
from mcdp_dp.primitive import Feasible, NotFeasible, NotSolvableNeedsApprox
from mcdp_lang import parse_ndp
from mcdp_posets import PosetProduct, SpaceProduct
from mcdp_posets import R_Energy, R_Time, R_Weight, R_dimensionless
from mcdp_tests.generation import for_all_dps
from nose.tools import assert_equal


@for_all_dps
def check_evaluate_f_m1(id_dp, dp):
    print('Testing %s: %s' % (id_dp, dp))
    F = dp.get_fun_space()
    R = dp.get_res_space()
    M = dp.get_imp_space_mod_res()
    
    f0 = F.get_bottom()
    m0 = M.witness()

    try:
        r = dp.evaluate_f_m(f0, m0)
        R.belongs(r)
    except NotFeasible:
        pass
    except NotSolvableNeedsApprox:
        pass

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
    mcdp {  
    sub f = instance mcdp {
        provides a [R]
            
        requires c [R]
            
        c >= square(a)
    }

    f.a >= square(f.c)
  
      # a^2 > c^2
  }
    """)
    dp = ndp.get_dp()
    print(dp.repr_long())
    M = dp.get_imp_space_mod_res()
    assert_equal(M, SpaceProduct((R_dimensionless,) * 4))
    assert_equal(dp.get_res_space(), SpaceProduct(()))
    assert_equal(dp.get_fun_space(), SpaceProduct(()))

    print dp.solve(())  # = ↑{⟨⟩}
    imps = dp.get_implementations_f_r((), ())
    print imps
    # here, (x,y) => (x,y,y,y) actually I'm not sure
    assert_feasible(dp, (), (0.0, 0.0, 0.0, 0.0), ())
    assert_feasible(dp, (), (1.0, 1.0, 1.0, 1.0), ())
    assert_unfeasible(dp, (), (0.0, 1.0, 1.0, 1.0), ())
    assert_unfeasible(dp, (), (0.0, 0.9, 0.9, 0.9), ())
    assert_feasible(dp, (), (0.5, 0.5, 0.5, 0.5), ())

    assert_unfeasible(dp, (), (1.0, 0.0, 0.0, 0.0), ())
    assert_unfeasible(dp, (), (1.1, 1.1, 1.1, 1.1), ())

    assert_unfeasible(dp, (), (0.9, 0.0, 0.0, 0.0), ())


    import numpy as np
    xs = np.linspace(0, 1.5, 30)
    ys = np.linspace(0, 1.5, 30)
    print_diagram(dp, xs, ys)


#
# y =      1.034  000000000000000000000000000000
# y =      0.982  000000000000000000010000000000
# y =      0.931  000000000000000001100000000000
# y =      0.879  000000000000000111100000000000
# y =      0.827  000000000000001111000000000000
# y =      0.775  000000000000111111000000000000
# y =      0.724  000000000001111110000000000000
# y =      0.672  000000000111111100000000000000
# y =      0.620  000000001111111100000000000000
# y =      0.568  000000011111111000000000000000
# y =      0.517  000000111111110000000000000000
# y =      0.465  000001111111110000000000000000
# y =      0.413  000011111111100000000000000000
# y =      0.362  000111111111000000000000000000
# y =      0.310  001111111110000000000000000000
# y =      0.258  001111111100000000000000000000
# y =      0.206  011111111000000000000000000000
# y =      0.155  011111110000000000000000000000
# y =      0.103  011111100000000000000000000000
# y =      0.051  011110000000000000000000000000
# y =        0.0  100000000000000000000000000000


@comptest
def check_evaluation2():
    ndp = parse_ndp("""
    mcdp {  
    sub f = instance mcdp {
        provides a [R]
            
        requires c [R]
            
        c >= sqrt(a)
    }

    f.a >= sqrt(f.c)
  
  }
    """)
    dp = ndp.get_dp()
    print(dp.repr_long())
    M = dp.get_imp_space_mod_res()

    assert_equal(M, SpaceProduct((R_dimensionless,) * 4))
    assert_equal(dp.get_res_space(), SpaceProduct(()))
    assert_equal(dp.get_fun_space(), SpaceProduct(()))

    assert_feasible(dp, (), (0.0, 0.0, 0.0, 0.0), ())
    assert_feasible(dp, (), (1.0, 1.0, 1.0, 1.0), ())
    assert_feasible(dp, (), (1.1, 1.1, 1.1, 1.1), ())
    assert_unfeasible(dp, (), (0.5, 0.5, 0.5, 0.5), ())
    assert_unfeasible(dp, (), (2.0, 1.0, 1.0, 1.0), ())
    assert_unfeasible(dp, (), (1.0, 2.0, 2.0, 2.0), ())

    import numpy as np
    xs = np.linspace(0, 3.5, 30)
    ys = np.linspace(0, 3.5, 30)
    print_diagram(dp, xs, ys)

# y =        3.5  000000000000000011111111111111
# y =      3.379  000000000000000011111111111111
# y =      3.258  000000000000000111111111111111
# y =      3.137  000000000000000111111111111111
# y =      3.017  000000000000000111111111111111
# y =      2.896  000000000000000111111111111111
# y =      2.775  000000000000001111111111111111
# y =      2.655  000000000000001111111111111111
# y =      2.534  000000000000001111111111111111
# y =      2.413  000000000000011111111111111111
# y =      2.293  000000000000011111111111111111
# y =      2.172  000000000000011111111111111111
# y =      2.051  000000000000111111111111111111
# y =      1.931  000000000000111111111111111111
# y =      1.810  000000000000111111111111111100
# y =      1.689  000000000001111111111111000000
# y =      1.568  000000000001111111111000000000
# y =      1.448  000000000011111111000000000000
# y =      1.327  000000000011111000000000000000
# y =      1.206  000000000011100000000000000000
# y =      1.086  000000000100000000000000000000
# y =      0.965  000000000000000000000000000000
# y =      0.844  000000000000000000000000000000
# y =      0.724  000000000000000000000000000000
# y =      0.603  000000000000000000000000000000
# y =      0.482  000000000000000000000000000000
# y =      0.362  000000000000000000000000000000
# y =      0.241  000000000000000000000000000000
# y =      0.120  000000000000000000000000000000
# y =        0.0  100000000000000000000000000000

def assert_check_feasible_raises(dp, *args):
    try:
        dp.check_feasible(*args)
    except NotFeasible:
        pass
    else:
        msg = 'Expected check_feasible() to raise NotFeasible.'
        msg += 'args = %s' % str(args)
        raise Exception(msg)

def assert_check_unfeasible_raises(dp, *args):
    try:
        dp.check_unfeasible(*args)
    except Feasible:
        pass
    else:
        msg = 'Expected check_unfeasible() to raise Feasible.'
        msg += 'args = %s' % str(args)
        raise Exception(msg)

def assert_feasible(dp, *args):
    dp.check_feasible(*args)
    assert_check_unfeasible_raises(dp, *args)

def assert_unfeasible(dp, *args):
    dp.check_unfeasible(*args)
    assert_check_feasible_raises(dp, *args)

def print_diagram(dp, xs, ys):
    s = ""
    for y in reversed(ys):
        res = []
        for x in xs:
            f = ()
            r = ()
            m = (x, y, y, y)
            try:
                dp.check_feasible(f, m, r)
            except NotFeasible:
                feasible = False
            else:
                feasible = True

            try:
                dp.check_unfeasible(f, m, r)
            except Feasible:
                unfeasible = False
            else:
                unfeasible = True
            if feasible and unfeasible or (not feasible and not unfeasible):
                raise Exception('Point is both feasible and unfeasible: %s %s %s' % (f, m, r))
            res.append(feasible)
            # res.append(unfeasible)

        res = "".join(str(int(w))   for w in res)
        line = 'y = %10.5s  ' % y + "".join(res)
        s += '\n' + line
        print(line)
    return s

