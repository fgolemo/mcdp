from contracts import contract
from contracts.utils import raise_wrapped
from mcdp_dp import IdentityDP
from mocdp.comp.composite import CompositeNamedDP, cndp_get_name_ndp_notfunres
from mocdp.comp.context import Connection
from mocdp.comp.interfaces import NotConnected
from mocdp.comp.wrap import SimpleWrap
from mocdp.exceptions import DPInternalError

__all__ = [
    'simplify_identities',
]

@contract(ndp=CompositeNamedDP, returns=CompositeNamedDP)
def simplify_identities(ndp):
    """
        Removes the identites from the NDP.
        
        Useful for visualization.
    """

    def can_simplify(child):
        if len(child.get_fnames()) != 1:
            return False

        if len(child.get_rnames()) != 1:
            return False

        if not isinstance(child, SimpleWrap):
            return False

        if not isinstance(child.dp, IdentityDP):
            return False

        return True

    try:
        ndp.check_fully_connected()
        connected = True
    except NotConnected:
        connected = False
    ndp = ndp.__copy__()
    
    for name, child in list(cndp_get_name_ndp_notfunres(ndp)):
        if not can_simplify(child):
            continue
        
        # (prev) -> (name) -> (succ)
        prev = succ = None
#         prevs = []
#         succs = []
        for c in ndp.context.connections:
            if c.dp2 == name:
                prev = c.dp1
                prev_s = c.s1
#                 prevs.append((c.dp1, c.s1))
            if c.dp1 == name:
                succ = c.dp2
                succ_s = c.s2
#                 succs.append((c.dp2, c.s2))

        # it has exactly 1 forward and 1 succ connections,
        # not to itself

        ok = prev is not None and succ is not None and prev != succ

        if not ok:
            continue
        
        # remove those two
        connections = [ c for c in ndp.context.connections if
                       c.dp1 != name and c.dp2 != name]

        ndp.context.connections = connections

        c = Connection(dp1=prev, s1=prev_s, dp2=succ, s2=succ_s)
        ndp.context.add_connection(c)


        del ndp.context.names[name]

    res = ndp.__copy__()
    if connected:
        try:
            res.check_fully_connected()
        except NotConnected as e:
            msg = 'Result is not fully connected.'
            raise_wrapped(DPInternalError, e, msg,  # res=res.repr_long(),
                           compact=True)

    return res
