# -*- coding: utf-8 -*-
from contracts.utils import check_isinstance
from mcdp_posets import R_dimensionless
from mocdp.exceptions import mcdp_dev_warning

from .helpers import create_operation
from .parts import CDPLanguage


CDP = CDPLanguage

def eval_rvalue_Uncertain(r, context):
    from .eval_resources_imp import eval_rvalue
    from mcdp_dp import UncertainGate

    check_isinstance(r, CDP.UncertainRes)

    rl = eval_rvalue(r.lower, context)
    ru = eval_rvalue(r.upper, context)
    Rl = context.get_rtype(rl)
    dp = UncertainGate(Rl)

    return create_operation(context, dp=dp, resources=[rl, ru])


def eval_rvalue_RValueBetween(r, context):
    from .eval_resources_imp import eval_rvalue
    from mcdp_dp import UncertainGate
    
    check_isinstance(r, CDP.RValueBetween)
    
    rl = eval_rvalue(r.lower, context)
    ru = eval_rvalue(r.upper, context)
    Rl = context.get_rtype(rl)
    dp = UncertainGate(Rl)

    return create_operation(context, dp=dp, resources=[rl, ru])
    
def eval_rvalue_RValuePlusOrMinus(r, context):
    from mcdp_dp import UncertainGate, MinusValueDP, PlusValueDP
    from .eval_resources_imp import eval_rvalue
    from .eval_constant_imp import eval_constant

    check_isinstance(r, CDP.RValuePlusOrMinus)
    median = eval_rvalue(r.median, context)
    extent = eval_constant(r.extent, context)
    
    Rl = context.get_rtype(median)

    dpl =  MinusValueDP(Rl, extent.value, extent.unit)
    rl = create_operation(context, dpl, resources=[median])
    dpu =  PlusValueDP(Rl, extent.value, extent.unit)
    ru = create_operation(context, dpu, resources=[median])
    
    dp = UncertainGate(Rl)

    return create_operation(context, dp=dp, resources=[rl, ru])

def eval_rvalue_RValuePlusOrMinusPercent(r, context):
    from mcdp_dp import UncertainGate, MultValueDP
    from .eval_resources_imp import eval_rvalue

    check_isinstance(r, CDP.RValuePlusOrMinusPercent)
    median = eval_rvalue(r.median, context)
    check_isinstance(r.perc, CDP.ValueExpr)
    
    p0 = r.perc.value
    pl = 1 - p0 / 100.0
    pu = 1 + p0 / 100.0
    
    Rl = context.get_rtype(median)

    dpl = MultValueDP(Rl, Rl, R_dimensionless, pl)
    dpu = MultValueDP(Rl, Rl, R_dimensionless, pu)
    
    rl = create_operation(context, dpl, resources=[median])
    ru = create_operation(context, dpu, resources=[median])
    
    dp = UncertainGate(Rl)

    return create_operation(context, dp=dp, resources=[rl, ru]) 
    
def eval_lfunction_Uncertain(r, context):
    from mcdp_dp import UncertainGateSym
    from .eval_lfunction_imp import eval_lfunction
    from .helpers import create_operation_lf

    assert isinstance(r, CDP.UncertainFun)

    fl = eval_lfunction(r.lower, context)
    fu = eval_lfunction(r.upper, context)

    F = context.get_ftype(fl)
    # Fu = context.get_rtype(fu)
    mcdp_dev_warning('Do explicit check of types.')

    dp = UncertainGateSym(F)

    return create_operation_lf(context, dp=dp, functions=[fl, fu])

def eval_lfunction_FValueBetween(r, context):
    from mcdp_dp import UncertainGateSym
    from .eval_lfunction_imp import eval_lfunction
    from .helpers import create_operation_lf
    
    fl = eval_lfunction(r.lower, context)
    fu = eval_lfunction(r.upper, context)

    F = context.get_ftype(fl) 
    dp = UncertainGateSym(F)
    return create_operation_lf(context, dp=dp, functions=[fl, fu])

def eval_lfunction_FValuePlusOrMinus(r, context):
    from mcdp_dp import UncertainGateSym
    from mcdp_dp import MinusValueDP
    from mcdp_dp import PlusValueDP

    from .eval_lfunction_imp import eval_lfunction
    from .eval_constant_imp import eval_constant
    from .helpers import create_operation_lf
    
    check_isinstance(r, CDP.FValuePlusOrMinus)
    median = eval_lfunction(r.median, context)
    extent = eval_constant(r.extent, context)
    
    F = context.get_ftype(median)

    # provides f = between 10 g and 20 g
    
    # MinusValueDP :   r + c ≥ f
    # PlusValueDP :   r ≥ f + c 
    
    # f <= f0 - c # pessimistic
    # f <= f0 + c # optimistic 
    dpl =  MinusValueDP(F, extent.value, extent.unit)
    dpu =  PlusValueDP(F, extent.value, extent.unit)
    
    fl = create_operation_lf(context, dpl, functions=[median])
    fu = create_operation_lf(context, dpu, functions=[median])
     
    dp = UncertainGateSym(F)
    return create_operation_lf(context, dp=dp, functions=[fl, fu])
 

def eval_lfunction_FValuePlusOrMinusPercent(r, context):
    from mcdp_lang.eval_lfunction_imp import eval_lfunction
    from mcdp_dp import InvMultValueDP
    from mcdp_dp.dp_uncertain import UncertainGateSym
    
    check_isinstance(r, CDP.FValuePlusOrMinusPercent)
    median = eval_lfunction(r.median, context)
    check_isinstance(r.perc, CDP.ValueExpr)
    
    p0 = r.perc.value
    pl = 1 - p0 / 100.0
    pu = 1 + p0 / 100.0
    
    Rl = context.get_ftype(median)

    dpl = InvMultValueDP(Rl, Rl, R_dimensionless, pl)
    dpu = InvMultValueDP(Rl, Rl, R_dimensionless, pu)
    
    from mcdp_lang.helpers import create_operation_lf
    rl = create_operation_lf(context, dpl, functions=[median])
    ru = create_operation_lf(context, dpu, functions=[median])
    
    dp = UncertainGateSym(Rl)

    return create_operation_lf(context, dp=dp, functions=[rl, ru]) 
