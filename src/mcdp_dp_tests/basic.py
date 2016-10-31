# -*- coding: utf-8 -*-
from contracts.utils import raise_wrapped
from mcdp_dp import NotSolvableNeedsApprox
from mcdp_posets import NotBounded, UpperSets, NotLeq
from mcdp_tests.generation import for_all_dps


@for_all_dps
def check_solve_top_bottom(id_dp, dp):
    print('Testing %s: %s' % (id_dp, dp))
    F = dp.get_fun_space()
    R = dp.get_res_space()
    UR = UpperSets(R)
    print('F: %s' % F)
    print('R: %s' % R)

    I = dp.get_imp_space()
    M = dp.get_imp_space()
    print('I: %s' % I)
    print('M: %s' % M)

    try:
        f_top = F.get_top()
        f_bot = F.get_bottom()
    except NotBounded:
        return
    
    print('⊥ = %s' % F.format(f_bot))
    print('⊤ = %s' % F.format(f_top))

    try:
        ur0 = dp.solve(f_bot)
        ur1 = dp.solve(f_top)
    except NotSolvableNeedsApprox:
        return

    print('f(%s) = %s' % (f_bot,  ur0))
    print('f(%s) = %s' % (f_top,  ur1))
    print('Checking that the order is respected')

    try:
        UR.check_leq(ur0, ur1)
    except NotLeq as e:
        msg = 'Not true that f(⊥) ≼ f(⊤).'
        raise_wrapped(Exception, e, msg, ur0=ur0,ur1=ur1) 
        
    # get implementations for ur0
    for r in ur0.minimals:
        ms = dp.get_implementations_f_r(f_bot, r)
        for m in ms:
            M.belongs(m)



@for_all_dps
def check_solve_chain(_, dp):
    from mcdp_posets.utils import poset_check_chain

    funsp = dp.get_fun_space()

    chain = funsp.get_test_chain(n=5)
    poset_check_chain(funsp, chain)

    try:
        trchain = map(dp.solve, chain)
    except NotSolvableNeedsApprox:
        return

    R = dp.get_res_space()
    UR = UpperSets(R)
    poset_check_chain(UR, trchain)

    print trchain
