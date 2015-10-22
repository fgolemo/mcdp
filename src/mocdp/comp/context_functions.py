from mocdp.dp.dp_identity import Identity
from mocdp.comp.context import Connection, Context
from contracts import contract


@contract(returns='list(tuple(str, str, set($Connection)))')
def find_nodes_with_multiple_connections(context):
    """ Finds pairs of nodes that have more than 
        one connection to one other in the same direction. 
    
        returns a list of tuples node1, node2, set(connections)
    """
    seq = []
    for name1 in context.names:
        for name2 in context.names:
            connections = context.get_connections_for(name1, name2)
            if len(connections) > 1:
                seq.append((name1, name2, connections))
    return seq




def dpgraph_making_sure_no_reps(context):
    from mocdp.comp.connection import dpgraph
    from collections import defaultdict
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
                print('need to translate F (%s, %s) because already in %s' %
                      (name, fn, functions[fn]))

                fn2 = '_%s_%s' % (name, fn)

                return dpgraph_translate_fn(context, name, fn, fn2)

            functions[fn].append(name)

    for name, ndp in context.names.items():
        if context.is_new_resource(name):
            continue
        for rn in ndp.get_rnames():

            if len(resources[rn]) != 0:
                print('need to translate R (%s, %s) because already in %s' %
                       (name, rn, resources[rn]))

                rn2 = '_%s_%s' % (name, rn)

                return dpgraph_translate_rn(context, name, rn, rn2)

            resources[rn].append(name)

    res0 = dpgraph(context.names, context.connections, split=[])
    res = make_sure_order_functions_and_resources(res0, context.fnames, context.rnames)
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
    second = dpwrap(Identity(R), rn, rn2)
    from mocdp.comp.connection import connect2
    connections = set([Connection('-', rn, '-', rn)])
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
    first = dpwrap(Identity(F), fn2, fn)
    from mocdp.comp.connection import connect2
    connections = set([Connection('-', fn, '-', fn)])
    return connect2(first, ndp, connections, split=[])

