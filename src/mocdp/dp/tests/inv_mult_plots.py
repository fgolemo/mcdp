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
from contracts.utils import raise_wrapped


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
    R0, R1 = dp.solve_approx(f=f, n=15)
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
    UR = UpperSets(dp.get_res_space())
    f = ()  # F.U(())

    r.text('dp', dp.tree_long())
    print('solving straight:')
    rmin = dp.solve(())
    print('Rmin: %s' % UR.format(rmin))

    trace = generic_solve(dp, f=f, max_steps=None)


    print('plotting')
    mx = 3.0
    my = 3.0
    axis = (0, mx * 1.1, 0, my * 1.1)

    fig0 = r.figure(cols=2)
    caption = 'Solution using solve()'
    with fig0.plot('S0', caption=caption) as pylab:
        plot_upset_R2(pylab, rmin, axis, color_shadow=[1.0, 0.8, 0.9])
        pylab.axis(axis)

    P2D = Plotter2D()
    P2D.check_plot_space(trace.S)

    fig = r.figure(cols=2)
    S_sequence = trace.get_s_sequence()
    S_axis = P2D.axis_for_sequence(S_sequence)

    R_sequence = trace.get_r_sequence()
    R_axis = P2D.axis_for_sequence(R_sequence)

    for i, s in enumerate(S_sequence):
        ri = R_sequence[i]

        with fig.plot('S%d' % i, caption=trace.S.format(s)) as pylab:
            plot_upset_R2(pylab, s, axis, color_shadow=[1.0, 0.8, 0.8])

            xs = np.linspace(0.001, 1, 100)
            ys = 1 / xs
            pylab.plot(xs, ys, 'k-')

            xs = np.linspace(1, mx, 100)
            ys = xs
            pylab.plot(xs, ys, 'k-')

            pylab.axis(axis)

        with fig.plot('R%d' % i, caption=UR.format(ri)) as pylab:
            plot_upset_R2(pylab, ri, axis, color_shadow=[0.8, 1.0, 0.8])
            pylab.axis(axis)

    return r

class NotPlottable(Exception):
    pass

class Plotter():
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def check_plot_space(self, space):
        pass
    
    @abstractmethod
    @contract(returns='seq[4]')
    def axis_for_sequence(self, seq):
        pass

    @abstractmethod
    def plot(self, pylab, x):
        pass

class Plotter2D():
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def check_plot_space(self, space):
        tu = get_types_universe()
        if not isinstance(space, UpperSets):
            return False
        
        R2 = PosetProduct((Rcomp(), Rcomp()))
        P = space.P 
        try:
            tu.leq(P, R2)
        except NotLeq as e:
            msg = ('cannot convert to R^2 from %s' % space)
            raise_wrapped(NotPlottable, e, msg)
        
        f1, f2 = tu.get_embedding(P, R2)
    
    @contract(returns='seq[4]')
    def axis_for_sequence(self, space, seq):
        R2 = PosetProduct((Rcomp(), Rcomp()))
        tu = get_types_universe()
        f1, f2 = tu.get_embedding(space.P, R2)

    def plot(self, pylab, axis, space, value):
        v = value
        plot_upset_R2(pylab, v, axis, color_shadow=[1.0, 0.8, 0.8])








