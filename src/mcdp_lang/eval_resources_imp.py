# -*- coding: utf-8 -*-
from contracts import contract
from contracts.utils import raise_desc, raise_wrapped, check_isinstance
from mcdp.exceptions import DPSemanticError, DPNotImplementedError, DPInternalError
from mcdp_dp import PlusValueDP, UncertainGate
from mcdp_dp.dp_approximation import makeLinearCeilDP, makeLinearFloor0DP
from mcdp_posets import (NotLeq, express_value_in_isomorphic_space,
    get_types_universe, poset_minima)
from mcdp_posets import RcompUnits
from mocdp.comp.context import (CResource, ValueWithUnits, get_name_for_fun_node,
    ModelBuildingContext, UncertainConstant)

from .eval_constant_imp import eval_constant
from .eval_warnings import warn_language, MCDPWarnings
from .helpers import create_operation, get_valuewithunits_as_resource
from .namedtuple_tricks import recursive_print
from .parse_actions import decorate_add_where
from .parts import CDPLanguage


CDP = CDPLanguage


class DoesNotEvalToResource(DPInternalError):
    """ also called "rvalue" """
    

@decorate_add_where
@contract(returns=CResource)
def eval_rvalue(rvalue, context):
    """
        raises DoesNotEvalToResource
        
        suggest_name: use this name for resources to be created
    """
    check_isinstance(context, ModelBuildingContext)

    if isinstance(rvalue, (CDP.NewResource, CDP.DerivFunctionRef)):
        msg = 'The resource %r cannot be used on this side of the constraint.'
        raise_desc(DPSemanticError, msg % rvalue.name.value)
        
    constants = (CDP.Collection, CDP.SimpleValue, CDP.SpaceCustomValue,
                 CDP.Top, CDP.Bottom, CDP.Maximals, CDP.Minimals,
                 CDP.NatConstant, CDP.RcompConstant, CDP.SpecialConstant)

    if isinstance(rvalue, constants):
        res = eval_constant(rvalue, context)
        assert isinstance(res, ValueWithUnits)
        return get_valuewithunits_as_resource(res, context)

    if isinstance(rvalue, CDP.Ellipsis):
        msg = 'Incomplete model (ellipsis)'
        raise_desc(DPSemanticError, msg)
        
    from .eval_resources_imp_power import eval_rvalue_Power
    from .eval_math import eval_rvalue_divide
    from .eval_math import eval_rvalue_MultN
    from .eval_math import eval_rvalue_PlusN
    from .eval_resources_imp_tupleindex import eval_rvalue_TupleIndex
    from .eval_resources_imp_maketuple import eval_rvalue_MakeTuple
    from .eval_uncertainty import eval_rvalue_Uncertain
    from .eval_resources_imp_tupleindex import eval_rvalue_resource_label_index
    from .eval_resources_imp_unary import  eval_rvalue_generic_operation
    from .eval_math import eval_rvalue_RValueMinusN
    from .eval_uncertainty import eval_rvalue_RValuePlusOrMinus
    from .eval_uncertainty import eval_rvalue_RValueBetween
    from .eval_uncertainty import eval_rvalue_RValuePlusOrMinusPercent
    
    
    cases = {
        CDP.Resource: eval_rvalue_Resource,
        CDP.Power: eval_rvalue_Power,
        
        CDP.NewFunction : eval_rvalue_NewFunction,
        CDP.PowerShort: eval_rvalue_Power,
        CDP.Divide: eval_rvalue_divide,
        CDP.MultN: eval_rvalue_MultN,
        CDP.PlusN: eval_rvalue_PlusN,
        CDP.RValueMinusN: eval_rvalue_RValueMinusN,
        CDP.TupleIndexRes: eval_rvalue_TupleIndex,
        CDP.MakeTuple: eval_rvalue_MakeTuple,
        CDP.UncertainRes: eval_rvalue_Uncertain,
        CDP.ResourceLabelIndex: eval_rvalue_resource_label_index,
        CDP.AnyOfRes: eval_rvalue_anyofres,
        CDP.ApproxStepRes: eval_rvalue_approx_step,
        CDP.ApproxURes: eval_rvalue_approx_u,
        CDP.GenericOperationRes: eval_rvalue_generic_operation,
        
        CDP.VariableRef: eval_rvalue_VariableRef,
        CDP.ActualVarRef: eval_rvalue_ActualVarRef,
        CDP.ConstantRef: eval_rvalue_ConstantRef,
        CDP.DerivResourceRef: eval_rvalue_DerivResourceRef,
        CDP.RValueBetween: eval_rvalue_RValueBetween,
        CDP.RValuePlusOrMinus: eval_rvalue_RValuePlusOrMinus,
        CDP.RValuePlusOrMinusPercent: eval_rvalue_RValuePlusOrMinusPercent,
        
        CDP.SumResources: eval_rvalue_SumResources,
    }

    for klass, hook in cases.items():
        if isinstance(rvalue, klass):
            return hook(rvalue, context)

    if True: # pragma: no cover    
        msg = 'eval_rvalue(): Cannot evaluate as resource.'
        rvalue = recursive_print(rvalue)
        raise_desc(DoesNotEvalToResource, msg, rvalue=rvalue)
 
def iterate_normal_ndps(context):
    for n, ndp in context.names.items():
        normal = not context.is_new_function(n) and not context.is_new_resource(n)
        if normal:
            yield n, ndp
            
def eval_rvalue_SumResources(rvalue, context):
    check_isinstance(rvalue, CDP.SumResources)
    rname = rvalue.rname.value
    
    cresources = []
    for n, ndp in iterate_normal_ndps(context):
        if rname in ndp.get_rnames():
            cr = CResource(n, rname)
            cresources.append(cr)
            
    if not cresources:
        msg = 'Cannot find any sub-design problem with resource "%s".' % rname
        raise DPSemanticError(msg, where=rvalue.rname.where)

    from mcdp_lang.eval_math import eval_PlusN_
    if len(cresources) == 1:
        return cresources[0]
    else:
        return eval_PlusN_(constants=[], resources=cresources, context=context)

def eval_rvalue_Resource(rvalue, context):
    if isinstance(rvalue, CDP.Resource):
        return context.make_resource(dp=rvalue.dp.value, s=rvalue.s.value)
    
def eval_rvalue_ConstantRef(rvalue, context):
    check_isinstance(rvalue, CDP.ConstantRef)
    _ = rvalue.cname.value
    if _ in context.constants:
        c = context.constants[_]
        assert isinstance(c, ValueWithUnits)
        return get_valuewithunits_as_resource(c, context)
    else:
        msg = 'Constant value %r not found.' % _
        raise DPSemanticError(msg, where=rvalue.where) # or internal?

def eval_rvalue_DerivResourceRef(rvalue, context):
    check_isinstance(rvalue, CDP.DerivResourceRef)
    _ = rvalue.drname.value
    if _  in context.var2resource:
        return context.var2resource[_]
    else:
        msg = 'Derivative resource %r not found.' % _
        raise DPSemanticError(msg, where=rvalue.where) # or internal?

def eval_rvalue_ActualVarRef(rvalue, context):
    check_isinstance(rvalue, CDP.ActualVarRef)

    _ = rvalue.vname.value
    if _  in context.var2resource:
        return context.var2resource[_]
    else:
        msg = 'Cannot resolve variable %r not found.' % _
        raise DPSemanticError(msg, where=rvalue.where) # or internal?

def eval_rvalue_VariableRef(rvalue, context):
    from .helpers import get_uncertainconstant_as_resource
    if rvalue.name in context.constants:
        c = context.constants[rvalue.name]
        assert isinstance(c, ValueWithUnits)
        return get_valuewithunits_as_resource(c, context)
    elif rvalue.name in context.uncertain_constants:
        uc = context.uncertain_constants[rvalue.name]
        assert isinstance(uc, UncertainConstant)
        return get_uncertainconstant_as_resource(uc, context)
    elif rvalue.name in context.var2resource:
        return context.var2resource[rvalue.name]
    try:
        dummy_ndp = context.get_ndp_fun(rvalue.name)
    except ValueError:  # as e:
        msg = 'Function %r not declared.' % rvalue.name

        if context.fnames:
            msg += ' Available functions: %s.' % ", ".join(context.fnames)
        else:
            msg += ' No function declared so far.'
        if context.constants:
            msg += ' Available constants: %s.' % ", ".join(context.constants)
        else:
            msg += ' No constants declared so far.'
        if context.uncertain_constants:
            msg += ' Available uncertain constants: %s.' % ", ".join(context.uncertain_constants)
        else:
            msg += ' No uncertain constants declared so far.'
        
        raise DPSemanticError(msg, where=rvalue.where)

    s = dummy_ndp.get_rnames()[0]
    
    msg = ('Please use the more precise form "provided %s" rather than simply "%s".'
           % (rvalue.name, rvalue.name))
    warn_language(rvalue, MCDPWarnings.LANGUAGE_REFERENCE_OK_BUT_IMPRECISE, msg, context)

    return context.make_resource(get_name_for_fun_node(rvalue.name), s)


def eval_rvalue_NewFunction(rvalue, context):
    check_isinstance(rvalue, CDP.NewFunction)
    check_isinstance(rvalue.name, CDP.FName)
    fname = rvalue.name.value
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
                               name_prefix='_sum')


    dpu = UncertainGate(R)

    return create_operation(context, dp=dpu, resources=[r2, r3],
                            name_prefix='_uncertain')





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

    if not isinstance(R, (RcompUnits)):
        msg = 'approx() not implemented for %s.'%R
        raise_desc(DPNotImplementedError, msg)
        
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
                               name_prefix='_anyof')

