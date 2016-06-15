# -*- coding: utf-8 -*-
from mcdp_tests.generation import for_all_dps
from mcdp_posets.uppersets import UpperSets

if False:
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

        uf_bot = UF.get_bottom()
        S_bot = S.get_bottom()

        x = (uf_bot, S_bot)
        alpha.get_domain().belongs(x)

        y = alpha(x)
        alpha.get_codomain().belongs(y)

        z = beta(x)

        print('codomain: %s' % beta.get_codomain())
        print('z = %s' % str(z))
        beta.get_codomain().belongs(z)

        f_fix = uf_bot
        print('f_fix: %s' % UF.format(f_fix))
        Ss = [S_bot]
        for i in range(10):
            Si = beta((f_fix, Ss[-1]))
            print('i = %s  %s' % (i, Si))
            S.belongs(Si)
            Ss.append(Si)
            # check increasing sequence
            S.check_leq(Ss[-2], Ss[-1])
            if S.leq(Ss[-1], Ss[-2]):  # => equality
                print('Converged exactly')
                break
        Sinf = Ss[-1]
        print('S converged to %s' % S.format(Sinf))
        ur = alpha((f_fix, Sinf))
        print('Results:')
        print(' uf: %s' % UF.format(f_fix))
        print(' ur: %s' % UR.format(ur))
        print(' Sinf: %s' % S.format(Sinf))




