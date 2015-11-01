# -*- coding: utf-8 -*-
from comptests.registrar import comptest_dynamic
from mocdp.drawing import plot_upset_R2
from mocdp.lang.syntax import parse_ndp
from mocdp.posets import UpperSets
from reprep import Report
import numpy as np
from mocdp.dp.solver import generic_solve
from abc import ABCMeta, abstractmethod
from contracts import contract
from mocdp.posets.types_universe import get_types_universe
from mocdp.posets.poset_product import PosetProduct
from mocdp.posets.rcomp import Rcomp
from mocdp.posets.poset import NotLeq
from contracts.utils import raise_wrapped, raise_desc
import itertools
import functools
from mocdp.posets.uppersets import UpperSet


@comptest_dynamic
def check_invmult(context):
    ndp = parse_ndp("""
    cdp {
      requires a [R]
      requires b [R]
      
      provides c [R]
      
      c <= a * b
    }
    """)
    dp = ndp.get_dp()

    r = context.comp(check_invmult_report, dp)
    context.add_report(r, 'check_invmult_report')

def check_invmult_report(dp):
#     from mocdp.dp.dp_loop import SimpleLoop
#     funsp = dp.get_fun_space()

#     assert isinstance(dp, SimpleLoop)

    f = 1.0
    R0, R1 = dp.solve_approx(f=f, nl=15, nu=15)
    UR = UpperSets(dp.get_res_space())

    UR.belongs(R0)
    UR.belongs(R1)
    UR.check_leq(R0, R1)
    # Payload2ET

    r = Report()
    caption = 'Two curves for each payload'
    with r.plot('p1', caption=caption) as pylab:
#        plot_upset_minima(pylab, R0)

        mx = max(x for (x, _) in R1.minimals)
        my = max(y for (_, y) in R1.minimals)
        axis = (0, mx * 1.1, 0, my * 1.1)

        plot_upset_R2(pylab, R0, axis, color_shadow=[1.0, 0.8, 0.8])
        plot_upset_R2(pylab, R1, axis, color_shadow=[0.8, 1.0, 0.8])


        xs = np.exp(np.linspace(-10, +10, 50))
        ys = f / xs
        pylab.plot(xs, ys, 'r-')

        pylab.xlabel('time')
        pylab.ylabel('energy')

        pylab.axis(axis) 

    return r


@comptest_dynamic
def check_invmult2(context):
    r = context.comp(check_invmult2_report)
    context.add_report(r, 'check_invmult2_report')

def check_invmult2_report():

    ndp = parse_ndp("""
    cdp {
    
        sub multinv = abstract cdp {
            requires x [R]
            requires y [R]
            
            provides c [R]
    
            c <= x * y
        }
    
        multinv.c >= max( square(multinv.x), 1.0 [R])
    
        requires y for multinv
    }
"""
    )
     
    dp = ndp.get_dp()


    r = Report()

    F = dp.get_fun_space()
    UR = UpperSets(dp.get_res_space())
    f = F.U(())

    print('solving straight:')
    rmin = dp.solve(())
    print('Rmin: %s' % UR.format(rmin))
    S, alpha, beta = dp.get_normal_form()

    s0 = S.get_bottom()

    ss = [s0]
    sr = [alpha((f, s0))]

    nsteps = 5
    for i in range(nsteps):
        s_last = ss[-1]
        print('Computing step')
        s_next = beta((f, s_last))

        if S.equal(ss[-1], s_next):
            print('%d: breaking because converged' % i)
            break

        rn = alpha((f, s_next))
        print('%d: rn  = %s' % (i, UR.format(rn)))
        
        ss.append(s_next)
        sr.append(rn)


    print('plotting')
    mx = 3.0
    my = 3.0
    axis = (0, mx * 1.1, 0, my * 1.1)

    fig = r.figure(cols=2)
    for i, s in enumerate(ss):

        with fig.plot('S%d' % i) as pylab:
            plot_upset_R2(pylab, s, axis, color_shadow=[1.0, 0.8, 0.8])

            xs = np.linspace(0.001, 1, 100)
            ys = 1 / xs
            pylab.plot(xs, ys, 'k-')

            xs = np.linspace(1, mx, 100)
            ys = xs
            pylab.plot(xs, ys, 'k-')

            pylab.axis(axis)

        with fig.plot('R%d' % i) as pylab:
            Rmin = sr[i]
            y = np.array(list(Rmin.minimals))
            x = y * 0
            pylab.plot(x, y, 'k.')
            pylab.axis((-mx / 10, mx / 10, 0, my))

    return r


@comptest_dynamic
def check_invmult3(context):
    r = context.comp(check_invmult3_report)
    context.add_report(r, 'check_invmult3_report')

def check_invmult3_report():

    ndp = parse_ndp("""
cdp {

    sub multinv = abstract cdp {
  requires x [R]
  requires y [R]

  provides c [R]

    c <= x * y
  }

   multinv.c >= max( square(multinv.x), 1.0 [R])

  requires x for multinv
  requires y for multinv

}"""
    )

    dp = ndp.get_dp()


    r = Report()

    F = dp.get_fun_space()
    R = dp.get_res_space()
    UR = UpperSets(R)
    f = ()  # F.U(())

    r.text('dp', dp.tree_long())
    print('solving straight:')
#     rmin = dp.solve(())
#     print('Rmin: %s' % UR.format(rmin))

    trace = generic_solve(dp, f=f, max_steps=None)


#
#     fig0 = r.figure(cols=2)
#     caption = 'Solution using solve()'
#     with fig0.plot('S0', caption=caption) as pylab:
#         plot_upset_R2(pylab, rmin, axis, color_shadow=[1.0, 0.8, 0.9])
#         pylab.axis(axis)

    def annotation(pylab, axis):
        minx, maxx, miny, maxy = axis
        xs = np.linspace(minx, 1, 100)
        xs = np.array([x for x in xs if  x != 0])
        ys = 1 / xs
        pylab.plot(xs, ys, 'k-')

        xs = np.linspace(1, maxx, 100)
        ys = xs
        pylab.plot(xs, ys, 'k--')

    # make sure it includes (0,0) and (2, 0)
    axis0 = (0, 2, 0, 0)

    generic_report(r, dp, trace, annotation=annotation, axis0=axis0)

    return r

def generic_report(r, dp, trace, annotation=None, axis0=(0, 0, 0, 0)):
    plotters = { 'UR2': PlotterUR2(),
                    'URRpR_12': PlotterURRpR_12(),
                    'URRpR_13': PlotterURRpR_13(),
                    'URRpR_23': PlotterURRpR_23(),
                    }
    # F = dp.get_fun_space()
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


def generic_try_plotters(r, plotters, space, sequence, axis0=None, annotation=None):
    nplots = 0
    for name, plotter in plotters.items():
        try:
            plotter.check_plot_space(space)
        except NotPlottable as e:
            # print('Plotter %r cannot plot %r:\n%s' % (name, space, e))
            continue
        nplots += 1
        
        f = r.figure(name, cols=5)
        generic_plot_sequence(f, plotter, space, sequence, axis0=axis0, annotation=annotation)

    if not nplots:
        r.text('error', 'No plotters for %s' % space)
        

def join_axes(a, b):
    return (min(a[0], b[0]),
            max(a[1], b[1]),
            min(a[2], b[2]),
            max(a[3], b[3]))

def generic_plot_sequence(r, plotter, space, sequence, axis0=None, annotation=None):

    axis = plotter.axis_for_sequence(space, sequence)

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
            if xlabel:
                pylab.xlabel(xlabel)
            if ylabel:
                pylab.ylabel(ylabel)

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
    def plot(self, pylab, axis, space, value):
        pass

    def get_xylabels(self, space):
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

        points2d = [[(P_TO_S(_)) for _ in s.minimals] for s in seq]
        axes = [get_bounds(_) for _ in points2d]
        return enlarge(functools.reduce(reduce_bounds, axes), 0.1)

#
#
#         for s in seq:
#             points = map(P_TO_R2, s.minimals)
#         if len(points) == 0:
#             return (0, 1, 0, 1)
#         xs = [p[0] for p in points]
#         ys = [p[1] for p in points]
#         return (min(xs), max(xs), min(ys), max(ys))

    def plot(self, pylab, axis, space, value):
        self.check_plot_space(space)

        v = value
        plot_upset_R2(pylab, v, axis, color_shadow=[1.0, 0.8, 0.8])


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


    def plot(self, pylab, axis, space, value):
        self.check_plot_space(space)
        tu = get_types_universe()
        P_TO_S, _ = tu.get_embedding(space.P, self.S)

#         y =-x+sqrt(x)+10,
        # y>=-2x+ 2sqrt(x)+20.
        xs = np.linspace(0, 20, 100)
        ys = -2 * (xs - np.sqrt(xs) - 10)
        pylab.plot(xs, ys, '--')

        points2d = [self.toR2(P_TO_S(_)) for _ in value.minimals]

        R2 = PosetProduct((Rcomp(), Rcomp()))


        class MyUpperSet(UpperSet):

            def __init__(self, minimals, P):
                self.minimals = frozenset(minimals)
                self.P = P


        v = MyUpperSet(points2d, P=R2)
        plot_upset_R2(pylab, v, axis, color_shadow=[1.0, 0.8, 0.8])
        for p in points2d:
            pylab.plot(p[0], p[1], 'rx')

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

 

def enlarge(b, f):
    w = b[1] - b[0]
    h = b[3] - b[2]
    dw = f * w
    dh = h * f
    return (b[0] - dw, b[1] + dw, b[2] - dh, b[3] + dh)

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
    return (min(xs), max(xs), min(ys), max(ys))




