# # -*- coding: utf-8 -*-
# from mcdp_tests.generation import for_all_dps
# from mcdp_posets.uppersets import UpperSets
# 
# if False:
#     @for_all_dps
#     def check_normalform(id_dp, dp):
#         S, alpha, beta = dp.get_normal_form()
#         print(f"design problem {id_dp} = {dp}")
#         print(f"S: {S}")
#         print(f"α: {alpha}")
#         print(f"β: {beta}")
# 
#         F = dp.get_fun_space()
#         R = dp.get_res_space()
#         UF = UpperSets(F)
#         UR = UpperSets(R)
# 
#         uf_bot = UF.get_bottom()
#         S_bot = S.get_bottom()
# 
#         x = (uf_bot, S_bot)
#         alpha.get_domain().belongs(x)
# 
#         y = alpha(x)
#         alpha.get_codomain().belongs(y)
# 
#         z = beta(x)
# 
#         print(f"codomain: {beta}".get_codomain())
#         print(f"z = {str}"(z))
#         beta.get_codomain().belongs(z)
# 
#         f_fix = uf_bot
#         print(f"f_fix: {UF}".format(f_fix))
#         Ss = [S_bot]
#         for i in range(10):
#             Si = beta((f_fix, Ss[-1]))
#             print(f"i = {i}  {Si}")
#             S.belongs(Si)
#             Ss.append(Si)
#             # check increasing sequence
#             S.check_leq(Ss[-2], Ss[-1])
#             if S.leq(Ss[-1], Ss[-2]):  # => equality
#                 print('Converged exactly')
#                 break
#         Sinf = Ss[-1]
#         print(f"S converged to {S}".format(Sinf))
#         ur = alpha((f_fix, Sinf))
#         print('Results:')
#         print(f" uf: {UF}".format(f_fix))
#         print(f" ur: {UR}".format(ur))
#         print(f" Sinf: {S}".format(Sinf))
# 
# 


