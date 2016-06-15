from .parts import CDPLanguage
from contracts import contract
from mcdp_lang.utils_lists import get_odd_ops, unwrap_list
from mcdp_posets.poset_product import PosetProduct
from mcdp_dp.dp_flatten import Mux
from mcdp_lang.helpers import create_operation_lf

CDP = CDPLanguage


@contract(mt=CDP.MakeTuple)
def eval_MakeTuple_as_lfunction(mt, context):
    from mcdp_lang.eval_lfunction_imp import eval_lfunction

    ops = get_odd_ops(unwrap_list(mt.ops))
    functions = [eval_lfunction(_, context) for _ in ops]
    Rs = [context.get_ftype(_) for _ in functions]
    R = PosetProduct(tuple(Rs))

    # Now it's easy - this corresponds to a simple Mux operation
    coords = list(range(len(Rs)))
    dp = Mux(R, coords)

    return create_operation_lf(context, dp=dp, functions=functions,
                            name_prefix='_demake_tuple', op_prefix='_factors',
                            res_prefix='_result')
