
from .eval_constant_imp import eval_constant
from .parse_actions import add_where_information
from .parts import CDPLanguage
from contracts import contract
from contracts.utils import raise_desc
from mcdp_maps.ceil_after import CeilAfter
from mcdp_posets import Nat, RCompUnitsPower, Rcomp, RcompUnits
from mocdp.comp import Connection, dpwrap
from mocdp.comp.context import CResource, ValueWithUnits, get_name_for_fun_node
from mocdp.dp import GenericUnary, Max, Max1, Min, WrapAMap
from mocdp.exceptions import DPInternalError, DPSemanticError
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
