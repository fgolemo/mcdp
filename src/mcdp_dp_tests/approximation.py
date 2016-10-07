from comptests.registrar import comptest
from mcdp_lang import parse_ndp
from mcdp_posets import UpperSets


# from mcdp_dp.dp_approximation import CombinedCeil
# 
# @comptest
# def check_approximation2():
#     import numpy as np
#     f = CombinedCeil(n_per_decade=10, step=0.01)
#     x = np.linspace(0.1, 100, 1000)
#     y = np.array(map(f, x))
#     
# #     for xi, yi in zip(x, y):
# #         print('%10s -> %10s' % (xi, yi))
# #
#     print np.unique(y)
#     ny = len(np.unique(y))
#     print(ny)
#     assert 25 <= ny <= 30
@comptest
def check_approximation3():
    # TODO: move in syntax
    ndp = parse_ndp("""
    approx(mass,0%,1g,Top kg) mcdp {
    provides in [g]
    requires mass [g]
    mass >= in
}""")
    dp = ndp.get_dp()
    R = dp.get_res_space()
    UR = UpperSets(R)
    UR.check_equal(dp.solve(55.0), R.U(55.0))
    UR.check_equal(dp.solve(55.01), R.U(56.0))


@comptest
def check_approximation4():
    ndp = parse_ndp("""
    approx(mass,0%,0g,Top kg) mcdp {
    provides in [g]
    requires mass [g]
    mass >= in
}""")
    dp = ndp.get_dp()
    R = dp.get_res_space()
    UR = UpperSets(R)
    UR.check_equal(dp.solve(55.0), R.U(55.0))
    UR.check_equal(dp.solve(55.01), R.U(55.01))

@comptest
def check_approximation5():
    ndp = parse_ndp("""
    approx(mass,0%,0g,Top kg) mcdp {
    provides in [g]
    requires mass [g]
    mass >= in
}""")
    dp = ndp.get_dp()
    R = dp.get_res_space()
    F = dp.get_fun_space()
    UR = UpperSets(R)
    res = dp.solve(F.get_top())
    UR.check_equal(res, R.U(R.get_top()))


@comptest
def check_approximation1():
    ndp = parse_ndp("""
    approx(mass,0%,0g,55 g) mcdp {
    provides in [g]
    requires mass [g]
    mass >= in
}""")
    dp = ndp.get_dp()
    R = dp.get_res_space()
    UR = UpperSets(R)
    res = dp.solve(55.0)
    print(res)
    UR.check_equal(res, R.U(55.0))
    res = dp.solve(55.1)
    print(res)
    UR.check_equal(res, R.Us(set()))

