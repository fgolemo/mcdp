from mocdp.unittests.generation import for_all_nameddps
from mcdp_posets.uppersets import UpperSets

@for_all_nameddps
def test_conversion(_, ndp):
    dp = ndp.get_dp()
    print dp
    F = dp.get_fun_space()

    fs = F.get_minimal_elements()
    UR = UpperSets(dp.get_res_space())
    for f in fs:
        res = dp.solve(f)
        print('%s -> %s' % (F.format(f), UR.format(res)))
