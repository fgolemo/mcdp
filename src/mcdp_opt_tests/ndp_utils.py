from mocdp.comp.composite import CompositeNamedDP
from contracts import contract
from mcdp_lang.blocks import get_missing_connections
from mocdp.comp.context import CResource, CFunction, Connection
from mcdp_dp.dp_limit import LimitMaximals
from mocdp.comp.wrap import dpwrap
from mcdp_dp.dp_constant import ConstantMinimals


@contract(cndp=CompositeNamedDP, returns=CompositeNamedDP,
          to_remove='str')
def cndp_remove_one_child(cndp, to_remove):
    """ 
        Removes a child from NDP. 
    
        Assumes ndp connected.
        
        Dangling arrows are substituted with top/bottom.
        
    """
    print('removing %r' % to_remove)

    cndp.check_fully_connected()

    name2ndp = cndp.get_name2ndp()
    assert to_remove in name2ndp
    connections = cndp.get_connections()
    fnames = cndp.get_fnames()
    rnames = cndp.get_rnames()

    name2ndp_i = dict((k, v) for k, v in name2ndp.items() if k != to_remove)
    filter_c = lambda c: not c.involves_any_of_these_nodes([to_remove])
    connections_i = filter(filter_c, connections)
    
    ndp2 = CompositeNamedDP.from_parts(name2ndp=name2ndp_i,
                                        connections=connections_i,
                                        fnames=fnames, rnames=rnames)

    unconnected_fun, unconnected_res = get_missing_connections(ndp2.context)

    for r in [CResource(*_) for _ in unconnected_res]:
        R = ndp2.context.get_rtype(r)
        values = R.get_maximal_elements()
        dp = LimitMaximals(R, values)
        new_ndp = dpwrap(dp, 'limit', [])
        name = ndp2.context.new_name('_limit_r')
        ndp2.context.add_ndp(name, new_ndp)
        c = Connection(dp2=name, s2='limit', dp1=r.dp, s1=r.s)
        ndp2.context.add_connection(c)


    for f in [CFunction(*_) for _ in unconnected_fun]:
        F = ndp2.context.get_ftype(f)
        values = F.get_minimal_elements()
        dp = ConstantMinimals(F, values)
        new_ndp = dpwrap(dp, [], 'limit')
        name = ndp2.context.new_name('_limit_f')
        ndp2.context.add_ndp(name, new_ndp)

        c = Connection(dp1=name, s1='limit', dp2=f.dp, s2=f.s)
        ndp2.context.add_connection(c)

    ndp2.check_fully_connected()

    return ndp2

