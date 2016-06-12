
from .parts import CDPLanguage
from mcdp_posets import RCompUnitsPower
from mocdp.dp import WrapAMap

CDP = CDPLanguage


def eval_Power(rvalue, context):
    from mcdp_lang.eval_resources_imp import eval_rvalue
    base = eval_rvalue(rvalue.op1, context)

    exponent = rvalue.exponent
    assert isinstance(exponent, CDP.IntegerFraction)
    num = exponent.num
    den = exponent.den

    F = context.get_rtype(base)
    m = RCompUnitsPower(F, num=num, den=den)
    dp = WrapAMap(m)
    from .helpers import create_operation
    return create_operation(context, dp=dp, resources=[base],
                            name_prefix='_prod', op_prefix='_factor',
                            res_prefix='_result')
