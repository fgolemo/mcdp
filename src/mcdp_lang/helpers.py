# -*- coding: utf-8 -*-
from contracts import contract
from mocdp.comp import Connection, dpwrap
from mocdp.comp.context import ValueWithUnits
from mcdp_dp import Constant
from mcdp_posets.types_universe import get_types_universe
from mcdp_dp.conversion import get_conversion
from mcdp_dp.dp_limit import Limit



@contract(resources='seq')
def create_operation(context, dp, resources, name_prefix, op_prefix, res_prefix):
    """
    
        This is useful to create operations that take possibly many inputs
        and produce one output.
        
        Example use:
        
            R = mult_table_seq(resources_types)
            dp = ProductN(tuple(resources_types), R)
    
            from mcdp_lang.helpers import create_operation
            r = create_operation(context, dp, resources,
                                 name_prefix='_prod', op_prefix='_factor',
                                 res_prefix='_result')
    
    """
    # new name for the ndp
    name = context.new_name(name_prefix)
    name_result = context.new_res_name(res_prefix)

    connections = []
    fnames = []
    for i, r in enumerate(resources):
        ni = context.new_fun_name('%s%s' % (op_prefix, i))
        fnames.append(ni)


    fnames_ = fnames if len(fnames) > 1 else fnames[0]
    ndp = dpwrap(dp, fnames_, name_result)
    context.add_ndp(name, ndp)

    tu = get_types_universe()

    for i, r in enumerate(resources):
        # this is where we check for types

        # source resource
        R = context.get_rtype(r)
        # function
        F = ndp.get_ftype(fnames[i])

        if not tu.equal(F, R):
            conversion = get_conversion(R, F)
            if conversion is None:
                pass
            else:
                r = create_operation(context, conversion, [r],
                                     name_prefix='_conv', op_prefix='_op',
                                     res_prefix='_res')

        R = context.get_rtype(r)
        assert tu.equal(F, R)

        c = Connection(dp1=r.dp, s1=r.s, dp2=name, s2=fnames[i])
        connections.append(c)

    if len(fnames) == 1:
        fnames = fnames[0]


    for c in connections:
        context.add_connection(c)

    res = context.make_resource(name, name_result)
    return res


def create_operation_lf(context, dp, functions, name_prefix, op_prefix, res_prefix):
    name = context.new_name(name_prefix)
    name_result = context.new_res_name(res_prefix)

    connections = []
    rnames = []
    for i, f in enumerate(functions):
        ni = context.new_fun_name('%s%s' % (op_prefix, i))
        c = Connection(dp2=f.dp, s2=f.s, dp1=name, s1=ni)
        rnames.append(ni)
        connections.append(c)

    if len(rnames) == 1:
        rnames = rnames[0]

    ndp = dpwrap(dp, name_result, rnames)
    context.add_ndp(name, ndp)

    for c in connections:
        context.add_connection(c)

    res = context.make_function(name, name_result)
    return res

@contract(v=ValueWithUnits)
def get_valuewithunits_as_resource(v, context):
    dp = Constant(R=v.unit, value=v.value)
    nres = context.new_res_name('c')
    ndp = dpwrap(dp, [], nres)
    context.add_ndp(nres, ndp)
    return context.make_resource(nres, nres)

@contract(v=ValueWithUnits)
def get_valuewithunits_as_function(v, context):
    dp = Limit(v.unit, v.value)
    n = context.new_name('lim')
    sn = context.new_fun_name('l')
    ndp = dpwrap(dp, sn, [])
    context.add_ndp(n, ndp)
    return context.make_function(n, sn)


def square(x):
    res = x * x
    return res

