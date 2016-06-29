from .helpers import get_valuewithunits_as_resource
from .parts import CDPLanguage
from contracts import contract
from contracts.utils import raise_desc
from mcdp_dp import Mux
from mcdp_posets import PosetProductWithLabels
from mocdp.comp.context import Connection, ValueWithUnits
from mocdp.comp.wrap import SimpleWrap
from mocdp.exceptions import DPSemanticError


CDP = CDPLanguage


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

    n = len(R.subs)
    
    coords = list(range(n))
    dp = Mux(R, coords)
    ndp_out = '_muxed'
    ndp = SimpleWrap(dp, fnames=R.labels, rnames=ndp_out)
    ndp_name = context.new_name('_label_index')
    
    #  0-->
    #  --> |ndp| --> fvalue
    #  0-->
    #
    #
        
    context.add_ndp(ndp_name, ndp)
    c = Connection(dp1=ndp_name, s1=ndp_out, dp2=fvalue.dp, s2=fvalue.s)
    context.add_connection(c)
    
    # now create 0 constants
    
    for sub, sub_label in zip(R.subs, R.labels):
        if label == sub_label:
            continue
        
        zero = sub.get_bottom()
        vu = ValueWithUnits(value=zero, unit=sub)
        res = get_valuewithunits_as_resource(vu, context)
        
        c = Connection(dp1=res.dp, s1=res.s, dp2=ndp_name, s2=sub_label)
        context.add_connection(c)

    res = context.make_function(ndp_name, label)
    return res
    
