# -*- coding: utf-8 -*-
from contracts import contract
from contracts.utils import raise_desc, raise_wrapped, check_isinstance
from mcdp_dp import MultValueMap, ProductNatN, ProductN, SumNNat, WrapAMap, sum_dimensionality_works, SumNRcompMap
from mcdp_dp.dp_plus_value import PlusValueRcompDP, PlusValueDP, PlusValueNatDP
from mcdp_dp.dp_sum import SumNDP
from mcdp_maps import MinusValueMap, MultNat, SumNInt, SumNRcomp
from mcdp_maps import PlusValueMap
from mcdp_posets import (Int, Nat, RbicompUnits, RcompUnits, Space,
    express_value_in_isomorphic_space, get_types_universe, mult_table, Rcomp)
from mocdp.comp.context import CResource, ValueWithUnits
from mocdp.exceptions import DPInternalError, DPSemanticError

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


def eval_constant_minus(op, context):
    from .eval_constant_imp import eval_constant

    ops = get_odd_ops(unwrap_list(op.ops))
    constants = [eval_constant(_, context) for _ in ops]

    R0 = constants[0].unit
    if not isinstance(R0, RcompUnits):
        msg = 'Cannot evaluate "-" on this space.'
        raise_desc(DPSemanticError, msg, R0=R0)

    # convert each factor to R0
    v0 = constants[0].value
    for c in constants[1:]:
        vi = express_value_in_isomorphic_space(c.unit, c.value, R0)

        if v0 < vi:
            msg = 'Underflow: %s - %s gives a negative number' % (c.unit.format(v0), c.unit.format(vi))
            raise_desc(DPSemanticError, msg)

        v0 = v0 - vi

    return ValueWithUnits(unit=R0, value=v0)

@contract(unit1=Space, unit2=Space)
def convert_vu(value, unit1, unit2, context):  # @UnusedVariable
    tu = get_types_universe()
    A_to_B, _ = tu.get_embedding(unit1, unit2)
    return A_to_B(value)


def eval_PlusN_as_constant(x, context):
    return eval_PlusN(x, context, wants_constant=True)


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


@contract(x=CDP.MultN, wants_constant=bool)
def eval_MultN(x, context, wants_constant):
    """ Raises NotConstant if wants_constant is True. """
    from .misc_math import generic_mult_constantsN, generic_mult_table
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
        return get_mult_op(context, r=resources[0], c=c)

    else:
        # there are some resources
        resources_types = [context.get_rtype(_) for _ in resources]
        promoted, R = generic_mult_table(resources_types)

        resources2 = []
        for resource, P in zip(resources, promoted):
            resources2.append(get_resource_possibly_converted(resource, P, context))
        
        if isinstance(R, Nat):
            n = len(resources2)
            dp = WrapAMap(ProductNatN(n))

        else:
            resources_types2 = [context.get_rtype(_) for _ in resources2]
            dp = ProductN(tuple(resources_types2), R)

        r = create_operation(context, dp, resources2,
                             name_prefix='_prod', op_prefix='_factor',
                             res_prefix='_result')

        if not constants:
            return r
        else:
            c = generic_mult_constantsN(constants)
            return get_mult_op(context, r, c)

class MultValueDP(WrapAMap):
    @contract(F=RcompUnits, R=RcompUnits, unit=RcompUnits)
    def __init__(self, F, R, unit, value):
        amap = MultValueMap(F=F, R=R, value=value)
        from mcdp_posets.rcomp_units import format_pint_unit_short

        label = '× %.5f %s' % (value, format_pint_unit_short(unit.units))
        # label = '× %s' % (c.unit.format(c.value))
        setattr(amap, '__name__', label)
        
        # unit2 = inverse_of_unit(unit)
        value2 = 1.0 / value
        amap_dual = MultValueMap(F=R, R=F, value=value2)
        WrapAMap.__init__(self, amap, amap_dual)


@contract(r=CResource, c=ValueWithUnits)
def get_mult_op(context, r, c):

    rtype = context.get_rtype(r)

    # Case 1: rcompunits, rcompunits
    if isinstance(rtype, RcompUnits) and isinstance(c.unit, RcompUnits):
        F = rtype
        R = mult_table(rtype, c.unit)

        dp = MultValueDP(F=F,R=R,unit=c.unit,value=c.value) 

    elif isinstance(rtype, Nat) and isinstance(c.unit, Nat):
        amap = MultNat(c.value)
        dp = WrapAMap(amap)
    else:
        msg = 'Cannot create multiplication operation.'
        raise_desc(DPInternalError, msg, rtype=rtype, c=c)

    r2 = create_operation(context, dp, resources=[r],
                          name_prefix='_mult', op_prefix='_x',
                          res_prefix='_y')
    return r2


def flatten_plusN(ops):
    res = []
    for op in ops:
        if isinstance(op, CDP.PlusN):
            res.extend(flatten_plusN(get_odd_ops(unwrap_list(op.ops))))
        else:
            res.append(op)
    return res

def eval_PlusN(x, context, wants_constant):
    """ Raises NotConstant if wants_constant is True. """
    from .eval_constant_imp import eval_constant

    assert isinstance(x, CDP.PlusN)
    assert len(x.ops) > 1

    ops = flatten_plusN(get_odd_ops(unwrap_list(x.ops)))
    pos_constants = []
    neg_constants = []
    resources = []

    for op in ops:
        try:
            x = eval_constant(op, context)
            assert isinstance(x, ValueWithUnits)

            if isinstance(x.unit, (RcompUnits, Nat)):
                pos_constants.append(x)
            elif isinstance(x.unit, RbicompUnits):
                neg_constants.append(x)
            else:
                msg = 'Invalid addition - needs error'
                raise_desc(DPInternalError, msg, x=x)
                
        except NotConstant as e:
            if wants_constant:
                msg = 'Product not constant because one op is not constant.'
                raise_wrapped(NotConstant, e, msg, op=op)
            x = eval_rvalue(op, context)
            assert isinstance(x, CResource)
            resources.append(x)

    # first, sum together all the constants

    res = eval_PlusN_(pos_constants, resources, context)

    if not neg_constants:
        return res
    else:
        if len(neg_constants) > 1:
            msg = 'Not implemented addition of more than one negative constant'
            raise_desc(DPInternalError, msg, neg_constants=neg_constants)
        else:
            # only one negative constant
            F = context.get_rtype(res)

            constant = neg_constants[0]
            assert constant.value < 0

            c_space = RcompUnits(pint_unit=constant.unit.units,
                                 string=constant.unit.string)
            amap = MinusValueMap(P=F, c_value=-constant.value, c_space=c_space)

            setattr(amap, '__name__', '- %s' % (constant.unit.format(-constant.value)))
            dp = WrapAMap(amap)

            r2 = create_operation(context, dp, resources=[res],
                              name_prefix='_minus', op_prefix='_x',
                              res_prefix='_y')
            return r2

class MinusValueDP(WrapAMap):
    """ Give a positive constant here """
    def __init__(self, F, c_value, c_space):
        check_isinstance(F, RcompUnits)
        assert c_value >= 0, c_value
        amap = MinusValueMap(P=F, c_value=c_value, c_space=c_space)
        amap_dual = PlusValueMap(F=F, c_value=c_value, c_space=c_space, R=F)
        WrapAMap.__init__(self, amap, amap_dual)
        
class MinusValueRcompDP(WrapAMap):
    """ Give a positive constant here """
    def __init__(self, c_value):
        assert c_value >= 0, c_value
        from mcdp_maps.plus_value_map import MinusValueRcompMap, PlusValueRcompMap

        amap = MinusValueRcompMap(c_value)
        amap_dual = PlusValueRcompMap(c_value=c_value)
        WrapAMap.__init__(self, amap, amap_dual)
        
class MinusValueNatDP(WrapAMap):
    """ Give a positive constant here """
    def __init__(self, c_value):
        assert c_value >= 0, c_value
        from mcdp_maps.plus_nat import MinusValueNatMap, PlusValueNatMap
        amap = MinusValueNatMap(c_value)
        amap_dual = PlusValueNatMap(c_value)
        WrapAMap.__init__(self, amap, amap_dual)

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
        resources_types = [context.get_rtype(_) for _ in resources]

        target_int = Int()
        tu = get_types_universe()
        def castable_to_int(_):
            return tu.leq(_, target_int)

        def exactly_Rcomp_or_Nat(x):
            return exactly_Rcomp(x) or isinstance(x, Nat)
            
        def exactly_Rcomp(x):
            return isinstance(x, Rcomp) and not isinstance(x, RcompUnits)

        if all(exactly_Rcomp(_) for _ in resources_types):
            n = len(resources_types)
            amap = SumNRcompMap(n)
            dp = WrapAMap(amap)
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
            R = Nat()
            dp = SumNNat(tuple(resources_types), R)
        elif all(castable_to_int(_) for _ in resources_types):
            R = Int()
            amap = SumNInt(tuple(resources_types), R)
            dp = WrapAMap(amap)
        elif all(exactly_Rcomp_or_Nat(_) for _ in resources_types):
            resources = [get_resource_possibly_converted(_, Rcomp(), context)
                         for _ in resources]
            amap = SumNRcomp(len(resources))
            dp = WrapAMap(amap)
        else:
            msg = 'Cannot find sum operator for combination of types.'
            raise_desc(DPInternalError, msg, resources_types=resources_types)

        r = create_operation(context, dp, resources,
                             name_prefix='_sum', op_prefix='_term',
                             res_prefix='_result')

        if not constants:
            return r
        else:
            c = plus_constantsN(constants)
            return get_plus_op(context, r=r, c=c)


    
        
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
