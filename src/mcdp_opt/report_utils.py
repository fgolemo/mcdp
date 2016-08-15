from reprep import Report

def get_optim_state_report(s, opt):
    r = Report()

    from mcdp_opt_tests.test_basic import plot_ndp
    plot_ndp(r, 'current', s.get_current_ndp(), opt.library)
    r.text('order', 'creation order: %s' % s.creation_order)
    r.text('msg', s.get_info())
    return r
