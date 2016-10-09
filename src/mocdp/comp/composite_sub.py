from .connection import get_connection_graph
from contracts import contract
from mocdp.comp.composite import CompositeNamedDP
from mocdp.comp.interfaces import NamedDP  # @UnusedImport contracts
import networkx as nx

@contract(cndp=CompositeNamedDP, returns='int, >=0')
def cndp_num_connected_components(cndp):
    """ Returns the number of connected components """
    components = cndp_connected_components(cndp)
    return len(components)

@contract(cndp=CompositeNamedDP, returns='list(set(str))')
def cndp_connected_components(cndp):
    """ Returns the connected components (set of nodes) """
    name2ndp = cndp.get_name2ndp()
    connections = cndp.get_connections()
    G = get_connection_graph(name2ndp, connections)
    Gu = G.to_undirected()
    components = list(nx.connected_components(Gu))
    return components

@contract(cndp=CompositeNamedDP, returns='set($NamedDP)')
def cndp_split_in_components(cndp):
    """ Splits one CompositeNamedDP in many CompositeNamedDPs that
        are fully connected. """
    components = cndp_connected_components(cndp)
    res = []
    for nodes_i in components:
        r = cndp_sub(cndp, nodes_i)
        n = cndp_num_connected_components(r)
        assert n == 1, n
        res.append(r)
    return set(res)

@contract(cndp=CompositeNamedDP, nodes_i='set|seq(str)', returns=CompositeNamedDP)
def cndp_sub(cndp, nodes_i):
    """ Returns a subset of the CompositeNamedDP with only certain nodes. """
    name2ndp = cndp.get_name2ndp()
    for n in nodes_i:
        assert n in name2ndp
    connections = cndp.get_connections()
    fnames = cndp.get_fnames()
    rnames = cndp.get_rnames()

    name2ndp_i = dict((k, v) for k, v in name2ndp.items() if k in nodes_i)
    filter_c = lambda c: c.involves_any_of_these_nodes(nodes_i)
    connections_i = filter(filter_c, connections)

    def filter_function(fn):
        for ndp in name2ndp_i.values():
            if fn in ndp.get_fnames():
                return True
        return False

    def filter_resource(rn):
        for ndp in name2ndp_i.values():
            if rn in ndp.get_rnames():
                return True
        return False

    fnames_i = filter(filter_function, fnames)
    rnames_i = filter(filter_resource, rnames)

    ndp_i = CompositeNamedDP.from_parts(name2ndp=name2ndp_i,
                                        connections=connections_i,
                                        fnames=fnames_i, rnames=rnames_i)
    return ndp_i


