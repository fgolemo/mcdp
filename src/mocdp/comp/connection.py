# -*- coding: utf-8 -*-
from collections import Counter

from networkx import DiGraph, MultiDiGraph, NetworkXUnfeasible
from networkx.algorithms import is_connected, simple_cycles, topological_sort

from contracts import contract
from contracts.utils import (format_dict_long, format_list_long, raise_desc,
    raise_wrapped)
from mcdp_dp import Identity, Mux, make_parallel, make_series
from mcdp_posets import PosetProduct
from mocdp.comp.composite import CompositeNamedDP
from mocdp.comp.connection_reps import (relabel, there_are_repetitions,
    there_are_reps)
from mocdp.comp.wrap import SimpleWrap
from mcdp.exceptions import DPInternalError, DPSemanticError

from .context import Connection
from .interfaces import NamedDP
from .wrap import dpwrap


class TheresALoop(Exception):
    pass


def check_connections(name2dp, connections):
    for c in connections:
        if not c.dp1 in name2dp:
            msg = 'Refers to unknown dp %r (known %r).' % (c.dp1, set(name2dp))
            raise ValueError(msg)
        try:
            ndp1 = name2dp[c.dp1]
            ndp1.rindex(c.s1)
        except ValueError as e:
            raise_wrapped(ValueError, e, 'Unknown signal.', s1=c.s1, c=c, ndp1=ndp1)
        if not c.dp2 in name2dp:
            msg = 'Refers to unknown dp %r (known %r).' % (c.dp2, set(name2dp))
            raise ValueError(msg)
        try:
            ndp2 = name2dp[c.dp2]
            ndp2.findex(c.s2)
        except ValueError as e:
            raise_wrapped(ValueError, e, 'Unknown signal.', s2=c.s2, c=c, ndp2=ndp2)
 
@contract(name2dp='dict(str:($NamedDP))',
          connections='set(str|$Connection)|list(str|$Connection)',
          returns=SimpleWrap)
def dpconnect(name2dp, connections, split=[]):
    """
        Raises TheresALoop
    """
    if len(name2dp) == 1:
        if connections:
            raise_desc(NotImplementedError, '')
        res = list(name2dp.values())[0]

        return res.abstract()

    connections = set(connections)
#     if do_extra_checks():
    check_connections(name2dp, connections)

    # A, B, C

    # A  I  C
    # I  B  I

    # First, we need to order the dps using topological sorting
    try:
        order = order_dps(name2dp, connections)
    except NetworkXUnfeasible:
        raise TheresALoop()

    # Now let's pick the first two
    first = order[0]
    G = get_connection_graph(set(name2dp), connections)
    # actually order[1] is not necessarily connected
    for second in order[1:]:
        if G.has_edge(first, second):
            break

    assert G.has_edge(first, second)


    # these are the connections for the first two
    belongs_first = lambda c: set([c.dp1, c.dp2]) == set([first, second])
    not_belongs_first = lambda c: not belongs_first(c)
    first_connections = filter(belongs_first, connections)

    # these are the signals that are going to be connected and hence closed
    to_be_connected = [c.s1 for c in first_connections]

    # these are other names that need to be preserved for the first 1
    split1 = [c.s1
             for c in connections
             if c.dp1 == first and c.dp2 != second]

    for c in first_connections:
        if c.s1 in split:
            split1.append(c.s1)

    # now we remove from split1 the ones that are not connected
    split1 = [s for s in split1 if s in to_be_connected]

    # note that this might produce repeated names in split1
    if len(split1) != len(set(split1)):
        split1_unique = []
        for x in split1:
            if not x in split1_unique:
                split1_unique.append(x)
        split1 = split1_unique

    # check that all the splitting is in connection
    for s in split1:
        for c in first_connections:
            if c.s1 == s:
                break
        else:
            msg = 'Cannot find split signal in first_connections.'
            raise_desc(Exception, msg, s=s, first_connections=first_connections, connections=connections, split1=split)


    dp = connect2(name2dp[first], name2dp[second], set(first_connections), split=split1)

    others = list(order)
    others.remove(first)
    others.remove(second)
    if not others:
        return dp

    # make a new name
    dpname = make_name(order)

    def translate(c):
        dp1 = c.dp1
        s1 = c.s1
        dp2 = c.dp2
        s2 = c.s2
        if dp1 in [first, second]:
            dp1 = dpname
        if dp2 in [first, second]:
            dp2 = dpname
        return Connection(dp1=dp1, dp2=dp2, s1=s1, s2=s2)

    other_connections = map(translate, filter(not_belongs_first, connections))

    name2dp = name2dp.copy()
    del name2dp[first]
    del name2dp[second]
    name2dp[dpname] = dp

    split2 = []
    for c in other_connections:
        if c.s1 in split:
            split2.append(c.s1)

    return dpconnect(name2dp, set(other_connections), split=split2)

def list_diff(l, toremove):
    """ Returns a copy of the list without the elements in toremove """
    return [x for x in l if not x in toremove]

def its_dp_as_product(ndp):
    """ If fnames == 1 """
    dp = ndp.get_dp()
    if len(ndp.get_fnames()) == 1:
        F0 = dp.get_fun_space()
        F = PosetProduct((F0,))
        down = Mux(F, 0)
        dp = make_series(down, dp)

    if len(ndp.get_rnames()) == 1:
        R0 = dp.get_res_space()
        lift = Mux(R0, [()])
        dp = make_series(dp, lift)
    return dp

@contract(ndp1=NamedDP, ndp2=NamedDP,
          connections='set($Connection)',
          split='list(str)',
          returns=SimpleWrap)
def connect2(ndp1, ndp2, connections, split, repeated_ok=False):
    """ 
        Note the argument split must be a list of strings so 
        that orders are preserved and deterministic. 
    """

    if ndp1 is ndp2:
        raise ValueError('Equal')
    
    def common(x, y):
        return len(set(x + y)) != len(set(x)) + len(set(y))

    if not repeated_ok:
        if (common(ndp1.get_fnames(), ndp2.get_fnames()) or
            common(ndp1.get_rnames(), ndp2.get_rnames())):
            raise_desc(DPInternalError, 'repeated names', ndp1=ndp1, ndp2=ndp2,
                       connections=connections, split=split)

    if len(set(split)) != len(split):
        msg = 'Repeated signals in split: %s' % str(split)
        raise ValueError(msg)
    try:
        if not connections:
            raise ValueError('Empty connections')

        #     |   |------------------------->A
        #     |   |          |-B1(split)----->
        # f1->|   |--B1----->|         ___
        #     | 1 |          |----B2->|   |   all_s2 = B2 + C2  all_s1 = B1 + C1
        #     |___| -C1--C2---------->| 2 |->r2
        # ---------D----------------->|___|
        #
        # ftot = f1 + D
        # rtot = A + b1 + r2
        # A + B + C = r1
        # B + C + D = f2
        # split = A + B

        # split = B1 is given
        # find B2 from B1
        def s2_from_s1(s1):
            for c in connections:
                if c.s1 == s1: return c.s2
            assert False, 'Cannot find connection with s1 = %s' % s1
        def s1_from_s2(s2):
            for c in connections:
                if c.s2 == s2: return c.s1
            assert False, 'Cannot find connection with s2 = %s' % s2

        f1 = ndp1.get_fnames()
        r1 = ndp1.get_rnames()
        f2 = ndp2.get_fnames()
        r2 = ndp2.get_rnames()

        all_s2 = set([c.s2 for c in connections])
        all_s1 = set([c.s1 for c in connections])

        # assert that all split are in s1
        for x in split: assert x in all_s1

        B1 = list(split)
        B2 = map(s2_from_s1, B1)
        C2 = list_diff(all_s2, B2)
        C1 = map(s1_from_s2, C2)
        A = list_diff(r1, B1 + C1)
        D = list_diff(f2, B2 + C2)

        # print('B1: %s' % B1)
        # print('B2: %s' % B2)
        # print('C2: %s' % C1)
        # print('C1: %s' % C1)
        # print(' A: %s' % A)
        # print(' D: %s' % D)
        fntot = f1 + D
        rntot = A + B1 + r2

        if there_are_repetitions(fntot) or there_are_repetitions(rntot):
            raise_desc(NotImplementedError, 'Repeated names', fnames=fntot, rnames=fntot)

        # now I can create Ftot and Rtot
        f1_types = ndp1.get_ftypes(f1)

        D_types = ndp2.get_ftypes(D)
#         print('f1: %s' % f1)
#         print('f1 types: %s' % f1_types)
#         print('D: %s' % D)
#         print('D types: %s' % D_types)

        Ftot = PosetProduct(tuple(list(f1_types) + list(D_types)))
        Rtot = PosetProduct(tuple(list(ndp1.get_rtypes(A)) +
                                  list(ndp1.get_rtypes(B1)) +
                                  list(ndp2.get_rtypes(r2))))

        # print('Ftot: %s' % str(Ftot))
        # print('      %s' % str(fntot))
        # print('Rtot: %s' % str(Rtot))
        # print('      %s' % str(rntot))
        assert len(fntot) == len(Ftot), (fntot, Ftot)
        assert len(rntot) == len(Rtot), (rntot, Rtot)

        # I can create the first muxer m1
        # from ftot to Product(f1, D)

        m1_for_f1 = [fntot.index(s) for s in f1]
        m1_for_D = [fntot.index(s) for s in D]

        m1coords = [m1_for_f1, m1_for_D]
        m1 = Mux(Ftot, m1coords)

        # print('m1: %s' % m1)
        # print('m1.R: %s' % m1.get_res_space())

        # Get Identity on D
        D_types = ndp2.get_ftypes(D)
        Id_D = Identity(D_types)

        ndp1_p = its_dp_as_product(ndp1)
        X = make_parallel(ndp1_p, Id_D)

        # make sure we can connect
        m1_X = make_series(m1, X)
        # print('m1_X = %s' % m1_X)
        # print('m1_X.R = %s' % m1_X.get_res_space()  )
        
        def coords_cat(c1, m):
            if m != ():
                return c1 + (m,)
            else:
                return c1
        
        A_B1_types = PosetProduct(tuple(ndp1.get_rtypes(A)) + tuple(ndp1.get_rtypes(B1)))
        Id_A_B1 = Identity(A_B1_types)
        ndp2_p = its_dp_as_product(ndp2)
        Z = make_parallel(Id_A_B1, ndp2_p)
        # print('Z.R = %s' % Z.get_res_space())
        # print('B1: %s' % B1)
        # print('R2: %s' % r2)
        m2coords_A = [(0, (A + B1).index(x)) for x in A]
        m2coords_B1 = [(0, (A + B1).index(x)) for x in B1]
        m2coords_r2 = [(1, r2.index(x)) for x in r2]
        m2coords = m2coords_A + m2coords_B1 + m2coords_r2
        # print('m2coords_A: %r' % m2coords_A)
        # print('m2coords_B1: %r' % m2coords_B1)
        # print('m2coords_r2: %r' % m2coords_r2)
        # print('m2coords: %r' % m2coords)

        # print('Z.R: %s' % Z.get_res_space())
        m2 = Mux(Z.get_res_space(), m2coords)
        
        assert len(m2.get_res_space()) == len(rntot), ((m2.get_res_space(), rntot))
        # make sure we can connect
        make_series(Z, m2)

        #
        #  f0 -> |m1| -> | X | -> |Y |-> |Z| -> |m2| -> r0
        #
        # X = dp1 | Id_D
        # Z = Id_B1 | dp2

        #      ___
        #     |   |------------------------->A
        #     |   |          |-B1----------->
        # f1->|   |--B1----->|         ___
        #     | 1 |          |----B2->|   |
        #     |___| -C1-----------C2->| 2 |->r2
        # ---------D----------------->|___|

        #      ___
        #     |   |-------------------------------->A
        #     |   |  .            *-B1-------.----->
        # f1->|   |  . |--B1----->*          .   ___
        #     | 1 |--.-|          *----B2->| .  |   |
        #     |___|  . |-C1------------C2->|-.->| 2 |->r2
        # ---------D-.-------------------->| .  |___|
        # m1  | X | Y                        |  Z    | m2

        # I need to write the muxer
        # look at the end
        # iterate 2's functions

        Y_coords_A_B1 = []
        for x in A:
            Y_coords_A_B1.append((0, r1.index(x)))
        for x in B1:
            Y_coords_A_B1.append((0, r1.index(x)))
        
        Y_coords_B2_C2_D = []
        for x in f2:
            if (x in B2) or (x in C2):
                Y_coords_B2_C2_D.append((0, r1.index(s1_from_s2(x))))
                assert x not in D
            elif x in D:
                Y_coords_B2_C2_D.append((1, D.index(x)))
            else:
                assert False

        # print ('Y_coords_A_B1: %s' % Y_coords_A_B1)
        # print ('Y_coords_B2_C2_D: %s' % Y_coords_B2_C2_D)
        Y_coords = [Y_coords_A_B1, Y_coords_B2_C2_D]
        Y = Mux(m1_X.get_res_space(), Y_coords)

        # m1* Xp Y* Zp m2*
        # Let's make series
        # m1_X is simplifed
        Y_Z = make_series(Y, Z)
        Y_Z_m2 = make_series(Y_Z, m2)

        res_dp = make_series(m1_X, Y_Z_m2)

        fnames = fntot
        rnames = rntot

        res_dp, fnames, rnames = simplify_if_only_one_name(res_dp, fnames, rnames)

        # print('res_dp: %s' % res_dp)
        res = dpwrap(res_dp, fnames, rnames)

        return res

    except Exception as e:
        msg = 'connect2() failed'
        raise_wrapped(DPInternalError, e, msg, ndp1=ndp1, ndp2=ndp2,
                      connections=connections, split=split)

def simplify_if_only_one_name(res_dp, fnames, rnames):
    if len(fnames) == 1:
        fnames = fnames[0]
        funsp = res_dp.get_fun_space()
        res_dp = make_series(Mux(funsp[0], [()]), res_dp)

    if len(rnames) == 1:
        rnames = rnames[0]
        ressp = res_dp.get_res_space()
        res_dp = make_series(res_dp, Mux(ressp, 0))
    return res_dp, fnames, rnames


def make_name(already):
    for i in range(1, 1000):
        candidate = 'group%d' % i
        if not candidate in already:
            return candidate
    assert False


@contract(connections='set($Connection)')
def get_connection_graph(names, connections):
    G = DiGraph()
    # add names to check if it is connected
    for n in names:
        G.add_node(n)
    for c in connections:
        dp1 = c.dp1
        dp2 = c.dp2
        G.add_edge(dp1, dp2)
    return G

@contract(name2dp='dict(str:*)', connections='set($Connection)')
def order_dps(name2dp, connections):
    """ Returns a total order consistent with the partial order """
    names = set(name2dp)

    # List the ones that have no functions or no resources

    # a >= 10 g (no functions)
    # b <= 10 s (no resources)

# #     no_functions = set()
# #     no_resources = set()
# #
# #     for name, ndp in name2dp.items():
# #         if not ndp.get_fnames():
# #             no_functions.add(name)
# #         if not ndp.get_rnames():
# #             no_resources.add(name)
#
#     print('no_functions: %s' % no_functions)
#     print('no_resources: %s' % no_resources)

    G = get_connection_graph(names, connections)
    # I should probably think more about this
#     for nf in no_functions:
#         for nr in no_resources:
#             G.add_edge(nr, nf)

    Gu = G.to_undirected()
    if not is_connected(Gu):
        msg = 'The graph is not weakly connected. (missing constraints?)'
        msg += '\nNames: %s' % names
        msg += '\nconnections: %s' % connections
        raise DPSemanticError(msg)
    l = topological_sort(G)
    if not (set(l) == names):
        msg = 'names = %s\n returned = %s\n connections: %s' % (names, l, connections)
        msg += '\n graph: %s %s' % (list(Gu.nodes()), list(Gu.edges()))
        raise DPInternalError(msg)
    return l


# 
# @contract(ndp=NamedDP, lf='str', lr='str', returns=NamedDP)
# def dploop0(ndp, lr, lf):
#     try:
#             
#         ndp.rindex(lr)
#         ndp.findex(lf)
#     
#         #
#         # This is the version in the papers
#         #           ______
#         #    f1 -> |  dp  |--->r
#         #    f2 -> |______|R|
#         #       `-----------/
#         #            _____
#         #  A------->|     |--B--|
#         #     |-o   | ndp |     |--->
#         #  -R-|-lf->|_____|--lr-| |
#         #  `--------(>=)----------/
#         #
#         # write as dploop0(series(X, dp))
#         #
#         # where X is a mux with function space A * R
#         # and coords
#         R = ndp.get_dp().get_res_space()
#     
#         F0 = ndp.get_fnames()
#         A = list(F0)  # preserve order
#         A.remove(lf)
#     
#         def coord_concat(a, b):
#             if b == (): return a
#             return a + (b,)
#     
#         if len(A) == 1:
#             F = PosetProduct((ndp.get_ftype(A[0]), R))
#         else:
#             F = PosetProduct((ndp.get_ftypes(A), R))
# 
#         # print('A: %s' % A)
#         # print('F: %s' % F)
# 
#         coords = []
#         for x in ndp.get_fnames():
#             if x in A:
#                 i = A.index(x)
#                 if len(A) != 1:
#                     coords.append(coord_concat((0,), i))
#                 else:
#                     coords.append(0)  # just get the one A
#             if x == lf:
#                 # print('x = lf = %s' % x)
#                 xc = coord_concat((1,), ndp.rindex(lr))
#                 coords.append(xc)
# 
# 
#         mcdp_dev_warning('This is a trick')
#         if len(coords) == 1:
#             coords = coords[0]
#     
#         X = Mux(F, coords)
#         # print('X = %s' % X.repr_long())
#         dp = ndp.get_dp()
#         # print('dp = %s' % dp.repr_long())
#         S = make_series(X, dp)
#         # print('S = %s' % S)
#         
#         res_dp = make_loop(S)
#         rnames = ndp.get_rnames()
#         fnames = A
#     
#         if len(fnames) == 1:
#     #         print('At this point, res_dp')
#     #         funsp = res_dp.get_fun_space()
#     #         res_dp = make_series(Mux(funsp[0], [()]), res_dp)
#             fnames = fnames[0]
#     
#         ressp = res_dp.get_res_space()
#         if len(rnames) == 1:
#             if isinstance(ressp, PosetProduct):
#                 res_dp = make_series(res_dp, Mux(ressp, 0))
#                 rnames = rnames[0]
#             else:
#                 rnames = rnames[0]  # XXX
#     
#         res = dpwrap(res_dp, fnames, rnames)
#         return res
#     except DPInternalError as e:
#         msg = 'Error while calling dploop0( lr = %s -> lf = %s) ' % (lr, lf)
#         raise_wrapped(DPInternalError, e, msg, ndp=ndp.repr_long())

@contract(cndp=CompositeNamedDP, returns=SimpleWrap)
def cndp_dpgraph(cndp):
    """ Assumes that the graph is weakly connected. """
    name2dp = cndp.get_name2ndp()
    connections = cndp.get_connections()
    return dpgraph(name2dp, connections, split=[])


@contract(returns='set(tuple(str, str))')
def find_resources_with_multiple_connections(connections):
    all_of_them = [(c.dp1, c.s1) for c in connections]
    counter = Counter(all_of_them)
    multiple = [k for k, v in counter.items() if v >= 2]
    return set(multiple)


@contract(returns='set(tuple(str, str))')
def find_functions_with_multiple_connections(connections):
    all_of_them = [(c.dp2, c.s2) for c in connections]
    counter = Counter(all_of_them)
    multiple = [k for k, v in counter.items() if v >= 2]
    return set(multiple)
    

@contract(name2dp='dict(str:$NamedDP)',
          connections='set(str|$Connection)|list(str|$Connection)',
          returns=SimpleWrap)
def dpgraph(name2dp, connections, split):
    """ 
    
        This assumes that the graph is weakly connected
        and that there are no repetitions of names of resources
        or functions.
        
        It also assumes that each function/resource 
        is connected to exactly one function/resource.
        
    """
    if not len(set(split)) == len(split):
        raise ValueError('dpgraph: Repeated signals in split: %s' % str(split))

    if not(name2dp):
        assert not connections
        assert not split
        dp = Mux(PosetProduct(()), [])
        return dpwrap(dp, [], [])

    rmc = find_resources_with_multiple_connections(connections)
    if rmc:
        msg = 'These resources have multiple connections.'
        raise_desc(ValueError, msg, rmc=rmc)

    fmc = find_functions_with_multiple_connections(connections)
    if fmc:
        msg = 'These resources have multiple connections.'
        raise_desc(ValueError, msg, fmc=fmc)

    # check that there are no repetitions
    if there_are_reps(name2dp):
        name2dp_, connections_, relabeling = relabel(name2dp, connections)
        print('relabeling: %s' % relabeling)
        assert not there_are_reps(name2dp_)
        # XXX: what do we do with split?
        return dpgraph(name2dp_, connections_, split)

    res = dpgraph_(name2dp, connections, split)

    try:
        for x in split:
            res.rindex(x)
    except DPInternalError as e:
        msg = 'Invalid result from dpgraph_().'
        raise_wrapped(DPInternalError, e, msg, res=res,
                      name2dp=name2dp, connections=connections,
                   split=split)
    return res

@contract(returns='set(tuple,seq(tuple(str, str)))')
def simple_cycles_as_edges(G):
    cycles = list(simple_cycles(G))
    def c2e(c):
        for i in range(len(c)):
            n1 = c[i]
            n2 = c[(i + 1) % len(c)]
            yield n1, n2

    return set([tuple(c2e(c)) for c in cycles])

@contract(returns=Connection)
def choose_connection_to_cut1(connections, name2dp):
    G = get_connection_multigraph(connections)

    from collections import defaultdict
    counts = defaultdict(lambda: 0)

    c_as_e = simple_cycles_as_edges(G)
    if not c_as_e:
        msg = 'There are no connections to cut.'
        raise_desc(ValueError, msg)
    
    for cycle in c_as_e:
        for edge in cycle:
            counts[edge] += 1

    ncycles = len(c_as_e)
    best_edge, ncycles_broken = max(list(counts.items()), key=lambda x: x[1])

    def find_one(a, b):
        for c in connections:
            if c.dp1 == a and c.dp2 == b:
                return c
        assert False

    its_connection = find_one(best_edge[0], best_edge[1])
    F = name2dp[its_connection.dp1].get_rtype(its_connection.s1)
    print('Min cut: breaking %d of %d cycles by removing %s, space = %s.' %
        (ncycles_broken, ncycles, str(its_connection), F))
    # print('its connection is %s' % str(its_connection))
    # print('querying F = %s ' % name2dp[its_connection.dp1].get_rtype(its_connection.s1))
    return its_connection


@contract(name2dp='dict(str:($NamedDP))',
          connections='set(str|$Connection)|list(str|$Connection)',
          returns=SimpleWrap)
def dpgraph_(name2dp, connections, split):

    try:
        connections = set(connections)
        check_connections(name2dp, connections)

        G = get_connection_multigraph(connections)
        cycles = list(simple_cycles(G))
        if not cycles:
            res = dpconnect(name2dp, connections, split=split)
            assert isinstance(res, SimpleWrap), (type(res), name2dp)
            return res

        # At this point we never resort to the rest -
        # this is always called without cycles
        assert False
#         c = choose_connection_to_cut1(connections, name2dp)
# 
#         other_connections = set()
#         other_connections.update(connections)
#         other_connections.remove(c)
# 
#         def connections_include_resource(conns, s):
#             for c in conns:
#                 if c.s1 == s:
#                     return True
#             else:
#                 return False
# 
#         # we have to make sure that the signal that we need is not closed
#         if connections_include_resource(other_connections, c.s1):
#             split1 = [c.s1]
#         else:
#             split1 = []
# 
#         split1.extend(split)
# 
#         ndp = dpgraph(name2dp, other_connections, split=split1)
# 
#         # now we make sure that the signals we have are preserved
#         ndp.rindex(c.s1)
#         ndp.findex(c.s2)
#         l = dploop0(ndp, c.s1, c.s2)
# 
#         l.rindex(c.s1)
# 
#         if c.s1 in split:
#             return l
# 
#         else:
#             F = ndp.get_rtype(c.s1)
#             term = dpwrap(Terminator(F), c.s1, [])
# 
#             res = connect2(l, term,
#                            set([Connection("-", c.s1, "-", c.s1)]), split=[])
# 
#             return res
    except DPSemanticError as e:
        raise_wrapped(DPSemanticError, e, 'Error while calling dpgraph().',
                      compact=True,
                      names=format_dict_long(name2dp, informal=True),
                      connection=format_list_long(connections, informal=True))
    except DPInternalError as e:
        raise_wrapped(DPInternalError, e, 'Error while calling dpgraph().',
                      names=format_dict_long(name2dp, informal=True),
                      connection=format_list_long(connections, informal=True))


@contract(connections='set($Connection)')
def get_connection_multigraph(connections):
    G = MultiDiGraph()
    for c in connections:
        dp1 = c.dp1
        dp2 = c.dp2
        G.add_edge(dp1, dp2, s1=c.s1)
    return G


@contract(connections='set($Connection)')
def get_connection_multigraph_weighted(name2dp, connections):
    G = MultiDiGraph()
    for c in connections:
        dp1 = c.dp1
        dp2 = c.dp2
        if not G.has_edge(dp1, dp2):
            already = []
            G.add_edge(dp1, dp2)
        else:
            already = G.edge[dp1][dp2]['spaces']
        R = name2dp[c.dp1].get_rtype(c.s1)
        already.append(R)
        G.edge[dp1][dp2]['spaces'] = already

#     cycles = list(simple_cycles(G))
#     for cycle in cycles:
#         cycle = list(cycle)
#         cycle = cycle + [cycle[0]]
#         
#         for i in range(len(cycle) - 1):
#             # XXX
#             _val = G.edge[cycle[i]][cycle[i + 1]]['spaces']
#             # print('%s -> %s -> %s' % (cycle[i], val, cycle[i + 1]))

    return G
    