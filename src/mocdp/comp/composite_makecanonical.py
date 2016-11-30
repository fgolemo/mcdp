# -*- coding: utf-8 -*-
from collections import namedtuple

from networkx.algorithms.cycles import simple_cycles

from contracts import contract
from contracts.utils import raise_desc, raise_wrapped
from mcdp_dp import Identity, Mux
from mcdp_posets import PosetProduct, get_types_universe
from mocdp import logger
from mocdp.comp.composite import CompositeNamedDP
from mocdp.comp.connection import get_connection_multigraph
from mocdp.comp.context import (CResource, Connection, get_name_for_fun_node,
    get_name_for_res_node, is_fun_node_name, is_res_node_name)
from mocdp.comp.flattening.flatten import cndp_flatten
from mocdp.comp.interfaces import NotConnected
from mocdp.comp.wrap import SimpleWrap, dpwrap
from mocdp.exceptions import DPSemanticErrorNotConnected
from mocdp.memoize_simple_imp import memoize_simple
import numpy as np


@contract(ndp=CompositeNamedDP)
def cndp_makecanonical(ndp, name_inner_muxed='_inner_muxed', s_muxed='_muxed'):
    """ 
        Returns a composite with only one ndp, called <named_inner_muxed>.
        If there were cycles, then this will also have a signal caled s_muxed
        and there will be one connection to it.
        
        raises DPSemanticErrorNotConnected
    """

    assert isinstance(ndp, CompositeNamedDP), type(ndp)

    try:
        ndp.check_fully_connected()
    except NotConnected as e:
        msg = 'Cannot put in canonical form because not all subproblems are connected.'
        raise_wrapped(DPSemanticErrorNotConnected, e, msg, compact=True)

    fnames = ndp.get_fnames()
    rnames = ndp.get_rnames()


    # First, we flatten it
    ndp = cndp_flatten(ndp)

    assert ndp.get_fnames() == fnames
    assert ndp.get_rnames() == rnames


    # then we compact it (take the product of edges)
    # Note also that this abstract() the children;
    # however, because we flattened before, this is redundant,
    # as every DP is a SimpleDP 
    ndp = ndp.compact()
    assert ndp.get_fnames() == fnames
    assert ndp.get_rnames() == rnames


    # Check that we have some cycles
    G = get_connection_multigraph(ndp.get_connections())
    cycles = list(simple_cycles(G))
    if not cycles:
        ndp_inner = ndp
        cycles_names = []
    else:

        # then we choose which edges to remove
        connections_to_cut = choose_connections_to_cut(
                                connections=ndp.get_connections(),
                                name2dp=ndp.get_name2ndp())


        connections_to_cut = list(connections_to_cut)
        n = len(connections_to_cut)
        cycles_names = list(['cut%d' % _ for _ in range(n)])
        ndp_inner = cndp_create_one_without_some_connections(ndp, connections_to_cut, cycles_names)

    assert ndp_inner.get_fnames() == fnames + cycles_names
    assert ndp_inner.get_rnames() == rnames + cycles_names

    if cycles_names:
        ndp_inner_muxed = add_muxes(ndp_inner, cs=cycles_names, s_muxed=s_muxed)
        mux_signal = s_muxed
        assert ndp_inner_muxed.get_fnames() == fnames + [mux_signal]
        assert ndp_inner_muxed.get_rnames() == rnames + [mux_signal]
    else:
        ndp_inner_muxed = ndp_inner

    name2ndp = {}
    name2ndp[name_inner_muxed] = ndp_inner_muxed
    connections = []

    connect_functions_to_outside(name2ndp, connections, ndp_name=name_inner_muxed, fnames=fnames)
    connect_resources_to_outside(name2ndp, connections, ndp_name=name_inner_muxed, rnames=rnames)

    if cycles_names:
        connections.append(Connection(name_inner_muxed, mux_signal, name_inner_muxed, mux_signal))

    outer = CompositeNamedDP.from_parts(name2ndp=name2ndp,
                                        connections=connections,
                                        fnames=fnames, rnames=rnames)
    return outer

@contract(cs='list(str)', s_muxed=str, returns=CompositeNamedDP)
def add_muxes(inner, cs, s_muxed, inner_name='_inner0', mux1_name='_mux1', mux2_name='_mux2'):
    """
        Add muxes before and after inner 
        
       
                  ---(extraf)--|       |---(extrar)--
                     |--c1-----| inner |--c1--|
             s_muxed-|--c2-----|       |--c2--|--s_muxed
           
    """

    extraf = [f for f in inner.get_fnames() if not f in cs]
    extrar = [r for r in inner.get_rnames() if not r in cs]
    
    fnames = extraf + [s_muxed]
    rnames = extrar + [s_muxed]

    name2ndp = {}
    connections = []
    name2ndp[inner_name] = inner
    
    # Second mux
    if len(cs) == 1:
        F = inner.get_ftype(cs[0])
        nto1 = SimpleWrap(Identity(F), fnames=cs[0], rnames=s_muxed)
    else:
        types = inner.get_ftypes(cs)
        F = PosetProduct(types.subs)
        # [0, 1, 2]
        coords = list(range(len(cs)))
        mux = Mux(F, coords)
        nto1 = SimpleWrap(mux, fnames=cs, rnames=s_muxed)

    if len(cs) == 1:
        R = inner.get_rtype(cs[0])
        _1ton = SimpleWrap(Identity(R), fnames=s_muxed, rnames=cs[0])
    else:

        # First mux
        coords = list(range(len(cs)))
        R = mux.get_res_space()
        mux2 = Mux(R, coords)
        _1ton = SimpleWrap(mux2, fnames=s_muxed, rnames=cs)
        F2 = mux2.get_res_space()
        tu = get_types_universe()
        tu.check_equal(F, F2)
    
    name2ndp[mux1_name] = nto1
    name2ndp[mux2_name] = _1ton

    for n in cs:
        connections.append(Connection(inner_name, n, mux1_name, n))
    for n in cs:
        connections.append(Connection(mux2_name, n, inner_name, n))

    # Now add the remaining names
    connect_functions_to_outside(name2ndp, connections, ndp_name=inner_name, fnames=extraf)
    connect_resources_to_outside(name2ndp, connections, ndp_name=inner_name, rnames=extrar)
    
    connect_resources_to_outside(name2ndp, connections, ndp_name=mux1_name, rnames=[s_muxed])
    connect_functions_to_outside(name2ndp, connections, ndp_name=mux2_name, fnames=[s_muxed])

    outer = CompositeNamedDP.from_parts(name2ndp=name2ndp,
                                        connections=connections,
                                        fnames=fnames, rnames=rnames)
    return outer


def connect_resources_to_outside(name2ndp, connections, ndp_name, rnames):
    """ 
        For each function in fnames of ndp_name,
        create a new outside function node and connect it to ndp_name.
    """
    assert ndp_name in name2ndp
    ndp = name2ndp[ndp_name]

    if not set(rnames).issubset(ndp.get_rnames()):
        msg = 'Some of the resources are not present.'
        raise_desc(ValueError, msg, rnames=rnames, ndp=ndp)

    for rn in rnames:
        nn = get_name_for_res_node(rn)
        R = ndp.get_rtype(rn)
        name2ndp[nn] = dpwrap(Identity(R), rn, rn)
        connections.append(Connection(ndp_name, rn, nn, rn))

def connect_functions_to_outside(name2ndp, connections, ndp_name, fnames):
    """ 
        For each function in fnames of ndp_name,
        create a new outside function node and connect it to ndp_name.
    """
    assert ndp_name in name2ndp
    ndp = name2ndp[ndp_name]

    if not set(fnames).issubset(ndp.get_fnames()):
        msg = 'Some of the functions are not present.'
        raise_desc(ValueError, msg, fnames=fnames, ndp=ndp)

    for fname in fnames:

        F = ndp.get_ftype(fname)
        nn = get_name_for_fun_node(fname)
        name2ndp[nn] = dpwrap(Identity(F), fname, fname)

        connections.append(Connection(nn, fname, ndp_name, fname))

@contract(names='list[N]', exclude_connections='list[N]')
def cndp_create_one_without_some_connections(ndp, exclude_connections, names):
    """ Creates a new CompositeNDP without some of the connections.
    A new function / resource pair is created for each cut connection. """
    from mocdp.comp.context import Context
    context = Context()
    
    # Create the fun/res node in the original order
    for fname in ndp.get_fnames():
        # simply copy the functionnode - it might be a LabeledNDP
        name = get_name_for_fun_node(fname)
        fndp = ndp.get_name2ndp()[name]
        context.fnames.append(fname)
        context.add_ndp(name, fndp)

    for rname in ndp.get_rnames():
        # simply copy the functionnode - it might be a LabeledNDP
        name = get_name_for_res_node(rname)
        rndp = ndp.get_name2ndp()[name]
        context.rnames.append(rname)
        context.add_ndp(name, rndp)

    for _name, _ndp in ndp.get_name2ndp().items():
        isf, fname = is_fun_node_name(_name)
        isr, rname = is_res_node_name(_name)

        if isf and fname in ndp.get_fnames():
            pass
        elif isr and rname in ndp.get_rnames():
            pass
        else:
            # print('regular: %r' % _name)
            context.add_ndp(_name, _ndp)

    for c in ndp.get_connections():
        if c in exclude_connections:
            continue
        # print('adding connection %s' % str(c))
        context.connections.append(c)

    # print('done')
    # for each cut connection
    for e, name in zip(exclude_connections, names):
        S = context.get_rtype(CResource(e.dp1, e.s1))
        fn = context.add_ndp_fun_node(name, S)
        rn = context.add_ndp_res_node(name, S)
        c1 = Connection(e.dp1, e.s1, rn, name)
        c2 = Connection(fn, name, e.dp2, e.s2)
        context.connections.append(c1)
        context.connections.append(c2)

    return CompositeNamedDP.from_context(context)



def find_one(connections, a, b):
    for c in connections:
        if c.dp1 == a and c.dp2 == b:
            return c
    assert False

def choose_connections_to_cut(connections, name2dp):
    # Compute the graph representation
    G = get_connection_multigraph(connections)
    
    def space_weight(R):
        if isinstance(R, PosetProduct):
            return len(R.subs)
        else:
            return 1

    @memoize_simple
    def edge_weight(e):
        (dp1, dp2) = e
        c = find_one(connections, dp1, dp2)
        R = name2dp[c.dp1].get_rtype(c.s1)
        return space_weight(R)

    edges_to_remove = enumerate_minimal_solution(G, edge_weight)
    connection_to_remove = [_ for _ in connections if (_.dp1, _.dp2) in edges_to_remove]

    return connection_to_remove


def enumerate_minimal_solution(G, edge_weight):
    """
        G: a graph
        edge_weight: a map from edge (i,j) of G to nonnegative weight
    """
    # Next optimization: consider equivalence classes of edges:
    # edges that belong to the same cycle. Then only keep the small ones.
    from mocdp.comp.connection import simple_cycles_as_edges
    
    State = namedtuple('State', 'cycles weight')
    # set of edges removed -> state 
    current_solutions = {} 
    current_partial_solutions = {}
    examined = set()
    
    freeze = frozenset
    
    # initial states
    all_edges = set(G.edges())

    all_cycles = simple_cycles_as_edges(G)

    def belongs_to_cycles(e):
        for c in all_cycles:
            assert isinstance(c, tuple)
            if e in c:
                return True
        return False

    def cycles_for_edge(e):
        cycles = set()
        for c in all_cycles:
            assert isinstance(c, tuple)
            if e in c:
                cycles.add(c)
        return freeze(cycles)

    # these are the ones we care about
    edges_belonging_to_cycles = set([e for e in all_edges if belongs_to_cycles(e)])

    def get_edges_to_consider():
        # For each set of cycles, find which edges are in the equivalence class
        from collections import defaultdict
        cycles2edges = defaultdict(lambda: set())
        for e in edges_belonging_to_cycles:
            cycles = freeze(cycles_for_edge(e))
            cycles2edges[cycles].add(e)


        cycles2champion = {}
        cycles2weight = {}
        for cycles, edges in cycles2edges.items():
            logger.debug('Found %s edges that remove a set of %s cycles' % (len(edges), len(cycles)))

            best = min(edges, key=edge_weight)

            cycles2champion[cycles] = best
            cycles2weight[cycles] = edge_weight(best)

        def a_contains_b(ca, cb):
            return cb.issubset(ca)

        consider = set()
        for cycles1 in cycles2weight:
            #logger.debug('cycles')
            for cycles2 in cycles2weight:
                w1 = cycles2weight[cycles1]
                w2 = cycles2weight[cycles2]
                if a_contains_b(cycles2, cycles1) and w2 < w1:
                    #logger.debug('dominated')
                    break
            else:
                # not dominated
                consider.add(cycles2champion[cycles1])

        logger.debug('From %d to %d edges to consider' % (len(edges_belonging_to_cycles), len(consider)))
        return consider


    edges_to_consider = get_edges_to_consider()

    logger.debug('Deciding between %s hot of %d edges' % (len(edges_to_consider), len(all_edges)))

    best_weight = np.inf
    

    current_partial_solutions[freeze([])] = \
        State(cycles=all_cycles, weight=0.0)
    
    while current_partial_solutions:
        # choose the solution to expand with minimum weight
        removed, state = pop_solution_minimum_weight(current_partial_solutions)
        examined.add(removed)
        logger.debug('nsolutions %s best w %s / current_partial_solutions %s / removed %s' %
              (len(current_solutions), best_weight, len(current_partial_solutions), removed))

        # now look at edges that we could remove
        to_remove = edges_to_consider - removed

        for edge in to_remove:
            new_weight = state.weight + edge_weight(edge)
            removed2 = set(removed)
            removed2.add(edge)
            removed2 = frozenset(removed2)

            if removed2 in examined:
                # print('do not consider')
                continue

            cycles = set([c for c in state.cycles if not edge in c])

            ss = State(cycles=cycles, weight=new_weight)
            if not cycles:
                current_solutions[removed2] = ss
                best_weight = min(best_weight, new_weight)
            else:
                if new_weight < best_weight:
                    current_partial_solutions[removed2] = ss

    solutions = list(current_solutions)
    weights = [current_solutions[k].weight for k in solutions]
    best = solutions[np.argmin(weights)]
    state = current_solutions[best]

    logger.debug('best: %s %s' % (best, state))
    return best


def pop_solution_minimum_weight(sols):
    keys = list(sols)
    weights = [sols[_].weight for _ in keys]
    best = np.argmin(weights)
    k = keys[best]
    res = sols[k]
    del  sols[k]
    return k, res




def get_canonical_elements(ndp0):
    """
        returns
        
            res['inner']
            res['cycles'] => variables
            res['extraf'] => list of extra functions
            res['extrar'] => list of extra resources
    """

    INNER = 'inner'
    MUXED = '_muxed'
    ndp = cndp_makecanonical(ndp0, name_inner_muxed=INNER, s_muxed=MUXED)
    subs = ndp.get_name2ndp()
    inner = subs[INNER]

    if MUXED in inner.get_fnames():
        cycles = [MUXED]
    else:
        cycles  = []

    extraf = [f for f in inner.get_fnames() if not f in cycles]
    extrar = [r for r in inner.get_rnames() if not r in cycles]

    res = {}
    res['inner'] = inner
    res['extraf'] = extraf
    res['extrar'] = extrar
    res['cycles'] = cycles
    return res
    
    

