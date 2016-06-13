# -*- coding: utf-8 -*-
from .parts import CDPLanguage
from contracts import contract
from contracts.utils import raise_desc, raise_wrapped
from mcdp_lang.parse_actions import add_where_information
from mcdp_lang.utils_lists import get_odd_ops, unwrap_list
from mcdp_posets import (FiniteCollection, FiniteCollectionsInclusion, Int, Nat,
    NotBelongs, PosetProduct, Rcomp, Space, UpperSet, UpperSets)
from mocdp.comp.context import ValueWithUnits
from mocdp.exceptions import DPSemanticError, mcdp_dev_warning
from mcdp_posets.poset import NotLeq
from mcdp_posets.types_universe import get_types_universe

CDP = CDPLanguage

class NotConstant(DPSemanticError):
    pass


@contract(returns=ValueWithUnits)
def eval_constant(op, context):
    """ 
        Raises NotConstant if not constant. 
        Returns ValueWithUnits
    """
    with add_where_information(op.where):

        if isinstance(op, CDP.Divide):
            from mcdp_lang.eval_math import eval_constant_divide
            return eval_constant_divide(op, context)

        if isinstance(op, CDP.NatConstant):
            return ValueWithUnits(unit=Nat(), value=op.value)

        if isinstance(op, CDP.IntConstant):
            return ValueWithUnits(unit=Int(), value=op.value)

        if isinstance(op, CDP.Collection):
            return eval_constant_collection(op, context)

        if isinstance(op, CDP.UpperSetFromCollection):
            return eval_constant_uppersetfromcollection(op, context)

        if isinstance(op, (CDP.Resource)):
            raise NotConstant(str(op))

        if isinstance(op, (CDP.OpMax, CDP.OpMin, CDP.Power)):
            # TODO: can implement optimization
            raise NotConstant(str(op))

        if isinstance(op, (CDP.SpaceCustomValue)):
            return eval_constant_space_custom_value(op, context)

        if isinstance(op, CDP.Top):
            from mcdp_lang.eval_space_imp import eval_space
            space = eval_space(op.space, context)
            v = space.get_top()
            return ValueWithUnits(unit=space, value=v)

        if isinstance(op, CDP.Bottom):
            from mcdp_lang.eval_space_imp import eval_space  # @Reimport
            space = eval_space(op.space, context)
            v = space.get_bottom()
            return ValueWithUnits(unit=space, value=v)

        if isinstance(op, CDP.SimpleValue):
            # assert isinstance(op.unit, CDP.Unit), op
            from mcdp_lang.eval_space_imp import eval_space  # @Reimport
            F = eval_space(op.space, context)
            assert isinstance(F, Space), op

            v = op.value.value

            if isinstance(v, int) and isinstance(F, Rcomp):
                v = float(v)

            try:
                F.belongs(v)
            except NotBelongs as e:
                msg = 'Not in space'
                raise_wrapped(DPSemanticError, e, msg, F=F, v=v, op=op)
            return ValueWithUnits(unit=F, value=v)

        if isinstance(op, CDP.VariableRef):
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

        if isinstance(op, CDP.GenericNonlinearity):
            raise_desc(NotConstant, 'GenericNonlinearity is not constant', op=op)

        if isinstance(op, CDP.PlusN):
            from mcdp_lang.eval_math import eval_PlusN_as_constant
            return eval_PlusN_as_constant(op, context)

        if isinstance(op, CDP.MultN):
            from mcdp_lang.eval_math import eval_MultN_as_constant
            return eval_MultN_as_constant(op, context)

        if isinstance(op, CDP.MakeTuple):
            ops = get_odd_ops(unwrap_list(op.ops))
            constants = [eval_constant(_, context) for _ in ops]
            # TODO: generic product
            Fs = [_.unit for _ in constants]
            vs = [_.value for _ in constants]
            F = PosetProduct(tuple(Fs))
            v = tuple(vs)
            F.belongs(v)
            return ValueWithUnits(v, F)

        if isinstance(op, CDP.SolveModel):
            from mcdp_lang.eval_ndp_imp import eval_ndp
            from mcdp_posets.types_universe import express_value_in_isomorphic_space
            ndp = eval_ndp(op.model, context)
            dp = ndp.get_dp()
            f0 = eval_constant(op.f, context)
            F = dp.get_fun_space()
            mcdp_dev_warning('I never understand this...')
            tu = get_types_universe()
            try:
                tu.check_leq(F, f0.unit)
            except NotLeq as e:
                msg = 'Input not correct.'
                raise_wrapped(DPSemanticError, e, msg, compact=True)
            f = express_value_in_isomorphic_space(f0.unit, f0.value, F)
            res = dp.solve(f)
            UR = UpperSets(dp.get_res_space())
            return ValueWithUnits(res, UR)

        msg = 'eval_constant() cannot evaluate this value as constant.'
        raise_desc(NotConstant, msg, op=str(op))


def eval_constant_space_custom_value(op, context):
    from mcdp_lang.eval_space_imp import eval_space
    assert isinstance(op, CDP.SpaceCustomValue)
    space = eval_space(op.space, context)
    
    from mcdp_posets.finite_set import FiniteCollectionAsSpace
    if isinstance(space, FiniteCollectionAsSpace):
        try:
            space.belongs(op.custom_string)
            mcdp_dev_warning('this does not seem to work...')
        except NotBelongs as e:
            msg = 'The value is not an element of this space.'
            raise_wrapped(DPSemanticError, e, msg, compact=True,
                          custom_string=op.custom_string, space=space)

        return ValueWithUnits(unit=space, value=op.custom_string)
    
    raise_desc(NotImplementedError, space=space)

def eval_constant_uppersetfromcollection(op, context):
    x = eval_constant(op.value, context)
    v = x.value
    u = x.unit
    S = u.S
    value = UpperSet(v.elements, S)
    unit = UpperSets(S)
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
    from mcdp_lang.eval_math import convert_vu
    elements = [convert_vu(_.value, _.unit, u0, context) for _ in elements]

    value = FiniteCollection(set(elements), u0)
    unit = FiniteCollectionsInclusion(u0)
    vu = ValueWithUnits(value, unit)
    return vu
