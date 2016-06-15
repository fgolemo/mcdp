# -*- coding: utf-8 -*-

from collections import defaultdict
from contracts import contract
from mocdp.comp.composite import CompositeNamedDP
from mocdp.comp.composite_sub import (cndp_num_connected_components,
    cndp_split_in_components)
from mocdp.comp.connection import cndp_dpgraph
from mocdp.comp.context import Connection, Context
from mocdp.comp.wrap import SimpleWrap
from mcdp_dp.dp_flatten import Mux
from mcdp_dp.dp_identity import Identity
from mcdp_dp.dp_parallel_simplification import make_parallel_n
from mcdp_dp.dp_series_simplification import make_series
from mcdp_posets.poset_product import PosetProduct

@contract(returns='list(tuple(str, str, set($Connection)))')
def find_nodes_with_multiple_connections(context):
    """ Finds pairs of nodes that have more than 
        one connection to one other in the same direction. 
    
        returns a list of tuples node1, node2, set(connections)
    """
    seq = []
    for name1 in context.names:
        for name2 in context.names:
            from mocdp.comp.context_eval_as_constant import get_connections_for
            connections = get_connections_for(context, name1, name2)
            if len(connections) > 1:
                seq.append((name1, name2, connections))
    return seq

def dpgraph_making_sure_no_reps(context):
    from mocdp.comp.connection import dpgraph
    # functionname -> list of names that use it
    functions = defaultdict(lambda: list())
    resources = defaultdict(lambda: list())

    for fname, name, ndp in context.iterate_new_functions():
        assert fname == ndp.get_fnames()[0]
        functions[fname].append(name)

    for rname, name, ndp in context.iterate_new_resources():
        assert rname == ndp.get_rnames()[0]
        resources[rname].append(name)

    for name, ndp in context.names.items():
        if context.is_new_function(name):
            continue
        for fn in ndp.get_fnames():

            if len(functions[fn]) != 0:
                # print('need to translate F (%s, %s) because already in %s' %
                #       (name, fn, functions[fn]))

                fn2 = '_%s_%s' % (name, fn)

                return dpgraph_translate_fn(context, name, fn, fn2)

            functions[fn].append(name)

    for name, ndp in context.names.items():
        if context.is_new_resource(name):
            continue
        for rn in ndp.get_rnames():

            if len(resources[rn]) != 0:
                # print('need to translate R (%s, %s) because already in %s' %
                #        (name, rn, resources[rn]))

                rn2 = '_%s_%s' % (name, rn)

                return dpgraph_translate_rn(context, name, rn, rn2)

            resources[rn].append(name)

    name2npd = context.names
    connections = context.connections
    fnames = context.fnames
    rnames = context.rnames

    # check if there are disconnected components
    cndp = CompositeNamedDP.from_context(context)

    n = cndp_num_connected_components(cndp)
    if n == 1:
        # This is the base case
        res0 = dpgraph(name2npd, connections, split=[])
        res = make_sure_order_functions_and_resources(res0, fnames, rnames)
        return res
    else:
        # This is the more complicated case
        cndp_list = cndp_split_in_components(cndp)
        assert len(cndp_list) == n

        # Now call each one in turn
        simple_wraps = []
        for cndp in cndp_list:
            dpi = cndp_dpgraph(cndp)
            assert isinstance(dpi, SimpleWrap)
            simple_wraps.append(dpi)
            
        final = ndps_parallel(simple_wraps)
        res = make_sure_order_functions_and_resources(final, fnames, rnames)
        return res


@contract(ndps='list($SimpleWrap)', returns=SimpleWrap)
def ndps_parallel(ndps):
    dps = [ndp.get_dp() for ndp in ndps]
    dp = make_parallel_n(dps)
    F = dp.get_fun_space()
    R = dp.get_res_space()
    fnames = []
    ftypes = []
    rnames = []
    rtypes = []

    coords_postfix = []
    coords_prefix = []
    for i, ndp_i in enumerate(ndps):
        fnames_i = ndp_i.get_fnames()
        if not fnames_i:
            coords_prefix.append([])
        else:
            mine = []
            for j, fn in enumerate(fnames_i):
                ft = ndp_i.get_ftype(fn)
                F0_index = len(fnames)
                mine.append(F0_index)
                fnames.append(fn)
                ftypes.append(ft)
            if len(mine) == 1:
                mine = mine[0]
            coords_prefix.append(mine)

        rnames_i = ndp_i.get_rnames()
        for j, rn in enumerate(rnames_i):
            rt = ndp_i.get_rtype(rn)
            if len(rnames_i) == 1:
                coords_postfix.append(i)
            else:
                coords_postfix.append((i, j))
            rnames.append(rn)
            rtypes.append(rt)

    F0 = PosetProduct(ftypes)
    prefix = Mux(F0, coords_prefix)
    assert F == prefix.get_res_space()

    R0 = PosetProduct(rtypes)

    postfix = Mux(R, coords_postfix)

    assert R0 == postfix.get_res_space()

    res_dp = make_series(make_series(prefix, dp), postfix)

    from mocdp.comp.connection import simplify_if_only_one_name
    res_dp, fnames, rnames = simplify_if_only_one_name(res_dp, fnames, rnames)
    
    res = SimpleWrap(res_dp, fnames, rnames)

    return res

def make_sure_order_functions_and_resources(res, fnames, rnames):
    from mocdp.comp.connection import  connect2
    from mocdp.comp.wrap import dpwrap

    def reorder_resources(ndp, rnames):
        R = ndp.get_rtypes(rnames)
        ndp2 = dpwrap(Identity(R), rnames, rnames)
        connections = [Connection('*', rn, '*', rn) for rn in rnames]
        return connect2(res, ndp2, set(connections), split=[], repeated_ok=True)

    def reorder_functions(ndp, rnames):
        F = ndp.get_ftypes(rnames)
        ndp0 = dpwrap(Identity(F), rnames, rnames)
        connections = [Connection('*', fn, '*', fn) for fn in rnames]
        return connect2(ndp0, res, set(connections), split=[], repeated_ok=True)

    if res.get_rnames() != rnames:
        res = reorder_resources(res, rnames)
    if res.get_fnames() != fnames:
        res = reorder_functions(res, fnames)

    assert res.get_fnames() == fnames
    assert res.get_rnames() == rnames
    return res


def dpgraph_translate_rn(context,
                         name, rn, rn2):

    def translate_connections(c):
        if c.dp1 == name and c.s1 == rn:
            c = Connection(name, rn2, c.dp2, c.s2)
        return c
    connections2 = map(translate_connections, context.connections)
    names2 = context.names.copy()
    names2[name] = wrap_change_name_resource(context.names[name], rn, rn2)
    c2 = Context()
    c2.rnames = context.rnames
    c2.fnames = context.fnames
    c2.connections = connections2
    c2.names = names2
    return dpgraph_making_sure_no_reps(c2)

def wrap_change_name_resource(ndp, rn, rn2):
    from mocdp.comp.wrap import dpwrap

    R = ndp.get_rtype(rn)
    tmpname = '__tmp_%s' % rn
    second = dpwrap(Identity(R), tmpname, rn2)
    from mocdp.comp.connection import connect2
    connections = set([Connection('-', rn, '-', tmpname)])
    return connect2(ndp, second, connections, split=[])

def dpgraph_translate_fn(context, name, fn, fn2):

    def translate_connections(c):
        if c.dp2 == name and c.s2 == fn:
            c = Connection(c.dp1, c.s1, name, fn2)
        return c

    connections2 = map(translate_connections, context.connections)
    names2 = context.names.copy()

    names2[name] = wrap_change_name_function(context.names[name], fn, fn2)

    c2 = Context()
    c2.rnames = context.rnames
    c2.fnames = context.fnames
    c2.connections = connections2
    c2.names = names2
    return dpgraph_making_sure_no_reps(c2)


def wrap_change_name_function(ndp, fn, fn2):
    from mocdp.comp.wrap import dpwrap

    F = ndp.get_ftype(fn)
    tmpname = '__tmp_%s' % fn
    first = dpwrap(Identity(F), fn2, tmpname)
    from mocdp.comp.connection import connect2
    connections = set([Connection('-', tmpname, '-', fn)])
    return connect2(first, ndp, connections, split=[])

