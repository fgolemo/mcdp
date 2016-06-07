# -*- coding: utf-8 -*-
from .parts import CDPLanguage
from contracts import contract
from mocdp.exceptions import DPInternalError
from mocdp.lang.utils_lists import get_odd_ops, unwrap_list
from mocdp.posets import PosetProduct
from mocdp.posets.finite_set import FiniteCollectionsInclusion
from mocdp.posets.nat import Int, Nat
from mocdp.posets.space import Space
CDP = CDPLanguage

@contract(returns=Space)
def eval_space(r, context):

    if isinstance(r, CDP.RcompUnit):
        from mocdp.posets.rcomp_units import make_rcompunit
        return make_rcompunit(r.pint_string)

    if isinstance(r, CDP.PowerSet):
        P = eval_space(r.space, context)
        return FiniteCollectionsInclusion(P)

    if isinstance(r, CDP.Nat):
        return Nat()

    if isinstance(r, CDP.Int):
        return Int()

    if isinstance(r, CDP.SpaceProduct):
        ops = get_odd_ops(unwrap_list(r.ops))
        Ss = [eval_space(_, context) for _ in ops]
        return PosetProduct(tuple(Ss))

    # This should be removed...
    if isinstance(r, CDP.Unit):
        return r.value

    raise DPInternalError('Invalid value to eval_space: %s' % str(r))

#
# @contract(returns=Space)
# def eval_unit(x, context):  # @UnusedVariable
#
#     if isinstance(x, CDP.Unit):
#         S = x.value
#         assert isinstance(S, Space), S
#         return S
#
#     msg = 'Cannot evaluate %s as unit.' % x.__repr__()
#     raise ValueError(msg)
