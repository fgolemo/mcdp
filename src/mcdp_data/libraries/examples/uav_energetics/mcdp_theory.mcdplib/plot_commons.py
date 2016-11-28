# -*- coding: utf-8 -*-

from common_stats import CommonStats
from mcdp_ipython_utils.plotting import color_functions, set_axis_colors, \
    color_resources
from plot_utils import   ieee_spines_zoom3, plot_field


fig = dict(figsize=(4.5, 4))
popt = dict(clip_on=False) 


def figure_num_implementations2(r, data, cs, fname1, fname2):
    assert isinstance(cs, CommonStats)
    
    f1 = cs.get_functionality(fname1)
    f2 = cs.get_functionality(fname2)
    
    def do_axes(pylab):
        pylab.xlabel(fname1)
        pylab.ylabel(fname2)
        set_axis_colors(pylab, color_functions, color_functions)


    with r.plot('feasibility', **fig) as pylab:
        ieee_spines_zoom3(pylab)
          
        pylab.plot(f1[cs.one_solution], 
                   f2[cs.one_solution],
                    'k.', markersize=4, **popt)
        pylab.plot(f1[cs.multiple_solutions], 
                   f2[cs.multiple_solutions],
                   'ms', markersize=4, **popt)
        pylab.plot(f1[cs.is_not_feasible],
                   f2[cs.is_not_feasible], 'r.', markersize=0.5, **popt)
          
        do_axes(pylab)

    with r.plot('implementations', **fig) as pylab:
        ieee_spines_zoom3(pylab) 
          
        pylab.plot(f1[cs.one_implementation], 
                   f2[cs.one_implementation],
                    'k.', markersize=4, **popt)
        pylab.plot(f1[cs.multiple_implementations], 
                   f2[cs.multiple_implementations],
                   'ms', markersize=4, **popt)
        pylab.plot(f1[cs.is_not_feasible],
                   f2[cs.is_not_feasible], 'r.', markersize=0.5, **popt)
          
        do_axes(pylab)
         
         
    with r.plot('num_implementations', **fig) as pylab:
  
        ieee_spines_zoom3(pylab)
  
        x = f1
        y = f2
        z = cs.all_num_implementations
        plot_field(pylab, x, y, z, cmap='winter', vmin=0, vmax=5)
        pylab.title('num implementations', color=color_resources, y=1.08)
        do_axes(pylab)

    with r.plot('num_solutions', **fig) as pylab:
  
        ieee_spines_zoom3(pylab)
  
        x = f1
        y = f2
        z = cs.all_num_solutions
        plot_field(pylab, x, y, z, cmap='winter', vmin=0, vmax=5)
        pylab.title('num solutions', color=color_resources,  y=1.08)
        do_axes(pylab)
        
    misc = 'num solutions: %s\n num implementations: %s' % (cs.all_num_solutions, cs.all_num_implementations)
#     r.text('misc', misc)
    
    
    