#!/usr/bin/env python
# -*- coding: utf-8 -*-
    
from common_stats import CommonStats
from discrete_choices import compute_discrete_choices, figure_discrete_choices2
from mcdp_ipython_utils.loading import solve_combinations
from mcdp_ipython_utils.plotting import (color_resources, color_functions,
    set_axis_colors)
from mcdp_library_tests.tests import get_test_librarian
import numpy as np
from plot_commons import figure_num_implementations2
from plot_utils import ieee_spines_zoom3, plot_field, ieee_fonts_zoom3
from quickapp.quick_app import QuickApp
from reprep import Report


colormap = 'YlOrRd'


def get_combinations_drone():
    z = 2
    nt = 15 * z
    nr = 15 * z
    combinations = {
        "endurance": (np.linspace(1, 120, nt), "min"),
        "num_missions": (np.linspace(1, 2000, nr), "[]"),
        "extra_payload": (100.0, "g"),
        "extra_power": (1.0, "W"),
        "velocity": (1.0, "m/s"),
    }
    return combinations


def go_drone1_mass_cost():
    librarian = get_test_librarian()
    lib = librarian.load_library('mcdp_theory') 
    ndp = lib.load_ndp('drone1')
    
    combinations = get_combinations_drone()
    
    result_like = dict(total_cost="USD", total_mass='g')

    data = solve_combinations(ndp, combinations, result_like)
    return data

def go_drone1_mass():
    librarian = get_test_librarian()
    lib = librarian.load_library('mcdp_theory') 
    ndp = lib.load_ndp('drone1_min_mass')
    
    combinations = get_combinations_drone()
    
    result_like = dict(total_mass='g')

    data = solve_combinations(ndp, combinations, result_like)
    return data

def go_drone1_cost():
    librarian = get_test_librarian()
    lib = librarian.load_library('mcdp_theory') 
    ndp = lib.load_ndp('drone1_min_cost')
    
    combinations = get_combinations_drone()
    
    result_like = dict(total_cost='USD')

    data = solve_combinations(ndp, combinations, result_like)
    return data

def get_combinations():
    z = 2
    nt = 15 * z
    nr = 15 * z
    combinations = {
        "capacity": (np.linspace(1, 1000, nt), "Wh"),
        "missions": (np.linspace(1, 2000, nr), "[]"),
    }
    return combinations

def go_batteries_min_joint():
    librarian = get_test_librarian()
    
    lib = librarian.load_library('mcdp_theory') 
    
    ndp = lib.load_ndp('batteries4_min_joint')
    
    combinations = get_combinations()
    
    result_like = dict(cost="USD", maintenance="R", mass='g')

    data = solve_combinations(ndp, combinations, result_like)
    return data


def go_batteries_min_tco():
    librarian = get_test_librarian()
    
    lib = librarian.load_library('mcdp_theory') 
    
    ndp = lib.load_ndp('batteries6_min_tco')
    
    combinations = get_combinations()
    
    result_like = dict(tco="USD")

    data = solve_combinations(ndp, combinations, result_like)
    return data

def go_batteries_min_maintenance():
    librarian = get_test_librarian()
    
    lib = librarian.load_library('mcdp_theory') 
    
    ndp = lib.load_ndp('batteries1_min_maintenance')
    
    combinations = get_combinations()
    
    result_like = dict(maintenance="R")

    data = solve_combinations(ndp, combinations, result_like)
    return data

def go_batteries_min_cost():
    librarian = get_test_librarian()
    
    lib = librarian.load_library('mcdp_theory') 
    
    ndp = lib.load_ndp('batteries2_min_cost')
    
    combinations = get_combinations()
    
    result_like = dict(cost="USD")
    

    data = solve_combinations(ndp, combinations, result_like)
    return data


def go_batteries_min_cost_mass():
    librarian = get_test_librarian()
    
    lib = librarian.load_library('mcdp_theory') 
    
    ndp = lib.load_ndp('batteries5_min_cost_mass')
    
    combinations = get_combinations()
    
    result_like = dict(cost="USD", mass='g')

    data = solve_combinations(ndp, combinations, result_like)
    return data


def go_batteries_min_mass():
    librarian = get_test_librarian()
    
    lib = librarian.load_library('mcdp_theory') 
    
    ndp = lib.load_ndp('batteries3_min_mass')
    
    combinations = get_combinations()
    
    result_like = dict(mass="g")

    data = solve_combinations(ndp, combinations, result_like)
    return data

fig = dict(figsize=(4.5, 4))

def do_axes(pylab):
    pylab.xlabel('missions')
    pylab.ylabel('capacity [J]')
    set_axis_colors(pylab, color_functions, color_functions)

def do_axes_drone(pylab):
    pylab.xlabel('missions')
    pylab.ylabel('endurance')
    set_axis_colors(pylab, color_functions, color_functions)

def create_report_min_maintenance(data):
    matplotlib_settings()

    cs = CommonStats(data)
    r = Report() 
    figure_num_implementations2(r, data, cs, 'missions', 'capacity')
    figure_discrete_choices2(r, data, cs, 'missions', 'capacity')
    
    f = r.figure()
    with f.plot('maintenance', **fig) as pylab:
  
        ieee_spines_zoom3(pylab)
  
        x = cs.get_functionality('missions')
        y = cs.get_functionality('capacity')
        z = cs.get_min_resource('maintenance')
        plot_field(pylab, x, y, z, cmap=colormap)
        pylab.title('maintenance', color=color_resources, y=1.08)

        do_axes(pylab)

    return r
    
def create_report_min_cost(data):
    matplotlib_settings()

    cs = CommonStats(data)
    r = Report() 
    figure_num_implementations2(r, data, cs, 'missions', 'capacity')
    figure_discrete_choices2(r, data, cs, 'missions', 'capacity')
  
    f = r.figure()
    with f.plot('cost', **fig) as pylab:
  
        ieee_spines_zoom3(pylab)
  
        x = cs.get_functionality('missions')
        y = cs.get_functionality('capacity')
        z = cs.get_min_resource('cost')
        plot_field(pylab, x, y, z, cmap=colormap)
        pylab.title('cost', color=color_resources,  y=1.08)
        do_axes(pylab)
        
    return r
 
def create_report_min_joint(data):
    matplotlib_settings()

    cs = CommonStats(data)
    r = Report() 
    figure_num_implementations2(r, data, cs, 'missions', 'capacity')
    figure_discrete_choices2(r, data, cs, 'missions', 'capacity')
    return r


def create_report_min_cost_mass(data):
    matplotlib_settings()

    cs = CommonStats(data)
    r = Report() 
    figure_num_implementations2(r, data, cs, 'missions', 'capacity')
    figure_discrete_choices2(r, data, cs, 'missions', 'capacity')

    return r

popt = dict(clip_on=False)

def create_report_min_tco(data):
    matplotlib_settings()

    cs = CommonStats(data)
    r = Report() 
    figure_num_implementations2(r, data, cs, 'missions', 'capacity')
    figure_discrete_choices2(r, data, cs, 'missions', 'capacity')
    
    all_min_tco = cs.get_min_resource('tco')
           
    f = r.figure() 
    with f.plot('tco', **fig) as pylab:
  
        ieee_spines_zoom3(pylab)
  
        x = cs.get_functionality('missions')
        y = cs.get_functionality('capacity')
        z = all_min_tco
        plot_field(pylab, x, y, z, cmap=colormap)
        pylab.title('tco', color=color_resources, y=1.08)
        do_axes(pylab)
    
    return r

    
def create_report_min_mass(data):
    matplotlib_settings()

    cs = CommonStats(data)
    r = Report() 
    figure_num_implementations2(r, data, cs, 'missions', 'capacity')
    figure_discrete_choices2(r, data, cs, 'missions', 'capacity')
    
    f = r.figure()
    with f.plot('mass', **fig) as pylab:
  
        ieee_spines_zoom3(pylab)
  
        x = cs.get_functionality('missions')
        y = cs.get_functionality('capacity')
        z = cs.get_min_resource('mass')
        plot_field(pylab, x, y, z, cmap=colormap)
        pylab.title('mass', color=color_resources,  y=1.08)
        do_axes(pylab)
        
    return r

def create_report_drone1_mass(data):
    matplotlib_settings()

    cs = CommonStats(data)
    
    r = Report() 
    figure_num_implementations2(r, data, cs, 'num_missions', 'endurance')
    figure_discrete_choices2(r, data, cs, 'num_missions', 'endurance')

    return r

def create_report_drone1_cost(data):
    matplotlib_settings()

    cs = CommonStats(data)
    
    r = Report() 
    figure_num_implementations2(r, data, cs, 'num_missions', 'endurance')
    figure_discrete_choices2(r, data, cs, 'num_missions', 'endurance')

    return r

def matplotlib_settings():
    from matplotlib import pylab
    ieee_fonts_zoom3(pylab)
    
def create_report_drone1_mass_cost(data):
    matplotlib_settings()
    cs = CommonStats(data)
    
    r = Report() 
    figure_num_implementations2(r, data, cs, 'num_missions', 'endurance')
    figure_discrete_choices2(r, data, cs, 'num_missions', 'endurance')

    f = r.figure()
    with f.plot('total_cost', **fig) as pylab:
  
        ieee_spines_zoom3(pylab)
  
        x = cs.get_functionality('num_missions')
        y = cs.get_functionality('endurance')
        z = cs.get_min_resource('total_cost')
        plot_field(pylab, x, y, z, cmap=colormap)
        pylab.title('total_cost', color=color_resources,  y=1.08)
        

    with f.plot('total_mass', **fig) as pylab:
  
        ieee_spines_zoom3(pylab)
  
        x = cs.get_functionality('num_missions')
        y = cs.get_functionality('endurance')
        z = cs.get_min_resource('total_mass')
        plot_field(pylab, x, y, z, cmap=colormap)
        pylab.title('total_mass', color=color_resources,  y=1.08)
        
    return r



class App(QuickApp):
    
    def define_options(self, params):
        pass

    def define_jobs_context(self, context):

        data = context.comp(go_batteries_min_maintenance)
        r = context.comp(create_report_min_maintenance, data)
        context.add_report(r, 'report_min_maintenance') 

        data = context.comp(go_batteries_min_cost)
        r = context.comp(create_report_min_cost, data)
        context.add_report(r, 'report_min_cost') 

        data = context.comp(go_batteries_min_mass)
        r = context.comp(create_report_min_mass, data)
        context.add_report(r, 'report_min_mass') 
        
        data = context.comp(go_batteries_min_joint)
        r = context.comp(create_report_min_joint, data)
        context.add_report(r, 'report_min_joint') 

        data = context.comp(go_batteries_min_cost_mass)
        r = context.comp(create_report_min_cost_mass, data)
        context.add_report(r, 'report_min_cost_mass') 

        data = context.comp(go_batteries_min_tco)
        r = context.comp(create_report_min_tco, data)
        context.add_report(r, 'report_min_tco') 

        data = context.comp(go_drone1_mass_cost)
        r = context.comp(create_report_drone1_mass_cost, data)
        context.add_report(r, 'drone1_mass_cost') 

        data = context.comp(go_drone1_mass)
        r = context.comp(create_report_drone1_mass, data)
        context.add_report(r, 'drone1_mass') 
        
        data = context.comp(go_drone1_cost)
        r = context.comp(create_report_drone1_cost, data)
        context.add_report(r, 'drone1_cost') 
        
        

main = App.get_sys_main()
if __name__ == '__main__':
    main()
