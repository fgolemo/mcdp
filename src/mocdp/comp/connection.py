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
from mocdp.comp.wrap import  dpwrap
from mocdp.posets.poset_product import PosetProduct
from mocdp.dp.dp_loop import DPLoop
from mocdp.configuration import get_conftools_nameddps

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
        raise TheresALoop()

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
    #     |   |          |-B1(split)----->
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
#     C1 = map(s1_from_s2, C2)
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
        if len(D) == 1:
            D_type = ndp2.get_ftype(D[0])
            Id_D = Identity(D_type)
        else:
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


    #      ___
    #     |   |  .            *-B1-------.----->
    # f1->|   |  . |--B1----->*          .   ___
    #     | 1 |--.-|          *----B2->| .  |   |
    #     |___|  . |-C1------------C2->|-.->| 2 |->r2
    # ---------D-.-------------------->| .  |___|


    # I need to write the muxer
    # look at the end
    # iterate 2's functions
    mux_B2_C2_D = []
    if D:
        for x in ndp2.get_fnames():
            if x in B2:
                i = (0,)
                a = ndp1.rindex(s1_from_s2(x))
                if a != ():
                    i = i + (a,)
                mux_B2_C2_D.append(i)
#                 print('B2[%s] got %s' % (x, i))
                assert x not in C2 and x not in D
            if x in C2:
                a = ndp1.rindex(s1_from_s2(x))
                i = (0,)
                if a != ():
                    i = i + (a,)
#                 print('C2[%s] got %s' % (x, i))
                mux_B2_C2_D.append(i)
                assert x not in D
            if x in D:
                if len(D) == 1:
                    i = (1,)
                else:
                    i = (1, D.index(x))

#                 print('D[%s] giv %s ' % (x, i))
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
#     print('Creating Mux from F = %r, coords= %r ' % (F, coords))
    if len(coords) == 1:
        coords = coords[0]
    Y = Mux(coords=coords, F=F)


    A = Series(X, Y)
    Series(Y, Z)
    res_dp = Series(A, Z)

    fnames = f1 + D
    rnames = B1 + r2
#     print('ndp1:%s' % ndp1.desc())
#     print('res_dp', res_dp.get_fun_space())
    if len(fnames) == 1:
        fnames = fnames[0]
    if len(rnames) == 1:
        rnames = rnames[0]
    res = dpwrap(res_dp, fnames, rnames)

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
    
    assert set(l) == names 
    return l

@contract(ndp=NamedDP, lf='str', lr='str', returns=NamedDP)
def dploop(ndp, lr, lf):
    print(ndp.desc())
    print('lr', lr)
    print('lf', lf)
    #  A----> |     |--B----->
    #         | ndp |
    #  lf---->|_____|-----lr
    #  `--------(>=)------/
    #

    # of --> |dp| --> or
    # lf              lr
    #
    ndp.rindex(lr)
    ndp.findex(lf)

    F0 = ndp.get_fnames()
    A = list(set(F0) - set([lf]))
    R0 = ndp.get_rnames()
    B = list(set(R0) - set([lr]))


    # loop(series(X, dp, Y))
    # X is now the product space
    F = PosetProduct((ndp.get_ftypes(A), ndp.get_ftype(lf)))
    coords = []
    for x in F0:
        if x == lf:
            coords.append(1)
        else:
            coords.append((0, A.index(x)))
    X = Mux(F, coords)

#     if B:
#     R = PosetProduct((ndp.get_rtypes(B), ndp.get_rtype(lr)))
    R = ndp.get_dp().get_res_space()
    coords_B = [ ndp.rindex(x) for x in B]
    coords = [coords_B, ndp.rindex(lr)]
    Y = Mux(R, coords)

    print('TRyingt to interconnect %s' % ndp.get_dp())
    Series(ndp.get_dp(), Y)
#     else:
# #         R = PosetProduct((ndp.get_rtypes(B), ndp.get_rtype(lr)))
# #         Y = Mux(R, ndp.rindex(lr))
#         Y = None

    a = Series(X, ndp.get_dp())

    if Y is not None:
        dp = Series(a, Y)
    else:
        dp = a
    res_dp = DPLoop(dp)

    res = dpwrap(res_dp, fnames=A, rnames=B)


    return res

