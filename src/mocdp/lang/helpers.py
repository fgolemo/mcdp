# -*- coding: utf-8 -*-
from contracts import contract
from contracts.utils import  raise_wrapped
from mocdp.comp import (Connection, dpwrap)
from mocdp.comp.context import ValueWithUnits

from mocdp.dp import Constant

from mocdp.dp.dp_generic_unary import WrapAMap

from mocdp.exceptions import DPSemanticError

from mocdp.posets import (NotLeq, get_types_universe)

def square(x):
    res = x * x
    return res



@contract(resources='seq')
def create_operation(context, dp, resources, name_prefix, op_prefix, res_prefix):
    name = context.new_name(name_prefix)
    name_result = context.new_res_name(res_prefix)

    connections = []
    fnames = []
    for i, r in enumerate(resources):
        ni = context.new_fun_name('%s%s' % (op_prefix, i))
        c = Connection(dp1=r.dp, s1=r.s, dp2=name, s2=ni)
        fnames.append(ni)
        connections.append(c)

    if len(fnames) == 1:
        fnames = fnames[0]

    ndp = dpwrap(dp, fnames, name_result)
    context.add_ndp(name, ndp)

    for c in connections:
        context.add_connection(c)

    res = context.make_resource(name, name_result)
    return res


@contract(v=ValueWithUnits)
def get_valuewithunits_as_resource(v, context):
    dp = Constant(R=v.unit, value=v.value)
    nres = context.new_res_name('c')
    ndp = dpwrap(dp, [], nres)
    context.add_ndp(nres, ndp)
    return context.make_resource(nres, nres)



def get_conversion(A, B):
    """ Returns None if there is no need. """
    tu = get_types_universe()
    try:
        tu.check_leq(A, B)
    except NotLeq as e:
        msg = 'Wrapping with incompatible units.'
        raise_wrapped(DPSemanticError, e, msg, A=A, B=B)

    if tu.equal(A, B):
        conversion = None
    else:
        A_to_B, _ = tu.get_embedding(A, B)
        conversion = WrapAMap(A_to_B)

    return conversion
