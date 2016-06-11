
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


def add_binary2(context, a, b, dp, nprefix, na, nb, nres):
    nres = context.new_res_name(nres)
    na = context.new_fun_name(na)
    nb = context.new_fun_name(nb)

    ndp = dpwrap(dp, [na, nb], nres)
    name = context.new_name(nprefix)
    c1 = Connection(dp1=a.dp, s1=a.s, dp2=name, s2=na)
    c2 = Connection(dp1=b.dp, s1=b.s, dp2=name, s2=nb)
    context.add_ndp(name, ndp)
    context.add_connection(c1)
    context.add_connection(c2)
    return context.make_resource(name, nres)


def eval_OpMin(rvalue, context):
    a, F1, b, F2 = eval_ops2(context, rvalue)
    if not (F1 == F2):
        msg = 'Incompatible units: %s and %s' % (F1, F2)
        raise DPSemanticError(msg, where=rvalue.where)

    dp = Min(F1)
    nprefix, na, nb, nres = 'opmin', 'm0', 'm1', 'min'

    return add_binary2(context, a, b, dp, nprefix, na, nb, nres)

def eval_ops2(context, rvalue):
    """ Returns a, F1, b, F2 """
    assert isinstance(rvalue, CDP.OpMin)
    from mcdp_lang.eval_resources_imp import eval_rvalue
    a = eval_rvalue(rvalue.a, context)
    b = eval_rvalue(rvalue.b, context)
    F1 = context.get_rtype(a)
    F2 = context.get_rtype(b)
    return a, F1, b, F2


def eval_OpMax(rvalue, context):
    from mcdp_lang.eval_resources_imp import eval_rvalue

    if isinstance(rvalue.a, CDP.SimpleValue):
        b = eval_rvalue(rvalue.b, context)
        # print('a is constant')
        name = context.new_name('max1')
        constant = eval_constant(rvalue.a, context)
        ndp = dpwrap(Max1(constant.unit, constant.value), '_in', '_out')
        context.add_ndp(name, ndp)
        c = Connection(dp1=b.dp, s1=b.s, dp2=name, s2='_in')
        context.add_connection(c)
        return context.make_resource(name, '_out')

    a = eval_rvalue(rvalue.a, context)

    if isinstance(rvalue.b, CDP.SimpleValue):
        name = context.new_name('max1')
        constant = eval_constant(rvalue.b, context)
        ndp = dpwrap(Max1(constant.unit, constant.value), '_in', '_out')
        context.add_ndp(name, ndp)
        c = Connection(dp1=a.dp, s1=a.s, dp2=name, s2='_in')
        context.add_connection(c)
        return context.make_resource(name, '_out')

    b = eval_rvalue(rvalue.b, context)

    F1 = context.get_rtype(a)
    F2 = context.get_rtype(b)

    if not (F1 == F2):  # ## BUG1 here
        msg = 'Incompatible units for Max(): %s and %s' % (F1, F2)
        msg += '%s and %s' % (type(F1), type(F2))
        raise DPSemanticError(msg, where=rvalue.where)

    dp = Max(F1)
    nprefix, na, nb, nres = 'opmax', 'm0', 'm1', 'max'

    return add_binary2(context, a, b, dp, nprefix, na, nb, nres)
