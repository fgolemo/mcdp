# -*- coding: utf-8 -*-
from contracts.utils import raise_desc
from mcdp_dp import WrapAMap
from mcdp_posets import RCompUnitsPowerMap, RcompUnits
from mocdp.exceptions import DPSemanticError

from .parts import CDPLanguage

CDP = CDPLanguage

class RcompUnitsPowerDP(WrapAMap):
    def __init__(self, F, num, den):
        amap = RCompUnitsPowerMap(F, num=num, den=den)
        amap_dual = RCompUnitsPowerMap(F, num=den, den=num) # swap
        WrapAMap.__init__(self, amap, amap_dual)

def eval_rvalue_Power(rvalue, context):
    assert isinstance(rvalue, (CDP.Power, CDP.PowerShort)), rvalue

    from .eval_resources_imp import eval_rvalue
    base = eval_rvalue(rvalue.op1, context)

    exponent = rvalue.exponent
    assert isinstance(exponent, CDP.IntegerFraction)
    num = exponent.num
    den = exponent.den

    F = context.get_rtype(base)
    if not isinstance(F, RcompUnits):
        msg = 'I can only compute pow() for floats with types; this is %r.' % (F)
        raise_desc(DPSemanticError, msg, F=F)
        
    dp = RcompUnitsPowerDP(F, num=num, den=den)
    from .helpers import create_operation
    return create_operation(context, dp=dp, resources=[base],
                            name_prefix='_prod', op_prefix='_factor',
                            res_prefix='_result')
