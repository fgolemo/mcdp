# -*- coding: utf-8 -*-
from .parts import CDPLanguage
from contracts import contract
from contracts.utils import raise_desc
from mocdp.comp import Connection, dpwrap
from mocdp.comp.context import CFunction, get_name_for_res_node
from mocdp.dp import InvMult2, InvPlus2, Limit
from mocdp.dp.dp_mult_inv import InvPlus2Nat
from mocdp.exceptions import DPInternalError, DPSemanticError
from mocdp.lang.utils_lists import get_odd_ops, unwrap_list
from mocdp.posets import mult_table
from mocdp.posets.nat import Nat
from mocdp.posets.rcomp_units import RcompUnits

CDP = CDPLanguage

__all__ = ['eval_lfunction']

@contract(returns=CFunction)
def eval_lfunction(lf, context):
    if isinstance(lf, CDP.Function):
        return context.make_function(dp=lf.dp.value, s=lf.s.value)

    if isinstance(lf, CDP.InvMult):
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

    if isinstance(lf, CDP.InvPlus):
        return eval_lfunction_invplus(lf, context)

    if isinstance(lf, CDP.NewResource):
        rname = lf.name
        try:
            dummy_ndp = context.get_ndp_res(rname)
        except ValueError as e:
            msg = 'New resource name %r not declared.' % rname
            msg += '\n%s' % str(e)
            raise DPSemanticError(msg, where=lf.where)

        return context.make_function(get_name_for_res_node(rname),
                        dummy_ndp.get_fnames()[0])

    if isinstance(lf, CDP.NewLimit):
        from mocdp.lang.eval_constant_imp import eval_constant
        A = eval_constant(lf.value_with_unit, context)
        dp = Limit(A.unit, A.value)
        n = context.new_name('lim')
        sn = context.new_fun_name('l')
        ndp = dpwrap(dp, sn, [])
        context.add_ndp(n, ndp)

        return context.make_function(n, sn)

    msg = 'Cannot eval_lfunction(%s)' % lf.__repr__()
    raise DPInternalError(msg)


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
