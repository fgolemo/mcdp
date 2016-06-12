from mocdp.unittests.generation import for_all_nameddps

@for_all_nameddps
def test_conversion(_, ndp):
    dp = ndp.get_dp()
    print dp
    F = dp.get_fun_space()
    f = F.get_bottom()
    res = dp.solve(f)
