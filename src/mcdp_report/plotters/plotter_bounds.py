# -*- coding: utf-8 -*-
from contracts.utils import raise_desc, raise_wrapped
from mcdp_posets import (PosetProduct,
    get_types_universe)

from .interface import Plotter, NotPlottable


class Plotter_Tuple2_UR2(Plotter):
    """ Plots a tuple of ur2 as min/max bounds """
    def __init__(self):
        from mcdp_report.plotters.plotter_ur2 import PlotterUR2

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