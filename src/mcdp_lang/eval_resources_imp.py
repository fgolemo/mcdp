# -*- coding: utf-8 -*-
from contracts import contract
from contracts.utils import raise_desc, raise_wrapped
from mcdp_dp.dp_approximation import  makeLinearCeilDP, \
    makeLinearFloor0DP
from mcdp_dp.dp_plus_value import PlusValueDP
from mcdp_dp.dp_uncertain import UncertainGate
from mcdp_lang.parse_actions import decorate_add_where
from mcdp_posets import (NotLeq, express_value_in_isomorphic_space,
    get_types_universe, poset_minima)
from mocdp.comp.context import CResource, ValueWithUnits, get_name_for_fun_node
from mocdp.exceptions import DPSemanticError

from .eval_constant_imp import eval_constant
from .helpers import create_operation, get_valuewithunits_as_resource
from .namedtuple_tricks import recursive_print
from .parts import CDPLanguage


CDP = CDPLanguage

class DoesNotEvalToResource(DPSemanticError):
    """ also called "rvalue" """

@decorate_add_where
@contract(returns=CResource)
def eval_rvalue(rvalue, context):
    """
        raises DoesNotEvalToResource
    """
    # assert not isinstance(rvalue, ValueWithUnits)
    # wants Resource or NewFunction
    #     with add_where_information(rvalue.where):

    constants = (CDP.Collection, CDP.SimpleValue, CDP.SpaceCustomValue,
                 CDP.Top, CDP.Bottom, CDP.Maximals, CDP.Minimals)

    if isinstance(rvalue, constants):
        res = eval_constant(rvalue, context)
        assert isinstance(res, ValueWithUnits)
        return get_valuewithunits_as_resource(res, context)

    from .eval_resources_imp_power import eval_rvalue_Power
    from .eval_math import eval_rvalue_divide
    from .eval_math import eval_rvalue_MultN
    from .eval_math import eval_rvalue_PlusN
    from .eval_resources_imp_minmax import eval_rvalue_OpMax
    from .eval_resources_imp_minmax import eval_rvalue_OpMin
    from .eval_resources_imp_tupleindex import eval_rvalue_TupleIndex
    from .eval_resources_imp_maketuple import eval_rvalue_MakeTuple
    from .eval_uncertainty import eval_rvalue_Uncertain
    from .eval_resources_imp_tupleindex import eval_rvalue_resource_label_index
    from .eval_resources_imp_unary import eval_rvalue_unary
    from .eval_math import eval_rvalue_RValueMinusN

    cases = {
        CDP.Resource: eval_rvalue_Resource,
        CDP.Power: eval_rvalue_Power,
        CDP.VariableRef: eval_rvalue_VariableRef,
        CDP.NewFunction : eval_rvalue_NewFunction,
        CDP.PowerShort: eval_rvalue_Power,
        CDP.Divide: eval_rvalue_divide,
        CDP.MultN: eval_rvalue_MultN,
        CDP.PlusN: eval_rvalue_PlusN,
        CDP.RValueMinusN: eval_rvalue_RValueMinusN,
        CDP.OpMax: eval_rvalue_OpMax,
        CDP.OpMin: eval_rvalue_OpMin,
        CDP.TupleIndexRes: eval_rvalue_TupleIndex,
        CDP.MakeTuple: eval_rvalue_MakeTuple,
        CDP.UncertainRes: eval_rvalue_Uncertain,
        CDP.ResourceLabelIndex: eval_rvalue_resource_label_index,
        CDP.AnyOfRes: eval_rvalue_anyofres,
        CDP.ApproxStepRes: eval_rvalue_approx_step,
        CDP.ApproxURes: eval_rvalue_approx_u,
        CDP.UnaryRvalue: eval_rvalue_unary,
    }

    for klass, hook in cases.items():
        if isinstance(rvalue, klass):
            return hook(rvalue, context)

    if True: # pragma: no cover    
        msg = 'eval_rvalue(): Cannot evaluate as resource.'
        rvalue = recursive_print(rvalue)
        raise_desc(DoesNotEvalToResource, msg, rvalue=rvalue)
 
def eval_rvalue_Resource(rvalue, context):
    if isinstance(rvalue, CDP.Resource):
        return context.make_resource(dp=rvalue.dp.value, s=rvalue.s.value)
    
def eval_rvalue_VariableRef(rvalue, context):
    if rvalue.name in context.constants:
        c = context.constants[rvalue.name]
        assert isinstance(c, ValueWithUnits)
        return get_valuewithunits_as_resource(c, context)
        # return eval_rvalue(context.constants[rvalue.name], context)

    elif rvalue.name in context.var2resource:
        return context.var2resource[rvalue.name]

    try:
        dummy_ndp = context.get_ndp_fun(rvalue.name)
    except ValueError:  # as e:
        msg = 'Function %r not declared.' % rvalue.name

        if context.fnames:
            msg += ' Available: %s.' % ", ".join(context.fnames)
        else:
            msg += ' No function declared so far.'
        raise DPSemanticError(msg, where=rvalue.where)

    s = dummy_ndp.get_rnames()[0]
    return context.make_resource(get_name_for_fun_node(rvalue.name), s)

def eval_rvalue_NewFunction(rvalue, context):
    fname = rvalue.name
    try:
        dummy_ndp = context.get_ndp_fun(fname)
    except ValueError:
        msg = 'New resource name %r not declared.' % fname
        if context.rnames:
            msg += ' Available: %s.' % ", ".join(context.rnames)
        else:
            msg += ' No resources declared so far.'
        raise DPSemanticError(msg, where=rvalue.where)

    return context.make_resource(get_name_for_fun_node(fname),
                                 dummy_ndp.get_rnames()[0])
        
def eval_rvalue_approx_u(r, context):
    assert isinstance(r, CDP.ApproxURes)

    #
    #  r1-approx-r2----------------- Uncertainty gate
    #          |____(+ step)--[r3]|

    r1 = eval_rvalue(r.rvalue, context)
    step = eval_constant(r.step, context)

    R = context.get_rtype(r1)
    tu = get_types_universe()
    try:
        tu.check_leq(step.unit, R)
    except NotLeq as e:
        msg = ('The step is specified in a unit (%s), which is not compatible '
               'with the resource (%s).' % (step.unit, R))
        raise_wrapped(DPSemanticError, e, msg, compact=True)

    stepu = step.cast_value(R)
    if stepu == 0.0:
        return r1

    dp = makeLinearFloor0DP(R, stepu)

    r2 = create_operation(context, dp=dp, resources=[r1],
                               name_prefix='_approx', op_prefix='_toapprox',
                                res_prefix='_result')

    dpsum = PlusValueDP(R, c_value=step.value, c_space=step.unit)
    r3 = create_operation(context, dp=dpsum, resources=[r2],
                               name_prefix='_sum', op_prefix='_op',
                                res_prefix='_result')


    dpu = UncertainGate(R)

    return create_operation(context, dp=dpu, resources=[r2, r3],
                            name_prefix='_uncertain', op_prefix='_resources',
                            res_prefix='_result')





def eval_rvalue_approx_step(r, context):
    assert isinstance(r, CDP.ApproxStepRes)

    resource = eval_rvalue(r.rvalue, context)
    step = eval_constant(r.step, context)
    
    R = context.get_rtype(resource)
    tu = get_types_universe()
    try:
        tu.check_leq(step.unit, R)
    except NotLeq:
        msg = ('The step is specified in a unit (%s), which is not compatible '
               'with the resource (%s).' % (step.unit, R))
        raise_desc(DPSemanticError, msg)

    stepu = express_value_in_isomorphic_space(S1=step.unit, s1=step.value, S2=R)

    dp = makeLinearCeilDP(R, stepu)

    return create_operation(context, dp=dp, resources=[resource],
                               name_prefix='_approx', op_prefix='_toapprox',
                                res_prefix='_result')



def eval_rvalue_anyofres(r, context):
    from mcdp_posets import FiniteCollectionsInclusion
    from mcdp_posets import FiniteCollection
    from mcdp_dp.dp_constant import ConstantMinimals

    assert isinstance(r, CDP.AnyOfRes)
    constant = eval_constant(r.value, context)
    if not isinstance(constant.unit, FiniteCollectionsInclusion):
        msg = ('I expect that the argument to any-of evaluates to '
              'a finite collection.')
        raise_desc(DPSemanticError, msg, constant=constant)
    assert isinstance(constant.unit, FiniteCollectionsInclusion)
    P = constant.unit.S
    assert isinstance(constant.value, FiniteCollection)

    elements = constant.value.elements
    minimals = poset_minima(elements, P.leq)
    if len(elements) != len(minimals):
        msg = 'The elements are not minimal.'
        raise_desc(DPSemanticError, msg, elements=elements, minimals=minimals)

    dp = ConstantMinimals(R=P, values=minimals)
    return create_operation(context, dp=dp, resources=[],
                               name_prefix='_anyof', op_prefix='_',
                                res_prefix='_result')

