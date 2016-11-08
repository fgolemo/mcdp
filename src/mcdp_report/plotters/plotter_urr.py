# -*- coding: utf-8 -*-
from abc import abstractmethod
import functools

from contracts import contract
from contracts.utils import raise_desc, raise_wrapped
from mcdp_posets import (NotLeq, PosetProduct, Rcomp, UpperSets,
    get_types_universe)
from mcdp_posets.uppersets import UpperSet
from mcdp_report.axis_algebra import get_bounds, reduce_bounds, enlarge
from mcdp_report.drawing import plot_upset_R2

from .interface import Plotter, NotPlottable


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
        
        if isinstance(P, PosetProduct) and len(P) == 2 and \
            isinstance(P[0], PosetProduct) and len(P[0]) == 2:
            self.P_to_S = lambda x: x
        else:
            try:
                tu.check_leq(P, self.S)
            except NotLeq as e:
                msg = ('cannot convert from %s to %s' % (P, self.S))
                raise_wrapped(NotPlottable, e, msg, compact=True)
    
            self.P_to_S, _f2 = tu.get_embedding(P, self.S)

    @contract(returns='seq[4]')
    def axis_for_sequence(self, space, seq):
        self.check_plot_space(space)

        points2d = [[self.toR2(self.P_to_S(_)) for _ in s.minimals] for s in seq]
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
#         tu = get_types_universe()
#         P_TO_S, _ = tu.get_embedding(space.P, self.S)

        points2d = [self.toR2(self.P_to_S(_)) for _ in value.minimals]

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