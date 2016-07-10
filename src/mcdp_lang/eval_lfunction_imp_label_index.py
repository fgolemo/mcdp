from .helpers import get_valuewithunits_as_resource
from .parts import CDPLanguage
from contracts import contract
from contracts.utils import raise_desc
from mcdp_dp import Mux
from mcdp_posets import PosetProductWithLabels
from mocdp.comp.context import Connection, ValueWithUnits
from mocdp.comp.wrap import SimpleWrap
from mocdp.exceptions import DPSemanticError, mcdp_dev_warning

CDP = CDPLanguage

@contract(f=CDP.TupleIndexFun)
def eval_lfunction_tupleindexfun(f, context):
    from mcdp_lang.eval_lfunction_imp import eval_lfunction
    fvalue = eval_lfunction(f.value, context)
    index = f.index

    F = context.get_ftype(fvalue)

    n = len(F.subs)

    if not (0 <= index < n):
        msg = 'Out of bounds.'
        raise_desc(DPSemanticError, msg, index=index, F=F)

    return context.ifun_get_index(fvalue, index)


@contract(r=CDP.FunctionLabelIndex)
def eval_lfunction_label_index(r, context):
    from mcdp_lang.eval_lfunction_imp import eval_lfunction
    assert isinstance(r, CDP.FunctionLabelIndex)

    label = r.label.label
    fvalue = eval_lfunction(r.fvalue, context)

    R = context.get_ftype(fvalue)

    if not isinstance(R, PosetProductWithLabels):
        msg = 'Cannot index by label for this space.'
        raise_desc(DPSemanticError, msg, space=R, label=label)

    if not label in R.labels:
        msg = 'Cannot find label %r in %r.' % (label, R.labels)
        raise_desc(DPSemanticError, msg, space=R)

    index = R.labels.index(label)
    return context.ifun_get_index(fvalue, index)


    
