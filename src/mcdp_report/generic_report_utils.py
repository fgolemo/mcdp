# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
import functools
import os
import traceback

from contracts import contract
from contracts.utils import indent, raise_desc, raise_wrapped
from mcdp_posets import (NotLeq, PosetProduct, Rcomp, UpperSet, UpperSets,
    get_types_universe)
from mcdp_posets.find_poset_minima.baseline_n2 import poset_minima
from mcdp_posets.rcomp import finfo
from mocdp import logger
from mocdp.exceptions import DPInternalError, mcdp_dev_warning
import numpy as np
from reprep.config import RepRepDefaults
from reprep.plot_utils.styles import ieee_spines, ieee_fonts

from .drawing import plot_upset_R2
from .utils import safe_makedirs


extra_space_finite = 0.025
extra_space_top = 0.05


def generic_report_trace(r, ndp, dp, trace, out, do_movie=False):  # @UnusedVariable
    r.text('dp', dp.repr_long())
    # r.text('trace', trace.format())
    nloops = 0
    for l, trace_loop in enumerate(trace.find_loops()):
        nloops += 1
        with r.subsection('loop%d' % l) as r2:
            _report_loop(r2, trace_loop, out, do_movie=do_movie)
    if nloops == 0:
        raise_desc(DPInternalError, 'There is no iteration; no movie available.')
        
def _report_loop(r, trace_loop, out, do_movie=True):
    from matplotlib import pylab
    ieee_fonts(pylab)
    RepRepDefaults.savefig_params = dict(dpi=400, 
                                         bbox_inches='tight', pad_inches=0.01,
                                         transparent=True)


    figsize = (2, 2)
    sips = list(trace_loop.get_iteration_values('sip'))
    converged = list(trace_loop.get_iteration_values('converged'))
    
    UR = trace_loop.get_value1('UR')
    R = trace_loop.get_value1('R')

    with r.subsection('sip') as r2:
        for name, plotter in get_plotters(plotters, UR):
            f = r2.figure(name, cols=5)

            axis = plotter.axis_for_sequence(UR, sips)

            axis = list(axis)
            axis[0] = 0.0
            axis[2] = 0.0
            axis[1] = min(axis[1], 1000.0)
            axis[3] = min(axis[3], 1000.0)
            axis = tuple(axis)
            RepRepDefaults.savefig_params['transparent'] = False

            outdir = os.path.join(out, 'video-%s' % name)

            visualized_axis = enlarge(axis, extra_space_top * 2)
#             print('Decided on axis %s' % str(axis))
            for i, sip in enumerate(sips):
                with f.plot('step%03d' % i, figsize=figsize) as pylab:
                    print('Step %d' % i)
                    ieee_spines(pylab)
                    c_orange = '#FFA500'
                    c_red = [1, 0.5, 0.5]
                    # plotting bottom (all in red
                    plotter.plot(pylab, axis, UR, R.U(R.get_bottom()),
                                 params=dict(color_shadow=c_red, markers=None))
                    #print('sip:\n  %s' % sip)
                    marker_params = dict(markersize=5, markeredgecolor='none')
                    plotter.plot(pylab, axis, UR, sip,
                                 params=dict(color_shadow=c_orange,
                                             markers_params=marker_params))
                    conv = converged[i]
                    c_blue = [0.6, 0.6, 1.0]
                    #print('converged:\n  %s' % conv)
                    plotter.plot(pylab, axis, UR, conv,
                                 params=dict(color_shadow=c_blue))
                    #print('minimal')
                    
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

                    safe_makedirs(outdir)
                    fn = os.path.join(outdir, '%05d.png' % i)
                    with open(fn, 'w') as fi:
                        fi.write(node.raw_data)

            if do_movie:
                outmp4 = os.path.join(out, 'video-%s.mp4' % name)

                try:
                    import procgraph_mplayer  # @UnusedImport
                
#                     from procgraph_mplayer.scripts.join_video import join_video_29
                except ImportError as e:
                    logger.error('Cannot use Procgraph to create video.')
                    logger.error(e)
                    logger.info('The frames are in the directory %s' % outdir)
                else:
                    join_video_29_fixed(output=outmp4, dirname=outdir,
                                        pattern='.*.png', fps=1.0)


mcdp_dev_warning('add this to the procgraph repository')


def join_video_29_fixed(output, dirname, pattern, fps):
    """ 
        Note that the pattern is a Python regex:
        
        pg-video-join -d anim-simple/ -p '*.png' -o anim-simple-collate.mp4 --fps 1 
        
    """
    from procgraph.core.registrar_other import register_model_spec
    from procgraph import pg

    register_model_spec("""
--- model join_video_helper_29
config output
config dirname
config pattern
config images_per_second

|files_from_dir dir=$dirname regexp=$pattern fps=$images_per_second| \
--> |imread_rgb| \
--> |fix_frame_rate fps=29.97| \
--> |mencoder quiet=1 file=$output timestamps=0|
    
    """)
    params = dict(dirname=dirname, 
                  pattern=pattern, 
                  output=output,
                  images_per_second=fps)
    pg('join_video_helper_29', params)



def generic_report(r, dp, trace, annotation=None, axis0=(0, 0, 0, 0)):
   
    R = dp.get_res_space()
    UR = UpperSets(R)

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

def get_best_plotter(space):
    p = list(get_plotters(plotters, space))
    if not p:
        msg = 'Could not find any plotter.'
        raise_desc(ValueError, msg, space=space)
    return p[0][1]

def get_plotters(plotters, space):
    available = []
    errors = []
    for name, plotter in plotters.items():
        try:
            plotter.check_plot_space(space)
            available.append((name, plotter))
        except NotPlottable as e:
            errors.append((name, e))
    if available:
        return available
    msg = 'Could not find any plotter.'
    for name, e in errors:
        msg += '%r:\n%s' % (name, indent(traceback.format_exc(e), '  '))
    raise_desc(NotPlottable, msg)


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


def join_axes(a, b):
    return (min(a[0], b[0]),
            max(a[1], b[1]),
            min(a[2], b[2]),
            max(a[3], b[3]))




def generic_plot(f, space, value):
    es = []
    for name, plotter in plotters.items():
        try:
            plotter.check_plot_space(space)
        except NotPlottable as e:
            es.append(e)
            # print('Plotter %r cannot plot %r:\n%s' % (name, space, e))
            continue

        axis = plotter.axis_for_sequence(space, [value])
        # axis = enlarge(axis, 0.15)
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
                print xlabel, xlabel.__repr__(), ylabel, ylabel.__repr__(), e
            
            if (axis[0] != axis[1]) or (axis[2] != axis[3]):
                pylab.axis(axis)

class NotPlottable(Exception):
    pass

class Plotter():
    __metaclass__ = ABCMeta

    @abstractmethod
    def check_plot_space(self, space):
        pass

    @abstractmethod
    @contract(returns='seq[4]')
    def axis_for_sequence(self, space, seq):
        pass

    @abstractmethod
    def plot(self, pylab, axis, space, value, params={}):
        pass

    def get_xylabels(self, _space):
        return None, None

class PlotterUR(Plotter):

    @abstractmethod
    def check_plot_space(self, space):
        tu = get_types_universe()
        if not isinstance(space, UpperSets):
            msg = 'I can only plot upper sets.'
            raise_desc(NotPlottable, msg, space=space)

        R = Rcomp()
        P = space.P
        try:
            tu.check_leq(P, R)
        except NotLeq as e:
            msg = ('cannot convert to R^2 from %s' % space)
            raise_wrapped(NotPlottable, e, msg)

        _f1, _f2 = tu.get_embedding(P, R)

    def get_xylabels(self, space):
        P = space.P
        return '', '%s' % P

    @contract(returns='seq[4]')
    def axis_for_sequence(self, space, seq):
        self.check_plot_space(space)

        R = Rcomp()
        tu = get_types_universe()
        P_TO_S, _ = tu.get_embedding(space.P, R)

        maxx, maxy = 1000.0, 1000.0
        def limit(p):
            x, y = p
            x = min(x, maxx)
            y = min(y, maxy)
            return x, y

        points2d = [[(limit(P_TO_S(_))) for _ in s.minimals] for s in seq]

        axes = [get_bounds(_) for _ in points2d]
        return enlarge(functools.reduce(reduce_bounds, axes), 0.1)

    def toR2(self, p):
        return self._get_screen_coords(p, self.axis)

    def _get_screen_coords(self, p, axis=None):
        x, y = p

        if axis is not None:
            dy = (axis[3] - axis[2]) * extra_space_top
            dx = (axis[1] - axis[0]) * extra_space_top
            top_x = axis[1] + dx
            top_y = axis[3] + dy

        if isinstance(x, (float, int)):
            x = min(axis[1], x)
        else:  # top
            x = top_x
        if isinstance(y, (float, int)):
            y = min(axis[3], y)
        else:  # top
            y = top_y

        p2 = x, y

#         print('p: %s -> %s' % (p, p2))
        return p2

    def plot(self, pylab, axis, space, value, params={}):
        params0 = dict(color_shadow=[1.0, 0.8, 0.8], markers='k.',
                       markers_params={})
        params0.update(params)

        color_shadow = params0.pop('color_shadow')
        markers = params0.pop('markers')
        marker_params = params0.pop('marker_params')
        if params0: 
            raise ValueError(params0)
        
        self.axis = axis
        self.check_plot_space(space)

        minimals = [self._get_screen_coords(_, axis) for _ in value.minimals]

        v = space.P.Us(minimals)

        plot_upset_R2(pylab, v, axis, extra_space_shadow=extra_space_finite,
                      color_shadow=color_shadow, markers=markers,
                      marker_params=marker_params)

class Plotter_Tuple2_UR2(Plotter):
    """ Plots a tuple of ur2 as min/max bounds """
    def __init__(self):
        self.p = PlotterUR2()

    def check_plot_space(self, space):
        tu = get_types_universe()
        if not (isinstance(space, PosetProduct) and len(space.subs) == 2):
            msg = 'I can only plot 2-tuples of upper sets.'
            raise_desc(NotPlottable, msg, space=space)

        tu.check_equal(space[0], space[1])

        try:
            self.p.check_plot_space(space[0])
        except NotPlottable as e:
            msg = 'It is a 2-tuple, but cannot plot inside. '
            raise_wrapped(NotPlottable, e, msg, compact=True)

    def axis_for_sequence(self, space, seq):
        s = []
        for a, b in seq:
            s.append(a)
            s.append(b)
        P = space.subs[0]
        return self.p.axis_for_sequence(P, s)
    
    def plot(self, pylab, axis, space, value, params={}):  # @UnusedVariable
        v1, v2 = value
        default_params = dict(color_shadow_L='#FFC35C',  # [1.0, 0.8, 0.8],
                              color_shadow_U='#C390D4', #[0.8, 0.8, 1.0])
                              )
        default_params.update(params)
        params1 = dict(color_shadow=default_params['color_shadow_L'], markers='k.')
        params2 = dict(color_shadow=default_params['color_shadow_U'], markers='k.')
        P = space.subs[0]
        self.p.plot(pylab, axis, P, v1, params1)
        self.p.plot(pylab, axis, P, v2, params2)

class PlotterUR2(Plotter):

    def check_plot_space(self, space):
        tu = get_types_universe()
        if not isinstance(space, UpperSets):
            msg = 'I can only plot upper sets.'
            raise_desc(NotPlottable, msg, space=space)

        R2 = PosetProduct((Rcomp(), Rcomp()))
        P = space.P
        try:
            tu.check_leq(P, R2)
        except NotLeq as e:
            msg = ('cannot convert to R^2 from %s' % space)
            raise_wrapped(NotPlottable, e, msg)

        _f1, _f2 = tu.get_embedding(P, R2)

    def get_xylabels(self, space):
        P = space.P
        return '%s' % P[0], '%s' % P[1]

    @contract(returns='seq[4]')
    def axis_for_sequence(self, space, seq):
        self.check_plot_space(space)

        R2 = PosetProduct((Rcomp(), Rcomp()))
        tu = get_types_universe()
        P_TO_S, _ = tu.get_embedding(space.P, R2)

        maxx, maxy = 1000.0, 1000.0
        def limit(p):
            x, y = p
            x = min(x, maxx)
            y = min(y, maxy)
            return x, y

        points2d = [[(limit(P_TO_S(_))) for _ in s.minimals] for s in seq]

        axes = [get_bounds(_) for _ in points2d]
        return enlarge(functools.reduce(reduce_bounds, axes), 0.1)

    def toR2(self, p):
        return self._get_screen_coords(p, self.axis)

    def _get_screen_coords(self, p, axis=None):
        x, y = p

        if axis is not None:
            dy = (axis[3] - axis[2]) * extra_space_top
            dx = (axis[1] - axis[0]) * extra_space_top
            top_x = axis[1] + dx
            top_y = axis[3] + dy

        if isinstance(x, (float, int)):
            x = min(axis[1], x)
        else:  # top
            x = top_x
        if isinstance(y, (float, int)):
            y = min(axis[3], y)
        else:  # top
            y = top_y

        p2 = x, y

#         print('p: %s -> %s' % (p, p2))
        return p2

    def plot(self, pylab, axis, space, value, params={}):
        params0 = dict(color_shadow=[1.0, 0.8, 0.8], markers='k.',
                       markers_params={}) 
        params0.update(params)

        color_shadow = params0.pop('color_shadow')
        markers = params0.pop('markers')
        markers_params = params0.pop('markers_params')
        if params0:
            msg = 'Extra parameters given.'
            raise_desc(ValueError, msg, params0=params0)

        self.axis = axis
        self.check_plot_space(space)

        minimals = [self._get_screen_coords(_, axis) for _ in value.minimals]

        minimals = poset_minima(minimals, space.P.leq)
        v = space.P.Us(minimals)

        plot_upset_R2(pylab, v, axis, extra_space_shadow=extra_space_finite,
                      color_shadow=color_shadow, markers=markers,
                      marker_params=markers_params)


# Upsets((R[s]×R[s])×R[s])
class PlotterURRpR(Plotter):
    def __init__(self):
        R = Rcomp()
        self.S = PosetProduct((PosetProduct((R, R)), R))

    @abstractmethod
    def toR2(self, z):
        pass

    def check_plot_space(self, space):
        tu = get_types_universe()
        if not isinstance(space, UpperSets):
            msg = 'I can only plot upper sets.'
            raise_desc(NotPlottable, msg, space=space)

        P = space.P
        try:
            tu.check_leq(P, self.S)
        except NotLeq as e:
            msg = ('cannot convert to %s from %s' % (P, self.S))
            raise_wrapped(NotPlottable, e, msg)

        _f1, _f2 = tu.get_embedding(P, self.S)

    @contract(returns='seq[4]')
    def axis_for_sequence(self, space, seq):
        self.check_plot_space(space)

        tu = get_types_universe()
        P_TO_S, _ = tu.get_embedding(space.P, self.S)

        points2d = [[self.toR2(P_TO_S(_)) for _ in s.minimals] for s in seq]
        axes = [get_bounds(_) for _ in points2d]
        return enlarge(functools.reduce(reduce_bounds, axes), 0.1)


    def plot(self, pylab, axis, space, value, params={}):
        params0 = dict(color_shadow=[1.0, 0.8, 0.8], markers='k.',
                       markers_params={})
        params0.update(params)
        color_shadow = params0['color_shadow']
        markers = params0['markers']
        markers_params = params0['markers_params']
        
        self.check_plot_space(space)
        tu = get_types_universe()
        P_TO_S, _ = tu.get_embedding(space.P, self.S)

        points2d = [self.toR2(P_TO_S(_)) for _ in value.minimals]

        R2 = PosetProduct((Rcomp(), Rcomp()))


        class MyUpperSet(UpperSet):

            def __init__(self, minimals, P):
                self.minimals = frozenset(minimals)
                self.P = P


        v = MyUpperSet(points2d, P=R2)
        plot_upset_R2(pylab, v, axis,
                      color_shadow=color_shadow, markers=markers,
                      marker_params=markers_params)
        # for p in points2d:
        #    pylab.plot(p[0], p[1], 'rx')

class PlotterURRpR_12(PlotterURRpR):

    def toR2(self, z):
        (a, b), _ = z
        return (a, b)

class PlotterURRpR_13(PlotterURRpR):

    def toR2(self, z):
        (a, _), c = z
        return (a, c)

class PlotterURRpR_23(PlotterURRpR):

    def toR2(self, z):
        (_, b), c = z
        return (b, c)


def enlarge_x(b, f):
    w = b[1] - b[0]
    # h = b[3] - b[2]
    dw = f * w
    dh = 0
    return (b[0] - dw, b[1] + dw, b[2] - dh, b[3] + dh)

def enlarge_y(b, f):
    # w = b[1] - b[0]
    h = b[3] - b[2]
    dw = 0
    dh = h * f
    return (b[0] - dw, b[1] + dw, b[2] - dh, b[3] + dh)

@contract(b='seq[4](float|int)', f='float,>=0')
def enlarge(b, f):
    w = b[1] - b[0]
    h = b[3] - b[2]
    # print b, f, w, h
    dw = fix_underflow(f) * fix_underflow(w)
    dh = fix_underflow(h) * fix_underflow(f)

    a = (b[0] - dw, b[1] + dw, b[2] - dh, b[3] + dh)
    return tuple(map(fix_underflow, a))


def fix_underflow(x):
    # using finfo.tiny gives problems to matplotlib
    return np.maximum(x, finfo.eps)


def enlarge_topright(b, f):
    w = b[1] - b[0]
    h = b[3] - b[2]
    dw = f * w
    dh = h * f
    return (b[0], b[1] + dw, b[2], b[3] + dh)

def reduce_bounds(b1, b2):
    return (min(b1[0], b2[0]),
            max(b1[1], b2[1]),
            min(b1[2], b2[2]),
            max(b1[3], b2[3]))

def get_bounds(points):
    if not points:
        return (0, 0, 0, 0)
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return (min_comp(xs, 0.0),
            max_comp(xs, 0.0),
            min_comp(ys, 0.0),
            max_comp(ys, 0.0))

def _get_finite(xs):
    return  [_ for _ in xs if isinstance(_, (int, float))]

def max_comp(xs, d):
    xs = _get_finite(xs)
    if not xs:
        return d
    return max(xs)

def min_comp(xs, d):
    xs = _get_finite(xs)
    if not xs:
        return d
    return min(xs)

plotters = {
       'UR2': PlotterUR2(),
        'Tuple2_UR2': Plotter_Tuple2_UR2(),
       'URRpR_12': PlotterURRpR_12(),
       'URRpR_13': PlotterURRpR_13(),
       'URRpR_23': PlotterURRpR_23(),
}
