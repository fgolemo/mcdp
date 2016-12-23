# -*- coding: utf-8 -*-
from contextlib import contextmanager
from contracts import contract
from matplotlib.cm import get_cmap
from mcdp_ipython_utils.loading import to_numpy_array
from reprep.plot_utils import (ieee_spines, x_axis_extra_space,
    y_axis_extra_space)
import itertools

color_resources = '#700000'
color_functions = '#007000'


def generate_colors(n, colormap_name):
    """ Generates n color strings. """
#     from itertools import cycle
#     cycol = cycle('bgrcmk').next
#     colors = [cycol() for _ in range(n)]

    colors = []
    cm = get_cmap(colormap_name)
    for i in range(n):
        color = cm(1.*i / n)  # color will now be an RGBA tuple
        colors.append(color)

    return colors

@contract(queries='list[N](dict)', results='list[N](list(dict))',
          what_to_plot_fun='dict', what_to_plot_res='dict')
def plot_all_directions(r, queries, results, what_to_plot_fun, what_to_plot_res):
    """
        result_like 
        
        result_like = dict(maintenance="s", cost="$", mass='kg')
    """
    n = len(queries)
    assert n == len(results)
    colors = generate_colors(n, colormap_name='Paired')

    marker_fun = marker_res = marker_joint = 'o'

    for xwhat, ywhat in itertools.combinations(what_to_plot_res, 2):
        name = '%s_%s' % (xwhat, ywhat)
        with r.plot(name) as pylab:
            with figure_style1(pylab):
                plot_axis(pylab, results, what_to_plot_res, colors, xwhat, ywhat,
                          marker=marker_res)
            set_axis_colors(pylab, color_resources, color_resources)

    qqueries = [ [ x ] for x in queries]            
    for xwhat, ywhat in itertools.combinations(what_to_plot_fun, 2):
        name = '%s_%s' % (xwhat, ywhat)
        with r.plot(name) as pylab:
            with figure_style1(pylab):                    
                plot_axis(pylab, qqueries, what_to_plot_fun, colors, xwhat, ywhat,
                          marker=marker_fun)
            set_axis_colors(pylab, color_functions, color_functions)


    for xwhat in what_to_plot_fun:
        for ywhat in what_to_plot_res:
            name = '%s_%s' % (xwhat, ywhat)
            with r.plot(name) as pylab:
                with figure_style1(pylab):
                    for fun, res, color in zip(qqueries, results, colors):
                        x = to_numpy_array(what_to_plot_fun, fun)[xwhat]
                        y = to_numpy_array(what_to_plot_res, res)[ywhat]
                        if len(y) == 0:  # unfeasible
                            pylab.plot(x, 0, 'x', color='black')
                        elif len(x) == 1 and len(y) > 1:
                            xs = [x[0]] * len(y)
                            pylab.plot(xs, y, marker_joint, color=color)
                        else:
                            # print x, y
                            pylab.plot(x, y, marker_joint, color=color)
                set_axis_colors(pylab, color_functions, color_resources)

                pylab.xlabel(axis_label(what_to_plot_fun, xwhat))
                pylab.ylabel(axis_label(what_to_plot_res, ywhat))


def plot_axis(pylab, results, what_to_plot, colors, xwhat, ywhat, marker):

    for res, color in zip(results, colors):
        a = to_numpy_array(what_to_plot, res)
        x = a[xwhat]
        y = a[ywhat]
        pylab.plot(x, y, marker, color=color)

    pylab.xlabel(axis_label(what_to_plot, xwhat))
    pylab.ylabel(axis_label(what_to_plot, ywhat))
    
def axis_label(what_to_plot, what) :
    if what_to_plot[what] == '[]':
        return what
    st = '%s [%s]' % (what, what_to_plot[what])
    st.replace('$', '\\$')
    return st

def set_axis_colors(pylab, color_x, color_y):
    ax = pylab.gca()
    ax.spines['bottom'].set_color(color_x)
    ax.spines['left'].set_color(color_y)
    ax.xaxis.label.set_color(color_x)
    ax.tick_params(axis='x', colors=color_x)
    ax.yaxis.label.set_color(color_y)
    ax.tick_params(axis='y', colors=color_y)

@contextmanager
def figure_style1(pylab):
    f = pylab.gcf()
    size = 1.57 * 3
    ratio = 1
    f.set_size_inches((size, size * ratio))
    ieee_spines(pylab)
    yield pylab
    y_axis_extra_space(pylab)
    x_axis_extra_space(pylab)
