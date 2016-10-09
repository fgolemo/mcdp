from mcdp_dp.primitive import NotSolvableNeedsApprox
from mcdp_posets import UpperSets
from mcdp_tests.generation import for_all_nameddps
from mocdp.comp.interfaces import NotConnected

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

    fs = F.get_minimal_elements()

    max_elements = 5
    if len(fs) >= max_elements:
        fs = list(fs)[:max_elements]

    UR = UpperSets(dp.get_res_space())
    for f in fs:
        try:
            res = dp.solve(f)
            print('%s -> %s' % (F.format(f), UR.format(res)))

            for r in res.minimals:
                imps = dp.get_implementations_f_r(f, r)
                print imps

        except NotSolvableNeedsApprox:
            pass

