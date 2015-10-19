from mocdp.unittests.generation import for_all_dps
from comptests.registrar import comptest
from nose.tools import assert_equal
from mocdp.posets.rcomp import R_dimensionless, R_Time, R_Weight, R_Energy
from mocdp.posets.space_product import SpaceProduct
from mocdp.lang.syntax import parse_ndp
from mocdp.dp.dp_series import get_product_compact
from mocdp.posets.poset_product import PosetProduct
from mocdp.dp.primitive import NotFeasible, Feasible



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
            
        requires c [R]
            
        c >= square(a)
    }

    f.a >= square(f.c)
  
  }
    """)
    dp = ndp.get_dp()
    print(dp.repr_long())
    M = dp.get_imp_space_mod_res()
    
    assert_equal(M, SpaceProduct((R_dimensionless, R_dimensionless)))
    assert_equal(dp.get_res_space(), SpaceProduct(()))
    assert_equal(dp.get_fun_space(), SpaceProduct(()))

#     # this is wrong
#     dp.check_feasible((), (0.9, 0.0), ())

    def assert_check_feasible_raises(*args):
        try:
            dp.check_feasible(*args)
        except NotFeasible:
            pass
        else:
            msg = 'Expected check_feasible() to raise NotFeasible.'
            msg += 'args = %s' % str(args)
            raise Exception(msg)

    def assert_check_unfeasible_raises(*args):
        try:
            dp.check_unfeasible(*args)
        except Feasible:
            pass
        else:
            msg = 'Expected check_unfeasible() to raise Feasible.'
            msg += 'args = %s' % str(args)
            raise Exception(msg)

#     dp.check_unfeasible((), (0.0, 0.0), ())

    def assert_feasible(*args):
        dp.check_feasible(*args)
        assert_check_unfeasible_raises(*args)
    def assert_unfeasible(*args):
        dp.check_unfeasible(*args)
        assert_check_feasible_raises(*args)


    assert_feasible((), (0.0, 0.0), ())
    assert_feasible((), (1.0, 1.0), ())
    assert_unfeasible((), (0.0, 1.0), ())
    assert_unfeasible((), (0.0, 0.9), ())
    assert_feasible((), (0.5, 0.5), ())


    assert_unfeasible((), (1.0, 0.0), ())
    assert_unfeasible((), (1.1, 1.1), ())

    assert_unfeasible((), (0.9, 0.0), ())


    import numpy as np
    xs = np.linspace(0, 1.5, 30)
    ys = np.linspace(0, 1.5, 30)
    
    for y in reversed(ys):

        res = []
        for x in xs:
            f = ()
            r = ()
            m = (x, y)
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
        print(line)

