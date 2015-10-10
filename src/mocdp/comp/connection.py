from collections import namedtuple
import re
from contracts import contract
from mocdp.comp.interfaces import NamedDP
import networkx
from networkx.algorithms.dag import topological_sort
from networkx.exception import NetworkXUnfeasible
from mocdp.dp.dp_identity import Identity
from mocdp.dp.dp_parallel import Parallel
from mocdp.dp.dp_flatten import Mux
from contracts.utils import raise_wrapped
from mocdp.dp.dp_series import Series
from mocdp.comp.wrap import SimpleWrap, dpwrap

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

@contract(name2dp='dict(str:$NamedDP)', connections='set(str|$Connection)|list(str|$Connection)',
          returns=NamedDP)
def dpconnect(name2dp, connections):
    if len(name2dp) < 2:
        raise ValueError()
    connections = set(map(parse_connection, connections))
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

    # A, B, C

    # A  I  C
    # I  B  I

    # First, we need to order the dps using topological sorting
    try:
        order = order_dps(set(name2dp), connections)
    except NetworkXUnfeasible:
        raise NotImplementedError()

    # Now let's pick the first two
    first = order[0]
    second = order[1]
    # these are the connections for the first two
    belongs_first = lambda c: set([c.dp1, c.dp2]) == set([first, second])
    not_belongs_first = lambda c: not belongs_first(c)
    first_connections = filter(belongs_first, connections)

    # these are other names that need to be preserved for the first 1

    split = set([c.s1
                 for c in connections
                 if c.dp1 == first and c.dp2 != second])

    dp = connect2(name2dp[first], name2dp[second], set(first_connections), split=split)

    others = order[2:]
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

@contract(ndp1=NamedDP, ndp2=NamedDP, returns=NamedDP, connections='set($Connection)')
def connect2(ndp1, ndp2, connections, split):
    #
    #     |   |          |-B1--------->
    # f1->|   |--B1----->|         ___
    #     | 1 |          |----B2->|   |
    #     |___| -C1--C2---------->| 2 |->r2
    # ---------D----------------->|___|
    #
    # f = f1 + D
    # r = r2 + A
    # A + B + C = r1
    # B + C + D = f2
    # split = A + B

    f1 = ndp1.get_fnames()
    f2 = ndp2.get_fnames()
    r1 = ndp1.get_rnames()
    r2 = ndp2.get_rnames()
    # split = B1 is given
    # find B2 from B1
    def s2_from_s1(s1):
        for c in connections:
            if c.s1 == s1: return c.s2
        assert False
    def s1_from_s2(s2):
        for c in connections:
            if c.s2 == s2: return c.s1
        assert False
    B1 = list(split)
    B2 = map(s2_from_s1, B1)
    # Find C2
    all_s2 = set([c.s2 for c in connections])
    C2 = [x for x in all_s2 if not x in B2]
    # Find C1
    C1 = map(s1_from_s2, C2)
    # Find D
    D = [x for x in f2 if (x not in B2) and (x not in C2)]

#     f0 = f1 + D
#     r0 = B1 + r2
  
    #
    #  f0 -> | X | -> |Y |-> |Z| -> r0
    #
    # X = [parallel 1, Id_D]
 
    #      ___
    #     |   |          |-B1--------->
    # f1->|   |--B1----->|         ___
    #     | 1 |          |----B2->|   |
    #     |___| -C1-----------C2->| 2 |->r2
    # ---------D----------------->|___|
    
    if D:
        D_types = ndp2.get_ftypes(D)
        Id_D = Identity(D_types)
        X = Parallel(ndp1.get_dp(), Id_D)
    else:
        X = ndp1.get_dp()

    if B1:
        B1_types = ndp1.get_rtypes(B1)
        Id_B1 = Identity(B1_types)
        Z = Parallel(Id_B1, ndp2.get_dp())
    else:
        Z = ndp2.get_dp()


#     B2_types = ndp2.get_ftypes(B2)



    #      ___
    #     |   |  .            *-B1-------.----->
    # f1->|   |  . |--B1----->*          .   ___
    #     | 1 |--.-|          *----B2->| .  |   |
    #     |___|  . |-C1------------C2->|-.->| 2 |->r2
    # ---------D-.-------------------->| .  |___|

#     print('Xr', X.get_res_space())
#     print('Zf', Z.get_fun_space())
#     print 'X', X
#     print 'Z', Z

    # I need to write the muxer
    # look at the end
    # iterate 2's functions
    mux_B2_C2_D = []
    if D:
        for x in ndp2.get_fnames():
            if x in B2:
                i = (0, ndp1.rindex(s1_from_s2(x)))
                mux_B2_C2_D.append(i)
                assert x not in C2 and x not in D
            if x in C2:
                i = (0, ndp1.rindex(s1_from_s2(x)))
                mux_B2_C2_D.append(i)
                assert x not in D
            if x in D:
                i = (1, D.index(x))
                mux_B2_C2_D.append(i)
    else:
        for x in ndp2.get_fnames():
            if x in B2:
                i = ndp1.rindex(s1_from_s2(x))
                mux_B2_C2_D.append(i)
            if x in C2:
                i = ndp1.rindex(s1_from_s2(x))
                mux_B2_C2_D.append(i)



    if B1:
        mux_B1 = [(0, ndp1.rindex(s)) for s in B1]
        coords = [mux_B1, mux_B2_C2_D]
    else:
        coords = mux_B2_C2_D

    F = X.get_res_space()
    Y = Mux(coords=coords, F=F)
#
#     print('fun m', Y.get_fun_space())
#     print('res m', Y.get_res_space())

    A = Series(X, Y)
    Series(Y, Z)
    res_dp = Series(A, Z)

    fnames = f1 + D
    rnames = B1 + r2
    res = dpwrap(res_dp, fnames, rnames)

    print('Connect fun = %s' % res_dp.get_fun_space())
    print('        res = %s' % res_dp.get_res_space())
    return res



def make_name(already):
    for i in range(1, 10):
        candidate = 'group%d' % i
        if not candidate in already:
            return candidate
    assert False



@contract(names='set(str)', connections='set($Connection)')
def order_dps(names, connections):
    """ Returns a total order consistent with the partial order """ 

    G = networkx.DiGraph()
    for c in connections:
        dp1 = c.dp1
        dp2 = c.dp2
        G.add_edge(dp1, dp2)
        
    l = topological_sort(G)
    print l
    
    assert set(l) == names 
    return l

