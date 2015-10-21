from comptests.registrar import comptest_dynamic
from mocdp.lang.syntax import parse_ndp
from reprep import Report
from mocdp.drawing import plot_upset_R2, plot_upset_minima
from mocdp.posets.uppersets import UpperSets




@comptest_dynamic
def check_invmult(context):
    ndp = parse_ndp("""
    cdp {
      requires a [R]
      requires b [R]
      
      provides c [R]
      
      c <= a * b
    }
    """)
    dp = ndp.get_dp()

    r = context.comp(check_invmult_report, dp)
    context.add_report(r, 'check_invmult_report')

def check_invmult_report(dp):
#     from mocdp.dp.dp_loop import SimpleLoop
#     funsp = dp.get_fun_space()

#     assert isinstance(dp, SimpleLoop)

    f = 1.0
    R0, R1 = dp.solve_approx(f=f, n=15)
    UR = UpperSets(dp.get_res_space())

    UR.belongs(R0)
    UR.belongs(R1)
    UR.check_leq(R0, R1)
    # Payload2ET

    r = Report()
    caption = 'Two curves for each payload'
    with r.plot('p1', caption=caption) as pylab:
#        plot_upset_minima(pylab, R0)

        mx = max(x for (x, _) in R1.minimals)
        my = max(y for (_, y) in R1.minimals)
        axis = (0, mx * 1.1, 0, my * 1.1)

        import numpy as np

        plot_upset_R2(pylab, R0, axis, color_shadow=[1.0, 0.8, 0.8])
        plot_upset_R2(pylab, R1, axis, color_shadow=[0.8, 1.0, 0.8])


        xs = np.exp(np.linspace(-10, +10, 50))
        ys = f / xs
        pylab.plot(xs, ys, 'r-')

        pylab.xlabel('time')
        pylab.ylabel('energy')

        pylab.axis(axis)
#     import numpy as np
#     payloads = np.linspace(0, 100, 100)
#     payloads_ = []
#     payload2payload = dp.dp1
#     for p in payloads:
#         res = payload2payload.solve(p)
#         assert len(res.minimals) == 1
#         pp = list(res.minimals)[0]
#         payloads_.append(pp)
#
#     with r.plot('p2') as pylab:
#         pylab.plot(payloads, payloads, 'k--')
#         pylab.plot(payloads, payloads_, 'r.')
#         pylab.xlabel('payload (g)')
#         pylab.ylabel('payload (g)')
#         pylab.xlim(0, max(payloads))
# #         pylab.ylim(0, max(payloads))

    return r
