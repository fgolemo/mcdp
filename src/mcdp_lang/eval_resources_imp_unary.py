from contracts import contract
from contracts.utils import raise_desc
from mcdp_dp import WrapAMap
from mcdp_lang.helpers import get_resource_possibly_converted, create_operation
from mcdp_maps import CeilMap, SquareMap, SqrtMap, SquareNatMap
from mcdp_posets import Nat, Rcomp, RcompUnits
from mcdp_posets.maps.identity import IdentityMap
from mocdp import logger
from mocdp.comp.context import CResource
from mocdp.exceptions import DPSemanticError

from .parts import CDPLanguage


CDP = CDPLanguage

class Rule():
    def __init__(self, opname, test_type, cast_type_to, use_map, warn=None):
        self.opname = opname
        self.test_type = test_type
        self.cast_type_to = cast_type_to
        self.use_map = use_map
        self.warn = warn
        
    def applies(self, opname, F):
        if self.opname != opname:
            return False
        
        if not self.test_type(F):
            return False
        else:
            return True
    
    @contract(op_r=CResource)
    def build(self, op_r, context):
        if self.warn:
            logger.warn(self.warn)
        F = context.get_rtype(op_r)
        if self.cast_type_to is not None:
            op_r = get_resource_possibly_converted(op_r, F, context)
            F = self.cast_type_to
            
        amap = self.use_map(F)
        dp = WrapAMap(amap)
        return create_operation(context, dp, [op_r],
                                         name_prefix='_%s'% self.opname, 
                                         op_prefix='_in',
                                         res_prefix='_out')
            
        
def get_unary_rules():
     
    
    # note that RcompUnits derives from Rcomp so we must have this check
    def is_RcompUnits(T):
        return isinstance(T, RcompUnits)
    def is_Rcomp(T):
        return isinstance(T, Rcomp) and not isinstance(T, RcompUnits)
    def is_Nat(T):
        return isinstance(T, Nat)
        
    rules = [
        # sqrt(Nat): promote to Rcomp()
        # sqrt(Rcomp)
        # sqrt(Rcomp)
        Rule('sqrt', is_Nat, Rcomp(), lambda _: SqrtMap(Rcomp())),
        Rule('sqrt', is_Rcomp, None,  lambda _: SqrtMap(Rcomp())),
        Rule('sqrt', is_RcompUnits, None,  lambda F: SqrtMap(F)),
             
        # square: Nat -> Nat
        # square: Rcomp -> Rcomp
        # square: Rcompunits -> Rcompunits
        Rule('square', is_Nat, None, lambda _: SquareNatMap()), 
        Rule('square', is_Rcomp, None, lambda F: SquareMap(F)), 
        Rule('square', is_RcompUnits, None, lambda F: SquareMap(F)), 

        Rule('ceil', is_Nat, None, lambda _: IdentityMap(Nat(), Nat()), warn='ceil() used on Nats'), 
        Rule('ceil', is_Rcomp, None, lambda _: CeilMap(Rcomp())), 
        Rule('ceil', is_RcompUnits, None, lambda F: CeilMap(F)),
        
        Rule('floor', is_Nat, None, lambda _: IdentityMap(Nat(), Nat()), warn='floor() used on Nats'), 
        Rule('floor', is_Rcomp, None, lambda _: CeilMap(Rcomp())), 
        Rule('floor', is_RcompUnits, None, lambda F: CeilMap(F)),
    ]
    return rules

unary_rules = get_unary_rules()
    

def eval_rvalue_unary(r, context):
    """ This is supposed to be a numpy function that takes a scalar float.
        The rvalue must have type Rcomp or Rcompunits.
    """
    from .eval_resources_imp import eval_rvalue

    assert isinstance(r, CDP.UnaryRvalue)
    proc = r.proc 
    assert isinstance(proc, CDP.ProcName)
    op_r = eval_rvalue(r.rvalue, context)
    F = context.get_rtype(op_r)
    
    for rule in unary_rules:
        if rule.applies(proc.name, F):
            return rule.build(op_r, context)
    
    msg = ('Cannot create unary operator %r for %s.'% (proc.name, F))
    raise_desc(DPSemanticError, msg, F=F)
    
    
#     
#     if isinstance(F, Nat):
#         if proc.name in ['sqrt']:
#             # convert to Rcomp
#             F = Rcomp()
#             op_r = get_resource_possibly_converted(op_r, F, context) 
#                 
#         
#     if not isinstance(F, (Rcomp, RcompUnits)):
#         msg = ('Cannot create unary operator %r for %s (only Rcomp/RcompUnits supported).'%
#                (proc.name, F))
#         raise_desc(DPSemanticError, msg, F=F)
# 
#     if proc.name == 'square':
#         amap = SquareMap(F)
#     elif proc.name == 'sqrt':
#         amap = SqrtMap(F)
#     elif proc.name == 'ceil':
#         amap = CeilMap(F)
#     elif proc.name == 'floor':
#         amap = FloorMap(F)
#     else:
#         msg = 'Unknown procedure %r.' % proc.name
#         raise_desc(DPInternalError, msg) 
#     
#     dp = WrapAMap(amap)
#     
#     return create_operation(context, dp, [op_r],
#                                  name_prefix='_%s'% proc.name, 
#                                  op_prefix='_in',
#                                  res_prefix='_out')
#         
        