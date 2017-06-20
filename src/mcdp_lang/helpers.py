# -*- coding: utf-8 -*-
import sys

from contracts import contract
from contracts.utils import raise_wrapped
from mcdp_dp import (Constant, ConstantMinimals, Limit, LimitMaximals,
    get_conversion)
from mcdp_posets import NotLeq, Poset, get_types_universe
from mocdp.comp import Connection, dpwrap
from mocdp.comp.context import CResource, ValueWithUnits, UncertainConstant,\
    CFunction
from mcdp.exceptions import DPSemanticError, DPInternalError, mcdp_dev_warning
import warnings


# from mcdp import logger
@contract(resources='seq')
def create_operation(context, dp, resources, name_prefix=None, op_prefix=None, res_prefix=None):
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
    if name_prefix is None:
        name_prefix = '_%s' % type(dp).__name__
    # new name for the ndp
    name = context.new_name(name_prefix)
    if op_prefix is None:
        op_prefix = '_op'
    if res_prefix is None:
        res_prefix = '_res'
        
    name_result = context.new_res_name(res_prefix)

    connections = []
    fnames = []
    for i, r in enumerate(resources):
        ni = context.new_fun_name('%s%s' % (op_prefix, i))
        fnames.append(ni)

    fnames_ = fnames[0] if len(fnames) == 1 else fnames
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
                msg = 'I need a conversion from %s to %s' % (R, F)
                raise DPInternalError(msg)
            else:
                r = create_operation(context, conversion, [r],
                                     name_prefix='_conversion_for_%s' % name_result)

        R = context.get_rtype(r)
        assert tu.equal(F, R)

        c = Connection(dp1=r.dp, s1=r.s, dp2=name, s2=fnames[i])
        connections.append(c)

    for c in connections:
        context.add_connection(c)

    res = context.make_resource(name, name_result)
    return res


def create_operation_lf(context, dp, functions, name_prefix=None, 
                        op_prefix='_op', res_prefix='_res', allow_conversion=True):
    if name_prefix is None:
        name_prefix = '_%s' % type(dp).__name__ 
    name = context.new_name(name_prefix)
    name_result = context.new_res_name(res_prefix)
    
    rnames = []
    for i, f in enumerate(functions):
        ni = context.new_fun_name('%s%s' % (op_prefix, i))
        rnames.append(ni)
        
    _rnames = rnames[0] if len(rnames) == 1 else rnames
    ndp = dpwrap(dp, name_result, _rnames)

    connections = []
    tu = get_types_universe()
    for i, f in enumerate(functions):
        # source resource
        Fi = context.get_ftype(f)
        # function
        Fhave = ndp.get_rtype(rnames[i])

#         print('------- argu %d' % i)
#         
#         print('I need to connect function %s of type %s to resource %s of new NDP with type %s'%
#               (f, Fi, rnames[i], Fhave))
#         
#         print('Fi: %s' % Fi)
#         print('Fhave: %s' % Fhave)
        
        if not tu.equal(Fi, Fhave):
            if not allow_conversion:
                msg = ('The types are %s and %s are not equal, and '
                       'allow_conversion is False' % (Fi, Fhave))
                raise DPInternalError(msg)
            
#             print('creating conversion')
            conversion = get_conversion(Fhave, Fi)
            if conversion is None:
                msg = 'I need a conversion from %s to %s' % (Fi, Fhave)
                raise DPInternalError(msg)
            else:
#                 print('Conversion: %s' % conversion.repr_long())
#                 print('Creating recursive...')
                f = create_operation_lf(context, conversion, [f],
                                        name_prefix='_conversion_for_%s' % name_result, 
                                        allow_conversion=False)
                 

        c = Connection(dp2=f.dp, s2=f.s, dp1=name, s1=rnames[i])
        connections.append(c)

    context.add_ndp(name, ndp)

    for c in connections:
        context.add_connection(c)

    res = context.make_function(name, name_result)
    return res


@contract(v=ValueWithUnits)
def get_valuewithunits_as_resource(v, context):
    dp = Constant(R=v.unit, value=v.value)
    nres = context.new_res_name('_c')
    ndp = dpwrap(dp, [], nres)
    context.add_ndp(nres, ndp)
    return context.make_resource(nres, nres)

def get_constant_minimals_as_resources(R, values, context):
    for v in values:
        R.belongs(v)

    dp = ConstantMinimals(R=R, values=values)
    nres = context.new_res_name('_c')
    ndp = dpwrap(dp, [], nres)
    context.add_ndp(nres, ndp)
    return context.make_resource(nres, nres)

def get_constant_maximals_as_function(F, values, context):
    for v in values:
        F.belongs(v)

    dp = LimitMaximals(F=F, values=values)
    nres = context.new_name('_c')
    ndp = dpwrap(dp, '_max', [])
    context.add_ndp(nres, ndp)
    return context.make_function(nres, '_max')


@contract(v=ValueWithUnits, returns=CFunction)
def get_valuewithunits_as_function(v, context):
    dp = Limit(v.unit, v.value)
    n = context.new_name('_lim')
    sn = context.new_fun_name('_l')
    ndp = dpwrap(dp, sn, [])
    context.add_ndp(n, ndp)
    return context.make_function(n, sn)


@contract(v=UncertainConstant, returns=CFunction)
def get_uncertainconstant_as_function(v, context):
    warnings.warn('This is a bit inefficient')
    from mcdp_dp.dp_uncertain import UncertainGateSym
    vlower = ValueWithUnits(unit=v.space, value=v.lower)
    vupper = ValueWithUnits(unit=v.space, value=v.upper)
    rl = get_valuewithunits_as_function(vlower, context)
    ru = get_valuewithunits_as_function(vupper, context)
    dp = UncertainGateSym(v.space)
    return create_operation_lf(context, dp=dp, functions=[rl, ru]) 

@contract(v=UncertainConstant, returns=CResource)
def get_uncertainconstant_as_resource(v, context):
    warnings.warn('This is a bit inefficient')
    from mcdp_dp.dp_uncertain import UncertainGate
    vlower = ValueWithUnits(unit=v.space, value=v.lower)
    vupper = ValueWithUnits(unit=v.space, value=v.upper)
    rl = get_valuewithunits_as_resource(vlower, context)
    ru = get_valuewithunits_as_resource(vupper, context)
    dp = UncertainGate(v.space)
    return create_operation(context, dp=dp, resources=[rl, ru]) 

@contract(returns=CResource, r=CResource, P=Poset)
def get_resource_possibly_converted(r, P, context):
    """ Returns a resource possibly converted to the space P """
    assert isinstance(r, CResource)

    R = context.get_rtype(r)
    tu = get_types_universe()
    
    if tu.equal(R, P):
        return r
    else:
        try:
            tu.get_super_conversion(R, P)
        except NotLeq as e:
            msg = 'Cannot convert %s to %s.' % (R, P)
            raise_wrapped(DPSemanticError, e, msg, R=R, P=P, exc=sys.exc_info())

        conversion = get_conversion(R, P)
        if conversion is None:
            return r
        else:
            r2 = create_operation(context, conversion, [r],
                                 name_prefix='_conv_grpc', op_prefix='_op',
                                 res_prefix='_res')
            return r2
# 
mcdp_dev_warning('get_function_possibly_converted() not used at all, but get_resource_possibly_converted')
# 
# @contract(returns=CFunction, cf=CFunction, P=Poset)
# def get_function_possibly_converted(cf, P, context):
#     """ Returns a resource possibly converted to the space P """
#     check_isinstance(cf, CFunction)
# 
#     F = context.get_ftype(cf)
#     tu = get_types_universe()
#     
#     if tu.equal(F, P):
#         return cf
#     else:
#         try:
#             tu.get_super_conversion(P, F)
#         except NotLeq as e:
#             msg = 'Cannot convert %s to %s.' % (P, F)
#             raise_wrapped(DPSemanticError, e, msg, P=P, F=F, exc=sys.exc_info())
# 
#         conversion = get_conversion(P, F)
#         if conversion is None:
#             return cf
#         else:
#             cf2 = create_operation_lf(context, dp=conversion, 
#                                       functions=[cf], 
#                                       name_prefix='_conv_gfpc', 
#                                       op_prefix='_op', res_prefix='_res')
#             return cf2

