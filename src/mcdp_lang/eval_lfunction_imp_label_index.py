from .helpers import get_valuewithunits_as_resource
from .parts import CDPLanguage
from contracts import contract
from contracts.utils import raise_desc
from mcdp_dp import Mux
from mcdp_posets import PosetProductWithLabels
from mocdp.comp.context import Connection, ValueWithUnits
from mocdp.comp.wrap import SimpleWrap
from mocdp.exceptions import DPSemanticError, mcdp_dev_warning
from mcdp_posets.poset import NotBounded
from mcdp_lang.helpers import get_constant_minimals_as_resources


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

    fnames = ['_f%d' % i for i in range(n)]
    coords = list(range(n))
    dp = Mux(F, coords)
    ndp_out = '_muxed'
    ndp = SimpleWrap(dp, fnames=fnames, rnames=ndp_out)
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

    for i, sub in enumerate(F.subs):
        if i == index:
            continue

        try:
            zero = sub.get_bottom()
            vu = ValueWithUnits(value=zero, unit=sub)
            res = get_valuewithunits_as_resource(vu, context)
        except NotBounded:
            minimals = sub.get_minimal_elements()
            # print ('minimals: %s' % minimals)
            res = get_constant_minimals_as_resources(sub, minimals, context)

        c = Connection(dp1=res.dp, s1=res.s, dp2=ndp_name, s2=fnames[i])
        context.add_connection(c)

    label = fnames[index]
    res = context.make_function(ndp_name, label)
    return res

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
        
        mcdp_dev_warning('Change with minimals...')
        zero = sub.get_bottom()
        vu = ValueWithUnits(value=zero, unit=sub)
        res = get_valuewithunits_as_resource(vu, context)
        
        c = Connection(dp1=res.dp, s1=res.s, dp2=ndp_name, s2=sub_label)
        context.add_connection(c)

    res = context.make_function(ndp_name, label)
    return res
    
