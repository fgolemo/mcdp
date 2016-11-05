# -*- coding: utf-8 -*-
from contracts import contract
from mcdp_dp import (ApproximableDP, CoProductDPLabels, Constant, DPLoop0,
    DPLoop2, LabelerDP, Limit, Mux, OpaqueDP, Parallel,
    PrimitiveDP, Series0, WrapAMap)
from multi_index.inversion import transform_pretty_print


__all__ = [
    'dp_graph_tree',
]

def get_dp_label(dp):
    label = type(dp).__name__
    if False:
        if isinstance(dp, Mux):
            label = 'Mux\nh: %s' % transform_pretty_print(dp.amap.dom, dp.amap.coords)
            if dp.amap_dual is not None:
                label += '\nh*: %s' %  transform_pretty_print(dp.amap_dual.dom, dp.amap_dual.coords, 'A')
            return label
        elif isinstance(dp, Constant):
            # x = '%s %s' % (dp.R.format(dp.c), dp.R)
            x = dp.R.format(dp.c)
            label = 'Constant\n%s' % x
        elif isinstance(dp, Limit):
            x = '<= %s [%s]' % (dp.F.format(dp.limit), dp.F)
            label = 'Limit\n%s' % x
        elif isinstance(dp, WrapAMap):
            label = 'WrapAMap\n%s' % dp.diagram_label()
        
#     label = type(dp).__name__ + '/' + label
    
    label += '\n h: ' + dp.repr_h_map() 
    label += '\n h*: ' + dp.repr_hd_map()
    
#     label += 'r<sub>1</sub>r<sup>2</sup>'
    # "₁₂₃₄₅₆₇₈₉"
    
#     subs ={ "₁": "1", "₂": "2", "₃": "3", "₄":"4", "₅": "5", 
#            "₆":"6", "₇": "7", "₈": "8", "₉": "9"}
#     for s, ss in subs.items():
#         label = label.replace(s, ss)
#     
    return label

@contract(dp0=PrimitiveDP)
def dp_graph_tree(dp0, imp= 
                  None, compact=False):
    """ 
        Visualizes the DP as a tree.
        
        if compact is True, no text is drawn on the edges.
        
    """
    do_imp = imp is not None

    add_edges_text = not compact
    add_leaf_text = not compact
    add_junction_text = not compact

    def go(dp, imp):
        """ Each of these must return a node """
        if isinstance(dp, Series0):
            r = go_series(dp, imp)
        elif isinstance(dp, Parallel):
            r = go_parallel(dp, imp)
        elif isinstance(dp, DPLoop0):
            r = go_loop(dp, imp)
        elif isinstance(dp, DPLoop2):
            r = go_loop2(dp, imp)
        elif isinstance(dp, OpaqueDP):
            r = go_opaque(dp, imp)
        elif isinstance(dp, ApproximableDP):
            r = go_simple_uncertain(dp, imp)
        elif isinstance(dp, CoProductDPLabels):
            r = go_coproductdplabels(dp, imp)
        elif isinstance(dp, LabelerDP):
            r = go_labeler(dp, imp)
        else:
            r = go_simple(dp, imp)
        return r

    def go_labeler(dp, imp):
        if add_junction_text:
            label = 'labeler\n{}'.format(dp.recname)
        else:
            label = ""
        n = gg.newItem(label)

        gg.styleApply('junction', n)
        gg.styleApply('junction_labeler', n)

        n1 = go(dp.dp, imp)

        create_edge(n, n1, dp.dp)

        return n

    def go_coproductdplabels(dp, imp):  # @UnusedVariable
        assert isinstance(dp, CoProductDPLabels)
        labels = dp.labels
        dps = dp.dp.dps
        if add_junction_text:
            label = 'coproduct'
        else:
            label = ""
        n = gg.newItem(label)
        gg.styleApply("junction", n)
        gg.styleApply('junction_coproduct', n)
        for label1, dp1 in zip(labels, dps):
            n1 = go(dp1, None)
            if add_edges_text:
                label = label1
            else:
                label = None
            l = gg.newLink(n, n1, label)
            gg.styleApply('edge_coproduct', l)
        return n
        
    def go_simple(dp, imp):
        if add_leaf_text:
            label = get_dp_label(dp)
            if imp is not None:
                label += ' m=%s' % dp.M.format(imp)
        else:
            label = ""

        n = gg.newItem(label)
        gg.styleApply("leaf_normal", n)
        return n

    def go_simple_uncertain(dp, imp):
        if add_leaf_text:
            label = get_dp_label(dp)

            if imp is not None:
                label += ' m=%s' % dp.M.format(imp)
        else:
            label = ""
        n = gg.newItem(label)
        gg.styleApply("leaf_uncertain", n)
        return n

    def create_edge(n_parent, n_child, dp):
        if add_edges_text:
            edge_label = get_edge_label(dp)
        else:
            edge_label = None
        l = gg.newLink(n_parent, n_child, edge_label)
        gg.styleApply('edge', l)

    def go_series(dp, imp):
        assert isinstance(dp, Series0)
        if imp is not None:
            m1, m2 = dp._unpack_m(imp)
        else:
            m1 = m2 = None

        n1 = go(dp.dp1, m1)
        n2 = go(dp.dp2, m2)

        if add_junction_text:
            label = 'series'
        else:
            label = ""
        n = gg.newItem(label)
        gg.styleApply("junction", n)
        gg.styleApply('junction_series', n)

        create_edge(n, n1, dp.dp1)
        create_edge(n, n2, dp.dp2)
        return n

    def go_parallel(dp, imp):
        if imp is not None:
            m1, m2 = dp._split_m(imp)
        else:
            m1 = m2 = None

        n1 = go(dp.dp1, m1)
        n2 = go(dp.dp2, m2)

        if add_junction_text:
            label = 'par'
        else:
            label = ""
        n = gg.newItem(label)
        gg.styleApply("junction", n)
        gg.styleApply('junction_par', n)

        create_edge(n, n1, dp.dp1)
        create_edge(n, n2, dp.dp2)
        return n

    def go_loop(dp, imp):
        if do_imp:
            m0, _f2 = dp._unpack_m(imp)
        else:
            m0 = _f2 = None

        if add_junction_text:
            label = 'loop'
        else:
            label = ""

        n = gg.newItem(label)
        n1 = go(dp.dp1, m0)
        gg.styleApply('junction', n)
        gg.styleApply('junction_loop', n)

        create_edge(n, n1, dp.dp1)
        return n

    def go_loop2(dp, imp):
        if do_imp:
            m0, _f2, _r2 = dp._unpack_m(imp)
        else:
            m0 = _f2 = _r2 = None

        if add_junction_text:
            label = 'loop'
        else:
            label = ""
        n = gg.newItem(label)

        gg.styleApply('junction', n)
        gg.styleApply('junction_loop', n)


        n1 = go(dp.dp1, m0)

        create_edge(n, n1, dp.dp1)

        return n
    
    def go_opaque(dp, imp):
        if add_junction_text:
            label = 'opaque'
        else:
            label = ""
        n = gg.newItem(label)

        gg.styleApply('junction', n)
        gg.styleApply('junction_opaque', n)

        n1 = go(dp.dp, imp)

        create_edge(n, n1, dp.dp)

        return n

    def get_edge_label(dp):
        F = dp.get_fun_space()
        R = dp.get_res_space()
        s = '%s\n↓\n%s' % (F, R)
        return s

    import my_gvgen as gvgen
    gg = gvgen.GvGen(options="rankdir=TB")

    gg.styleAppend("root", "shape", "none")

    gg.styleAppend("leaf_normal", "shape", "box")
    gg.styleAppend("leaf_normal", "style", "rounded")

    gg.styleAppend("leaf_uncertain", "shape", "box")
    gg.styleAppend("leaf_uncertain", "style", "filled,rounded")
    gg.styleAppend("leaf_uncertain", "fillcolor", "blue")
    gg.styleAppend("leaf_uncertain", "fontcolor", "white")

    gg.styleAppend("junction", "shape", "none")
    gg.styleAppend("junction", "fontname", "arial")

    gg.styleAppend("junction_series", "style", "filled")
    gg.styleAppend("junction_series", "fillcolor", "yellow")

    gg.styleAppend("junction_loop", "style", "filled")
    gg.styleAppend("junction_loop", "fillcolor", "red")

    gg.styleAppend("junction_opaque", "style", "filled")
    gg.styleAppend("junction_opaque", "fillcolor", "gray")

    gg.styleAppend("junction_par", "style", "filled")
    gg.styleAppend("junction_par", "fillcolor", "green")

    gg.styleAppend("junction_coproduct", "style", "filled")
    gg.styleAppend("junction_coproduct", "fillcolor", "magenta")

    gg.styleAppend("junction_labeler", "shape", "box")
    gg.styleAppend("junction_labeler", "style", "filled")
    gg.styleAppend("junction_labeler", "fillcolor", "gray")

    gg.styleAppend("edge", "arrowhead", "none")

    gg.styleAppend("edge_coproduct", "arrowhead", "none")
    gg.styleAppend("edge_coproduct", "style", "dashed")

    n = go(dp0, imp)
    n0 = gg.newItem("")
    gg.styleApply("root", n0)

    create_edge(n0, n, dp0)

    return gg
