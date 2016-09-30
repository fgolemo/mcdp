from contracts.utils import raise_desc
from mcdp_dp import WrapAMap
from mcdp_maps import CeilMap, FloorMap, SquareMap, SqrtMap
from mcdp_posets import Rcomp, RcompUnits
from mocdp.exceptions import DPInternalError, DPSemanticError

from .parts import CDPLanguage


CDP = CDPLanguage

def eval_rvalue_unary(r, context):
    """ This is supposed to be a numpy function that takes a scalar float.
        The rvalue must have type Rcomp or Rcompunits.
    """
    from .eval_resources_imp import eval_rvalue
    from .helpers import create_operation

    assert isinstance(r, CDP.UnaryRvalue)
    proc = r.proc 
    assert isinstance(proc, CDP.ProcName)
    op_r = eval_rvalue(r.rvalue, context)
    F = context.get_rtype(op_r)
    
    if not isinstance(F, (Rcomp, RcompUnits)):
        msg = ('Cannot create unary operator %r for %s (only Rcomp/RcompUnits supported).'%
               (proc.name, F))
        raise_desc(DPSemanticError, msg, F=F)

    if proc.name == 'square':
        amap = SquareMap(F)
    elif proc.name == 'sqrt':
        amap = SqrtMap(F)
    elif proc.name == 'ceil':
        amap = CeilMap(F)
    elif proc.name == 'floor':
        amap = FloorMap(F)
    else:
        msg = 'Unknown procedure %r.' % proc.name
        raise_desc(DPInternalError, msg) 
    
    dp = WrapAMap(amap)
    
    return create_operation(context, dp, [op_r],
                                 name_prefix='_%s'% proc.name, 
                                 op_prefix='_in',
                                 res_prefix='_out')
        
        