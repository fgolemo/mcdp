from mcdp_dp.primitive import NotSolvableNeedsApprox
from mcdp_posets import UpperSets
from mcdp_tests.generation import for_all_nameddps

@for_all_nameddps
def test_conversion(id_ndp, ndp):
    # plusinvnat3b_inf
    if '_inf' in id_ndp:
        print('Assuming that the suffix "_inf" in %r means that this will not converge'
              % (id_ndp))
        print('Skipping this test')
        return

    dp = ndp.get_dp()
    # print dp
    F = dp.get_fun_space()

    fs = F.get_minimal_elements()
    UR = UpperSets(dp.get_res_space())
    for f in fs:
        try:
            res = dp.solve(f)
            print('%s -> %s' % (F.format(f), UR.format(res)))
        except NotSolvableNeedsApprox:
            pass

