# -*- coding: utf-8 -*-
from .parts import CDPLanguage
from mcdp_posets import RCompUnitsPower
from mcdp_dp import WrapAMap
from mcdp_posets.rcomp_units import RcompUnits
from mocdp.exceptions import DPSemanticError
from contracts.utils import raise_desc

CDP = CDPLanguage


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
        
    m = RCompUnitsPower(F, num=num, den=den)
    dp = WrapAMap(m)
    from .helpers import create_operation
    return create_operation(context, dp=dp, resources=[base],
                            name_prefix='_prod', op_prefix='_factor',
                            res_prefix='_result')
