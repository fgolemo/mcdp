# -*- coding: utf-8 -*-
import os

from contracts.utils import raise_desc, raise_wrapped
from mcdp_posets import  UpperSets
from mcdp_report.axis_algebra import enlarge, join_axes
from mcdp_report.movies import create_movie_from_png_sequence
from mcdp_report.plotters.get_plotters_imp import get_all_available_plotters, \
    get_plotters
from mcdp_report.plotters.interface import NotPlottable
from mocdp import logger
from mocdp.exceptions import DPInternalError
from reprep.config import RepRepDefaults
from reprep.plot_utils.styles import ieee_spines, ieee_fonts

# XXX: floating constants
extra_space_finite = 0.025
extra_space_top = 0.05

def generic_report_trace(r, ndp, dp, trace, out, do_movie=False):  # @UnusedVariable
#     r.text('dp', dp.repr_long())
    nloops = 0
    for l, trace_loop in enumerate(trace.find_loops()):
        nloops += 1
        with r.subsection('loop%d' % l) as r2:
            _report_loop(r2, trace_loop, out, do_movie=do_movie)
    if nloops == 0:
        raise_desc(DPInternalError, 'There is no iteration; no movie available.')
        
def _report_loop(r, trace_loop, out, do_movie=True):
    # list of KleeneIteration
    iterations = trace_loop.get_value1('iterations')
    R = trace_loop.get_value1('R')
    R1 = R[0] 

    sips = [_.s for _ in iterations]
    converged = [_.s_converged for _ in iterations]
    rs = [_.r for _ in iterations]
    rs_converged = [_.r_converged for _ in iterations]

    with r.subsection('rs') as r2:
        sequences = _report_loop_sequence(r2, R1, rs, rs_converged, do_movie=do_movie)

        if do_movie:
            for name, sequence in sequences.items():                
                outmp4 = os.path.join(out, 'video-r-%s.mp4' % name)
                create_movie_from_png_sequence(sequence, outmp4)

    with r.subsection('sip') as r2:
        sequences = _report_loop_sequence(r2, R, sips, converged, do_movie=do_movie)

        if do_movie:
            for name, sequence in sequences.items():                
                outmp4 = os.path.join(out, 'video-s-%s.mp4' % name)
                create_movie_from_png_sequence(sequence, outmp4)
    
 
def _report_loop_sequence(report, R, sips, converged, do_movie):
    """
        Returns a dictionary dict(str: list of png data)
    """
    sequences = {}
    
    UR = UpperSets(R)
    from matplotlib import pylab
    ieee_fonts(pylab)
    RepRepDefaults.savefig_params = dict(dpi=400, bbox_inches='tight', 
                                         pad_inches=0.01, transparent=False)

    figsize = (2, 2)
    
    try:
        available_plotters = list(get_plotters(get_all_available_plotters(), UR))
    except NotPlottable as e:
        msg = 'Could not find plotter for space UR = %s.' % UR
        raise_wrapped(DPInternalError, e, msg , UR=UR, compact=True)
    
    with report.subsection('sip') as r2:
        for name, plotter in available_plotters:
            sequences[name] = [] # sequence of png
            f = r2.figure(name, cols=5)

            axis = plotter.axis_for_sequence(UR, sips)

            axis = list(axis)
            axis[0] = 0.0
            axis[2] = 0.0
            axis[1] = min(axis[1], 1000.0)
            axis[3] = min(axis[3], 1000.0)
            axis = tuple(axis)

            visualized_axis = enlarge(axis, extra_space_top * 2)

            for i, sip in enumerate(sips):
                with f.plot('step%03d' % i, figsize=figsize) as pylab:
                    logger.debug('Plotting iteration %d/%d' % (i, len(sips)))
                    ieee_spines(pylab)
                    c_orange = '#FFA500'
                    c_red = [1, 0.5, 0.5]
                    plotter.plot(pylab, axis, UR, R.U(R.get_bottom()),
                                 params=dict(color_shadow=c_red, markers=None))
                    marker_params = dict(markersize=5, markeredgecolor='none')
                    plotter.plot(pylab, axis, UR, sip,
                                 params=dict(color_shadow=c_orange,
                                             markers_params=marker_params))
                    conv = converged[i]
                    c_blue = [0.6, 0.6, 1.0]
                    plotter.plot(pylab, axis, UR, conv,
                                 params=dict(color_shadow=c_blue))
                    
                    for c in conv.minimals:
                        p = plotter.toR2(c)
                        pylab.plot(p[0], p[1], 'go',
                                   markersize=5, markeredgecolor='none', 
                                   markerfacecolor='g', clip_on=False)
                    pylab.axis(visualized_axis)
                    from mcdp_ipython_utils.plotting import color_resources, set_axis_colors

                    set_axis_colors(pylab, color_resources, color_resources)

                if do_movie:
                    node = f.resolve_url('step%03d/png' % i)
                    png = node.raw_data
                    sequences[name].append(png)

    return sequences


def generic_report(r, dp, trace, annotation=None, axis0=(0, 0, 0, 0)):
   
    R = dp.get_res_space()
    UR = UpperSets(R)

    plotters = get_all_available_plotters()
    
    with r.subsection('S', caption='S') as rr:
        space = trace.S
        sequence = trace.get_s_sequence()
        generic_try_plotters(rr, plotters, space, sequence, axis0=axis0,
                             annotation=annotation)

    with r.subsection('R', caption='R') as rr:
        space = UR
        sequence = trace.get_r_sequence()
        generic_try_plotters(rr, plotters, space, sequence, axis0=axis0,
                             annotation=annotation)




def generic_plot(f, space, value):
    plotters = get_all_available_plotters()

    es = []
    for name, plotter in plotters.items():
        try:
            plotter.check_plot_space(space)
        except NotPlottable as e:
            es.append(e)
            # print('Plotter %r cannot plot %r:\n%s' % (name, space, e))
            continue

        axis = plotter.axis_for_sequence(space, [value])
        axis = enlarge(axis, 0.15)
        #print('enlarged:  %s' % str(axis))
        with f.plot(name) as pylab:
            plotter.plot(pylab, axis, space, value, params={})
            pylab.axis(axis)

def generic_plot_sequence(r, plotter, space, sequence,
                          axis0=None, annotation=None):

    axis = plotter.axis_for_sequence(space, sequence)

    if axis[0] == axis[1]:
        dx = 1
#         dy = 1
        axis = (axis[0] - dx, axis[1] + dx, axis[2], axis[3])
    axis = enlarge(axis, 0.15)
    if axis0 is not None:
        axis = join_axes(axis, axis0)

    for i, x in enumerate(sequence):
        caption = space.format(x)
        caption = None
        with r.plot('S%d' % i, caption=caption) as pylab:
            plotter.plot(pylab, axis, space, x)
            if annotation is not None:
                annotation(pylab, axis)

            xlabel, ylabel = plotter.get_xylabels(space)
            try:
                if xlabel:
                    pylab.xlabel(xlabel)
                if ylabel:
                    pylab.ylabel(ylabel)

            except UnicodeDecodeError as e:
                # print xlabel, xlabel.__repr__(), ylabel, ylabel.__repr__(), e
                pass
            
            if (axis[0] != axis[1]) or (axis[2] != axis[3]):
                pylab.axis(axis)


def generic_try_plotters(r, plotters, space, sequence,
                         axis0=None, annotation=None):
    nplots = 0
    es = []
    for name, plotter in plotters.items():
        try:
            plotter.check_plot_space(space)
        except NotPlottable as e:
            es.append(e)
            # print('Plotter %r cannot plot %r:\n%s' % (name, space, e))
            continue
        nplots += 1

        f = r.figure(name, cols=5)
        generic_plot_sequence(f, plotter, space, sequence, axis0=axis0,
                              annotation=annotation)

    if not nplots:
        r.text('error', 'No plotters for %s' % space +
               '\n\n' + "\n".join(str(e) for e in es))

