# -*- coding: utf-8 -*-
from .parts import CDPLanguage
from contracts import contract
from contracts.utils import raise_desc
from mcdp_posets import PosetProduct, PosetProductWithLabels
from mocdp.exceptions import DPInternalError, DPSemanticError

CDP = CDPLanguage


def eval_rvalue_resource_label_index(r, context):
    from .eval_resources_imp import eval_rvalue
    assert isinstance(r, CDP.ResourceLabelIndex)
    label = r.label.label
    rvalue = eval_rvalue(r.rvalue, context)

    F = context.get_rtype(rvalue)

    if not isinstance(F, PosetProductWithLabels):
        msg = 'Cannot index by label for this space.'
        raise_desc(DPSemanticError, msg, space=F, label=label)

    if not label in F.labels:
        msg = 'Cannot find label %r in %r.' % (label, F.labels)
        raise_desc(DPSemanticError, msg, space=F)

    i = F.labels.index(label)

    return context.ires_get_index(rvalue, i)

@contract(ti=CDP.TupleIndex)
def eval_rvalue_TupleIndex(ti, context):
    # TupleIndex = namedtuplewhere('TupleIndex', 'value index')
    # value evaluates as resources
    # index is an integer

    # Evaluate the resource
    from .eval_resources_imp import eval_rvalue
    index = ti.index
    value = eval_rvalue(ti.value, context)
    F = context.get_rtype(value)
    
    # We want that F is a PosetProduct
    if not isinstance(F, PosetProduct):
        msg = "Expected a PosetProduct as argument of take() operation."
        raise_desc(DPSemanticError, msg, F=F)

    # let's check that the index is correct
    if not isinstance(index, int) or index < 0:
        msg = "Invalid index."
        raise_desc(DPInternalError, msg, index=index)

    # Now we check that the length is consistent
    l = len(F)
    if ti.index >= l:
        msg = 'Invalid index %d for product of size %d.' % (index, l)
        raise_desc(DPSemanticError, msg)

    return context.ires_get_index(value, index)
