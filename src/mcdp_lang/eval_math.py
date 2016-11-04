# -*- coding: utf-8 -*-
from contracts import contract
from contracts.utils import raise_desc, raise_wrapped, check_isinstance
from mcdp_dp import (MinusValueNatDP, MinusValueRcompDP, MinusValueDP,
                     MultValueDP, MultValueNatDP, PlusValueRcompDP, PlusValueDP,
                     PlusValueNatDP , ProductNDP, SumNNatDP, ProductNNatDP,
                     SumNRcompDP, SumNDP, SumNIntDP)
from mcdp_dp.dp_products import ProductNRcompDP
from mcdp_maps.SumN_xxx_Map import sum_dimensionality_works
from mcdp_posets import (Int, Nat, RbicompUnits, RcompUnits, Space,
    express_value_in_isomorphic_space, get_types_universe, mult_table, Rcomp)
from mcdp_posets import is_top
from mcdp_posets.rcomp_units import RbicompUnits_subtract, RbicompUnits_reflect
from mocdp import MCDPConstants
from mocdp.comp.context import CResource, ValueWithUnits
from mocdp.exceptions import DPInternalError, DPSemanticError, DPNotImplementedError

from .eval_constant_imp import NotConstant
from .eval_resources_imp import eval_rvalue
from .helpers import create_operation, get_valuewithunits_as_resource, get_resource_possibly_converted
from .misc_math import inv_constant
from .parts import CDPLanguage
from .utils_lists import get_odd_ops, unwrap_list


CDP = CDPLanguage

def eval_constant_divide(op, context):
    from .eval_constant_imp import eval_constant

    ops = get_odd_ops(unwrap_list(op.ops))
    if len(ops) != 2:
        raise DPSemanticError('divide by more than two')

    constants = [eval_constant(_, context) for _ in ops]

    factors = [constants[0], inv_constant(constants[1])]
    from .misc_math import generic_mult_constantsN
    return generic_mult_constantsN(factors)

@contract(x=ValueWithUnits, constants='seq($ValueWithUnits)')
def x_minus_constants(x, constants):
    R0 = x.unit
    
    if not isinstance(R0, RcompUnits):
        msg = 'Cannot evaluate "-" on this space.'
        raise_desc(DPSemanticError, msg, R0=R0)

    Rb = RbicompUnits.from_rcompunits(R0)
    
    # convert each factor to R0
    try:
        v0 = x.value
        for c in constants:
            vi = express_value_in_isomorphic_space(c.unit, c.value, Rb)
            v0 = RbicompUnits_subtract(Rb, v0, vi)
    except TypeError as e:
        msg = 'Failure to compute subtraction.'
        raise_wrapped(DPInternalError, e, msg, x=x, constants=constants)
    
    if Rb.leq(0.0, v0):
        R1 = R0
    else:
        R1 = Rb
        
    return ValueWithUnits(unit=R1, value=v0)
    
    
def eval_PlusN_as_constant(x, context):
    return eval_PlusN(x, context, wants_constant=True)


def eval_RValueMinusN_as_constant(x, context):
    return eval_rvalue_RValueMinusN(x, context, wants_constant=True)


def eval_MultN_as_constant(x, context):
    return eval_MultN(x, context, wants_constant=True)


def eval_rvalue_MultN(x, context):
    res = eval_MultN(x, context, wants_constant=False)
    if isinstance(res, ValueWithUnits):
        return get_valuewithunits_as_resource(res, context)
    else:
        return res

@contract(returns=CResource)
def eval_rvalue_divide(op, context):
    from .eval_constant_imp import eval_constant

    ops = get_odd_ops(unwrap_list(op.ops))

    try:
        c2 = eval_constant(ops[1], context)
    except NotConstant as e:
        msg = 'Cannot divide by a non-constant.'
        raise_wrapped(DPSemanticError, e, msg, ops[0])

    c2_inv = inv_constant(c2)

    try:
        c1 = eval_constant(ops[0], context)
        # also the first one is a constant
        from .misc_math import generic_mult_constantsN

        c = generic_mult_constantsN([c1, c2_inv])
        assert isinstance(c, ValueWithUnits)
        return get_valuewithunits_as_resource(c, context)

    except NotConstant:
        pass

    # then eval as resource
    r = eval_rvalue(ops[0], context)

    res = get_mult_op(context, r=r, c=c2_inv)
    return res

def eval_rvalue_RValueMinusN(x, context, wants_constant=False):
    """ If wants_constant is True, returns a ValueWithUnit """
    from .eval_constant_imp import eval_constant
    ops = get_odd_ops(unwrap_list(x.ops))
    
    # ops after the first should be constant, otherwise
    # we lose monotonicity
    must_be_constants = ops[1:]
    constants = []
    for mc in must_be_constants:
        try:
            c = eval_constant(mc, context)
            assert isinstance(c, ValueWithUnits)
            constants.append(c)
        except NotConstant as e:
            msg = 'This expression is not monotone.'
            raise_wrapped(DPSemanticError, e, msg, compact=True)
        
    # Is the first value a constant?
    try:
        x = eval_constant(ops[0], context)
        assert isinstance(x, ValueWithUnits)
        # if so, this is just x - constants[0] - constants[1] - ...
        vu = x_minus_constants(x, constants)
        if wants_constant:
            return vu
        else:
            return get_valuewithunits_as_resource(vu, context)
        
    except NotConstant:
        # if we wanted this to be constant, it's a problem
        if wants_constant:
            raise 

    # first value is not constant

    rvalue = eval_rvalue(ops[0], context)
 
    # we cannot do it with more than 1
    if len(constants) > 1:
        msg = 'This code works only with 1 constant.'
        raise_desc(DPNotImplementedError, msg)
    
    constant = constants[0] 
    R = context.get_rtype(rvalue)
    if isinstance(R, Nat) and isinstance(constant.unit, Nat):
        dp = MinusValueNatDP(constant.value)
    elif isinstance(R, Rcomp) and not isinstance(R, RcompUnits):
        dp = MinusValueRcompDP(constant.value)
    elif isinstance(R, RcompUnits):
        dp = MinusValueDP(F=R, c_value=constant.value, c_space=constant.unit)
    else:
        msg = 'Could not create this operation with %s ' % R
        raise_desc(DPSemanticError, msg, R=R)
             
    return create_operation(context, dp=dp, resources=[rvalue],
                            name_prefix='_minusvalue', op_prefix='_op',
                            res_prefix='_result')
    
def eval_rvalue_PlusN(x, context):
    res = eval_PlusN(x, context, wants_constant=False)
    if isinstance(res, ValueWithUnits):
        return get_valuewithunits_as_resource(res, context)
    else:
        return res

def flatten_multN(ops):
    res = []
    for op in ops:
        if isinstance(op, CDP.MultN):
            res.extend(flatten_multN(get_odd_ops(unwrap_list(op.ops))))
        else:
            res.append(op)
    return res


@contract(x=CDP.MultN, wants_constant=bool,
          returns='$CResource|$ValueWithUnits')
def eval_MultN(x, context, wants_constant):
    """ Raises NotConstant if wants_constant is True. """
    from .misc_math import generic_mult_constantsN
    from .eval_constant_imp import eval_constant

    assert isinstance(x, CDP.MultN)

    ops = flatten_multN(get_odd_ops(unwrap_list(x.ops)))
    assert len(ops) > 1

    # divide constants and resources
    constants = []
    resources = []

    for op in ops:
        try:
            x = eval_constant(op, context)
            assert isinstance(x, ValueWithUnits)
            constants.append(x)
        except NotConstant as e:
            if wants_constant:
                msg = 'Product not constant because one op is not constant.'
                raise_wrapped(NotConstant, e, msg, op=op)
            x = eval_rvalue(op, context)
            assert isinstance(x, CResource)
            resources.append(x)

    # it's a constant value
    if len(resources) == 0:
        return generic_mult_constantsN(constants)

    # it's only resource * (c1*c2*c3*...)
    if len(resources) == 1:
        c = generic_mult_constantsN(constants)
        res = get_mult_op(context, r=resources[0], c=c)
        return res
    else:
        r = eval_MultN_ops(resources, context)
        
        if not constants:
            return r
        else:
            c = generic_mult_constantsN(constants)
            return get_mult_op(context, r, c)

@contract(returns=CResource)
def eval_MultN_ops(resources,  context):
    """ Creates the Product?ops, using the strategy in MCDPConstants.force_mult_two_resources. """
    assert len(resources) >= 2
    
    if MCDPConstants.force_mult_two_resources:
        return eval_MultN_ops_onlytwo(resources,  context)
    else:
        return eval_MultN_ops_multi(resources, context)
    
@contract(returns=CResource)
def eval_MultN_ops_onlytwo(resources,  context):
    if len(resources) == 2:
        return eval_MultN_ops_multi(resources, context)
    else:
        first = resources[0]
        rest = eval_MultN_ops_onlytwo(resources[1:], context)
        return eval_MultN_ops_onlytwo([first, rest],  context)
    
@contract(returns=CResource)
def eval_MultN_ops_multi(resources,  context):
    from .misc_math import  generic_mult_table
    resources_types = [context.get_rtype(_) for _ in resources]
    promoted, R = generic_mult_table(resources_types)

    resources2 = []
    for resource, P in zip(resources, promoted):
        resources2.append(get_resource_possibly_converted(resource, P, context))

    if isinstance(R, Nat):
        n = len(resources)
        dp = ProductNNatDP(n)
    elif isinstance(R, Rcomp):
        dp = ProductNRcompDP(len(resources))
    elif isinstance(R, RcompUnits):
        resources_types2 = [context.get_rtype(_) for _ in resources2]
        dp = ProductNDP(tuple(resources_types2), R)
    else:
        msg = 'Something wrong'
        raise_desc(DPInternalError, msg, resources=resources, promoted=promoted, R=R)
        
    r = create_operation(context, dp, resources,
                         name_prefix='_prod', op_prefix='_factor',
                         res_prefix='_result')
    return r


@contract(r=CResource, c=ValueWithUnits)
def get_mult_op(context, r, c):
    rtype = context.get_rtype(r)

    # Case 1: rcompunits, rcompunits
    if isinstance(rtype, RcompUnits) and isinstance(c.unit, RcompUnits):
        F = rtype
        R = mult_table(rtype, c.unit)
        dp = MultValueDP(F=F, R=R, unit=c.unit, value=c.value) 
    elif isinstance(rtype, Nat) and isinstance(c.unit, Nat):
        dp = MultValueNatDP(c.value)
    else:
        msg = 'Cannot create multiplication operation.'
        raise_desc(DPInternalError, msg, rtype=rtype, c=c)

    r2 = create_operation(context, dp, resources=[r],
                          name_prefix='_mult', op_prefix='_x',
                          res_prefix='_y')
    return r2


def flatten_plusN(ops):
    """ Flattens recursively nested CDP.PlusN operators """
    res = []
    for op in ops:
        if isinstance(op, CDP.PlusN):
            res.extend(flatten_plusN(get_odd_ops(unwrap_list(op.ops))))
        else:
            res.append(op)
    return res

def eval_PlusN_sort_ops(ops, context, wants_constant):
    """
            pos_constants, neg_constants, resources = sort_ops(ops, context)
    """
    from .eval_constant_imp import eval_constant

    pos_constants = []
    neg_constants = []
    resources = []

    for op in ops:
        try:
            x = eval_constant(op, context)
            check_isinstance(x, ValueWithUnits)

            if isinstance(x.unit, (RcompUnits, Nat)):
                pos_constants.append(x)
            elif isinstance(x.unit, RbicompUnits):
                neg_constants.append(x)
            else:
                msg = 'Invalid addition - needs error'
                raise_desc(DPInternalError, msg, x=x)
                
        except NotConstant as e:
            if wants_constant:
                msg = 'Sum not constant because one op is not constant.'
                raise_wrapped(NotConstant, e, msg, op=op)
            x = eval_rvalue(op, context)
            assert isinstance(x, CResource)
            resources.append(x)
            
    return pos_constants, neg_constants, resources

def eval_PlusN(x, context, wants_constant):
    """ Raises NotConstant if wants_constant is True. """
    assert isinstance(x, CDP.PlusN)
    assert len(x.ops) > 1

    # ops as a list
    ops_list = get_odd_ops(unwrap_list(x.ops))
    
    # First, we flatten all operators
    ops = flatten_plusN(ops_list)
    
    # Then we divide in positive constants, negative constants, and resources.
    pos_constants, neg_constants, resources = \
        eval_PlusN_sort_ops(ops, context, wants_constant)
     
    # first, sum the positive constants and the resources
    res = eval_PlusN_(pos_constants, resources, context)

    if len(neg_constants) == 0:
        # If there are no negative constants, we are done
        return res
    elif len(neg_constants) > 1:
            msg = 'Not implemented addition of more than one negative constant.'
            raise_desc(DPInternalError, msg, neg_constants=neg_constants)
    else:
        # we have only one negative constant
        assert len(neg_constants) == 1
        constant = neg_constants[0]
        
        check_isinstance(constant.unit, RbicompUnits)
        
        constant.unit.check_leq(constant.value, 0.0)
        # now it's a positive value
        valuepos = RbicompUnits_reflect(constant.unit, constant.value)
        
        F = context.get_rtype(res)
        
        c_space = RcompUnits(pint_unit=constant.unit.units,
                             string=constant.unit.string)

        # mainly to make sure we handle Top
        if is_top(constant.unit, valuepos):
            valuepos2 = c_space.get_top()
        else:
            valuepos2 = valuepos
            
        #valuepos2 = express_value_in_isomorphic_space(constant.unit, valuepos, c_space)
        
        dp = MinusValueDP(F=F, c_value=valuepos2, c_space=c_space)

        r2 = create_operation(context, dp, resources=[res],
                              name_prefix='_minus', op_prefix='_x',
                              res_prefix='_y')
        return r2

def eval_PlusN_(constants, resources, context):
    from .misc_math import plus_constantsN
    # it's a constant value
    if len(resources) == 0:
        return plus_constantsN(constants)

    elif len(resources) == 1:
        if len(constants) > 0:
            c = plus_constantsN(constants)
            return get_plus_op(context, r=resources[0], c=c)
        else:
            return resources[0]
    else:
        # there are some resources

        r =  eval_PlusN_ops(resources, context) 
        if not constants:
            return r
        else:
            c = plus_constantsN(constants)
            return get_plus_op(context, r=r, c=c)


def eval_PlusN_ops(resources, context):
    if MCDPConstants.force_plus_two_resources:
        return eval_PlusN_ops_two(resources, context)
    else:
        return eval_PlusN_ops_multi(resources, context)

def eval_PlusN_ops_two(resources, context):
    if len(resources) == 2:
        return eval_PlusN_ops_multi(resources, context)
    else:
        first = resources[0]
        rest = eval_PlusN_ops_multi(resources[1:], context)
        return eval_PlusN_ops_multi([first, rest], context) 
        
def eval_PlusN_ops_multi(resources, context):
    resources_types = [context.get_rtype(_) for _ in resources]
    target_int = Int()
    tu = get_types_universe()
    def castable_to_int(_):
        return tu.leq(_, target_int)

    def exactly_Rcomp_or_Nat(x):
        return exactly_Rcomp(x) or isinstance(x, Nat)
        
    def exactly_Rcomp(x):
        return isinstance(x, Rcomp)

    if all(exactly_Rcomp(_) for _ in resources_types):
        n = len(resources_types)
        dp = SumNRcompDP(n)
    elif all(isinstance(_, RcompUnits) for _ in resources_types):
        # addition between floats
        R = resources_types[0]
        Fs = tuple(resources_types)
        try:
            sum_dimensionality_works(Fs, R)
        except ValueError:
            msg = ''
            for r, rt in zip(resources, resources_types):
                msg += '- %s has type %s\n' % (r, rt)
            raise_desc(DPSemanticError, 'Incompatible units:\n%s' % msg)

        dp = SumNDP(Fs, R)
    elif all(isinstance(_, Nat) for _ in resources_types):
        # natural number
        dp = SumNNatDP(len(resources))
    elif all(castable_to_int(_) for _ in resources_types):
        # XXX cast
        dp = SumNIntDP(len(resources))
    elif all(exactly_Rcomp_or_Nat(_) for _ in resources_types):
        resources = [get_resource_possibly_converted(_, Rcomp(), context)
                     for _ in resources]
        dp = SumNRcompDP(len(resources))
    else:
        msg = 'Cannot find sum operator for combination of types.'
        raise_desc(DPInternalError, msg, resources_types=resources_types)

    r = create_operation(context, dp, resources,
                         name_prefix='_sum', op_prefix='_term',
                         res_prefix='_result')
    return r


@contract(r=CResource, c=ValueWithUnits)
def get_plus_op(context, r, c):
    """ r + constant """
    rtype = context.get_rtype(r)
    
    T1 = rtype
    T2 = c.unit

    if isinstance(T1, Rcomp) and isinstance(T2, Rcomp):
        dp = PlusValueRcompDP(c.value)
    if isinstance(T1, Rcomp) and isinstance(T2, Nat):
        # cast Nat to Rcomp
        val = float(c.value)
        dp = PlusValueRcompDP(val)
    elif isinstance(T1, RcompUnits) and isinstance(T2, RcompUnits):
        dp = PlusValueDP(F=T1, c_value=c.value, c_space=T2)
    elif isinstance(T1, Nat) and isinstance(T2, Nat):
        dp = PlusValueNatDP(c.value)
    else:
        msg = 'Cannot create addition operation.'
        raise_desc(DPInternalError, msg, rtype=T1, c=c)

    r2 = create_operation(context, dp, resources=[r],
                          name_prefix='_plus', op_prefix='_x',
                          res_prefix='_y')
    return r2
