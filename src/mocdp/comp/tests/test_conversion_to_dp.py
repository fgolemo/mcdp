# -*- coding: utf-8 -*-
import warnings

from mcdp_dp.primitive import NotSolvableNeedsApprox
from mcdp_dp_tests.basic import check_solve_r_chain, check_solve_f_chain
from mcdp_dp_tests.dual import dual01_chain
from mcdp_posets import UpperSets
from mcdp_tests.generation import for_all_nameddps
from mocdp import MCDPConstants
from mocdp.comp.interfaces import  NotConnected


if MCDPConstants.test_dual01_chain:
    dec = for_all_nameddps
else:
    warnings.warn('disabled test ndp_dual01_chain')
    dec = lambda x: x

@dec
def ndp_dual01_chain(id_ndp, ndp):
    if '_inf' in id_ndp:
        # plusinvnat3b_inf
        print('Assuming that the suffix "_inf" in %r means that this will not converge'
              % (id_ndp))
        print('Skipping this test')
        return

    try:
        ndp.check_fully_connected()
    except NotConnected:
        print('Skipping test_conversion because %r not connected.' % id_ndp)
        return

    dp = ndp.get_dp()
    
    return dual01_chain(id_ndp, dp)

    
@for_all_nameddps
def ndp_check_solve_r_chain(id_ndp, ndp):
    if '_inf' in id_ndp:
        # plusinvnat3b_inf
        print('Assuming that the suffix "_inf" in %r means that this will not converge'
              % (id_ndp))
        print('Skipping this test')
        return

    try:
        ndp.check_fully_connected()
    except NotConnected:
        print('Skipping test_conversion because %r not connected.' % id_ndp)
        return

    dp = ndp.get_dp()
    
    return check_solve_r_chain(id_ndp, dp)


@for_all_nameddps
def ndp_check_solve_f_chain(id_ndp, ndp):
    if '_inf' in id_ndp:
        # plusinvnat3b_inf
        print('Assuming that the suffix "_inf" in %r means that this will not converge'
              % (id_ndp))
        print('Skipping this test')
        return

    try:
        ndp.check_fully_connected()
    except NotConnected:
        print('Skipping test_conversion because %r not connected.' % id_ndp)
        return

    dp = ndp.get_dp()
    
    return check_solve_f_chain(id_ndp, dp)

@for_all_nameddps
def test_conversion(id_ndp, ndp):
    if '_inf' in id_ndp:
        # plusinvnat3b_inf
        print('Assuming that the suffix "_inf" in %r means that this will not converge'
              % (id_ndp))
        print('Skipping this test')
        return

    try:
        ndp.check_fully_connected()
    except NotConnected:
        print('Skipping test_conversion because %r not connected.' % id_ndp)
        return

    dp = ndp.get_dp()

    F = dp.get_fun_space()
    R = dp.get_res_space()
    
    fs = F.get_minimal_elements()

    max_elements = 5
    if len(fs) >= max_elements:
        fs = list(fs)[:max_elements]

    UR = UpperSets(R)
    for f in fs:
        try:
            res = dp.solve(f)
            print('%s -> %s' % (F.format(f), UR.format(res)))

            for r in res.minimals:
                imps = dp.get_implementations_f_r(f, r)
                print(imps)

        except NotSolvableNeedsApprox:
            break

