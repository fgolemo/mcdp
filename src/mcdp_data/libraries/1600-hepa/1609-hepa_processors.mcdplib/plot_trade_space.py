#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
from reprep import Report
from mcdp_library.library import MCDPLibrary
from mcdp_ipython_utils.loading import solve_combinations
from mcdp_ipython_utils.plotting import color_functions, set_axis_colors,\
    color_resources
from quickapp.quick_app import QuickApp
from plot_utils import ieee_fonts_zoom3, ieee_spines_zoom3
import itertools


def get_library():
    lib = MCDPLibrary()
    lib.use_cache_dir('_cached/plot_batteries_cache')
    lib.add_search_dir('.')
    return lib

def go(model_name):
    lib = get_library()
    nt = 15 * 4
    nr = 15 * 3
    combinations = {
        "min_throughput": (np.linspace(10, 1000, nt), "Hz"),
        "resolution": (np.linspace(1.3, 10, nr), "pixels/deg"),
        "inverse_of_max_latency": (0.0, '1/s')
    }
    result_like = dict(power="W", budget="USD")
    ndp = lib.load_ndp(model_name)

    data = solve_combinations(ndp, combinations, result_like)
    return data

def create_report1(data, model_name):
    
    all_min_throughput = []
    all_resolution = []
    all_num_solutions = []
    all_min_budget = []
    all_min_power = []

    
    for query, query_results in zip(data['queries'], data['results']):
        resolution = query['resolution']
        min_throughput = query['min_throughput']
        num_solutions = len(query_results)

        if num_solutions == 0:
            min_power = np.nan
            min_budget = np.nan
        else:
            min_power = np.min([_['power'] for _ in query_results])
            min_budget = np.min([_['budget'] for _ in query_results])
        
        all_min_throughput.append(min_throughput)
        all_resolution.append(resolution)
        all_num_solutions.append(num_solutions)
        all_min_power.append(min_power)
        all_min_budget.append(min_budget)

    all_min_throughput = np.array(all_min_throughput)
    all_resolution = np.array(all_resolution)
    all_num_solutions = np.array(all_num_solutions)
    all_min_power = np.array(all_min_power)
    all_min_budget = np.array(all_min_budget)
        
    one_solution = all_num_solutions == 1
    multiple_solutions = all_num_solutions > 1
    is_not_feasible = all_num_solutions == 0
    is_feasible =  all_num_solutions> 0

    from matplotlib import pylab
    ieee_fonts_zoom3(pylab)

    fig = dict(figsize=(4.5, 4))
    popt = dict(clip_on=False)

    def do_axes(pylab):
        pylab.xlabel('resolution [pixels/deg]')
        pylab.ylabel('min_throughput [Hz]')
        set_axis_colors(pylab, color_functions, color_functions)

    r = Report(model_name)
    with r.plot('feasibility', **fig) as pylab:
        ieee_spines_zoom3(pylab)
        
        pylab.plot(all_resolution[one_solution], all_min_throughput[one_solution],
                    'k.', markersize=4, **popt)
        pylab.plot(all_resolution[multiple_solutions], all_min_throughput[multiple_solutions],
                   'ms', markersize=4, **popt)
        pylab.plot(all_resolution[is_not_feasible],
                   all_min_throughput[is_not_feasible], 'r.', markersize=0.5, **popt)
        
        do_axes(pylab)

    with r.plot('power', **fig) as pylab:

        ieee_spines_zoom3(pylab)

        x = all_resolution
        y = all_min_throughput
        z = all_min_power
        plot_field(pylab, x, y, z, cmap='afmhot')
        pylab.title('power', color=color_resources)
        do_axes(pylab)

    with r.plot('budget', **fig) as pylab:

        ieee_spines_zoom3(pylab)

        x = all_resolution
        y = all_min_throughput
        z = all_min_budget
        plot_field(pylab, x, y, z, cmap='afmhot')
        pylab.title('budget', color=color_resources)
        do_axes(pylab)

    with r.plot('budget2', **fig) as pylab:
        ieee_spines_zoom3(pylab)

        unique_budgets = np.unique(all_min_budget[is_feasible])

        markers = [ 'b.', 'g.', 'm.', 'y.']
        for i, ub in enumerate(unique_budgets):
            which = all_min_budget == ub
            pylab.plot(all_resolution[which], all_min_throughput[which], markers[i],
                       markersize=4, **popt)


        pylab.plot(all_resolution[is_not_feasible],
           all_min_throughput[is_not_feasible], 'r.', markersize=0.5, **popt)

        do_axes(pylab)

    r.text('about_budget', '%s = %s' % (unique_budgets, markers))
    r.text('misc',
           'min_power: %s W - %s W' % (np.min(all_min_power[is_feasible]),
                                       np.max(all_min_power[is_feasible])))
    return r


def plot_field(pylab, x, y, z, cmap):

    def value_at(cx, cy):
        for x0, y0, z0 in itertools.product(x, y, z):
            if cx == x0 and cy == y0:
                return z0
        raise ValueError((cx, cy))

    xu = np.sort(np.unique(x))
    yu = np.sort(np.unique(y))

    zoom = 5
    xu = np.linspace(xu[0], xu[-1], len(xu) * zoom)
    yu = np.linspace(yu[0], yu[-1], len(xu) * zoom)

    X, Y = np.meshgrid(xu, yu)

    from matplotlib.mlab import griddata
    resampled = griddata(x, y, z, xu, yu, interp='linear')

    pylab.pcolor(X, Y, resampled,  # vmin=1, vmax=100,
                 cmap=cmap)
#     plot_all_directions(r, queries=data['queries'], results=data['results'],
#                         what_to_plot_res=what_to_plot_res,
#                         what_to_plot_fun=what_to_plot_fun)

class App(QuickApp):
    
    def define_options(self, params):
        pass

    def define_jobs_context(self, context):

        for model_name in ['ARM_A15', 'Intel_i7', 'NVidiaKepler', 'ARM_plus_Intel',
                           'ARM_plus_Nvidia', 'Intel_plus_Nvidia',
                           'AnyAlternative']:
            data = context.comp(go, model_name)
            r = context.comp(create_report1, data, model_name)
            context.add_report(r, 'report1', model_name=model_name)
#
#     fn = 'out/trade_space.html'
#     print('writing to %r' % fn)
#     r.to_html(fn)


main = App.get_sys_main()
if __name__ == '__main__':
    main()
