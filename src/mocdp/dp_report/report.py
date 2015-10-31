# -*- coding: utf-8 -*-
from .gg_ndp import gvgen_from_ndp
from .gg_utils import gg_figure
from contracts import contract
from mocdp.comp.interfaces import NamedDP
from mocdp.dp import DPLoop0, Mux, Parallel, Series0
from mocdp.dp.dp_generic_unary import GenericUnary
from mocdp.posets.poset_product import PosetProduct
from mocdp.posets import R_dimensionless
from reprep import Report
from mocdp.dp.dp_constant import Constant
from mocdp.dp.dp_limit import Limit
from mocdp.exceptions import mcdp_dev_warning

@contract(ndp=NamedDP)
def report_ndp1(ndp):
    r = Report()

    gg = gvgen_from_ndp(ndp)
    gg_figure(r, 'graph', gg)

    return r



def report_dp1(dp):
    r = Report()
    gg = gvgen_from_dp(dp)    
    gg_figure(r, 'graph', gg)

    r.text('long', dp.repr_long())

    S, alpha, beta = dp.get_normal_form()

    s = ""
    s += 'S: %s' % S
    s += '\nα: %s' % alpha
    s += '\nβ: %s' % beta
    r.text('normalform', s)

    r.text('tree_long', dp.tree_long())

    M = dp.get_imp_space_mod_res()
    r.text('ImodR', str(M))

    R = dp.get_res_space()
    F = dp.get_fun_space()
    Rinf = R.get_top()
    Fbot = F.get_bottom()
    
    if False:
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


def gvgen_from_dp(dp0):

    def go(dp):
        if isinstance(dp, Series0):
            r = go_series(dp)
        elif isinstance(dp, Parallel):
            r = go_parallel(dp)
        elif isinstance(dp, DPLoop0):
            r = go_loop(dp)
        else:
            r = go_simple(dp)
        return r
            
    def go_simple(dp):
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
        n = gg.newItem(label)
        gg.styleApply("simple", n)
        return (n, n)
            
    def go_series(dp):
        (n1i, n1o) = go(dp.dp1)
        (n2i, n2o) = go(dp.dp2)

        R1 = str(dp.dp1.get_res_space())
        gg.newLink(n1o, n2i, label=str(R1))

        return (n1i, n2o)
        
    def go_parallel(dp):
        (n1i, n1o) = go(dp.dp1)
        (n2i, n2o) = go(dp.dp2)

        i = gg.newItem("|")
        o = gg.newItem("|")
        gg.styleApply("connector", i)
        gg.styleApply("connector", o)

        gg.newLink(i, n1i, label=str(dp.dp1.get_fun_space()))
        gg.newLink(i, n2i, label=str(dp.dp2.get_fun_space()))
        gg.newLink(n1o, o, label=str(dp.dp1.get_res_space()))
        gg.newLink(n2o, o, label=str(dp.dp2.get_res_space()))

        return (i, o)

    def go_loop(dp):
        (n1i, n1o) = go(dp.dp1)

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


    import gvgen  # @UnresolvedImport
    gg = gvgen.GvGen(options="rankdir=LR")


    gg.styleAppend("prim", "shape", "plaintext")
    gg.styleAppend("connector", "shape", "plaintext")
    gg.styleAppend("simple", "shape", "box")
    gg.styleAppend("simple", "style", "rounded")
#     gg.styleAppend("simple", "color", "blue")

    f0 = gg.newItem("")
    (f, r) = go(dp0)
    r0 = gg.newItem("")
    gg.newLink(f0, f, label=str(dp0.get_fun_space()))
    gg.newLink(r, r0, label=str(dp0.get_res_space()))

    gg.styleApply("prim", f0)
    gg.styleApply("prim", r0)
    return gg
