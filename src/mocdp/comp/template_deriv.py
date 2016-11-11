from contracts import contract
from contracts.utils import check_isinstance, raise_desc
from mocdp.comp.context import Connection
from mocdp.exceptions import DPSemanticError

from .composite import CompositeNamedDP
from .template_for_nameddp import TemplateForNamedDP


@contract(ndp=CompositeNamedDP, name=str, returns=TemplateForNamedDP)
def cndp_eversion(ndp, name):
    check_isinstance(ndp, CompositeNamedDP)    
    check_isinstance(name, str)
    
    context = ndp.__copy__().context
     
    if not name in context.names:
        msg = 'Could not find %r as a sub model.' % name
        available = [_ for _ in context.names if _[0] != '_' ]
        msg += ' Available: %s.' % (", ".join(sorted(available)))
        raise_desc(DPSemanticError, msg) # todo: where = name.where

    # we want to delete the ndp
    ndp0 = context.names.pop(name)

    connections = context.connections
    
    for rname in ndp0.get_rnames():
        if rname in context.fnames: # it will become a function
            msg = 'Function %r already exists in the big ndp.' % rname
            raise DPSemanticError(msg)
       
        # we need to create a *function* node
        R = ndp0.get_rtype(rname)
        new_fun_name = context.add_ndp_fun_node(rname, R)
        # now we need to change connections    
        def filter_connections(c):
            if c.dp1 == name and c.s1 == rname:
                return Connection(new_fun_name, rname, c.dp2, c.s2)
            else:
                return c
        connections = map(filter_connections, connections)
                 
    for fname in ndp0.get_fnames():
        #   |
        #   | ... --- (<=) === fname === [ ndp0 ]  
        #   |
        # Becomes:
        #   |           |
        #   | ... ----- | --- fname (a resource)   
        #   |           | 

        if fname in context.rnames:
            msg = 'Resource %r already exists in the big ndp.' % fname
            raise DPSemanticError(msg)
        
        F = ndp0.get_ftype(fname)
        new_res_name = context.add_ndp_res_node(fname, F)
        
        def filter_connections(c):
            if c.dp2 == name and c.s2 == fname:
                return Connection( c.dp1, c.s1, new_res_name, fname)
            else:
                return c
        connections = map(filter_connections, connections)
                 
    context.connections = connections
    return CompositeNamedDP.from_context(context)
           
                
    
# 
# @contract(ndp=CompositeNamedDP, name=str, returns=TemplateForNamedDP)
# def ndp_deriv(ndp, name):
#     """ 
#         Create a template by computing the derivative 
#         with respect to a DP.
#         
#         Raises:
#         - DPSemanticError if no child is found
#         
#     """
#     check_isinstance(ndp, CompositeNamedDP)    
#     check_isinstance(name, str)
#     
#     names = ndp.get_name2ndp()
#     
#     if not name in names:
#         msg = 'Could not find %r as a child.' % name
#         msg += ' Available: %s.' % (", ".join(sorted(names)))
#         raise_desc(DPSemanticError, msg)
#         
#     standin = ndp_templatize(names[name], mark_as_template=True)
#     parameters = {name: standin}        
#     
#     res = TemplateForNamedDP(parameters, template_code)
#     return res