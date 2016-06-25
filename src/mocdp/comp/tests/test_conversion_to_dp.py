from mcdp_tests.generation import for_all_nameddps
from mcdp_posets.uppersets import UpperSets
from mcdp_dp.primitive import NotSolvableNeedsApprox

@for_all_nameddps
def test_conversion(_, ndp):
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

