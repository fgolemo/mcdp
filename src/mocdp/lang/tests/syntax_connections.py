from comptests.registrar import comptest
from mocdp.lang.tests.utils import assert_parsable_to_connected_ndp
from mocdp.posets.uppersets import UpperSets

@comptest
def check_lang_connections1():
    """ This is considered connected. """

    ndp = assert_parsable_to_connected_ndp("""
mcdp {
    provides a [g]
    
    a <= 10 g 
}""")

    dp = ndp.get_dp()

    I = dp.get_imp_space()
    R = dp.get_res_space()
    M = dp.get_imp_space_mod_res()

    print("I: %s" % I)
    print("M: %s" % M)
    print("R: %s" % R)
    UR = UpperSets(R)
    empty = R.Us(set())

    ur1 = dp.solve(5.0)
    ur2 = dp.solve(14.0)

    print('ur1: %s' % ur1)
    print('ur2: %s' % ur2)

    UR.check_equal(empty, ur2)
    # UR.check_not_equal(empty, ur1)



@comptest
def check_lang_connections2():
    """ This is considered connected. """

    ndp = assert_parsable_to_connected_ndp("""
mcdp {
    requires b [s]
    
    b >= 10 s
}""")

    dp = ndp.get_dp()

    I = dp.get_imp_space()
    F = dp.get_fun_space()
    R = dp.get_res_space()
    M = dp.get_imp_space_mod_res()

    print("F: %s" % F)
    print("R: %s" % R)
    print("I: %s" % I)
    print("M: %s" % M)

    UR = UpperSets(R)

    ur = dp.solve(())

    print('ur: %s' % ur)

    UR.check_equal(ur, R.U(10.0))




@comptest
def check_lang_connections2aa():
    """ This is considered connected. """

    assert_parsable_to_connected_ndp("""
mcdp {
    provides f1 [g]
    provides f2 [s]
    
    f1 <= 1 g
    f2 <= 2 s
}""")


@comptest
def check_lang_connections2ab():
    """ This is considered connected. """

    assert_parsable_to_connected_ndp("""
mcdp {
    provides f1 [g]
    requires r1 [J]
    provides f2 [s]
    
    f1 <= 1 g
    f2 <= 2 s
    r1 >= 1 J
}""")

@comptest
def check_lang_connections2a():
    assert_parsable_to_connected_ndp("""
    mcdp {
    provides lift1  [N]
    provides lift2  [N]
    requires power [W]
    requires mass1 [g]
    requires mass2 [g]
    provides endurance [s]
    
    c = 0.002 W/N^2
    lift = lift1+lift2
    power >= (lift^2) * c

    endurance <= 1 hour
    mass1 + mass2 >= 50 g
}
""")

@comptest
def check_lang_connections3a():
    """ This is considered connected. """

    ndp = assert_parsable_to_connected_ndp("""
mcdp {
    provides a [g]
    requires b [s]
    
    a <= 1 g 
    b >= 2 s
}""")

    dp = ndp.get_dp()

    I = dp.get_imp_space()
    F = dp.get_fun_space()
    R = dp.get_res_space()
    M = dp.get_imp_space_mod_res()

    print("F: %s" % F)
    print("R: %s" % R)
    print("I: %s" % I)
    print("M: %s" % M)

    UR = UpperSets(R)

    ur = dp.solve(0.5)
    print('ur: %s' % ur)

    UR.check_equal(ur, R.U(2.0))



@comptest
def check_lang_connections3():
    """ This is considered connected. """

    ndp = assert_parsable_to_connected_ndp("""
mcdp {
    provides f1 [g]
    provides f2 [s]
    requires r1 [s]
    
    f1 <= 1 g 
    f2 <= 2 s
    r1 >= 2 s
}""")

    dp = ndp.get_dp()

    I = dp.get_imp_space()
    F = dp.get_fun_space()
    R = dp.get_res_space()
    M = dp.get_imp_space_mod_res()

    print("F: %s" % F)
    print("R: %s" % R)
    print("I: %s" % I)
    print("M: %s" % M)

    UR = UpperSets(R)

    ur = dp.solve((0.5, 0.4))

    print('ur: %s' % ur)

    UR.check_equal(ur, R.U(2.0))

    f_infeasible = (1.1, 1.0)
    ur = dp.solve(f_infeasible)
    print('ur: %s' % ur)

    empty = R.Us(set())
    UR.check_equal(ur, empty)


    imps = dp.get_implementations_f_r(f=(0.4, 0.4), r=2.0)
    print('imps: %s' % imps)


@comptest
def check_lang_connections4():
    assert_parsable_to_connected_ndp("""
    mcdp {
    provides lift  [N]
    requires power [W]
    requires mass [g]
    
    c = 0.002 W/N^2
    power >= (lift^2) * c

    mass >= 50 g
}
""")
