# -*- coding: utf-8 -*-

from contracts import contract
from contracts.utils import raise_wrapped
from mcdp_dp.tracer import Tracer
from mcdp_posets import Nat, NotBelongs, RcompUnits
from mcdp_posets.rcomp import RcompTop
from mcdp_report.gg_ndp import format_unit
import numpy as np


class SolverState(object):

    def __init__(self, ndp):
        self.fun = []
        self.ures = []
        self.ndp = ndp
        dp = self.ndp.get_dp()
        self.dp = dp

    def interpret_point(self, f):
        """
            f: dict(functionality -> value)
            
            This is permissive; for example, ints are converted to floats.
            
        """
        def permissive_parse(F, v):
            if isinstance(F, RcompUnits) and isinstance(v, int):
                v = float(v)

            if isinstance(F, Nat) and isinstance(v, float):
                v = int(v)

            # TODO: parse floats as ints
            return v

        fnames = self.ndp.get_fnames()

        fv = [None] * len(fnames)
        if len(f) != len(fnames):
            raise ValueError("Not valid: %s" % f)

        for k, v in f.items():
            
            k = k.encode('utf8') # XXX do before
            i = fnames.index(k)
            F = self.ndp.get_ftype(k)
            fv[i] = permissive_parse(F, v)
        fv = tuple(fv)
        if len(fv) == 1:
            fv = fv[0]
        return fv

    @contract(fd=dict)
    def new_point(self, fd):
        fv = self.interpret_point(fd)

        F = self.dp.get_fun_space()
        try:
            F.belongs(fv)
        except NotBelongs as e:
            raise_wrapped(ValueError, e, "Point does not belong.", compact=True)
        self.fun.append(fv)

        from mcdp import logger
        trace = Tracer(logger=logger)
        print('solving... %s' % F.format(fv))
        ures = self.dp.solve_trace(fv, trace)

        self.ures.append(ures)

    @contract(fun_index='seq[>=1](int)',
              res_index='seq[>=1](int)')
    def get_data_for_js(self, fun_index, res_index):
        ndp = self.ndp

        res = {}

        decisions = get_decisions_for_axes(ndp, fun_index, res_index)

        res['datasets_fun'] = self.get_datasets_fun(wx=decisions['fun_name_x'], wy=decisions['fun_name_y'])
        res['datasets_res'] = self.get_datasets_res(wx=decisions['res_name_x'], wy=decisions['res_name_y'])

        def fun_label(fn):
            if fn is None:
                return '(unused)'
            return fn + ' ' + format_unit(self.ndp.get_ftype(fn))

        def res_label(rn):
            if rn is None:
                return '(unused)'
            return rn + ' ' + format_unit(self.ndp.get_rtype(rn))

        res['fun_xlabel'] = fun_label(decisions['fun_name_x'])
        res['fun_ylabel'] = fun_label(decisions['fun_name_y'])
        res['res_xlabel'] = res_label(decisions['res_name_x'])
        res['res_ylabel'] = res_label(decisions['res_name_y'])

        return res

    def get_color(self, i):
        colors = ['green', 'blue', 'brown']
        color = colors[ i % len(colors) ]
        n = len(self.fun)
        if i < n - 3:
            color = 'gray'

        infeasible = len(self.ures[i].minimals) == 0
        if infeasible:
            return 'red'
        return color

    def get_datasets_fun(self, wx, wy):
        # one dataset per point in fun
        fnames = self.ndp.get_fnames()
        if wx is not None:
            xi = fnames.index(wx)
        if wy is not None:
            yi = fnames.index(wy)

        def make_tuple(p):
            if len(fnames) == 1:
                return (p,)
            else:
                return p

        def make_point(p):
            p = make_tuple(p)
            res = {}
            if wx is not None:
                res['x'] = make_value(p[xi])
            else:
                res['x'] = 0
            if wy is not None:
                res['y'] = make_value(p[yi])
            else:
                res['y'] = 0
            return res

        datasets = [{'data': [make_point(p)],
                 'backgroundColor': self.get_color(i)} for i, p in enumerate(self.fun)]
        # print datasets
        return datasets

    def get_datasets_res(self, wx, wy):
        # one dataset per point in fun
        rnames = self.ndp.get_rnames()
        if wx is not None:
            xi = rnames.index(wx)
        if wy is not None:
            yi = rnames.index(wy)

        def make_tuple(p):
            if len(rnames) == 1:
                return (p,)
            else:
                return p

        def make_point(p):
            p = make_tuple(p)
            res = {}
            if wx is not None:
                res['x'] = make_value(p[xi])
            else:
                res['x'] = 0
            if wy is not None:
                res['y'] = make_value(p[yi])
            else:
                res['y'] = 0
            return res

        def get_points(ui):
            return [make_point(p) for p in ui.minimals]

        datasets = [{'data': get_points(ui),
                 'backgroundColor': self.get_color(i)} for i, ui in enumerate(self.ures)]
        # print datasets
        return datasets

def make_value(x):
    """ Converts the value to something we can send over json.
        Primarely used for dealing with Top. 
        
    """
    if isinstance(x, RcompTop):
        return np.inf
    else:
        return x


def get_decisions_for_axes(ndp, fun_axes, res_axes):
    fnames = ndp.get_fnames()
    rnames = ndp.get_rnames()
    if len(fun_axes) == 2:
        fun_name_x = fnames[fun_axes[0]]
        fun_name_y = fnames[fun_axes[1]]
    elif len(fun_axes) == 1:
        fun_name_x = None
        fun_name_y = fnames[fun_axes[0]]
    else:
        assert False

    if len(res_axes) == 2:
        res_name_x = rnames[res_axes[0]]
        res_name_y = rnames[res_axes[1]]
    elif len(res_axes) == 1:
        res_name_x = None
        res_name_y = rnames[res_axes[0]]
    else:
        assert False
    return {'fun_name_x': fun_name_x,
            'fun_name_y': fun_name_y,
            'res_name_x': res_name_x,
            'res_name_y': res_name_y, }
