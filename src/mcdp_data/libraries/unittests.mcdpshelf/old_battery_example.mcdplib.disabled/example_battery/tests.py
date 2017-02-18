# -*- coding: utf-8 -*-
from reprep import Report
from mocdp.drawing import plot_upset_minima, plot_upset_R2
from mocdp.exceptions import mcdp_dev_warning


# @for_some_dps('ex16_loop')
def check_ex16(_id_dp, dp):
    funsp = dp.get_fun_space()
    bot = funsp.get_bottom()
    res = dp.solve(bot)
    print('res', res)

# @for_some_dps_dyn('ex16_loop')
def check_ex16b(context, _id_dp, dp):
    r = context.comp(check_ex16b_r, dp)
    context.add_report(r, 'ex16')

def check_ex16b_r(dp):
    funsp = dp.get_fun_space()
    bot = funsp.get_bottom()
    res = dp.solve(bot)
    print 'res', res
    r = Report()

    return r

mcdp_dev_warning('readd')
# @for_some_dps_dyn('ex16_loop')
def check_ex16c(context, _id_dp, dp):
    r = context.comp(check_ex16c_r, dp)
    context.add_report(r, 'ex16c')

def check_ex16c_r(dp):
#     from mocdp.dp.dp_loop import SimpleLoop
#     funsp = dp.get_fun_space()

#     assert isinstance(dp, SimpleLoop)

    # Payload2ET
    dp1 = dp.dp1.dp1
    payload1 = 10.0
    payload2 = 12.0
#     bot = dp1.get._fun_space().get_bottom()


    res1 = dp1.solve(payload1)
    res2 = dp1.solve(payload2)

    r = Report()
    caption = 'Two curves for each payload'
    with r.plot('p1', caption=caption) as pylab:
        plot_upset_minima(pylab, res1)
        plot_upset_minima(pylab, res2)
        axis = pylab.axis()
        plot_upset_R2(pylab, res1, axis, color_shadow=[0.5, 0.5, 0.5])
        plot_upset_R2(pylab, res2, axis, color_shadow=[0.7, 0.7, 0.6])
        pylab.xlabel('time')
        pylab.ylabel('energy')

    import numpy as np
    payloads = np.linspace(0, 100, 100)
    payloads_ = []
    payload2payload = dp.dp1
    for p in payloads:
        res = payload2payload.solve(p)
        assert len(res.minimals) == 1
        pp = list(res.minimals)[0]
        payloads_.append(pp)

    with r.plot('p2') as pylab:
        pylab.plot(payloads, payloads, 'k--')
        pylab.plot(payloads, payloads_, 'r.')
        pylab.xlabel('payload (g)')
        pylab.ylabel('payload (g)')
        pylab.xlim(0, max(payloads))
#         pylab.ylim(0, max(payloads))

    return r
