#!/usr/bin/env python
from contracts import contract
from mcdp_cli.query_interpretation import convert_string_query
from mcdp_dp.dp_inv_mult import InvMult2
from mcdp_dp.dp_transformations import get_dp_bounds
from mcdp_dp.tracer import Tracer
from mcdp_lang import parse_ndp
from mcdp_library import Librarian
from mcdp_posets import UpperSets
from mocdp.comp.composite import CompositeNamedDP
from mocdp.comp.context import Context
from mocdp.comp.ignore_some_imp import ignore_some
from plot_utils import ieee_fonts_zoom3, ieee_spines_zoom3
from quickapp import QuickApp
from reprep import Report
import numpy as np


@contract(returns=CompositeNamedDP)
def create_ndp(context):

    ndp = parse_ndp('`test1', context)
    ndp = ignore_some(ndp,
                      ignore_fnames=[],
                      ignore_rnames=['total_cost_ownership'])

    return ndp

def go():
    librarian = Librarian()
    librarian.find_libraries('../..')
    library = librarian.load_library('droneD_complete_templates')
    library.use_cache_dir('_cached/drone_unc3')
    context = library._generate_context_with_hooks()

    res = {}
    res['n'] = [1, 5, 10, 15, 25, 50, 61, 75, 92, 100, 125, 150, 160,
                 175, 182, 200,
                300, 400, 500, 600, 1000, 2000]

#     res['n'] = [1, 5, 10, 15, 25, 50, 61, 100]
#     res['n'] = [3000]
    res['results'] = []
    for n in res['n']:
        ndp = create_ndp(context)
        result = solve_stats(ndp, n)
        result['ndp'] = ndp
        res['results'].append(result)

    return res


def solve_stats(ndp, n):


    res = {}
    query = {
        "travel_distance": " 2 km",
        "carry_payload": "100 g",
        "num_missions": "100 []",
    }
    context = Context()
    f = convert_string_query(ndp=ndp, query=query, context=context)

    dp0 = ndp.get_dp()
    dpL, dpU = get_dp_bounds(dp0, nl=n, nu=n)


    F = dp0.get_fun_space()
    F.belongs(f)

    logger = None
    InvMult2.ALGO = InvMult2.ALGO_VAN_DER_CORPUT
    traceL = Tracer(logger=logger)
    resL = dpL.solve_trace(f, traceL)
    traceU = Tracer(logger=logger)
    resU = dpU.solve_trace(f, traceU)
    R = dp0.get_res_space()
    UR = UpperSets(R)
    print('resultsL: %s' % UR.format(resL))
    print('resultsU: %s' % UR.format(resU))

    res['traceL'] = traceL
    res['traceU'] = traceU
    res['resL'] = resL
    res['resU'] = resU
    res['n'] = n
    res['query'] = query

    return res


def report(data):
#     font = {'family' : 'Times',
#         'size'   : 24}
#     import matplotlib
#     
#     matplotlib.rc('font', **font)
    from matplotlib import pylab
    
    ieee_fonts_zoom3(pylab)

    r = Report()

    num = np.array(data['n'])
    print num

    print('reading iterations')
    num_iterations_L = [get_num_iterations(res_i['traceL']) for res_i in data['results']]
    num_iterations_U = [get_num_iterations(res_i['traceU']) for res_i in data['results']]

    def get_mass(res):
        if not res.minimals:
            return np.inf
        return list(res.minimals)[0]

    res_L = np.array([ get_mass(res_i['resL']) for res_i in data['results']])
    res_U = np.array([ get_mass(res_i['resU']) for res_i in data['results']])

    accuracy = np.array(res_U) - np.array(res_L)

    num_iterations = np.array(num_iterations_L) + np.array(num_iterations_U)

    print res_L
    print res_U
    print num_iterations_L
    print num_iterations_U


    print('Plotting')
    f = r.figure('fig1', cols=2)

    LOWER = 'bo-'
    UPPER = 'mo-'

    attrs = dict(clip_on=False)
#     fig = dict(figsize=(14.4, 14.4))
    fig = dict()

    with f.plot('fig_num_iterations', **fig) as pylab:
        ieee_spines_zoom3(pylab)
        pylab.plot(num, num_iterations_L, LOWER, **attrs)
        pylab.plot(num, num_iterations_U, UPPER, **attrs)
        pylab.ylabel('iterations')
        pylab.xlabel('n')


    if False:
        with f.plot('fig_num_iterations_log', **fig) as pylab:
            ieee_spines_zoom3(pylab)
            pylab.loglog(num, num_iterations_L, LOWER, **attrs)
            pylab.loglog(num, num_iterations_U, UPPER, **attrs)
            pylab.ylabel('iterations')
            pylab.xlabel('n')

    with f.plot('mass', **fig) as pylab:
        ieee_spines_zoom3(pylab)
        pylab.plot(num, res_L, LOWER, **attrs)
        pylab.plot(num, res_U, UPPER, **attrs)
        pylab.ylabel('total_mass [g]')
        pylab.xlabel('n')

#     with f.plot('mass_log') as pylab:
#         ieee_spines(pylab)
#         pylab.loglog(intervals, res_L, LOWER, **attrs)
#         pylab.loglog(intervals, res_U, UPPER, **attrs)
#         pylab.xlabel('tolerance [mW]')
#         pylab.ylabel('total_mass [g]')

    with f.plot('mass2', **fig) as pylab:
        ieee_spines_zoom3(pylab)

        valid = np.isfinite(res_U)
        invalid = np.logical_not(valid)
        print valid

        res_L_valid = res_L[valid]
        res_U_valid = res_U[valid]
        num_valid = num[valid]

        mean = res_L_valid * 0.5 + res_U_valid * 0.5
        err = (res_U_valid - res_L_valid) / 2

        e = pylab.errorbar(num_valid, mean, yerr=err,
                           color='black', linewidth=2,
                           linestyle="None", **attrs)
#         plotline: Line2D instance #         x, y plot markers and/or line
#         caplines: list of error bar cap#         Line2D instances
#         barlinecols: list of         LineCollection instances for the horizontal and vertical error ranges.
        e[0].set_clip_on(False)
        for b in e[1]:
            b.set_clip_on(False)
        for b in e[2]:
            b.set_clip_on(False)
            b.set_linewidth(2)

        num_invalid = num[invalid]
        res_L_invalid = res_L[invalid]
        max_y = pylab.axis()[3]
        for n, res_L in zip(num_invalid, res_L_invalid):
            pylab.plot([n, n], [max_y, res_L], '--', color='gray', **attrs)
        pylab.plot(num_invalid, res_L_invalid, 'ko', **attrs)

        pylab.xlabel('n')
        pylab.ylabel('total_mass [g]')
#
#     with f.plot('mass2_log') as pylab:
#         ieee_spines(pylab)
#         pylab.loglog(intervals, res_L, LOWER, **attrs)
#         pylab.loglog(intervals, res_U, UPPER, **attrs)
#         pylab.xlabel('tolerance [mW]')
#         pylab.ylabel('total_mass [g]')

    with f.plot('accuracy', **fig) as pylab:
        ieee_spines_zoom3(pylab)
        pylab.plot(num_iterations, accuracy, 'o', **attrs)
        pylab.xlabel('iterations')
        pylab.ylabel('solution uncertainty [g]')
#
#     with f.plot('accuracy_log', **fig) as pylab:
#         ieee_spines_zoom3(pylab)
#         pylab.loglog(num_iterations, accuracy, 'o', **attrs)
#         pylab.xlabel('iterations')
#         pylab.ylabel('solution uncertainty [g]')

    return r


def get_num_iterations(trace):
    v = list(trace.rec_get_value('num_iterations'))
    if not isinstance(v, list) and len(v) == 1:
        raise ValueError(v)
    return v[0]

class DroneUnc3(QuickApp):

    def define_options(self, params):
        pass

    def define_jobs_context(self, context):
        result = context.comp(go)
        r = context.comp(report, result)
        context.add_report(r, 'report')


if __name__ == '__main__':
    main = DroneUnc3.get_sys_main()
    main()



