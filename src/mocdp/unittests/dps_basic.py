from mocdp.unittests.generation import for_all_dps

@for_all_dps
def check_dp1(_id_dp, dp):
    funsp = dp.get_fun_space()
    f_top = funsp.get_top()
    f_bot = funsp.get_bottom()

    ressp = dp.get_res_space()
    f_top = ressp.get_top()
    f_bot = ressp.get_bot()

    u0 = dp.solve(f_bot)
    u1 = dp.solve(f_top)

    trsp = dp.get_res_space()

    assert trsp.leq(u0, u1)

    print u0
    print u1

    pass
#     bot = poset.get_bottom()
#     top = poset.get_top()
#     poset.leq(bot, top)

