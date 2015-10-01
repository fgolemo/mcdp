# -*- coding: utf-8 -*-
from mocdp.unittests.generation import for_all_dps
from mocdp.posets.uppersets import UpperSets

@for_all_dps
def check_normalform(id_dp, dp):
    S, alpha, beta = dp.get_normal_form()
    print('design problem %s = %s' % (id_dp, dp))
    print('S: %s' % S)
    print('α: %s' % alpha)
    print('β: %s' % beta)

    F = dp.get_fun_space()
    R = dp.get_res_space()
    UF = UpperSets(F)
    UR = UpperSets(R)

    f_bot = UF.get_bottom()
    S_bot = S.get_bottom()

    x = (f_bot, S_bot)
    alpha.get_domain().belongs(x)

    y = alpha(x)
    alpha.get_codomain().belongs(y)

    z = beta(x)

    print('codomain: %s' % beta.get_codomain())
    print('z = %s' % str(z))
    beta.get_codomain().belongs(z)
