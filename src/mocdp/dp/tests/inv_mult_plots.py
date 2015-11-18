# -*- coding: utf-8 -*-
from comptests.registrar import comptest_dynamic, comptest
from mocdp.dp.solver import generic_solve
from mocdp.dp_report.generic_report_utils import generic_report
from mocdp.drawing import plot_upset_R2
from mocdp.lang.syntax import parse_ndp
from mocdp.posets import UpperSets
from reprep import Report

import numpy as np
from nose.tools import assert_equal
from mocdp.posets.space import Map, NotEqual
from mocdp.posets.nat import Nat
from mocdp.lang.tests.utils import assert_semantic_error
from mocdp.dp.dp_generic_unary import WrapAMap
from mocdp.posets.poset_product import PosetProduct
import itertools
from mocdp.dp.dp_parallel_simplification import make_parallel
from mocdp.dp.dp_mult_inv import InvPlus2Nat
from mocdp.lang.eval_math import PlusNat
from mocdp.dp.dp_sum import SumNNat
from mocdp.dp.dp_series_simplification import wrap_series
from mocdp.dp.dp_loop import make_loop
from mocdp.dp.dp_flatten import Mux
from mocdp.dp.tracer import Tracer


# @comptest_dynamic
def check_invmult(context):
    ndp = parse_ndp("""
    mcdp {
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
    mcdp {
    
        sub multinv = instance abstract mcdp {
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
mcdp {

    sub multinv = instance abstract mcdp {
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

#     F = dp.get_fun_space()
#     R = dp.get_res_space()
#     UR = UpperSets(R)
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
        minx, maxx, _, _ = axis
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



@comptest
def check_loop_result1():

    ndp = parse_ndp("""
mcdp {
    s = instance mcdp {
      requires x [Nat]
      requires y [Nat]
      provides c [Nat]

         x + y >= c
    }
    
  requires x, y for s
  provides c using s

}"""
    )

    dp = ndp.get_dp()

    f = 2
    res = dp.solve(f)
    expected = set([(0, 2), (1, 1), (2, 0)])
    assert_equal(expected, res.minimals)


@comptest
def check_loop_result2():

    ndp = parse_ndp("""
mcdp {
    s = instance mcdp {
      requires x [Nat]
      requires y [Nat]
      provides c [Nat]

         x + y >= c
    }
    
    requires x for s
    provides c using s
    
    requires y2 >= s.y * nat:2
    
}"""
    )

    dp = ndp.get_dp()

    f = 2
    res = dp.solve(f)
    expected = set([(0, 4), (1, 2), (2, 0)])
    assert_equal(expected, res.minimals)


class CounterMap(Map):
    """ This is:
    
        f(x) = {  x + 1  for x <= n-1
                  n      for x >= n
    """
    def __init__(self, n):
        self.n = n
        Map.__init__(self, Nat(), Nat())
    def _call(self, x):
        if self.dom.leq(x, self.n - 1):
            return x + 1
        return self.n
    def __repr__(self):
        return 'CounterMap(%r)' % self.n

class CounterDP(WrapAMap):
    def __init__(self, n):
        WrapAMap.__init__(self, CounterMap(n))

@comptest
def check_loop_result3():
    assert_semantic_error("""
mcdp {
    s = instance dp {
        requires x [Nat]
        provides c [Nat]

        # semantic error: does not exist
        implemented-by code mocdp.dp.tests.inv_mult_plots.CounterMap___(n=3)
    }
   
}"""
    )

    assert_semantic_error("""
mcdp {
    s = instance dp {
        requires x [Nat]
        provides c [Nat]

        # semantic error: not a DP
        implemented-by code mocdp.dp.tests.inv_mult_plots.CounterMap(n=3)
    }
   
}"""
    )
    
    ndp = parse_ndp("""
mcdp {
    adp1 = dp {
        requires x [Nat]
        provides c [Nat]

        implemented-by code mocdp.dp.tests.inv_mult_plots.CounterDP(n=3)
    }

    s = instance adp1 
    
    s.c >= s.x
   
}"""
    )
    
#     UNat = UpperSets(Nat())

    dp = ndp.get_dp()
    print dp
    res = dp.solve(())
    print res.__repr__()
    One = PosetProduct(())
    U1 = UpperSets(One)
    U1.check_equal(res, One.U(()))

    ndp = parse_ndp("""
mcdp {
    adp1 = dp {
        requires x [Nat]
        provides c [Nat]

        implemented-by code mocdp.dp.tests.inv_mult_plots.CounterDP(n=3)
    }
    
    adp2 = dp {
        requires x [Nat]
        provides c [Nat]

        implemented-by code mocdp.dp.tests.inv_mult_plots.CounterDP(n=2)
    }

    s = instance adp1 ^ adp2
    
    s.c >= s.x
   
    requires x for s
}"""
    )
    N = Nat()
    UNat = UpperSets(N)
    dp = ndp.get_dp()
    print dp
    res = dp.solve(())
    print res
    UNat.check_equal(res, N.U(2))

@comptest
def check_loop_result4():
    # Exploration of 2 technologies,
    # with two resources: money and time

    ndp = parse_ndp("""
mcdp {
    adp1 = dp {
        requires x [Nat]
        provides c [Nat]

        implemented-by code mocdp.dp.tests.inv_mult_plots.CounterDP(n=3)
    }
    
    adp2 = dp {
        requires x [Nat]
        provides c [Nat]

        implemented-by code mocdp.dp.tests.inv_mult_plots.CounterDP(n=2)
    }
    
    t1 = mcdp {
        # solution of this = (0,6)
        requires money [Nat]
        requires time  [Nat]
        w = instance adp1
        w.c >= w.x
        money >= nat:0 * w.x
        time  >= nat:2 * w.x 
    }

    t2 = mcdp {
        # solution of this = (2,0)
        requires money [Nat]
        requires time  [Nat]
        w = instance adp2
        w.c >= w.x
        money >= nat:1 * w.x
        time  >= nat:0 * w.x 
    }

    s = instance t1 ^ t2
    
    requires money, time for s
}"""
    )
    dp = ndp.get_dp()
    print dp
    res = dp.solve(())
    print res

    R = dp.get_res_space()
    UR = UpperSets(R)
    UR.check_equal(res, R.Us([(2, 0), (0, 6)]))
#     UNat.check_equal(res, N.U(2))
    print('***')
    print('Now using the generic solver')
    trace = generic_solve(dp, f=(), max_steps=None)


@comptest
def check_loop_result4b():
    # Exploration of 2 technologies,
    # with two resources: money and time

    ndp = parse_ndp("""
mcdp {
    adp1 = dp {
        requires x [Nat]
        provides c [Nat]

        implemented-by code mocdp.dp.tests.inv_mult_plots.CounterDP(n=3)
    }
    
    adp2 = dp {
        requires x [Nat]
        provides c [Nat]

        implemented-by code mocdp.dp.tests.inv_mult_plots.CounterDP(n=2)
    }
    
    t1 = mcdp {
        # solution of this = (0,6)
        requires money [Nat]
        requires time  [Nat]
        w = instance adp1
        
        provides c using w
        requires x for w
        
        money >= nat:0 * w.x
        time  >= nat:2 * w.x 
    }

    t2 = mcdp {
        # solution of this = (2,0)
        requires money [Nat]
        requires time  [Nat]
        w = instance adp2
        
        provides c using w
        requires x for w
        
        money >= nat:1 * w.x
        time  >= nat:0 * w.x 
    }

    s = instance t1 ^ t2
    
    s.c >= s.x
    
    requires money, time for s
}"""
    )
    dp = ndp.get_dp()
    print dp
    res = dp.solve(())
    print res

    R = dp.get_res_space()
    UR = UpperSets(R)
    expected = R.Us([(2, 0), (0, 6)])
    UR.check_equal(res, expected)
#     UNat.check_equal(res, N.U(2))
    print('***')
    print('Now using the generic solver')
    trace = generic_solve(dp, f=(), max_steps=None)
    res2 = trace.get_r_sequence()[-1]
    print res2
    UR.check_equal(res2, expected)

@comptest
def check_loop_result5a():

    mx = 10
    my = 10
    gridx = np.array(range(mx + 1))
    gridy = np.array(range(my + 1))
    points = set(itertools.product(gridx, gridy))

    def feasible(x, y):
        isqrt = lambda _: np.ceil(np.sqrt(_))
        return x + y >= isqrt(x) + isqrt(y) + 4

    pf = [p for p in points if feasible(p[0], p[1])]
    pu = [p for p in points if not feasible(p[0], p[1])]

    r = Report()
    f = r.figure()
    with f.plot('real') as pylab:
        for x, y in pf:
            pylab.plot(x, y, 'go')
        for x, y in pu:
            pylab.plot(x, y, 'rs')
        pylab.axis((-0.5, mx + 0.5, -0.5, my + 0.5))
    fn = 'a.html'
    r.to_html(fn)
    print('written to %s' % fn)


    ndp = parse_ndp("""
mcdp {
    f = instance mcdp {
        requires x [Nat]
        requires y [Nat]
        provides z [Nat]
        x + y >= z
    }
    
    requires x, y for f
    #provides v [Nat]
    
    f.z >= sqrt(f.x) + sqrt(f.y) + nat:4
    
}"""
    )
    dp = ndp.get_dp()
    R = dp.get_res_space()
    UR = UpperSets(R)
    print dp
    print dp.repr_long()
    f0 = ()
    res1 = dp.solve(f0)
    print('res1: %s' % res1)


    trace = generic_solve(dp, f=f0, max_steps=None)
    res2 = trace.get_r_sequence()[-1]
    print('res2: %s' % res2)

    solution = R.Us([(0, 7), (3, 6), (4, 4), (6, 3), (7, 0)])
    UR.check_equal(res1, solution)
    UR.check_equal(res2, solution)


def get_simple_equiv():
    class RoundSqrt(Map):
        def __init__(self):
            Map.__init__(self, Nat(), Nat())

        def _call(self, x):
            return int(np.ceil(np.sqrt(1.0 * x)))

    One = PosetProduct(())
    F = PosetProduct((One, PosetProduct((Nat(), Nat()))))
    s0 = Mux(F, 1)
    s1 = make_parallel(WrapAMap(RoundSqrt()), WrapAMap(RoundSqrt()))
    s2 = SumNNat((Nat(), Nat()), Nat())
    s3 = WrapAMap(PlusNat(4))
    s4 = InvPlus2Nat(Nat(), (Nat(), Nat()))
    print s0
    print s1
    dp0 = wrap_series(s1.get_fun_space(), [s0, s1, s2, s3, s4])
    dp = make_loop(dp0)
    return dp0, dp

@comptest
def check_loop_result5c():

    dp0, dp = get_simple_equiv()
    print dp.repr_long()

    res = dp.solve(())
    print res


    R = dp0.get_res_space()
    UR = UpperSets(R)
    print('R: %s' % R)
    print('UR: %s' % UR)

    def check_dp0(f0, expected):
        expected = list(expected)
        res0 = dp0.solve(((), f0))
        print res0
        UR.check_equal(res0, R.Us(expected))

    def check_minimal(f0):
        """ The point is one of the minimal points
        
            f0 \in h(-, f0)
        """
        res0 = dp0.solve(((), f0))
        minimals = list(res0.minimals)
        print('check_minimal f0: %s  minimals: %s' % (f0, UR.format(res0)))
        assert f0 in minimals

    def check_feasible(f0):
        """ The point is feasible
        
            ^f0 \subset ^h(-, f0)
        """
        res0 = dp0.solve(((), f0))
        # minimals = list(res0.minimals)
        print('check_feasible')
        print(' f0: %s ' % str(f0))
        print(' minimals: %s' %  UR.format(res0))

        Uf0 = R.U(f0)
        UR.check_leq(res0, Uf0)


    def get_tradeoff(s):
        for i in range(s + 1):
            yield (i, s - i)

    check_dp0(f0=(0, 0), expected=get_tradeoff(4))
    check_dp0(f0=(0, 4), expected=get_tradeoff(6))
    check_dp0(f0=(0, 6), expected=get_tradeoff(7))

    solutions = [(0, 7), (3, 6), (4, 4), (6, 3), (7, 0)]
    for s in solutions:
        check_minimal(f0=s)

    check_feasible((1, 7))
    check_feasible((10, 10))

    trace = Tracer()
    res = dp.solve_trace((), trace)
    print trace.format()
    converged = list(trace.get_iteration_values('converged'))

    print converged
#     for i, r in enumerate(result):
#         print('%d: %s' % (i, UR.format(r.s)))
#         print('converged: %s' % str(r.converged))

    expected = [
        [(0, 0)],
        list(get_tradeoff(4)),
        list(get_tradeoff(6)),  # FIXME
        list(get_tradeoff(7)),
        [(0, 7), (2, 6), (3, 5), (4, 4), (5, 3), (6, 2), (7, 0)],
        [(0, 7), (3, 6), (4, 4), (6, 3), (7, 0)],
        [(0, 7), (3, 6), (4, 4), (6, 3), (7, 0)],
    ]
    sip = list(trace.get_iteration_values('sip'))
    for i, found in enumerate(sip):
        want = R.Us(expected[i])
        print('step: %d' % i)
        print('want:  %s' % UR.format(want))
        print('found: %s' % UR.format(found))
        try:
            UR.check_equal(found, R.Us(expected[i]))
        except NotEqual as e:
            print e

@comptest
def check_loop_result5():
    dp0, dp = get_simple_equiv()
    print dp.repr_long()

    dp0, dp = get_simple_equiv()

    R = dp0.get_res_space()

    S, alpha, beta = dp.get_normal_form()
    One = PosetProduct(())
    uf = One.U(())
    s0 = S.get_bottom()
    ss = [s0]
    for i in range(4):
        snext = beta((uf, ss[-1]))
        ss.append(snext)
        print('S[%d]: %s' % (i + 1, S.format(snext)))
    print('S: %s' % S)
    print('α: %s' % alpha)
    print('β: %s' % beta)

