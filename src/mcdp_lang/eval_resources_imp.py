# -*- coding: utf-8 -*-
from .eval_constant_imp import eval_constant
from .helpers import get_valuewithunits_as_resource
from .namedtuple_tricks import recursive_print
from .parse_actions import add_where_information
from .parts import CDPLanguage
from contracts import contract
from contracts.utils import raise_desc, raise_wrapped
from mcdp_posets.find_poset_minima.baseline_n2 import poset_minima
from mocdp.comp.context import CResource, ValueWithUnits, get_name_for_fun_node
from mocdp.exceptions import DPSemanticError
from mcdp_posets.types_universe import express_value_in_isomorphic_space, \
    get_types_universe
from mcdp_dp.dp_approximation import CombinedCeilMap
from mcdp_dp.dp_generic_unary import WrapAMap
from mcdp_lang.helpers import create_operation
from mcdp_posets.poset import NotLeq


CDP = CDPLanguage

class DoesNotEvalToResource(DPSemanticError):
    """ also called "rvalue" """

@contract(returns=CResource)
def eval_rvalue(rvalue, context):
    """
        raises DoesNotEvalToResource
    """
    assert not isinstance(rvalue, ValueWithUnits)
    # wants Resource or NewFunction
    with add_where_information(rvalue.where):

        constants = (CDP.Collection, CDP.SimpleValue, CDP.SpaceCustomValue,
                     CDP.Top, CDP.Bottom, CDP.Maximals, CDP.Minimals)
        if isinstance(rvalue, constants):
            res = eval_constant(rvalue, context)
            assert isinstance(res, ValueWithUnits)
            return get_valuewithunits_as_resource(res, context)

        if isinstance(rvalue, CDP.Resource):
            return context.make_resource(dp=rvalue.dp.value, s=rvalue.s.value)

        if isinstance(rvalue, CDP.NewFunction):
            fname = rvalue.name
            try:
                dummy_ndp = context.get_ndp_fun(fname)
            except ValueError as e:
                msg = 'New resource name %r not declared.' % fname
                msg += '\n%s' % str(e)
                raise DPSemanticError(msg, where=rvalue.where)

            return context.make_resource(get_name_for_fun_node(fname),
                                         dummy_ndp.get_rnames()[0])



        if isinstance(rvalue, CDP.VariableRef):
            if rvalue.name in context.constants:
                c = context.constants[rvalue.name]
                assert isinstance(c, ValueWithUnits)
                return get_valuewithunits_as_resource(c, context)
                # return eval_rvalue(context.constants[rvalue.name], context)

            elif rvalue.name in context.var2resource:
                return context.var2resource[rvalue.name]

            try:
                dummy_ndp = context.get_ndp_fun(rvalue.name)
            except ValueError as e:
                msg = 'Resource %r not declared.' % rvalue.name
#                 msg += '\n%s' % str(e)
                raise DPSemanticError(msg, where=rvalue.where)

            s = dummy_ndp.get_rnames()[0]
            return context.make_resource(get_name_for_fun_node(rvalue.name), s)

        from .eval_resources_imp_power import eval_rvalue_Power
        from .eval_math import eval_rvalue_divide
        from .eval_math import eval_rvalue_MultN
        from .eval_math import eval_rvalue_PlusN
        from .eval_resources_imp_minmax import eval_rvalue_OpMax
        from .eval_resources_imp_minmax import eval_rvalue_OpMin
        from .eval_resources_imp_genericnonlin import eval_rvalue_GenericNonlinearity
        from .eval_resources_imp_tupleindex import eval_rvalue_TupleIndex
        from .eval_resources_imp_maketuple import eval_rvalue_MakeTuple
        from .eval_uncertainty import eval_rvalue_Uncertain
        from mcdp_lang.eval_resources_imp_tupleindex import eval_rvalue_resource_label_index

        cases = {
            CDP.GenericNonlinearity : eval_rvalue_GenericNonlinearity,
            CDP.Power: eval_rvalue_Power,
            CDP.Divide: eval_rvalue_divide,
            CDP.MultN: eval_rvalue_MultN,
            CDP.PlusN: eval_rvalue_PlusN,
            CDP.OpMax: eval_rvalue_OpMax,
            CDP.OpMin: eval_rvalue_OpMin,
            CDP.TupleIndexRes: eval_rvalue_TupleIndex,
            CDP.MakeTuple: eval_rvalue_MakeTuple,
            CDP.UncertainRes: eval_rvalue_Uncertain,
            CDP.ResourceLabelIndex: eval_rvalue_resource_label_index,
            CDP.AnyOfRes: eval_rvalue_anyofres,
            CDP.ApproxStepRes: eval_rvalue_approx_step,
        }

        for klass, hook in cases.items():
            if isinstance(rvalue, klass):
                return hook(rvalue, context)

        msg = 'eval_rvalue(): Cannot evaluate as resource.'
        rvalue = recursive_print(rvalue)
        raise_desc(DoesNotEvalToResource, msg, rvalue=rvalue)


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

    ccm = CombinedCeilMap(R, alpha=0.0, step=stepu, max_value=None)
    dp = WrapAMap(ccm)

    return create_operation(context, dp=dp, resources=[resource],
                               name_prefix='_approx', op_prefix='_toapprox',
                                res_prefix='_result')



def eval_rvalue_anyofres(r, context):
    from mcdp_posets import FiniteCollectionsInclusion
    from mcdp_posets import FiniteCollection
    from mcdp_dp.dp_constant import ConstantMinimals
    from mcdp_lang.helpers import create_operation

    assert isinstance(r, CDP.AnyOfRes)
    constant = eval_constant(r.value, context)
    if not isinstance(constant.unit, FiniteCollectionsInclusion):
        msg = 'I expect that the argument to any-of evaluates to a finite collection.'
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

