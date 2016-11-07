# -*- coding: utf-8 -*-
from contracts import contract
from contracts.utils import raise_desc, check_isinstance, raise_wrapped, indent
from mcdp_dp import (InvMult2, InvPlus2, InvPlus2Nat, InvMult2Nat,
                     InvMultValueNatDP, PlusValueNatDP,
                     PlusValueRcompDP, PlusValueDP)
from mcdp_dp.dp_multvalue import InvMultValueDP
from mcdp_lang.eval_resources_imp_unary import eval_lfunction_genericoperationfun
from mcdp_lang.parse_actions import decorate_add_where
from mcdp_posets import (Nat, RcompUnits, get_types_universe, mult_table,
    poset_maxima)
from mcdp_posets import Rcomp
from mocdp.comp.context import CFunction, get_name_for_res_node, ValueWithUnits
from mocdp.exceptions import (DPInternalError, DPNotImplementedError,
    DPSemanticError, mcdp_dev_warning)

from .helpers import create_operation_lf, get_valuewithunits_as_function
from .namedtuple_tricks import recursive_print
from .parts import CDPLanguage
from .utils_lists import get_odd_ops, unwrap_list


CDP = CDPLanguage

__all__ = [
    'eval_lfunction',
]


def eval_lfunction_Function(lf, context):
    return context.make_function(dp=lf.dp.value, s=lf.s.value)

@decorate_add_where
@contract(returns=CFunction)
def eval_lfunction(lf, context):
    constants = (CDP.Collection, CDP.SimpleValue, CDP.SpaceCustomValue,
                 CDP.Top, CDP.Bottom, CDP.Minimals, CDP.Maximals)

    if isinstance(lf, constants):
        from mcdp_lang.eval_constant_imp import eval_constant
        res = eval_constant(lf, context)
        assert isinstance(res, ValueWithUnits)
        return get_valuewithunits_as_function(res, context)
    
    from .eval_lfunction_imp_maketuple import eval_MakeTuple_as_lfunction
    from .eval_uncertainty import eval_lfunction_Uncertain
    from .eval_lfunction_imp_label_index import eval_lfunction_label_index
    from .eval_lfunction_imp_label_index import eval_lfunction_tupleindexfun
    
    cases = {
        CDP.Function: eval_lfunction_Function,
        CDP.NewResource: eval_lfunction_newresource,
        CDP.MakeTuple: eval_MakeTuple_as_lfunction,
        CDP.UncertainFun: eval_lfunction_Uncertain,
        CDP.DisambiguationFun: eval_lfunction_disambiguation,
        CDP.FunctionLabelIndex: eval_lfunction_label_index,
        CDP.TupleIndexFun: eval_lfunction_tupleindexfun,
        CDP.AnyOfFun: eval_lfunction_anyoffun, 
        CDP.InvMult: eval_lfunction_invmult,
        CDP.InvPlus: eval_lfunction_invplus,
        CDP.VariableRef: eval_lfunction_variableref,
        CDP.FValueMinusN: eval_lfunction_FValueMinusN,
        CDP.GenericOperationFun: eval_lfunction_genericoperationfun,
    }

    for klass, hook in cases.items():
        if isinstance(lf, klass):
            return hook(lf, context)

    if True: # pragma: no cover
        r = recursive_print(lf)
        msg = 'eval_lfunction(): cannot evaluate this as a function:'
        msg += '\n' + indent(r, '  ')
        raise_desc(DPInternalError, msg) 

# 
# def eval_lfunction_opminf(lf, context):
#     """
#         f <= min(required r1, required r2)
#     """
#     check_isinstance(lf, CDP.OpMinF)
#     
#     a = eval_lfunction(lf.a, context)
#     b = eval_lfunction(lf.b, context)
#  
#     Fa = context.get_ftype(a)
#     b = get_function_possibly_converted(b, Fa, context)
#         
#     dp = MeetNDualDP(2, Fa)
#     
#     return create_operation_lf(context, dp=dp, functions=[a, b],
#                             name_prefix='max', op_prefix='_ops',
#                             res_prefix='_result')
#     
#     
# def eval_lfunction_opmaxf(lf, context):
#     """
#         f <= max(required r1, required r2)
#     """
#     check_isinstance(lf, CDP.OpMaxF)
#     
#     a = eval_lfunction(lf.a, context)
#     b = eval_lfunction(lf.b, context)
#  
#     Fa = context.get_ftype(a)
#     b = get_function_possibly_converted(b, Fa, context)
#         
#     dp = JoinNDualDP(2, Fa)
#     
#     return create_operation_lf(context, dp=dp, functions=[a, b],
#                             name_prefix='max', op_prefix='_ops',
#                             res_prefix='_result')
    
            
def eval_lfunction_anyoffun(lf, context):
    from .eval_constant_imp import eval_constant
    from mcdp_posets import FiniteCollectionsInclusion
    from mcdp_dp import LimitMaximals
    from mcdp_posets import FiniteCollection
    
    assert isinstance(lf, CDP.AnyOfFun)
    constant = eval_constant(lf.value, context)
    if not isinstance(constant.unit, FiniteCollectionsInclusion):
        msg = 'I expect that the argument to any-of evaluates to a finite collection.'
        raise_desc(DPSemanticError, msg, constant=constant)
    assert isinstance(constant.unit, FiniteCollectionsInclusion)
    P = constant.unit.S

    assert isinstance(constant.value, FiniteCollection)
    elements = set(constant.value.elements)
    maximals = poset_maxima(elements, P.leq)
    if len(elements) != len(maximals):
        msg = 'The elements are not maximals.'
        raise_desc(DPSemanticError, msg, elements=elements, maximals=maximals)

    dp = LimitMaximals(values=maximals, F=P)
    return create_operation_lf(context, dp=dp, functions=[],
                               name_prefix='_anyof')


def eval_lfunction_disambiguation(lf, context):
    return eval_lfunction(lf.fvalue, context)


def eval_lfunction_variableref(lf, context):
    if lf.name in context.constants:
        c = context.constants[lf.name]
        assert isinstance(c, ValueWithUnits)
        return get_valuewithunits_as_function(c, context)

    if lf.name in context.var2function:
        return context.var2function[lf.name]

    try:
        dummy_ndp = context.get_ndp_res(lf.name)
    except ValueError:
        msg = 'Function %r not declared.' % lf.name
        raise DPSemanticError(msg, where=lf.where)

    s = dummy_ndp.get_rnames()[0]
    return context.make_function(get_name_for_res_node(lf.name), s)


def eval_lfunction_FValueMinusN(lf, context):
    ops = get_odd_ops(unwrap_list(lf.ops))    
    
    # first one should be a functionality 
    fvalue = eval_lfunction(ops[0], context)
    
    # ops after the first should be constant
    must_be_constants = ops[1:]
    from .eval_constant_imp import eval_constant

    constants = []
    for mc in must_be_constants:
        try:
            c  = eval_constant(mc, context)
            constants.append(c)
        except:
            raise
        
    if len(constants) > 1:
        msg = 'FValueMinusN not implemented for more than one constant.'
        raise_desc(DPNotImplementedError, msg)
    
    constant = constants[0] 

    # f - constant <= (x)
    # f <= (x) + Constant 

    F = context.get_ftype(fvalue)
    if isinstance(F, Nat) and isinstance(constant.unit, Nat):
        dp = PlusValueNatDP(constant.value)
    elif isinstance(F, Rcomp):
        dp = PlusValueRcompDP(constant.value)
    elif isinstance(F, RcompUnits):
        dp = PlusValueDP(F=F, c_value=constant.value, c_space=constant.unit)
    else:
        msg = 'Could not create this operation with %s. ' % F
        raise_desc(DPSemanticError, msg, F=F)
             
    return create_operation_lf(context, dp=dp, functions=[fvalue],
                            name_prefix='_minusvalue', op_prefix='_op',
                            res_prefix='_result')
    
    
def eval_lfunction_invplus(lf, context):
    ops = get_odd_ops(unwrap_list(lf.ops))

    fs = []

    for op_i in ops:
        fi = eval_lfunction(op_i, context)
        fs.append(fi)

    return eval_lfunction_invplus_ops(fs, context)


def eval_lfunction_invplus_ops(fs, context):
    if len(fs) == 1:
        raise DPInternalError(fs)
    elif len(fs) > 2: # pragma: no cover
        mcdp_dev_warning('Maybe this should be smarter?')
        
        rest = eval_lfunction_invplus_ops(fs[1:], context)
        return eval_lfunction_invplus_ops([fs[0], rest], context) 
    else:   
        Fs = map(context.get_ftype, fs)
        R = Fs[0]
    
        if all(isinstance(_, RcompUnits) for _ in Fs):
            tu = get_types_universe()
            if not tu.leq(Fs[1], Fs[0]):
                msg = 'Inconsistent units %s and %s.' % (Fs[1], Fs[0])
                raise_desc(DPSemanticError, msg, Fs0=Fs[0], Fs1=Fs[1])
    
            if not tu.equal(Fs[1], Fs[0]):
                msg = 'This case was not implemented yet. Differing units %s and %s.' % (Fs[1], Fs[0])
                raise_desc(DPNotImplementedError, msg, Fs0=Fs[0], Fs1=Fs[1])
            
            dp = InvPlus2(R, tuple(Fs))            
        elif all(isinstance(_, Rcomp) for _ in Fs):
            dp = InvPlus2(R, tuple(Fs))
        elif all(isinstance(_, Nat) for _ in Fs):
            dp = InvPlus2Nat(R, tuple(Fs))
            
        else: # pragma: no cover
            msg = 'Cannot find operator for these types.'
            raise_desc(DPInternalError, msg, Fs=Fs)
        
        return create_operation_lf(context, dp=dp, functions=fs,
                               name_prefix='_invplus', op_prefix='_',
                                res_prefix='_result') 

def eval_lfunction_invmult_sort_ops(ops, context, wants_constant):
    """ Divides in resources and constants 
    
        Returns functions, constants
    """ 
    from mcdp_lang.eval_constant_imp import eval_constant
    from mcdp_lang.eval_constant_imp import NotConstant
    constants = []
    functions = []

    for op in ops:
        try:
            x = eval_constant(op, context)
            check_isinstance(x, ValueWithUnits)
            constants.append(x)
            continue
        except NotConstant as e:
            pass
        except DPSemanticError as e:
            if 'Variable ref' in str(e):
                pass
            else:
                raise
        
        if wants_constant:
            msg = 'Product not constant because one op is not constant.'
            raise_wrapped(NotConstant, e, msg, op=op)
        x = eval_lfunction(op, context)
        assert isinstance(x, CFunction)
        functions.append(x)
    return functions, constants

def flatten_invmult(ops):
    """ Flattens recursively nested CDP.InvMult operators """
    res = []
    for op in ops:
        if isinstance(op, CDP.InvMult):
            res.extend(flatten_invmult(get_odd_ops(unwrap_list(op.ops))))
        else:
            res.append(op)
    return res

def eval_lfunction_create_invmultvalue(lf, constant, context):
    assert isinstance(lf, CFunction), lf
    assert isinstance(constant, ValueWithUnits), constant
    
    F1 = context.get_ftype(lf)
    F2 = constant.unit
    
    if isinstance(F1, Nat) and isinstance(F2, Nat):
        dp = InvMultValueNatDP(constant.value)    
    elif isinstance(F1, RcompUnits) and isinstance(F2, RcompUnits):
        R = mult_table(F1, F2)
        dp = InvMultValueDP(R, F1, constant.unit, constant.value)
    else:
        msg = 'Cannot get InvMultValue for spaces %s and %s' % (F1, F2)
        raise_desc(DPNotImplementedError, msg, F1=F1, F2=F2)

    return create_operation_lf(context, dp=dp, functions=[lf],
                        name_prefix='_invmultvalue', op_prefix='_ops',
                        res_prefix='_result')
    
def eval_lfunction_invmult(lf, context, wants_constant=False):
    assert isinstance(lf, CDP.InvMult)
    from mcdp_lang.misc_math import generic_mult_constantsN
        
    ops_list = get_odd_ops(unwrap_list(lf.ops))
    ops = flatten_invmult(ops_list)
    
    functions, constants = eval_lfunction_invmult_sort_ops(ops, context, 
                                                wants_constant=wants_constant)
     
    if functions: 
        res = eval_lfunction_invmult_ops(functions, context)
        
        if constants:
            constant = generic_mult_constantsN(constants)
            return eval_lfunction_create_invmultvalue(res, constant, context)
        else:
            return res
        
    else:
        # no functions, just constants
        constant = generic_mult_constantsN(constants)
        return get_valuewithunits_as_function(constant)


def eval_lfunction_invmult_ops(fs, context):
    if len(fs) == 1:
        return fs[0]
    elif len(fs) > 2: 
        mcdp_dev_warning('Maybe this should be smarter?')
        rest = eval_lfunction_invmult_ops(fs[1:], context)
        return eval_lfunction_invmult_ops([fs[0], rest], context) 
    else:   
        assert len(fs) == 2
        Fs = tuple(map(context.get_ftype, fs))
    
        if isinstance(Fs[0], Nat) and isinstance(Fs[1], Nat):
            dp = InvMult2Nat(Nat(), Fs)
        else:
            if isinstance(Fs[0], RcompUnits) and \
               isinstance(Fs[1], RcompUnits):
                R = mult_table(Fs[0], Fs[1])
                dp = InvMult2(R, Fs)
            elif isinstance(Fs[0], Rcomp) and isinstance(Fs[1], Rcomp):
                R = Rcomp()
                dp = InvMult2(R, Fs)
            else:
                msg = 'Could not create invplus for types {}.'.format(Fs)
                raise_desc(DPNotImplementedError, msg, Fs0=Fs[0], Fs1=Fs[1])
                
        return create_operation_lf(context, dp=dp, functions=fs,
                        name_prefix='_invmult', op_prefix='_ops',
                        res_prefix='_result') 

def eval_lfunction_newresource(lf, context):
    rname = lf.name
    try:
        dummy_ndp = context.get_ndp_res(rname)
    except ValueError:
        msg = 'New resource name %r not declared.' % rname
        if context.rnames:
            msg += ' Available: %s.' % ", ".join(context.rnames)
        else:
            msg += ' No resources declared so far.'
        # msg += '\n%s' % str(e)
        raise DPSemanticError(msg, where=lf.where)

    return context.make_function(get_name_for_res_node(rname),
                                 dummy_ndp.get_fnames()[0])
