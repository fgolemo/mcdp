# -*- coding: utf-8 -*-
from contracts.utils import raise_desc
from mcdp_dp import RcompUnitsPowerDP
from mcdp_posets import RcompUnits
from mcdp.exceptions import DPSemanticError

from .parts import CDPLanguage


CDP = CDPLanguage


def eval_rvalue_Power(rvalue, context):
    assert isinstance(rvalue, (CDP.Power, CDP.PowerShort)), rvalue

    from .eval_resources_imp import eval_rvalue
    base = eval_rvalue(rvalue.op1, context)

    exponent = rvalue.exponent
    assert isinstance(exponent, CDP.IntegerFraction)

    num = exponent.num
    den = exponent.den

    if num == 0 or den == 0:
        msg = ('Invalid fraction %s/%s: both numerator and denominator'
               ' should be greater than zero.' %(num, den))
        raise_desc(DPSemanticError, msg)
    
    F = context.get_rtype(base)
    if not isinstance(F, RcompUnits):
        msg = 'I can only compute pow() for floats with types; this is %r.' % (F)
        raise_desc(DPSemanticError, msg, F=F)
        
    dp = RcompUnitsPowerDP(F, num=num, den=den)
    from .helpers import create_operation
    return create_operation(context, dp=dp, resources=[base],
                            name_prefix='_prod', op_prefix='_factor',
                            res_prefix='_result')
