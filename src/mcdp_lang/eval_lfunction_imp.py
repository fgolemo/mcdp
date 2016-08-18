# -*- coding: utf-8 -*-
from .helpers import get_valuewithunits_as_function
from .namedtuple_tricks import recursive_print
from .parse_actions import add_where_information
from .parts import CDPLanguage
from .utils_lists import get_odd_ops, unwrap_list
from contracts import contract
from contracts.utils import raise_desc
from mcdp_dp import InvMult2, InvPlus2, InvPlus2Nat
from mcdp_posets import Nat, RcompUnits, mult_table
from mcdp_posets.find_poset_minima.baseline_n2 import poset_maxima
from mocdp.comp import Connection, dpwrap
from mocdp.comp.context import CFunction, get_name_for_res_node
from mocdp.exceptions import DPInternalError, DPSemanticError, \
    DPNotImplementedError
from mcdp_posets.types_universe import get_types_universe


CDP = CDPLanguage

__all__ = [
    'eval_lfunction',
]

@contract(returns=CFunction)
def eval_lfunction(lf, context):
    with add_where_information(lf.where):

        if isinstance(lf, CDP.Function):
            return context.make_function(dp=lf.dp.value, s=lf.s.value)

        if isinstance(lf, CDP.InvMult):
            return eval_lfunction_invmult(lf, context)

        if isinstance(lf, CDP.InvPlus):
            return eval_lfunction_invplus(lf, context)

        if isinstance(lf, CDP.NewResource):
            return eval_lfunction_newresource(lf, context)

        if isinstance(lf, CDP.MakeTuple):
            from .eval_lfunction_imp_maketuple import eval_MakeTuple_as_lfunction
            return eval_MakeTuple_as_lfunction(lf, context)

        from mocdp.comp.context import ValueWithUnits

        if isinstance(lf, CDP.VariableRef):
            return eval_lfunction_variableref(lf, context)

        constants = (CDP.Collection, CDP.SimpleValue, CDP.SpaceCustomValue,
                     CDP.Top, CDP.Bottom, CDP.Minimals, CDP.Maximals)

        if isinstance(lf, constants):
            from mcdp_lang.eval_constant_imp import eval_constant
            res = eval_constant(lf, context)
            assert isinstance(res, ValueWithUnits)
            return get_valuewithunits_as_function(res, context)
        
        from mcdp_lang.eval_uncertainty import eval_lfunction_Uncertain
        from mcdp_lang.eval_lfunction_imp_label_index import eval_lfunction_label_index

        from mcdp_lang.eval_lfunction_imp_label_index import eval_lfunction_tupleindexfun
        cases = {
            CDP.UncertainFun: eval_lfunction_Uncertain,
            CDP.DisambiguationFun: eval_lfunction_disambiguation,
            CDP.FunctionLabelIndex: eval_lfunction_label_index,
            CDP.TupleIndexFun: eval_lfunction_tupleindexfun,
            CDP.AnyOfFun: eval_lfunction_anyoffun,
        }

        for klass, hook in cases.items():
            if isinstance(lf, klass):
                return hook(lf, context)

        r = recursive_print(lf)
        msg = 'eval_lfunction(): cannot evaluate as a function.'
        raise_desc(DPInternalError, msg, r=r)

def eval_lfunction_anyoffun(lf, context):
    from mcdp_lang.eval_constant_imp import eval_constant
    from mcdp_posets.finite_collections_inclusion import FiniteCollectionsInclusion
    from mcdp_dp.dp_limit import LimitMaximals
    from mcdp_posets.finite_collection import FiniteCollection
    from mcdp_lang.helpers import create_operation_lf

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
                               name_prefix='_anyof', op_prefix='_',
                                res_prefix='_result')

def eval_lfunction_disambiguation(lf, context):
    return eval_lfunction(lf.fvalue, context)

def eval_lfunction_variableref(lf, context):
    from mocdp.comp.context import ValueWithUnits

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
#         msg += '\n%s' % str(e)
        raise DPSemanticError(msg, where=lf.where)

    s = dummy_ndp.get_rnames()[0]
    return context.make_function(get_name_for_res_node(lf.name), s)

def eval_lfunction_invplus(lf, context):
    ops = get_odd_ops(unwrap_list(lf.ops))
    if len(ops) != 2:
        raise DPInternalError('Only 2 expected')

    fs = []

    for op_i in ops:
        fi = eval_lfunction(op_i, context)
        fs.append(fi)

    assert len(fs) == 2

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
        
    elif all(isinstance(_, Nat) for _ in Fs):
        dp = InvPlus2Nat(R, tuple(Fs))
    else:
        msg = 'Cannot find operator for mixed values'
        raise_desc(DPInternalError, msg, Fs=Fs)
    

    ndp = dpwrap(dp, '_input', ['_f0', '_f1'])

    name = context.new_name('_invplus')
    context.add_ndp(name, ndp)

    c1 = Connection(dp2=fs[0].dp, s2=fs[0].s, dp1=name, s1='_f0')
    c2 = Connection(dp2=fs[1].dp, s2=fs[1].s, dp1=name, s1='_f1')
    context.add_connection(c1)
    context.add_connection(c2)

    res = context.make_function(name, '_input')
    return res

def eval_lfunction_invmult(lf, context):
    ops = get_odd_ops(unwrap_list(lf.ops))
    if len(ops) != 2:
        raise DPInternalError('Only 2 expected')

    fs = []

    for op_i in ops:
        fi = eval_lfunction(op_i, context)
        fs.append(fi)

    assert len(fs) == 2

    Fs = map(context.get_ftype, fs)
    R = mult_table(Fs[0], Fs[1])


    dp = InvMult2(R, tuple(Fs))
    ndp = dpwrap(dp, '_input', ['_f0', '_f1'])

    name = context.new_name('_invmult')
    context.add_ndp(name, ndp)

    c1 = Connection(dp2=fs[0].dp, s2=fs[0].s, dp1=name, s1='_f0')
    c2 = Connection(dp2=fs[1].dp, s2=fs[1].s, dp1=name, s1='_f1')
    context.add_connection(c1)
    context.add_connection(c2)

    res = context.make_function(name, '_input')
    return res

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
