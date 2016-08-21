from matplotlib import pylab
from mcdp_dp.dp_inv_mult import InvMult2
from mcdp_dp.dp_transformations import get_dp_bounds
from mcdp_lang.parse_interface import parse_poset
from mcdp_posets.poset_product import PosetProduct
from mcdp_posets.uppersets import UpperSets
from mcdp_report.generic_report_utils import generic_plot, get_best_plotter
from plot_utils import ieee_fonts_zoom3, ieee_spines_zoom3
from reprep import Report
import numpy as np
from mcdp_dp.dp_inv_plus import InvPlus2

def plot_nominal_invmult(pylab):
    nomimal_x = np.linspace(0.1, 10, 100)
    nomimal_y = 1.0 / nomimal_x
    pylab.plot(nomimal_x, nomimal_y, 'k-')
    axes = pylab.gca()
    axes.xaxis.set_ticklabels([])
    axes.yaxis.set_ticklabels([])

def plot_nominal_invplus(pylab):
    nomimal_x = np.linspace(0, 1.0, 100)
    nomimal_y = 1.0 - nomimal_x
    pylab.plot(nomimal_x, nomimal_y, 'k-')
    axes = pylab.gca()
    axes.xaxis.set_ticklabels([])
    axes.yaxis.set_ticklabels([])

def go1(r, ns, dp, plot_nominal, axis):

    f = r.figure(cols=len(ns))

    for n in ns:
        dpL, dpU = get_dp_bounds(dp, n, n)

        f0 = 1.0
        R = dp.get_res_space()
        UR = UpperSets(R)
        space = PosetProduct((UR, UR))

        urL = dpL.solve(f0)
        urU = dpU.solve(f0)
        value = urL, urU

        plotter = get_best_plotter(space)
        figsize = (4, 4)
        with f.plot('plot_n%d' % n, figsize=figsize) as pylab:
            ieee_spines_zoom3(pylab)
            plotter.plot(pylab, axis, space, value)
            plot_nominal(pylab)
            pylab.axis(axis)

def go():
    ieee_fonts_zoom3(pylab)

    r = Report()
    algos = [InvMult2.ALGO_UNIFORM, InvMult2.ALGO_VAN_DER_CORPUT]
    for algo in algos:
        InvMult2.ALGO = algo
        InvPlus2.ALGO = algo
        print('Using algorithm %s ' % algo)
        with r.subsection(algo) as r2:
            # first
            F = parse_poset('R')
            R = F
            dp = InvMult2(F, (R, R))
            ns = [ 3, 4, 5, 6, 10, 15]

            axis = (0.0, 6.0, 0.0, 6.0)

            with r2.subsection('invmult2') as rr:
                go1(rr, ns, dp, plot_nominal_invmult, axis)

            # second
            axis = (0.0, 1.2, 0.0, 1.2)
            dp = InvPlus2(F, (R, R))
            with r2.subsection('invplus2') as rr:
                go1(rr, ns, dp, plot_nominal_invplus, axis)

    fn = 'out/plot_approximations/report.html'
    print('writing to %s' % fn)
    r.to_html(fn)

if __name__ == '__main__':
    go()
