from contracts import contract
from mocdp.comp.context import CResource, ValueWithUnits
from mocdp.dp.dp_constant import Constant
from mocdp.dp.dp_generic_unary import WrapAMap

def get_connections_for(context, name1, name2):
    s = set()
    for c in context.connections:
        if c.dp1 == name1 and c.dp2 == name2:
            s.add(c)
    return s

@contract(r=CResource)
def can_resource_be_constant(context, r):
    """ 
        Checks that this resource can be evaluated as a constant. 
    
        Necessary condition is that it doesn't depend on 
        external new functions.
        
        We should also check that we can actually solve
        each one... maybe limit to WrapAMap?
    """
    dependencies = get_resource_dependencies(context, r)
    # print('This depends on %r' % dependencies)
    not_constants = [_ for _ in dependencies if context.is_new_function(_) ]
    if not_constants:
        # print('Not constant because of these deps: %s' % not_constants)
        return False
    else:
        return True

@contract(r=CResource, returns=ValueWithUnits)
def eval_constant_resource(context, r):
    assert can_resource_be_constant(context, r)

    def find_connection_to(s2, dp2):
        for c in context.connections:
            if c.s2 == s2 and c.dp2 == dp2:
                return c
        assert False

    @contract(functions=dict)
    def run_ndp(ndp, functions):
        f = []
        for fn in ndp.get_fnames():
            vu = functions[fn]
            f.append(vu.value)
        f = tuple(f)
        if len(ndp.get_fnames()) == 1:
            f = f[0]
        dp = ndp.get_dp()
        if isinstance(dp, Constant):
            res = ValueWithUnits(dp.c, dp.R)
        elif isinstance(dp, WrapAMap):
            amap = dp.amap
            res = ValueWithUnits(amap(f), dp.get_res_space())
        else:
            raise NotImplementedError(type(dp))

        rnames = ndp.get_rnames()

        if len(rnames) == 1:
            resources = {rnames[0]: res}
        else:
            resources = {}
            for i, rn in enumerate(rnames):
                resources[rn] = res[i]

        return resources


    @contract(r=CResource, returns=ValueWithUnits)
    def evaluate(r):
        dp = r.dp
        ndp = context.names[dp]
        # we need to evaluate all functions
        functions = {}
        for f in ndp.get_fnames():
            c = find_connection_to(s2=f, dp2=dp)
            functions[f] = evaluate(CResource(c.dp1, c.s1))
        results = run_ndp(ndp, functions)
        return results[r.s]
    return evaluate(r)

@contract(r=CResource)
def get_resource_dependencies(context, r):
    G = cndp_get_digraph(context.names, context.connections)
    # print G.nodes(), G.edges()
    # XXX do we need to remove the self-loops?
    from networkx.algorithms.dag import ancestors
    all_ancestors = ancestors(G, r.dp)
    # print('ancestors: %s')
    return all_ancestors


def cndp_get_digraph(name2ndps, connections):
    import networkx as nx
    G = nx.DiGraph()
    for n in name2ndps:
        G.add_node(n)
    for c in connections:
        G.add_edge(c.dp1, c.dp2)
    return G
