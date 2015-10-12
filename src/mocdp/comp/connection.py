from collections import namedtuple
from contracts import contract
from contracts.utils import raise_wrapped
from mocdp.comp.interfaces import NamedDP
from mocdp.comp.wrap import dpwrap
from mocdp.configuration import get_conftools_nameddps
from mocdp.dp.dp_flatten import Mux
from mocdp.dp.dp_identity import Identity
from mocdp.dp.dp_loop import DPLoop, DPLoop0
from mocdp.dp.dp_parallel import Parallel
from mocdp.dp.dp_series import Series
from mocdp.posets.poset_product import PosetProduct
from networkx.algorithms.components.connected import is_connected
from networkx.algorithms.cycles import simple_cycles
from networkx.algorithms.dag import topological_sort
from networkx.exception import NetworkXUnfeasible
import networkx
import re

Connection = namedtuple('Connection', 'dp1 s1 dp2 s2')

def _parse(cstring):
    """ power.a >= battery.b """
    c = re.compile(r'\s*(\w+)\s*\.(\w+)\s*>=\s*(\w+)\s*\.(\w+)\s*')
    m = c.match(cstring)

    dp2 = m.group(1)
    s2 = m.group(2)
    dp1 = m.group(3)
    s1 = m.group(4)
    return Connection(dp1=dp1, s1=s1, dp2=dp2, s2=s2)


def parse_connection(s):
    if isinstance(s, Connection):
        return s
    if isinstance(s, str):
        return _parse(s)

    raise ValueError(s)

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
 
@contract(name2dp='dict(str:($NamedDP|str|code_spec))',
          connections='set(str|$Connection)|list(str|$Connection)',
          returns=NamedDP)
def dpconnect(name2dp, connections):
    """
        Raises TheresALoop
    """
    if len(name2dp) < 2:
        raise ValueError()

    for k, v in name2dp.items():
        _, name2dp[k] = get_conftools_nameddps().instance_smarter(v)

    connections = set(map(parse_connection, connections))
    check_connections(name2dp, connections)

    # A, B, C

    # A  I  C
    # I  B  I

    # First, we need to order the dps using topological sorting
    try:
        order = order_dps(set(name2dp), connections)
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

    # these are other names that need to be preserved for the first 1

    split = [c.s1
             for c in connections
             if c.dp1 == first and c.dp2 != second]

    dp = connect2(name2dp[first], name2dp[second], set(first_connections), split=split)

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

    return dpconnect(name2dp, set(other_connections))

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
        dp = Series(down, dp)

    if len(ndp.get_rnames()) == 1:
        R0 = dp.get_res_space()
#         R = PosetProduct((R0,))
        lift = Mux(R0, [()])
        dp = Series(dp, lift)

    return dp

@contract(ndp1=NamedDP, ndp2=NamedDP,
          connections='set($Connection)',
          split='list(str)',
          returns=NamedDP)
def connect2(ndp1, ndp2, connections, split):
    """ Note the argument split must be strings so that orders are preserved
        and deterministic. """
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

        print('B1: %s' % B1)
        print('B2: %s' % B2)
        print('C2: %s' % C1)
        print('C1: %s' % C1)
        print(' A: %s' % A)
        print(' D: %s' % D)
        fntot = f1 + D
        rntot = A + B1 + r2

        # now I can create Ftot and Rtot
        Ftot = PosetProduct(tuple(list(ndp1.get_ftypes(f1)) + list(ndp2.get_ftypes(D))))
        Rtot = PosetProduct(tuple(list(ndp1.get_rtypes(A)) +
                                  list(ndp1.get_rtypes(B1)) +
                                  list(ndp2.get_rtypes(r2))))

        print('Ftot: %s' % str(Ftot))
        print('      %s' % str(fntot))
        print('Rtot: %s' % str(Rtot))
        print('      %s' % str(rntot))
        assert len(fntot) == len(Ftot)
        assert len(rntot) == len(Rtot)


        # I can create the first muxer m1
        # from ftot to Product(f1, D)

        m1_for_f1 = [fntot.index(s) for s in f1]
        m1_for_D = [fntot.index(s) for s in D]

        m1coords = [m1_for_f1, m1_for_D]
        m1 = Mux(Ftot, m1coords)

        print('m1: %s' % m1)
        print('m1.R: %s' % m1.get_res_space())

        # Get Identity on D
        D_types = ndp2.get_ftypes(D)
        Id_D = Identity(D_types)

        ndp1_p = its_dp_as_product(ndp1)
        X = Parallel(ndp1_p, Id_D)

        # make sure we can connect
        m1_X = Series(m1, X)
        print('m1_X = %s' % m1_X)
        print('m1_X.R = %s' % m1_X.get_res_space()  )      
        
        
        def coords_cat(c1, m):
            if m != ():
                return c1 + (m,)
            else:
                return c1
        
        A_B1_types = PosetProduct(tuple(ndp1.get_rtypes(A)) + tuple(ndp1.get_rtypes(B1)))
        Id_A_B1 = Identity(A_B1_types)
        ndp2_p = its_dp_as_product(ndp2)
        Z = Parallel(Id_A_B1, ndp2_p)
        print('Z.R = %s' % Z.get_res_space())
        print('B1: %s' % B1)
        print('R2: %s' % r2)
        m2coords_A = [(0, (A + B1).index(x)) for x in A]
        m2coords_B1 = [(0, (A + B1).index(x)) for x in B1]
        m2coords_r2 = [(1, r2.index(x)) for x in r2]
        m2coords = m2coords_A + m2coords_B1 + m2coords_r2
        print('m2coords_A: %r' % m2coords_A)
        print('m2coords_B1: %r' % m2coords_B1)
        print('m2coords_r2: %r' % m2coords_r2)
        print('m2coords: %r' % m2coords)

        print('Z.R: %s' % Z.get_res_space())
        m2 = Mux(Z.get_res_space(), m2coords)
        
        assert len(m2.get_res_space()) == len(rntot), ((m2.get_res_space(), rntot))
        # make sure we can connect
        Z_m2 = Series(Z, m2)

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

        print ('Y_coords_A_B1: %s' % Y_coords_A_B1)
        print ('Y_coords_B2_C2_D: %s' % Y_coords_B2_C2_D)
        Y_coords = [Y_coords_A_B1, Y_coords_B2_C2_D]
        Y = Mux(m1_X.get_res_space(), Y_coords)

        m1_X_Y = Series(m1_X, Y)
        _Y_Z_m2 = Series(Y, Z_m2)
        res_dp = Series(m1_X_Y, Z_m2)

        fnames = fntot
        rnames = rntot

        if len(fnames) == 1:
            fnames = fnames[0]
            funsp = res_dp.get_fun_space()
            res_dp = Series(Mux(funsp[0], [()]), res_dp)

        if len(rnames) == 1:
            rnames = rnames[0]
            ressp = res_dp.get_res_space()
            res_dp = Series(res_dp, Mux(ressp, 0))

        print('res_dp: %s' % res_dp)
        res = dpwrap(res_dp, fnames, rnames)

        return res

#         mux_B2_C2_D = []
#         if D:
#             for x in ndp2.get_fnames():
#                 if x in B2:
#                     i = (0,)
#                     a = ndp1.rindex(s1_from_s2(x))
#                     if a != ():
#                         i = i + (a,)
#                     mux_B2_C2_D.append(i)
#     #                 print('B2[%s] got %s' % (x, i))
#                     assert x not in C2 and x not in D
#                 if x in C2:
#                     a = ndp1.rindex(s1_from_s2(x))
#                     i = (0,)
#                     if a != ():
#                         i = i + (a,)
#     #                 print('C2[%s] got %s' % (x, i))
#                     mux_B2_C2_D.append(i)
#                     assert x not in D
#                 if x in D:
#                     if len(D) == 1:
#                         i = (1,)
#                     else:
#                         i = (1, D.index(x))
#
#     #                 print('D[%s] giv %s ' % (x, i))
#                     mux_B2_C2_D.append(i)
#         else:
#             for x in ndp2.get_fnames():
#                 if x in B2:
#                     i = ndp1.rindex(s1_from_s2(x))
#                     mux_B2_C2_D.append(i)
#                 if x in C2:
#                     i = ndp1.rindex(s1_from_s2(x))
#                     mux_B2_C2_D.append(i)
#
#         if B1:
#             mux_B1 = [(0, ndp1.rindex(s)) for s in B1]
#             coords = [mux_B1, mux_B2_C2_D]
#         else:
#             coords = mux_B2_C2_D
#
#         F = X.get_res_space()
#     #     print('Creating Mux from F = %r, coords= %r ' % (F, coords))
#         if len(coords) == 1:
#             coords = coords[0]
#         Y = Mux(coords=coords, F=F)



    except Exception as e:
        msg = 'connect2() failed'
        raise_wrapped(Exception, e, msg, ndp1=ndp1, ndp2=ndp2, connections=connections, split=split)


def make_name(already):
    for i in range(1, 10):
        candidate = 'group%d' % i
        if not candidate in already:
            return candidate
    assert False


@contract(connections='set($Connection)')
def get_connection_graph(names, connections):
    G = networkx.DiGraph()
    # add names to check if it is connected
    for n in names:
        G.add_node(n)
    for c in connections:
        dp1 = c.dp1
        dp2 = c.dp2
        G.add_edge(dp1, dp2)
    return G

@contract(names='set(str)', connections='set($Connection)')
def order_dps(names, connections):
    """ Returns a total order consistent with the partial order """
    G = get_connection_graph(names, connections)
    Gu = G.to_undirected()
    if not is_connected(Gu):
        msg = 'The graph is not weakly connected. (missing constraints?)'
        msg += '\nNames: %s' % names
        msg += '\nconnections: %s' % connections
        raise Exception(msg)
    l = topological_sort(G)
    if not (set(l) == names):
        msg = 'names = %s\n returned = %s\n connections: %s' % (names, l, connections)
        msg += '\n graph: %s %s' % (list(Gu.nodes()), list(Gu.edges()))
        raise Exception(msg)
    return l

#
# @contract(ndp=NamedDP, lf='str', lr='str', returns=NamedDP)
# def dploop(ndp, lr, lf):
#     #  A----> |     |--B----->
#     #         | ndp |
#     #  lf---->|_____|-----lr
#     #  `--------(>=)------/
#     #
#
#     ndp.rindex(lr)
#     ndp.findex(lf)
#
#     F0 = ndp.get_fnames()
#     A = list(set(F0) - set([lf]))
#     assert not lf in A
#     R0 = ndp.get_rnames()
#     B = list(set(R0) - set([lr]))
#     # X is now the product space
#     F = PosetProduct((ndp.get_ftypes(A), ndp.get_ftype(lf)))
#     coords = []
#     for x in F0:
#         if x == lf:
#             coords.append(1)
#         else:
#             coords.append((0, A.index(x)))
#     X = Mux(F, coords)
#
#     R = ndp.get_dp().get_res_space()
#     coords_B = [ ndp.rindex(x) for x in B]
#     coords = [coords_B, ndp.rindex(lr)]
#     Y = Mux(R, coords)
#
#     print('Y res: %s' % Y.get_res_space())
# #     print('TRyingt to interconnect %s' % ndp.get_dp())
#     Series(ndp.get_dp(), Y)
#
#     a = Series(X, ndp.get_dp())
#
#     if Y is not None:
#         dp = Series(a, Y)
#     else:
#         dp = a
#
#     res_dp = DPLoop(dp)
#
#     print('fnames: %s ' % A)
#     print('rnames: %s ' % B)
#     if len(A) == 1:
#         A = A[0]
#     if len(B) == 1:
#         B = B[0]
#     res = dpwrap(res_dp, fnames=A, rnames=B)
#
#     return res


if False:
    @contract(ndp=NamedDP, lf='str', lr='str', returns=NamedDP)
    def dploop2(ndp, lr, lf):
        #  A----> |     |--B----->
        #         | ndp |  *---lr->
        #  lf---->|_____|--*--lr
        #  `--------(>=)------/
        #

        ndp.rindex(lr)
        ndp.findex(lf)

        F0 = ndp.get_fnames()
        A = list(set(F0) - set([lf]))
        R0 = ndp.get_rnames()
        B = list(set(R0) - set([lr]))
        # X is now the product space
        F = PosetProduct((ndp.get_ftypes(A), ndp.get_ftype(lf)))
        coords = []
        for x in F0:
            if x == lf:
                coords.append(1)
            else:
                coords.append((0, A.index(x)))
        X = Mux(F, coords)

        R = ndp.get_dp().get_res_space()
        coords_Blr = [ ndp.rindex(x) for x in B]
        coords_Blr.append(ndp.rindex(lr))
        coords = [coords_Blr, ndp.rindex(lr)]
        Y = Mux(R, coords)

        Series(ndp.get_dp(), Y)

        a = Series(X, ndp.get_dp())

        if Y is not None:
            dp = Series(a, Y)
        else:
            dp = a
        res_dp = DPLoop(dp)

        fnames = A
        rnames = R0
        if len(fnames) == 1:
            funsp = res_dp.get_fun_space()
            res_dp = Series(Mux(funsp[0], [()]), res_dp)
            fnames = fnames[0]
        if len(rnames) == 1:
            ressp = res_dp.get_res_space()
            res_dp = Series(res_dp, Mux(ressp, 0))
            rnames = rnames[0]
        res = dpwrap(res_dp, fnames, rnames)

        return res


@contract(ndp=NamedDP, lf='str', lr='str', returns=NamedDP)
def dploop0(ndp, lr, lf):
    ndp.rindex(lr)
    ndp.findex(lf)

    #
    # This is the version in the papers
    #           ______
    #    f1 -> |  dp  |--->r
    #    f2 -> |______|R|
    #       `-----------/
    #            _____
    #  A------->|     |--B--|
    #     |-o   | ndp |     |--->
    #  -R-|-lf->|_____|--lr-| |
    #  `--------(>=)----------/
    #
    # write as dploop0(series(X, dp))
    #
    # where X is a mux with function space A * R
    # and coords
    R = ndp.get_dp().get_res_space()

    F0 = ndp.get_fnames()
    A = list(F0)  # preserve order
    A.remove(lf)

    def coord_concat(a, b):
        if b == (): return a
        return a + (b,)

    F = PosetProduct((ndp.get_ftypes(A), R))
    coords = []
    for x in ndp.get_fnames():
        if x in A:
            i = A.index(x)
            coords.append(coord_concat((0,), i))
        if x == lf:
            coords.append(coord_concat((1,), ndp.rindex(lr)))

    X = Mux(F, coords)
    
    res_dp = DPLoop0(Series(X, ndp.get_dp()))
    rnames = ndp.get_rnames()
    fnames = A

    if len(fnames) == 1:
        funsp = res_dp.get_fun_space()
        res_dp = Series(Mux(funsp[0], [()]), res_dp)
        fnames = fnames[0]

    ressp = res_dp.get_res_space()
    if len(rnames) == 1:
        if isinstance(ressp, PosetProduct):
            res_dp = Series(res_dp, Mux(ressp, 0))
            rnames = rnames[0]
        else:
            rnames = rnames[0]  # XXX

    res = dpwrap(res_dp, fnames, rnames)
    return res


@contract(name2dp='dict(str:($NamedDP|str|code_spec))',
          connections='set(str|$Connection)|list(str|$Connection)',
          returns=NamedDP)
def dpgraph(name2dp, connections):
    if len(name2dp) < 2:
        msg = 'I only have %d names: %s' % (len(name2dp), list(name2dp))
        raise ValueError(msg)

    for k, v in name2dp.items():
        _, name2dp[k] = get_conftools_nameddps().instance_smarter(v)

    connections = set(map(parse_connection, connections))
    check_connections(name2dp, connections)

    G = get_connection_multigraph(connections)
    cycles = list(simple_cycles(G))
    if not cycles:
        return dpconnect(name2dp, connections)

    # choose one constraint
    cycle0 = cycles[0]
    # get one connection that breaks the cycle
    first = cycle0[0]
    second = cycle0[1]
    def find_one(a, b):
        for c in connections:
            if c.dp1 == a and c.dp2 == b:
                return c
        assert False
    c = find_one(first, second)
    
    other_connections = set()
    other_connections.update(connections)
    other_connections.remove(c)
    
    ndp = dpgraph(name2dp, other_connections)
#     print('Ignoring %s, obtain %s' % (c, ndp.desc()))
    return dploop0(ndp, c.s1, c.s2)


@contract(connections='set($Connection)')
def get_connection_multigraph(connections):
    G = networkx.MultiDiGraph()
    for c in connections:
        dp1 = c.dp1
        dp2 = c.dp2
        G.add_edge(dp1, dp2, s1=c.s1)
    return G

    


