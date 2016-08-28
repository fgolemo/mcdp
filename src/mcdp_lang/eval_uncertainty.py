# -*- coding: utf-8 -*-
from .helpers import create_operation
from .parts import CDPLanguage
from mocdp.exceptions import mcdp_dev_warning

CDP = CDPLanguage

def eval_rvalue_Uncertain(r, context):
    from .eval_resources_imp import eval_rvalue
    from mcdp_dp import UncertainGate

    assert isinstance(r, CDP.UncertainRes)

    # print 'evaluating %s ' % recursive_print(r.lower)
    rl = eval_rvalue(r.lower, context)
    # print 'evaluating %s ' % recursive_print(r.upper)
    ru = eval_rvalue(r.upper, context)

    Rl = context.get_rtype(rl)
    # Ru = context.get_rtype(ru)
    mcdp_dev_warning('Do explicit check of types.')

    dp = UncertainGate(Rl)

    return create_operation(context, dp=dp, resources=[rl, ru],
                            name_prefix='_uncertain', op_prefix='_resources',
                            res_prefix='_result')


def eval_lfunction_Uncertain(r, context):
    from .eval_lfunction_imp import eval_lfunction
    from mcdp_dp import UncertainGateSym
    from mcdp_lang.helpers import create_operation_lf

    assert isinstance(r, CDP.UncertainFun)

    fl = eval_lfunction(r.lower, context)
    fu = eval_lfunction(r.upper, context)

    F = context.get_ftype(fl)
    # Fu = context.get_rtype(fu)
    mcdp_dev_warning('Do explicit check of types.')

    dp = UncertainGateSym(F)

    return create_operation_lf(context, dp=dp, functions=[fl, fu],
                            name_prefix='_uncertainf', op_prefix='_functions',
                            res_prefix='_result')
