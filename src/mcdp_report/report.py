# -*- coding: utf-8 -*-
from .gg_ndp import gvgen_from_ndp
from .gg_utils import gg_figure
from contracts import contract
from mcdp_dp import (Constant, DPLoop0, GenericUnary, Limit, Mux, Parallel,
    PrimitiveDP, Series0)
from mcdp_posets import PosetProduct, R_dimensionless
from mocdp.comp.interfaces import NamedDP
from mocdp.exceptions import mcdp_dev_warning
from reprep import Report
import warnings
from mcdp_dp.dp_loop2 import DPLoop2



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
    gg = gvgen_from_dp(dp, imp=imp)
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



    M = dp.get_imp_space_mod_res()
    r.text('ImodR', str(M))


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


@contract(dp0=PrimitiveDP)
def gvgen_from_dp(dp0, imp=None):
    do_imp = imp is not None


    def go(dp, imp):
        if isinstance(dp, Series0):
            r = go_series(dp, imp)
        elif isinstance(dp, Parallel):
            r = go_parallel(dp, imp)
        elif isinstance(dp, DPLoop0):
            r = go_loop(dp, imp)
        elif isinstance(dp, DPLoop2):
            r = go_loop2(dp, imp)
        else:
            r = go_simple(dp, imp)
        return r
            
    def go_simple(dp, imp):
        label = type(dp).__name__
        if isinstance(dp, Mux):
            label = 'Mux\n%s' % str(dp.coords)
        if isinstance(dp, Constant):
            x = '%s %s' % (dp.R.format(dp.c), dp.R)
            label = 'Constant\n%s' % x
        if isinstance(dp, Limit):
            x = '<= %s [%s]' % (dp.F.format(dp.limit), dp.F)
            label = 'Limit\n%s' % x
        if isinstance(dp, GenericUnary):
            label = dp.__repr__()

        s = label
        if imp is not None:
            s += ' m=%s' % dp.M.format(imp)
        n = gg.newItem(s)

        gg.styleApply("simple", n)
        return (n, n)
            
    def go_series(dp, imp):
        assert isinstance(dp, Series0)
        if imp is not None:
            m1, m_extra, m2 = dp._unpack_m(imp)
        else:
            m1 = m_extra = m2 = None

        (n1i, n1o) = go(dp.dp1, m1)
        (n2i, n2o) = go(dp.dp2, m2)

        R1 = str(dp.dp1.get_res_space())
        label = str(R1)
        if m_extra is not None:
            label += ' m_extra: %s' % str(m_extra)
        gg.newLink(n1o, n2i, label=label)

        return (n1i, n2o)
        
    def go_parallel(dp, imp):
        if imp is not None:
            m1, m2 = dp._split_m(imp)
        else:
            m1 = m2 = None

        (n1i, n1o) = go(dp.dp1, m1)
        (n2i, n2o) = go(dp.dp2, m2)

        i = gg.newItem("|")
        o = gg.newItem("|")
        gg.styleApply("connector", i)
        gg.styleApply("connector", o)

        gg.newLink(i, n1i, label=str(dp.dp1.get_fun_space()))
        gg.newLink(i, n2i, label=str(dp.dp2.get_fun_space()))
        gg.newLink(n1o, o, label=str(dp.dp1.get_res_space()))
        gg.newLink(n2o, o, label=str(dp.dp2.get_res_space()))

        return (i, o)

    def go_loop(dp, imp):
        if do_imp:
            m0, _f2 = dp._unpack_m(imp)
        else:
            m0 = _f2 = None

        (n1i, n1o) = go(dp.dp1, m0)

        i = gg.newItem('|')
        gg.propertyAppend(i, "shape", "plaintext")
        o = gg.newItem('')
        gg.propertyAppend(o, "shape", "point")

        gg.newLink(i, n1i, label=str(dp.dp1.get_fun_space()))

        gg.newLink(n1o, o, label=str(dp.dp1.get_res_space()))
        loop_label = str(dp.dp1.get_res_space())

        mcdp_dev_warning('add option')
        if False:
            M = dp.get_imp_space_mod_res()
            M0 = dp.dp1.get_imp_space_mod_res()
            loop_label += ' M0: %s' % M0
            loop_label += ' M: %s' % M
        l = gg.newLink(o, i, label=loop_label)
        gg.propertyAppend(l, "color", "red")
        gg.propertyAppend(l, "headport", "sw")
        gg.propertyAppend(l, "tailport", "s")

        return (i, o)

    def go_loop2(dp, imp):
        if do_imp:
            m0, _f2 = dp._unpack_m(imp)
        else:
            m0 = _f2 = None

        (n1i, n1o) = go(dp.dp1, m0)

        i = gg.newItem('|')
        gg.propertyAppend(i, "shape", "plaintext")
        o = gg.newItem('|')
        gg.propertyAppend(o, "shape", "plaintext")

        gg.newLink(i, n1i, label=str(dp.dp1.get_fun_space()))

        gg.newLink(n1o, o, label=str(dp.dp1.get_res_space()))
        loop_label = str(dp.F2)

        mcdp_dev_warning('add option')
        if False:
            M = dp.get_imp_space_mod_res()
            M0 = dp.dp1.get_imp_space_mod_res()
            loop_label += ' M0: %s' % M0
            loop_label += ' M: %s' % M
        l = gg.newLink(o, i, label=loop_label)
        gg.propertyAppend(l, "color", "red")
        gg.propertyAppend(l, "headport", "sw")
        gg.propertyAppend(l, "tailport", "s")

        return (i, o)


    import my_gvgen as gvgen
    gg = gvgen.GvGen(options="rankdir=LR")


    gg.styleAppend("prim", "shape", "plaintext")
    gg.styleAppend("connector", "shape", "plaintext")
    gg.styleAppend("simple", "shape", "box")
    gg.styleAppend("simple", "style", "rounded")
#     gg.styleAppend("simple", "color", "blue")

    f0 = gg.newItem("")
    (f, r) = go(dp0, imp)
    r0 = gg.newItem("")
    gg.newLink(f0, f, label=str(dp0.get_fun_space()))
    gg.newLink(r, r0, label=str(dp0.get_res_space()))

    gg.styleApply("prim", f0)
    gg.styleApply("prim", r0)
    return gg
