#!/usr/bin/env python
# -*- coding: utf-8 -*-
from contracts import contract
from mcdp_cli.query_interpretation import convert_string_query
from mcdp_dp.dp_transformations import get_dp_bounds
from mcdp_dp.tracer import Tracer
from mcdp_lang import parse_ndp, parse_template
from mcdp_library import Librarian
from mcdp_posets import UpperSets
from mocdp.comp.composite import CompositeNamedDP
from mocdp.comp.context import Context
from mocdp.comp.ignore_some_imp import ignore_some
from plot_utils import ieee_fonts_zoom3, ieee_spines_zoom3
from quickapp import QuickApp
from reprep import Report
import numpy as np
from mcdp_ipython_utils.plotting import set_axis_colors

@contract(interval_mw='float,>=0')
def create_power_approx(interval_mw, context):
    s = """
    mcdp {
    provides power [W]
    requires power [W]

    required power  >= approxu(provided power, %s mW)
    }
    """ % interval_mw
    
    ndp = parse_ndp(s, context)

    return ndp

@contract(interval_mw='float,>=0', returns=CompositeNamedDP)
def create_ndp(context, interval_mw):
    template = parse_template('`ActuationEnergeticsTemplate', context)
    Battery = parse_ndp('`batteries_nodisc.batteries', context)
    Actuation = parse_ndp('`droneD_complete_v2.Actuation', context)
    PowerApprox = create_power_approx(interval_mw=interval_mw, context=context)
    params = dict(Battery=Battery,
                  PowerApprox=PowerApprox,
                  Actuation=Actuation)
    ndp = template.specialize(params, context)

    ndp = ignore_some(ndp, ignore_fnames=[], ignore_rnames=['total_cost'])
    return ndp

def go():
    librarian = Librarian()
    librarian.find_libraries('../..')
    library = librarian.load_library('droneD_complete_templates')
    library.use_cache_dir('_cached/drone_unc2')
    context = library._generate_context_with_hooks()

    res = {}
    res['intervals'] = [0, 0.01, 0.1, 1.0, 5.0, 10.0, 50, 100.0, 250, 500, 1000]
    res['results'] = []
    for interval_mw in res['intervals']:
        ndp = create_ndp(context=context, interval_mw=interval_mw)
        result = solve_stats(ndp)
        result['ndp'] = ndp
        res['results'].append(result)

    return res


def solve_stats(ndp):
    res = {} 
    query = {
        "endurance": "1.5 hour",
        "velocity":  "1 m/s",
        "extra_power": " 1 W",
        "extra_payload": "100 g",
        "num_missions": "100 []",
    }
    context = Context()
    f = convert_string_query(ndp=ndp, query=query, context=context)
    
    dp0 = ndp.get_dp()
    dpL, dpU = get_dp_bounds(dp0, nl=1, nu=1)


    F = dp0.get_fun_space()
    F.belongs(f)

    from mocdp import logger
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
    res['nsteps'] = 100

    return res


def report(data):
    from matplotlib import pylab
    ieee_fonts_zoom3(pylab)
    r = Report()

    print('reading iterations')
    num_iterations_L = [get_num_iterations(res_i['traceL']) for res_i in data['results']]
    num_iterations_U = [get_num_iterations(res_i['traceU']) for res_i in data['results']]

    def get_mass(res):
        if not res.minimals:
            return None
        return list(res.minimals)[0]

    res_L = np.array([ get_mass(res_i['resL']) for res_i in data['results']])
    res_U = np.array([ get_mass(res_i['resU']) for res_i in data['results']])

    accuracy = np.array(res_U) - np.array(res_L)

    num_iterations = np.array(num_iterations_L) + np.array(num_iterations_U)

    print res_L
    print res_U
    print num_iterations_L
    print num_iterations_U

    intervals = data['intervals']

    print('Plotting')
    f = r.figure('fig1', cols=2)

    LOWER = 'bo-'
    UPPER = 'mo-'

    markers = dict(markeredgecolor='none', markerfacecolor='black', markersize=6,
                   marker='o')
    LOWER2 = dict(color='orange', linewidth=4, linestyle='-', clip_on=False)
    UPPER2 = dict(color='purple', linewidth=4, linestyle='-', clip_on=False)
    LOWER2.update(markers)
    UPPER2.update(markers)
    color_resources = '#700000'
    # color_functions = '#007000'
    color_tolerance = '#000000'


    attrs = dict(clip_on=False)
    
    fig = dict(figsize=(4.5, 4))
    fig_tall = dict(figsize=(3.5    , 7))

    label_tolerance = u'tolerance α [mW]'
#     label_tolerance = 'tolerance $\\alpha$ [mW]'

    with f.plot('fig_num_iterations', **fig) as pylab:
        ieee_spines_zoom3(pylab)
        pylab.plot(intervals, num_iterations_L, **LOWER2)
        pylab.plot(intervals, num_iterations_U, **UPPER2)
        pylab.xlabel(label_tolerance)
        pylab.ylabel('iterations')

    with f.plot('fig_num_iterations_log', **fig) as pylab:
        ieee_spines_zoom3(pylab)
        pylab.loglog(intervals, num_iterations_L, **LOWER2)
        pylab.loglog(intervals, num_iterations_U, **UPPER2)
        pylab.xlabel(label_tolerance)
        pylab.ylabel('iterations')

    with f.plot('mass', **fig_tall) as pylab:
        ieee_spines_zoom3(pylab)
        pylab.plot(intervals, res_L, LOWER, **attrs)
        pylab.plot(intervals, res_U, UPPER, **attrs)
        pylab.xlabel(label_tolerance)
        pylab.ylabel('total mass [g]')
        set_axis_colors(pylab, color_tolerance, color_resources)

    with f.plot('mass3', **fig_tall) as pylab:
        ieee_spines_zoom3(pylab)
        pylab.plot(intervals, res_L, **LOWER2)
        pylab.plot(intervals, res_U, **UPPER2)
        pylab.xlabel(label_tolerance)
        pylab.ylabel('total mass [g]')
        set_axis_colors(pylab, color_tolerance, color_resources)

    with f.plot('mass3log', **fig) as pylab:
        ieee_spines_zoom3(pylab)
        pylab.semilogx(intervals, res_L, **LOWER2)
        pylab.semilogx(intervals, res_U, **UPPER2)
        pylab.xlabel(label_tolerance)
        pylab.ylabel('total mass [g]')
        set_axis_colors(pylab, color_tolerance, color_resources)

    with f.plot('mass_log', **fig) as pylab:
        ieee_spines_zoom3(pylab)
        pylab.loglog(intervals, res_L, LOWER, **attrs)
        pylab.loglog(intervals, res_U, UPPER, **attrs)
        pylab.xlabel(label_tolerance)
        pylab.ylabel('total mass [g]')
        set_axis_colors(pylab, color_tolerance, color_resources)

    with f.plot('mass2', **fig) as pylab:
        ieee_spines_zoom3(pylab)

        mean = np.array(res_L) * 0.5 + np.array(res_U) * 0.5
        err = (res_U - res_L) / 2

        e = pylab.errorbar(intervals, mean, yerr=err,
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

        pylab.xlabel(label_tolerance)
        pylab.ylabel('total mass [g]')
        set_axis_colors(pylab, color_tolerance, color_resources)

    with f.plot('mass2_log',  **fig) as pylab:
        ieee_spines_zoom3(pylab)
        pylab.loglog(intervals, res_L, LOWER, **attrs)
        pylab.loglog(intervals, res_U, UPPER, **attrs)
        pylab.xlabel(label_tolerance)
        pylab.ylabel('total mass [g]')
        set_axis_colors(pylab, color_tolerance, color_resources)

    with f.plot('accuracy',  **fig) as pylab:
        ieee_spines_zoom3(pylab)
        pylab.plot(accuracy, num_iterations, 'o', **attrs)
        pylab.ylabel('iterations')
        pylab.xlabel('solution uncertainty [g]')

    with f.plot('accuracy_log',  **fig) as pylab:
        ieee_spines_zoom3(pylab)
        pylab.loglog(accuracy, num_iterations, 'o', **attrs)
        pylab.ylabel('iterations')
        pylab.xlabel('solution uncertainty [g]')

    return r
    
    
def get_num_iterations(trace):
    v = list(trace.rec_get_value('num_iterations'))
    if not isinstance(v, list) and len(v) == 1:
        raise ValueError(v)
    return v[0]


class DroneUnc2(QuickApp):

    def define_options(self, params):
        pass

    def define_jobs_context(self, context):
        result = context.comp(go)
        r = context.comp(report, result)
        context.add_report(r, 'report')


if __name__ == '__main__':
    main = DroneUnc2.get_sys_main()
    main()



