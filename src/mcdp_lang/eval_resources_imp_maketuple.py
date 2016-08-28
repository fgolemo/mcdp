# -*- coding: utf-8 -*-
from .helpers import create_operation
from .parts import CDPLanguage
from .utils_lists import get_odd_ops, unwrap_list
from contracts import contract
from mcdp_dp import TakeFun
from mcdp_posets import PosetProduct

CDP = CDPLanguage


@contract(mt=CDP.MakeTuple)
def eval_rvalue_MakeTuple(mt, context):
    from mcdp_lang.eval_resources_imp import eval_rvalue

    ops = get_odd_ops(unwrap_list(mt.ops))
    resources = [eval_rvalue(_, context) for _ in ops]
    Fs = [context.get_rtype(_) for _ in resources]
    F = PosetProduct(tuple(Fs))

    # Now it's easy - this corresponds to a simple Mux operation
    n = len(Fs)
    coords = list(range(n))
    dp = TakeFun(F, coords)

    return create_operation(context, dp=dp, resources=resources,
                            name_prefix='_make_tuple', op_prefix='_factors',
                            res_prefix='_result')
