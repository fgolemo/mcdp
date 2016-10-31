# -*- coding: utf-8 -*-
from contracts.utils import raise_wrapped
from mcdp_dp import NotSolvableNeedsApprox
from mcdp_posets import LowerSets, NotBounded, UpperSets, NotLeq
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


def try_with_approximations(id_dp, dp, test):
    from mcdp_dp.dp_transformations import get_dp_bounds
    nl = nu = 5
    dpL, dpU = get_dp_bounds(dp, nl, nu)
    
    test(id_dp + '_L%s' % nl, dpL)
    test(id_dp + '_U%s' % nu, dpU)
    
    
@for_all_dps
def check_solve_f_chain(id_dp, dp):
    from mcdp_posets.utils import poset_check_chain

    F = dp.get_fun_space()

    f_chain = F.get_test_chain(n=5)
    poset_check_chain(F, f_chain)

    try:
        trchain = map(dp.solve, f_chain)
    except NotSolvableNeedsApprox:
        return try_with_approximations(id_dp, dp, check_solve_r_chain)

    R = dp.get_res_space()
    UR = UpperSets(R)
    try:
        poset_check_chain(UR, trchain)
    except ValueError as e:
        msg = 'The map solve() for %r is not monotone.' % id_dp
        raise_wrapped(Exception, e, msg, f_chain=f_chain, trchain=trchain, compact=True)



@for_all_dps
def check_solve_r_chain(id_dp, dp):
    from mcdp_posets.utils import poset_check_chain

    R = dp.get_res_space()
    F = dp.get_fun_space()
    LF = LowerSets(F)
    
    r_chain = R.get_test_chain(n=5)
    poset_check_chain(R, r_chain)

    try:
        lfchain = map(dp.solve_r, r_chain)
    except NotSolvableNeedsApprox:
        return try_with_approximations(id_dp, dp, check_solve_r_chain)
    
    try:
        # now, notice that we need to reverse this
        lfchain_reversed = list(reversed(lfchain))
        poset_check_chain(LF, lfchain_reversed)
    except ValueError as e:
        msg = 'The map solve() for %r is not monotone.' % id_dp
        raise_wrapped(Exception, e, msg, r_chain=r_chain, lfchain=lfchain,
                      lfchain_reversed=lfchain_reversed, compact=True)




