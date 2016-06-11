
from .parts import CDPLanguage
from contracts.utils import raise_desc
from mcdp_maps.ceil_after import CeilAfter
from mcdp_posets import Nat, Rcomp, RcompUnits
from mocdp.comp import Connection, dpwrap
from mocdp.dp import GenericUnary, WrapAMap
from mocdp.exceptions import DPInternalError

CDP = CDPLanguage


def eval_GenericNonlinearity(rvalue, context):
    from mcdp_lang.eval_resources_imp import eval_rvalue
    op_r = eval_rvalue(rvalue.op1, context)
    # this is supposed to be a numpy function that takes a scalar float
    function = rvalue.function
    F = context.get_rtype(op_r)

    if isinstance(F, Rcomp) or isinstance(F, RcompUnits):
        R = F
        dp = GenericUnary(F=F, R=R, function=function)
    elif isinstance(F, Nat):
        m = CeilAfter(function, dom=Nat(), cod=Nat())
        dp = WrapAMap(m)
    else:
        msg = 'Cannot create unary operator'
        raise_desc(DPInternalError, msg, function=function, F=F)

    fnames = context.new_fun_name('s')
    name = context.new_name(function.__name__)
    rname = context.new_res_name('res')

    ndp = dpwrap(dp, fnames, rname)
    context.add_ndp(name, ndp)

    c = Connection(dp1=op_r.dp, s1=op_r.s, dp2=name, s2=fnames)

    context.add_connection(c)

    return context.make_resource(name, rname)
