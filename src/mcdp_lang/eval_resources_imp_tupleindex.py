from .parts import CDPLanguage
from contracts import contract
from contracts.utils import raise_desc
from mcdp_posets.poset_product import PosetProduct
from mcdp_dp.dp_flatten import Mux
from mocdp.exceptions import DPInternalError, DPSemanticError

CDP = CDPLanguage


@contract(ti=CDP.TupleIndex)
def eval_rvalue_TupleIndex(ti, context):
    # TupleIndex = namedtuplewhere('TupleIndex', 'value index')
    # value evaluates as resources
    # index is an integer

    # Evaluate the resource
    from .eval_resources_imp import eval_rvalue
    value = eval_rvalue(ti.value, context)
    F = context.get_rtype(value)
    
    # We want that F is a PosetProduct
    if not isinstance(F, PosetProduct):
        msg = "Expected a PosetProduct as argument of take() operation."
        raise_desc(DPSemanticError, msg, F=F)

    # let's check that the index is correct
    if not isinstance(ti.index, int) or ti.index < 0:
        msg = "Invalid index."
        raise_desc(DPInternalError, msg, index=ti.index)

    # Now we check that the length is consistent
    l = len(F)
    if ti.index >= l:
        msg = 'Invalid index %d for product of size %d.' % (ti.index, l)
        raise_desc(DPSemanticError, msg)

    # Now it's easy - this corresponds to a simple Mux operation
    coords = ti.index
    dp = Mux(F, coords)

    from .helpers import create_operation
    return create_operation(context, dp=dp, resources=[value],
                            name_prefix='_take', op_prefix='_in_product',
                            res_prefix='_result')
