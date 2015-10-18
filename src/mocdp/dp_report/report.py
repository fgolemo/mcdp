# -*- coding: utf-8 -*-
from .gg_ndp import gvgen_from_ndp
from .gg_utils import gg_figure
from contracts import contract
from mocdp.comp.interfaces import NamedDP
from mocdp.dp import DPLoop0, Mux, Parallel, Series0
from reprep import Report

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
        n = gg.newItem(label)
#
#         {'color': 'blue', 'shape': 'box', 'style': 'rounded',
#                         'fontname': 'Palatino italic', 'fontsize': 10},

        gg.styleApply("simple", n)
        # F = dp.get_fun_space()
        # R = dp.get_res_space()

        # nin = 1 if not isinstance(F, PosetProduct) else len(F)
        # nout = 1 if not isinstance(R, PosetProduct) else len(R)

        return (n, n)
#         return (tuple([n for _ in range(nin)]),
#                 tuple([n for _ in range(nout)]))
#         if is_cgraph_io_node(cnode):
#             gg.styleApply(STYLE_CGRAPH_NODE_IO, n)
#         else:
#             gg.styleApply(STYLE_CGRAPH_NODE, n)

#         cc[cnode] = n
        
            
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

        i = gg.newItem('L')
        o = gg.newItem('L')
        gg.newLink(i, n1i, label=str(dp.dp1.get_fun_space()))

        gg.newLink(n1o, o, label=str(dp.dp1.get_res_space()))
        gg.newLink(o, i, label=str(dp.dp1.get_res_space()))

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
