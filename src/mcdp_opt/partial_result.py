from contracts import contract
from mcdp_lang.blocks import get_missing_connections
from mcdp_lang.helpers import get_constant_minimals_as_resources
from mcdp_opt.context_utils import clone_context
from mocdp.comp.composite import CompositeNamedDP
from mocdp.comp.context import (CFunction, CResource, Connection,
    get_name_for_res_node)

@contract(returns='tuple($CompositeNamedDP, dict($CResource:str))')
def get_lower_bound_ndp(context):
    """
        We create an NDP where each open resource becomes a new resource.
        and all the functions are given a lower bound of 0.
    """
    context = clone_context(context)
    unconnected_fun, unconnected_res = get_missing_connections(context)

    # create a new resource for each unconnected resource
    resource2var = {} # CResource -> str
    for dp, s in unconnected_res:
        r = CResource(dp, s)
        R = context.get_rtype(r)
        rname = 'dummy%d' % len(resource2var)
        context.add_ndp_res_node(rname, R)
        c = Connection(dp1=dp, s1=s, dp2=get_name_for_res_node(rname), s2=rname)
        context.add_connection(c)
        resource2var[r] = rname
        
    # add a minimal bound for all unconnected functions
    for dp, s in unconnected_fun:
        f = CFunction(dp, s)
        F = context.get_ftype(f)
        minimals = F.get_minimal_elements()
        res = get_constant_minimals_as_resources(F, minimals, context)
        c = Connection(dp1=res.dp, s1=res.s, dp2=dp, s2=s)
        context.add_connection(c)
    
    ndp = CompositeNamedDP.from_context(context)
    
    ndp.check_fully_connected()
    return ndp, resource2var
   

