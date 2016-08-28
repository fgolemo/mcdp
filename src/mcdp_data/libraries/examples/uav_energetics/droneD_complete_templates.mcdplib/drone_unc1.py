#!/usr/bin/env python
# -*- coding: utf-8 -*-
from mcdp_ipython_utils.loading import solve_combinations, to_numpy_array
from mcdp_ipython_utils.plotting import plot_all_directions, set_axis_colors
from mcdp_library import Librarian
from plot_utils import ieee_fonts_zoom3, ieee_spines_zoom3
from quickapp import QuickApp
from reprep import Report
import numpy as np


def get_ndp(library, battery):
    s = """\
specialize [
  Battery: %s, 
  Actuation: `droneD_complete_v2.Actuation, 
  PowerApprox: mcdp {
    provides power [W]
    requires power [W]

    required power  >= approxu(provided power, 1 mW)
   }
] `ActuationEnergeticsTemplate
""" % battery
    return  library.parse_ndp(s)

def process(battery):
    librarian = Librarian()
    librarian.find_libraries('../..')
    library = librarian.load_library('droneD_complete_templates')
    library.use_cache_dir('_cached/drone_unc1')

    ndp = get_ndp(library, battery)

    combinations = {
        "endurance": (np.linspace(1, 1.5, 10), "hour"),
        "extra_payload": (100, "g"),
        "num_missions": ( 1000, "[]"),
        "velocity": (1.0, "m/s"),
        'extra_power': (0.5, 'W'),
    }

    result_like = dict(total_cost="USD", total_mass='kg')

    dataU = solve_combinations(ndp, combinations, result_like, upper=1, lower=None)
    dataL = solve_combinations(ndp, combinations, result_like, upper=None, lower=1)

    return dict(dataL=dataL, dataU=dataU)

def report(res):

    r = Report()

    dataL = res['dataL']
    dataU = res['dataU']

    what_to_plot_res = dict(total_cost="USD", total_mass='kg')
    what_to_plot_fun = dict(endurance="hour", extra_payload="g")

    queries = dataL['queries']
    endurance = [q['endurance'] for q in queries]

    def get_value(data, field):
        for res in data['results']:
            a = to_numpy_array({field: 'kg'}, res)

            if len(a):
                a = min(a[field])
            else:
                a = None
            yield a


    from matplotlib import pylab
    ieee_fonts_zoom3(pylab)


    markers = dict(markeredgecolor='none', markerfacecolor='black', markersize=6,
                   marker='o')
    LOWER2 = dict(color='orange', linewidth=4, linestyle='-', clip_on=False)
    UPPER2 = dict(color='purple', linewidth=4, linestyle='-', clip_on=False)
    LOWER2.update(markers)
    UPPER2.update(markers)
    color_resources = '#700000'
    color_functions = '#007000'


    fig = dict(figsize=(4.5, 4))

    with r.plot('total_mass', **fig) as pylab:
        ieee_spines_zoom3(pylab)
        total_massL = np.array(list(get_value(dataL, 'total_mass')))
        total_massU = np.array(list(get_value(dataU, 'total_mass')))
        print endurance
        print total_massL, total_massU
        pylab.plot(endurance, total_massL, **LOWER2)
        pylab.plot(endurance, total_massU, **UPPER2)
        set_axis_colors(pylab, color_functions, color_resources)
        pylab.xlabel('endurance [hours]')
        pylab.ylabel('total_mass [kg]')

    return r


    print('Plotting lower')
    with r.subsection('lower') as rL:
        plot_all_directions(rL,
                            queries=dataL['queries'],
                            results=dataL['results'],
                            what_to_plot_res=what_to_plot_res,
                            what_to_plot_fun=what_to_plot_fun)
    
    print('Plotting upper')
    with r.subsection('upper') as rU:
        plot_all_directions(rU,
                            queries=dataU['queries'],
                            results=dataU['results'],
                            what_to_plot_res=what_to_plot_res,
                            what_to_plot_fun=what_to_plot_fun)

    return r

class DroneU(QuickApp):

    def define_options(self, params):
        pass

    def define_jobs_context(self, context):
        for l in ['batteries_uncertain1', 'batteries_uncertain2',
                  'batteries_uncertain3']:
            battery = '`%s.batteries' % l
            result = context.comp(process, battery)
            r = context.comp(report, result)
            context.add_report(r, 'report', l=l)


if __name__ == '__main__':
    main = DroneU.get_sys_main()
    main()



