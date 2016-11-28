# -*- coding: utf-8 -*-
import functools

from contracts import contract
from contracts.utils import raise_desc, raise_wrapped
from mcdp_posets import (NotLeq, PosetProduct, Rcomp, UpperSets,
    get_types_universe)
from mcdp_posets.find_poset_minima.baseline_n2 import poset_minima
from mcdp_posets.rcomp_units import RcompUnits
from mcdp_report.axis_algebra import get_bounds, reduce_bounds
from mcdp_report.drawing import plot_upset_R2

from .interface import Plotter, NotPlottable


class PlotterUR2(Plotter):

    def check_plot_space(self, space):
        tu = get_types_universe()
        if not isinstance(space, UpperSets):
            msg = 'I can only plot upper sets of something isomorphic to R2.'
            raise_desc(NotPlottable, msg, space=space)
        P = space.P
        self.R2 = PosetProduct((Rcomp(), Rcomp()))

        if isinstance(space.P, PosetProduct) and len(space.P) == 2 and \
            isinstance(space.P[0], RcompUnits) and isinstance(space.P[1], RcompUnits):
            self.P_to_S = lambda x: x            
        else:   
            #logger.debug('space = %s ; P = %s; R2 = %s' % (space,space.P,R2))
            try:
                tu.check_leq(P, self.R2)
            except NotLeq as e:
                msg = ('cannot convert to R^2 from %s' % space) 
                raise_wrapped(NotPlottable, e, msg, compact=True)
    
            self.P_to_S, _f2 = tu.get_embedding(P, self.R2)
            
    def get_xylabels(self, space):
        P = space.P
        return '%s' % P[0], '%s' % P[1]

    @contract(returns='seq[4]')
    def axis_for_sequence(self, space, seq):
        self.check_plot_space(space)
        
        R2 = PosetProduct((Rcomp(), Rcomp()))
        self.R2 = R2
#         tu = get_types_universe()
#         P_TO_S, _ = tu.get_embedding(space.P, R2)

        maxx, maxy = 1000.0, 1000.0
        def limit(p):
            x, y = p
            x = min(x, maxx)
            y = min(y, maxy)
            return x, y

        points2d = [[(limit(self.P_to_S(_))) for _ in s.minimals] for s in seq]

        axes = [get_bounds(_) for _ in points2d]
        merged = functools.reduce(reduce_bounds, axes) 
        return merged

    def toR2(self, p):
        return self._get_screen_coords(p, self.axis)

    def _get_screen_coords(self, p, axis=None):
        x, y = p

        # XXX
        from mcdp_report.generic_report_utils import extra_space_top
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

#         tu = get_types_universe()
#         P_TO_S, _ = tu.get_embedding(space.P, self.R2)

        minimals = [self._get_screen_coords(self.P_to_S(_), axis) for _ in value.minimals]

        minimals = poset_minima(minimals, self.R2.leq)
        v = self.R2.Us(minimals)

        from mcdp_report.generic_report_utils import extra_space_finite
        plot_upset_R2(pylab, v, axis, extra_space_shadow=extra_space_finite,
                      color_shadow=color_shadow, markers=markers,
                      marker_params=markers_params)

