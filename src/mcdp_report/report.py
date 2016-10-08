# -*- coding: utf-8 -*-
import warnings

from contracts import contract
from mcdp_posets import PosetProduct, R_dimensionless
from mocdp.comp.interfaces import NamedDP
from reprep import Report

from .dp_graph_flow_imp import dp_graph_flow
from .gg_ndp import gvgen_from_ndp
from .gg_utils import gg_figure


@contract(ndp=NamedDP)
def report_ndp1(ndp):
    r = Report()

    gg = gvgen_from_ndp(ndp)
    gg_figure(r, 'graph', gg)

    styles = ['greenred', 'clean', 'greenredsym']
    for style in styles:
        with r.subsection(style) as r2:
            gg = gvgen_from_ndp(ndp, style=style)
            gg_figure(r2, 'graph', gg)

    return r

def report_dp1(dp, imp=None):
    r = Report()
    gg = dp_graph_flow(dp, imp=imp)
    gg_figure(r, 'graph', gg)

    r.text('long', dp.repr_long())

    try:
        S, alpha, beta = dp.get_normal_form()

        s = ""
        s += 'S: %s' % S
        s += '\nα: %s' % alpha
        s += '\nβ: %s' % beta

        r.text('normalform', s)
        r.text('tree_long', dp.tree_long())
    except Exception as e:
        warnings.warn('Normal form not implemented %s' % e)



    M = dp.get_imp_space()
    r.text('I', str(M))


    if False:
        R = dp.get_res_space()
        F = dp.get_fun_space()
        Rinf = R.get_top()
        Fbot = F.get_bottom()
        if M == PosetProduct((R_dimensionless,)):
            s = ""
            ms = [0.0, 0.25, 0.5, 0.75, 1.0]
            for m in ms:
                feasible = dp.is_feasible(Fbot, (m,), Rinf)
                s += '\n m = %s  = %s' % (m, feasible)
            r.text('scalarres', s)
        else:
            m = M.witness()
            print(Fbot, m, Rinf)
            feasible = dp.is_feasible(Fbot, m, Rinf)
            r.text('some', 'bot feasible( %s, %s,%s): %s' % (Fbot, m, Rinf, feasible))

    return r

