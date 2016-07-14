from mcdp_tests.generation import for_all_dps
from mcdp_posets.uppersets import UpperSets

if False:
    @for_all_dps
    def check_normalform_approx(id_dp, dp):
        S, gamma, delta = dp.get_normal_form_approx()
        print('design problem %s = %s' % (id_dp, dp))
        print('S: %s' % S)
        print('gamma: %s' % gamma)
        print('delta: %s' % delta)


        F = dp.get_fun_space()
        UF = UpperSets(F)
        _R = dp.get_res_space()

        uf_bot = UF.get_bottom()
        S_bot = S.get_bottom()

        x = (uf_bot, S_bot, 0, 0)
        gamma.get_domain().belongs(x)

        y = gamma(x)
        gamma.get_codomain().belongs(y)

        z = delta(x)

        print('codomain: %s' % delta.get_codomain())
        print('z = %s' % str(z))
        delta.get_codomain().belongs(z)


    # Start with bottom

#     x1 = (uf_bot, S_bot, 0, 0)



#     f_fix = uf_bot
#     print('f_fix: %s' % UF.format(f_fix))
#     Ss = [S_bot]
#     for i in range(10):
#         Si = beta((f_fix, Ss[-1]))
#         print('i = %s  %s' % (i, Si))
#         S.belongs(Si)
#         Ss.append(Si)
#         # check increasing sequence
#         S.check_leq(Ss[-2], Ss[-1])
#         if S.leq(Ss[-1], Ss[-2]):  # => equality
#             print('Converged exactly')
#             break
#     Sinf = Ss[-1]
#     print('S converged to %s' % S.format(Sinf))
#     ur = alpha((f_fix, Sinf))
#     print('Results:')
#     print(' uf: %s' % UF.format(f_fix))
#     print(' ur: %s' % UR.format(ur))
#     print(' Sinf: %s' % S.format(Sinf))

