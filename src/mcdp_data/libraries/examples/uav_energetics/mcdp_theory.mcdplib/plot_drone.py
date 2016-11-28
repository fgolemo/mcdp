#!/usr/bin/env python
# -*- coding: utf-8 -*-
import itertools

from common_stats import CommonStats
from contracts import contract
from discrete_choices import compute_discrete_choices, figure_discrete_choices2
from mcdp_ipython_utils.loading import solve_combinations, solve_queries
from mcdp_ipython_utils.plotting import  plot_all_directions, generate_colors
from mcdp_ipython_utils.plotting import (color_resources, color_functions,
    set_axis_colors)
from mcdp_lang import parse_poset
from mcdp_library.library import MCDPLibrary
from mcdp_library_tests.tests import get_test_librarian
from mcdp_report.drawing import plot_upset_R2
import numpy as np
from plot_commons import figure_num_implementations2
from plot_utils import ieee_spines_zoom3, ieee_fonts_zoom3
from quickapp import QuickApp
from reprep import Report


def go_plane1():
     
    librarian = get_test_librarian()
    lib = librarian.load_library('mcdp_theory') 
    ndp = lib.load_ndp('drone1_plane1')


    n = 10
    
    def interpolate_endurance(i): 
        assert 0 <= i< n 
        x = np.linspace(5, 120, n)[i]
        return (x, "minutes")
    
    def interpolate_missions(i): 
        assert 0 <= i< n 
        x = np.linspace(1, 1000, n)[i]
        return (x, "[]")
    
    queries = []
    for i in range(n):
        q = {}
        q['endurance'] = interpolate_endurance(i)
        q['num_missions'] = interpolate_missions(i)
        queries.append(q)
    
    result_like = dict(total_mass="kg", total_cost="USD")
    data = solve_queries(ndp, queries, result_like, lower=None, upper=None)
    return data


def go_plane2():
#     combinations = {
#         "endurance": (np.linspace(5, 120, 10), "minutes"),
#         "extra_payload": (np.linspace(1, 1000, 10), "g"),
#     }
#     
    librarian = get_test_librarian()
    lib = librarian.load_library('mcdp_theory') 
    ndp = lib.load_ndp('drone1_plane2')


    n = 10
    
    def interpolate_endurance(i): 
        assert 0 <= i< n 
        x = np.linspace(5, 60, n)[i]
        return (x, "minutes")
    
    def interpolate_extra_payload(i): 
        assert 0 <= i< n 
        x = np.linspace(1, 500, n)[i]
        return (x, "g")
    
    queries = []
    for i in range(n):
        q = {}
        q['endurance'] = interpolate_endurance(i)
        q['extra_payload'] = interpolate_extra_payload(i)
        queries.append(q)
    
    result_like = dict(total_mass="kg", total_cost="USD")
    data = solve_queries(ndp, queries, result_like, lower=None, upper=None)
    return data



def matplotlib_settings():
    from matplotlib import pylab
    ieee_fonts_zoom3(pylab)
    

def report_plane2(data):
    matplotlib_settings()
    cs = CommonStats(data)
    r = Report()
    
    what_to_plot_res = dict(total_mass="kg", total_cost="USD")
    what_to_plot_fun = dict(endurance="Wh", extra_payload="g")

    plot_all_directions(r, queries=data['queries'], results=data['results'],
                        what_to_plot_res=what_to_plot_res,
                        what_to_plot_fun=what_to_plot_fun)
    
    fig1 = dict(figsize=(3, 3)) 
    fig2 = dict(figsize=(4, 4))
    
    fnames = ('endurance', 'extra_payload')
    rnames = ('total_cost', 'total_mass')
    
    axis = (108, 145,  0.05, 0.8)
    axis2 = (105, 111.5,  0.05, 0.27)
    fs, rs = cs.iterate(fnames, rnames)
    
    colors = get_colors(len(fs))
    f = r.figure()
    
    with f.plot('resources1', **fig1) as pylab:
        ieee_spines_zoom3(pylab)
  
        for i, ((f1, f2), resources) in enumerate(zip(fs, rs)):
            color = colors[i]
            if resources:
                marker = 'k.'
            else:
                marker = 'x'
            pylab.plot(f1, f2, marker, markerfacecolor=color, clip_on=False)
  
        pylab.xlabel('endurance [min]')
        pylab.ylabel('extra_payload [g]')
#         pylab.xticks([0, 30, 60, 90, 120])
        set_axis_colors(pylab, color_functions, color_functions)
        

    params0 = dict(color_shadow=[1.0, 0.8, 0.8], markers='k.',
                       markers_params={})

    color_shadow = params0['color_shadow']
    markers = params0['markers']

    P = parse_poset('dimensionless x dimensionless')
    
    with f.plot('resources2', **fig2) as pylab:
        ieee_spines_zoom3(pylab)

        for i, resources in enumerate(rs):
            v = P.Us(resources)
            color = colors[i]
            plot_upset_R2(pylab, v, axis, extra_space_shadow=0,
                      color_shadow=color, markers=markers,
                      marker_params=dict(markerfacecolor=color))
        
        pylab.ylabel('total mass [kg]')
        pylab.xlabel('total cost [USD]')
        pylab.xticks([110, 120, 130, 140, 150])
#         pylab.yticks([0.2, 0.25, 0.3, 0.35])
        set_axis_colors(pylab, color_resources, color_resources)
        pylab.axis(axis)

    rs_subset = rs[:3]
    with f.plot('resources3', **fig2) as pylab:
        ieee_spines_zoom3(pylab)

        for i, resources in enumerate(rs_subset):
            v = P.Us(resources)
            color = colors[i]
            plot_upset_R2(pylab, v, axis2, extra_space_shadow=0,
                      color_shadow=color, markers=markers,
                      marker_params=dict(markerfacecolor=color))
        
        pylab.ylabel('total mass [kg]')
        pylab.xlabel('total cost [USD]')
        pylab.xticks([110, 110.5, 111,111.5,])
        set_axis_colors(pylab, color_resources, color_resources)

    return r
    
def get_colors(n):
    colors = generate_colors(n + 1, colormap_name='Paired')
    del colors[5]
    return colors
    
def report_plane1(data):
    matplotlib_settings()
    r = Report()
    result_like = dict(total_mass="kg", total_cost="USD")
    what_to_plot_res = result_like
    what_to_plot_fun = dict(endurance="Wh", num_missions="[]")
# 
#     plot_all_directions(r, queries=data['queries'], results=data['results'],
#                         what_to_plot_res=what_to_plot_res,
#                         what_to_plot_fun=what_to_plot_fun)
    
    
    cs = CommonStats(data)
    r = Report() 
    
    fig1 = dict(figsize=(3, 3)) 
    fig2 = dict(figsize=(4, 4))
    
    fnames = ('endurance', 'num_missions')
    rnames = ('total_cost', 'total_mass')
    
    axis = (105, 155,  0.2, 0.37)
    axis2 = (105, 112.5,  0.2, 0.235)
    fs, rs = cs.iterate(fnames, rnames)
    
    colors = get_colors(len(fs))
    f = r.figure()
    
    with f.plot('resources1', **fig1) as pylab:
        ieee_spines_zoom3(pylab)
  
        for i, ((f1, f2), resources) in enumerate(zip(fs, rs)):
            color = colors[i]
            if resources:
                marker = 'k.'
            else:
                marker = 'x'
            pylab.plot(f1, f2, marker, markerfacecolor=color, clip_on=False)
  
        pylab.xlabel('endurance [min]')
        pylab.ylabel('# missions')
        pylab.xticks([0, 30, 60, 90, 120])
        set_axis_colors(pylab, color_functions, color_functions)

    params0 = dict(color_shadow=[1.0, 0.8, 0.8], markers='k.',
                       markers_params={})

    color_shadow = params0['color_shadow']
    markers = params0['markers']

    P = parse_poset('dimensionless x dimensionless')
    
    with f.plot('resources2', **fig2) as pylab:
        ieee_spines_zoom3(pylab)

        for i, resources in enumerate(rs):
            v = P.Us(resources)
            color = colors[i]
            plot_upset_R2(pylab, v, axis, extra_space_shadow=0,
                      color_shadow=color, markers=markers,
                      marker_params=dict(markerfacecolor=color))
        
        pylab.ylabel('total mass [kg]')
        pylab.xlabel('total cost [USD]')
        pylab.xticks([110, 120, 130, 140, 150])
        pylab.yticks([0.2, 0.25, 0.3, 0.35])
        set_axis_colors(pylab, color_resources, color_resources)

    rs_subset = rs[:3]
    with f.plot('resources3', **fig2) as pylab:
        ieee_spines_zoom3(pylab)

        for i, resources in enumerate(rs_subset):
            v = P.Us(resources)
            color = colors[i]
            plot_upset_R2(pylab, v, axis2, extra_space_shadow=0,
                      color_shadow=color, markers=markers,
                      marker_params=dict(markerfacecolor=color))
        
        pylab.ylabel('total mass [kg]')
        pylab.xlabel('total cost [USD]')
        pylab.xticks([110, 111, 112])
        set_axis_colors(pylab, color_resources, color_resources)

    return r


class DroneApp(QuickApp):
    
    def define_options(self, params):
        pass

    def define_jobs_context(self, context):

        data = context.comp(go_plane1)
        r = context.comp(report_plane1, data)
        context.add_report(r, 'plane1') 
        data = context.comp(go_plane2)
        r = context.comp(report_plane2, data)
        context.add_report(r, 'plane2') 



main = DroneApp.get_sys_main()
if __name__ == '__main__':
    main()

        
