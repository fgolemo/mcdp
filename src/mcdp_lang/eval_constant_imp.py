# -*- coding: utf-8 -*-
from contracts import contract
from contracts.utils import raise_desc, raise_wrapped, check_isinstance
from mcdp_posets import (FiniteCollection, FiniteCollectionsInclusion, Int, Nat,
    NotBelongs, NotLeq, PosetProduct, Rcomp, Space, UpperSet, UpperSets,
    get_types_universe, poset_minima)
from mcdp_posets import FiniteCollectionAsSpace
from mcdp_posets import LowerSets, LowerSet, RbicompUnits, RcompUnits
from mcdp_posets.types_universe import express_value_in_isomorphic_space
from mocdp.comp.context import ValueWithUnits
from mocdp.exceptions import (DPInternalError, DPSemanticError, mcdp_dev_warning,
    do_extra_checks)

from .eval_constant_asserts import (eval_assert_empty, eval_assert_equal,
    eval_assert_geq, eval_assert_gt, eval_assert_leq, eval_assert_lt,
    eval_assert_nonempty)
from .namedtuple_tricks import recursive_print
from .parse_actions import add_where_information
from .parts import CDPLanguage
from .utils_lists import get_odd_ops, unwrap_list


CDP = CDPLanguage

class NotConstant(DPSemanticError):
    pass 
         

@contract(returns=ValueWithUnits)
def eval_constant(op, context):
    """ 
        Raises NotConstant if not constant. 
        Returns ValueWithUnits
    """
    from .eval_math import (eval_constant_divide, eval_PlusN_as_constant,
                            eval_RValueMinusN_as_constant, eval_MultN_as_constant)


    with add_where_information(op.where):

        if isinstance(op, (CDP.Resource)):
            raise NotConstant(str(op))

        if isinstance(op, (CDP.OpMax, CDP.OpMin, CDP.Power)):
            # TODO: can implement optimization
            raise NotConstant(str(op))

        cases = {
            CDP.NatConstant: eval_constant_NatConstant,
            CDP.IntConstant: eval_constant_IntConstant,
            CDP.SimpleValue: eval_constant_SimpleValue,
            CDP.VariableRef: eval_constant_VariableRef,
            CDP.MakeTuple: eval_constant_MakeTuple,
            CDP.AssertEqual: eval_assert_equal,
            CDP.AssertLEQ: eval_assert_leq,
            CDP.AssertGEQ: eval_assert_geq,
            CDP.AssertLT: eval_assert_lt,
            CDP.AssertGT: eval_assert_gt,
            CDP.AssertNonempty: eval_assert_nonempty,
            CDP.AssertEmpty: eval_assert_empty,
            CDP.Divide: eval_constant_divide,
            CDP.Collection: eval_constant_collection,
            CDP.SpaceCustomValue: eval_constant_space_custom_value,
            CDP.PlusN: eval_PlusN_as_constant,
            CDP.RValueMinusN: eval_RValueMinusN_as_constant,
            CDP.MultN: eval_MultN_as_constant,
            CDP.EmptySet: eval_EmptySet,
            CDP.UpperSetFromCollection: eval_constant_uppersetfromcollection,
            CDP.LowerSetFromCollection: eval_constant_lowersetfromcollection,
            CDP.SolveModel: eval_solve_f,
            CDP.SolveRModel: eval_solve_r,
            CDP.Top: eval_constant_Top,
            CDP.Maximals: eval_constant_Maximals,
            CDP.Minimals: eval_constant_Minimals,
            CDP.Bottom: eval_constant_Bottom,
        }
        
        for klass, hook in cases.items():
            if isinstance(op, klass):
                return hook(op, context)

        if True: # pragma: no cover    
            msg = 'eval_constant(): Cannot evaluate this as constant.'
            op = recursive_print(op)
            raise_desc(NotConstant, msg, op=op)


def eval_constant_NatConstant(op, context):  # @UnusedVariable
    return ValueWithUnits(unit=Nat(), value=op.value)

def eval_constant_IntConstant(op, context):  # @UnusedVariable
    return ValueWithUnits(unit=Int(), value=op.value)

def eval_constant_VariableRef(op, context):
    if op.name in context.constants:
        return context.constants[op.name]

    if op.name in context.var2resource:
        res = context.var2resource[op.name]
        msg = 'This is a resource.'
        raise_desc(NotConstant, msg, res=res)

    try:
        x = context.get_ndp_fun(op.name)
    except ValueError:
        pass
    else:
        raise_desc(NotConstant, 'Corresponds to new function.', x=x)

    msg = 'Variable ref %r unknown.' % op.name
    raise DPSemanticError(msg, where=op.where)


def eval_constant_SimpleValue(op, context):
    from .eval_space_imp import eval_space  # @Reimport
    F = eval_space(op.space, context)
    assert isinstance(F, Space), op
    assert isinstance(F, RcompUnits)

    v = op.value.value

    # promote integer to float
    if isinstance(v, int) and isinstance(F, (Rcomp, RcompUnits)):
        v = float(v)

    if v < 0:
        if isinstance(F, RcompUnits):
            F = RbicompUnits(F.units, F.string)
        else:
            msg = 'Negative %s not implemented yet.' % F
            raise_desc(NotImplementedError, msg, F=F)

    try:
        F.belongs(v)
    except NotBelongs as e:
        msg = 'Not in space'
        raise_wrapped(DPSemanticError, e, msg, F=F, v=v, op=op)
    return ValueWithUnits(unit=F, value=v)


def eval_constant_Top(op, context):
    from .eval_space_imp import eval_space
    space = eval_space(op.space, context)
    v = space.get_top()
    return ValueWithUnits(unit=space, value=v)


def eval_constant_Maximals(op, context):
    from .eval_space_imp import eval_space  # @Reimport
    space = eval_space(op.space, context)
    elements = space.get_maximal_elements()
    v = FiniteCollection(elements=elements, S=space)
    S = FiniteCollectionsInclusion(space)
    return ValueWithUnits(unit=S, value=v)

    
def eval_constant_Minimals(op, context):
    from .eval_space_imp import eval_space  # @Reimport
    space = eval_space(op.space, context)
    elements = space.get_minimal_elements()
    v = FiniteCollection(elements=elements, S=space)
    S = FiniteCollectionsInclusion(space)
    return ValueWithUnits(unit=S, value=v)


def eval_constant_Bottom(op, context):
    from .eval_space_imp import eval_space  # @Reimport
    space = eval_space(op.space, context)
    v = space.get_bottom()
    return ValueWithUnits(unit=space, value=v)


def eval_constant_MakeTuple(op, context):
    ops = get_odd_ops(unwrap_list(op.ops))
    constants = [eval_constant(_, context) for _ in ops]
    # TODO: generic product
    Fs = [_.unit for _ in constants]
    vs = [_.value for _ in constants]
    F = PosetProduct(tuple(Fs))
    v = tuple(vs)
    F.belongs(v)
    return ValueWithUnits(v, F)


def eval_solve_f(op, context):
    check_isinstance(op, CDP.SolveModel)
    from .eval_ndp_imp import eval_ndp
    ndp = eval_ndp(op.model, context)
    dp = ndp.get_dp()
    f0 = eval_constant(op.f, context)
    F = dp.get_fun_space()
    R = dp.get_res_space()

    tu = get_types_universe()
    try:
        tu.check_leq(f0.unit, F)
    except NotLeq as e:
        msg = 'Input not correct.'
        raise_wrapped(DPSemanticError, e, msg, compact=True)
    f = express_value_in_isomorphic_space(f0.unit, f0.value, F)
    res = dp.solve(f)
    UR = UpperSets(R)
    return ValueWithUnits(res, UR)

def eval_solve_r(op, context):
    check_isinstance(op, CDP.SolveRModel)
    from .eval_ndp_imp import eval_ndp
    
    ndp = eval_ndp(op.model, context)
    dp = ndp.get_dp()
    r0 = eval_constant(op.r, context)
    F = dp.get_fun_space()
    R = dp.get_res_space()

    tu = get_types_universe()
    try:
        tu.check_leq(r0.unit, R)
    except NotLeq as e:
        msg = 'Input not correct.'
        raise_wrapped(DPSemanticError, e, msg, compact=True)
    r = express_value_in_isomorphic_space(r0.unit, r0.value, R)
    
    res = dp.solve_r(r)
    LF = LowerSets(F)
    return ValueWithUnits(res, LF)
                                  
def eval_EmptySet(op, context):
    check_isinstance(op, CDP.EmptySet)
    from .eval_space_imp import eval_space
    space = eval_space(op.space, context)
    
    P = FiniteCollectionsInclusion(space)
    value = FiniteCollection(set([]), space)
    return ValueWithUnits(unit=P, value=value)



def eval_constant_space_custom_value(op, context):
    from .eval_space_imp import eval_space
    assert isinstance(op, CDP.SpaceCustomValue)
    space = eval_space(op.space, context)
    custom_string = op.custom_string

    if isinstance(space, FiniteCollectionAsSpace):
        if custom_string == '*':
            if len(space.elements) == 1:
                value = list(space.elements)[0]
                return ValueWithUnits(unit=space, value=value)
            else:
                msg = 'You can use "*" only if the space has one element.'
                raise_desc(DPSemanticError, msg, elements=space.elements)
        try:
            space.belongs(custom_string)
            mcdp_dev_warning('this does not seem to work...')
        except NotBelongs as e:
            msg = 'The value is not an element of this space.'
            raise_wrapped(DPSemanticError, e, msg, compact=True,
                          custom_string=op.custom_string, space=space)

        return ValueWithUnits(unit=space, value=op.custom_string)
    
    if isinstance(space, Nat):
        mcdp_dev_warning('Top?')
        value = int(custom_string)
        return ValueWithUnits(unit=Nat(), value=value)

    if isinstance(space, Int):
        mcdp_dev_warning('Top?')
        value = int(custom_string)
        return ValueWithUnits(unit=Int(), value=value)

    if isinstance(space, Rcomp):
        mcdp_dev_warning('Top?')
        value = float(custom_string)
        return ValueWithUnits(unit=Rcomp(), value=value)
        
    msg = 'Custom parsing not implemented for space.'
    raise_desc(DPInternalError, msg, space=space, custom_string=custom_string)

def eval_constant_uppersetfromcollection(op, context):
    x = eval_constant(op.value, context)
    v = x.value
    u = x.unit
    S = u.S
    minimals = poset_minima(v.elements, S.leq)
    value = UpperSet(minimals, S)
    unit = UpperSets(S)
    if do_extra_checks():
        unit.belongs(value)
    vu = ValueWithUnits(value, unit)
    return vu

def eval_constant_lowersetfromcollection(op, context):
    x = eval_constant(op.value, context)
    v = x.value
    u = x.unit
    S = u.S
    maximals = poset_minima(v.elements, S.leq)
    value = LowerSet(maximals, S)
    unit = LowerSets(S)
    if do_extra_checks():
        unit.belongs(value)
    vu = ValueWithUnits(value, unit)
    return vu


def eval_constant_collection(op, context):
    ops = get_odd_ops(unwrap_list(op.elements))
    if len(ops) == 0:
        raise DPSemanticError('empty list')
    elements = [eval_constant(_, context) for _ in ops]

    e0 = elements[0]

    u0 = e0.unit
    from .eval_math import convert_vu
    elements = [convert_vu(_.value, _.unit, u0, context) for _ in elements]

    value = FiniteCollection(set(elements), u0)
    unit = FiniteCollectionsInclusion(u0)
    vu = ValueWithUnits(value, unit)
    return vu
