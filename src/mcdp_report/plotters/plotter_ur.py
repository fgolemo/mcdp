# -*- coding: utf-8 -*-
from contracts import contract
from contracts.utils import raise_desc, raise_wrapped
from mcdp_posets import (NotLeq, Rcomp, UpperSets,
    get_types_universe)
from mcdp_report.axis_algebra import enlarge
from mcdp_report.drawing import plot_upset_R2
from mcdp_report.plotters.interface import Plotter, NotPlottable
from mocdp import logger
from mocdp.exceptions import mcdp_dev_warning


class PlotterUR(Plotter):
    """ XXX this doesn't work """

    def check_plot_space(self, space):
        tu = get_types_universe()
        if not isinstance(space, UpperSets):
            msg = 'I can only plot upper sets of R.'
            raise_desc(NotPlottable, msg, space=space)

        R = Rcomp()
        P = space.P
        try:
            tu.check_leq(P, R)
        except NotLeq as e:
            msg = ('cannot convert to R^2 from %s' % space)
            raise_wrapped(NotPlottable, e, msg, compact=True)

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

        maxy = 1000.0
        def limit(p): # XXX trick for Top?
            y = p
            y = min(y, maxy)
            return y

        ys = [ max([limit(P_TO_S(_)) for _ in s.minimals]) 
              
              for s in seq]
        axes = (-1, 1, 0, max(ys))
        
        return enlarge(axes, 0.1)

    def toR2(self, p):
        return self._get_screen_coords(p, self.axis)

    def _get_screen_coords(self, p, axis=None):
        x, y = 0, p

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

        # print('p: %s -> %s' % (p, p2))
        return p2

    def plot(self, pylab, axis, space, value, params={}):
        params0 = dict(color_shadow=[1.0, 0.8, 0.8], markers='k.',
                       markers_params={})
        params0.update(params)

        color_shadow = params0.pop('color_shadow')
        markers = params0.pop('markers')
        markers_params = params0.pop('markers_params')
        if params0: 
            raise ValueError(params0)
        
        self.axis = axis
        self.check_plot_space(space)

        minimals = [self._get_screen_coords(_, axis) for _ in value.minimals]

        v = space.P.Us(minimals)

        from mcdp_report.generic_report_utils import extra_space_finite

        mcdp_dev_warning('incomplete PlotterUR')
        logger.error('todo: change this to plot a line')
        plot_upset_R2(pylab, v, axis, extra_space_shadow=extra_space_finite,
                      color_shadow=color_shadow, markers=markers,
                      marker_params=markers_params)


