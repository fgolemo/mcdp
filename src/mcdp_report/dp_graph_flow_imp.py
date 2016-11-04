# -*- coding: utf-8 -*-
from contracts import contract
from mcdp_dp import DPLoop0, DPLoop2, Parallel, PrimitiveDP, Series0
from mocdp.exceptions import mcdp_dev_warning

__all__ = [
    'dp_graph_flow',
]

@contract(dp0=PrimitiveDP)
def dp_graph_flow(dp0, imp=None):
    """
    
        TODO: Coproduct
        TODO: LabelerDP
        
    """
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
        from .dp_graph_tree_imp import get_dp_label
        label = get_dp_label(dp)
        if imp is not None:
            label += ' m=%s' % dp.M.format(imp)
        n = gg.newItem(label)

        gg.styleApply("simple", n)
        return (n, n)

    def go_series(dp, imp):
        assert isinstance(dp, Series0)
        if imp is not None:
            m1, m2 = dp._unpack_m(imp)
            m_extra = None
        else:
            m1 = m_extra = m2 = None

        (n1i, n1o) = go(dp.dp1, m1)
        (n2i, n2o) = go(dp.dp2, m2)

        R1 = str(dp.dp1.get_res_space())
        label = str(R1)
        if m_extra is not None:
            label += ' m_extra: %s' % str(m_extra)
        
        l = gg.newLink(n1o, n2i, label=label)
        gg.propertyAppend(l, 'arrowhead', 'none')
        
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

        l1 = gg.newLink(i, n1i, label=str(dp.dp1.get_fun_space()))
        l2 = gg.newLink(i, n2i, label=str(dp.dp2.get_fun_space()))
        l3 = gg.newLink(n1o, o, label=str(dp.dp1.get_res_space()))
        l4 = gg.newLink(n2o, o, label=str(dp.dp2.get_res_space()))

        for _ in [l1, l2, l3, l4]:
            gg.propertyAppend(_, 'arrowhead', 'none')
            
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

        l0 = gg.newLink(i, n1i, label=str(dp.dp1.get_fun_space()))
        l1 = gg.newLink(n1o, o, label=str(dp.dp1.get_res_space()))
        loop_label = str(dp.dp1.get_res_space())

        mcdp_dev_warning('add option')
#         if False:
#             M = dp.get_imp_space_mod_res()
#             M0 = dp.dp1.get_imp_space_mod_res()
#             loop_label += ' M0: %s' % M0
#             loop_label += ' M: %s' % M
        l = gg.newLink(o, i, label=loop_label)
        gg.propertyAppend(l, "color", "red")
        gg.propertyAppend(l, "headport", "sw")
        gg.propertyAppend(l, "tailport", "s")

        for _ in [l0, l1, l]:
            gg.propertyAppend(_, 'arrowhead', 'none')

        return (i, o)

    def go_loop2(dp, imp):
        if do_imp:
            m0, _f2, _r2 = dp._unpack_m(imp)
        else:
            m0 = _f2 = _r2 = None

        (n1i, n1o) = go(dp.dp1, m0)

        i = gg.newItem('|')
        gg.propertyAppend(i, "shape", "plaintext")
        o = gg.newItem('|')
        gg.propertyAppend(o, "shape", "plaintext")

        l0 = gg.newLink(i, n1i, label=str(dp.dp1.get_fun_space()))
        l1 = gg.newLink(n1o, o, label=str(dp.dp1.get_res_space()))
        gg.propertyAppend(l0, 'arrowhead', 'none')
        gg.propertyAppend(l1, 'arrowhead', 'none')

        loop_label = str(dp.F2)

        mcdp_dev_warning('add option')
#         if False:
#             M = dp.get_imp_space_mod_res()
#             M0 = dp.dp1.get_imp_space_mod_res()
#             loop_label += ' M0: %s' % M0
#             loop_label += ' M: %s' % M
        l = gg.newLink(o, i, label=loop_label)
        gg.propertyAppend(l, "color", "red")
        gg.propertyAppend(l, "headport", "sw")
        gg.propertyAppend(l, "tailport", "s")
        
        gg.propertyAppend(l, 'arrowhead', 'none')

        return (i, o)


    import my_gvgen as gvgen
    gg = gvgen.GvGen(options="rankdir=LR")

    gg.styleAppend("prim", "shape", "plaintext")
    gg.styleAppend("connector", "shape", "plaintext")
    gg.styleAppend("simple", "shape", "box")
    gg.styleAppend("simple", "style", "rounded")

    f0 = gg.newItem("")
    (f, r) = go(dp0, imp)
    r0 = gg.newItem("")
    l0 = gg.newLink(f0, f, label=str(dp0.get_fun_space()))
    l1 = gg.newLink(r, r0, label=str(dp0.get_res_space()))
    gg.propertyAppend(l0, 'arrowhead', 'none')
    gg.propertyAppend(l1, 'arrowhead', 'none')

    gg.styleApply("prim", f0)
    gg.styleApply("prim", r0)
    return gg
