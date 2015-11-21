# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from cdpview.go import safe_makedirs
from contracts import contract
from contracts.utils import raise_desc, raise_wrapped
from mocdp.drawing import plot_upset_R2
from mocdp.posets.poset import NotLeq
from mocdp.posets.poset_product import PosetProduct
from mocdp.posets.rcomp import Rcomp
from mocdp.posets.types_universe import get_types_universe
from mocdp.posets.uppersets import UpperSet, UpperSets
from reprep.config import RepRepDefaults
import functools
import os

extra_space_finite = 0.025
extra_space_top = 0.05

def generic_report_trace(r, ndp, dp, trace, out):
    r.text('dp', dp.repr_long())
    # r.text('trace', trace.format())
    
    for l, trace_loop in enumerate(trace.find_loops()):
        with r.subsection('loop%d' % l) as r2:
            _report_loop(r2, trace_loop, out)
        
        
def _report_loop(r, trace_loop, out):
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
            print('Decided on axis %s' % str(axis))
            for i, sip in enumerate(sips):
                with f.plot('step%d' % i) as pylab:

                    c_orange = '#FFA500'
                    c_red = [1, 0.5, 0.5]
                    print('bottom')
                    plotter.plot(pylab, axis, UR, R.U(R.get_bottom()),
                                 params=dict(color_shadow=c_red, markers=None))
                    print('sip')
                    plotter.plot(pylab, axis, UR, sip,
                                 params=dict(color_shadow=c_orange))
                    conv = converged[i]
                    c_blue = [0.6, 0.6, 1.0]
                    print('converged')
                    plotter.plot(pylab, axis, UR, R.Us(converged[i]),
                                 params=dict(color_shadow=c_blue))
                    print('minimal')
                    for c in conv:
                        p = plotter.toR2(c)
                        pylab.plot(p[0], p[1], 'go',
                                   markersize=10, markeredgecolor='g')
                    # pylab.axis(enlarge_topright(axis, extra_space_top * 2))
                    pylab.axis(visualized_axis)
#
#                     pylab.gcf().patch.set_facecolor('blue')
#                     pylab.gcf().patch.set_alpha(0.7)

                node = f.resolve_url('step%d/png' % i)

                safe_makedirs(outdir)
                fn = os.path.join(outdir, '%05d.png' % i)
                with open(fn, 'w') as fi:
                    fi.write(node.raw_data)

            outmp4 = os.path.join(out, 'video-%s.mp4' % name)

            try:
                from procgraph_mplayer.scripts.join_video import join_video_29
            except ImportError as e:
                print(e)
            else:
                join_video_29(output=outmp4, dirname=outdir,
                              pattern='.*.png', fps=1.0)
#
#             cmd2 = ['pg-video-join',
#                 '-d', outdir,
#                 '-p', '.*.png',
#                 '--fps', '1',
#                 '-o', outmp4]
#
#             try:
#                 system_cmd_show('.', cmd2)
#                 metadata = outmp4 + '.metadata.yaml'
#                 if os.path.exists(metadata):
#                     os.unlink(metadata)
#             except CmdException as e:
#                 if 'No such file or directory' in str(e):
#                     print('Could not create video - ignoring')
#                     print(indent(str(e), '> '))


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

def get_plotters(plotters, space):
    for name, plotter in plotters.items():
        try:
            plotter.check_plot_space(space)
            yield name, plotter
        except NotPlottable as e:
            pass


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
        color_shadow = params0['color_shadow']
        markers = params0['markers']

        self.axis = axis
        self.check_plot_space(space)

        minimals = [self._get_screen_coords(_, axis) for _ in value.minimals]

        # R2 = PosetProduct((Rcomp(), Rcomp()))
        v = space.P.Us(minimals)
#         print('drawing v= %s' % str(v))
        plot_upset_R2(pylab, v, axis, extra_space_shadow=extra_space_finite,
                      color_shadow=color_shadow)


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

#         y =-x+sqrt(x)+10,
        # y>=-2x+ 2sqrt(x)+20.
#         xs = np.linspace(0, 20, 100)
#         ys = -2 * (xs - np.sqrt(xs) - 10)
#         pylab.plot(xs, ys, '--')

        points2d = [self.toR2(P_TO_S(_)) for _ in value.minimals]

        R2 = PosetProduct((Rcomp(), Rcomp()))


        class MyUpperSet(UpperSet):

            def __init__(self, minimals, P):
                self.minimals = frozenset(minimals)
                self.P = P


        v = MyUpperSet(points2d, P=R2)
        plot_upset_R2(pylab, v, axis,
                      color_shadow=color_shadow, markers=markers)
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
    h = b[3] - b[2]
    dw = f * w
    dh = 0
    return (b[0] - dw, b[1] + dw, b[2] - dh, b[3] + dh)

def enlarge_y(b, f):
    w = b[1] - b[0]
    h = b[3] - b[2]
    dw = 0
    dh = h * f
    return (b[0] - dw, b[1] + dw, b[2] - dh, b[3] + dh)


@contract(b='seq[4](float|int)', f='float,>=0')
def enlarge(b, f):
    w = b[1] - b[0]
    h = b[3] - b[2]
    dw = f * w
    dh = h * f
    return (b[0] - dw, b[1] + dw, b[2] - dh, b[3] + dh)

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
       'URRpR_12': PlotterURRpR_12(),
       'URRpR_13': PlotterURRpR_13(),
       'URRpR_23': PlotterURRpR_23(),
}
