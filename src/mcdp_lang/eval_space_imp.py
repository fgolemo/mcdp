# -*- coding: utf-8 -*-
from .parts import CDPLanguage
from contracts import contract
from .parse_actions import add_where_information
from .utils_lists import get_odd_ops, unwrap_list
from mcdp_posets import PosetProduct
from mcdp_posets.finite_set import FiniteCollectionsInclusion, FinitePoset
from mcdp_posets.nat import Int, Nat
from mcdp_posets.poset import Poset
from mcdp_posets.space import Space
from mocdp.exceptions import DPInternalError

CDP = CDPLanguage

@contract(returns=Space)
def eval_space(r, context):
    with add_where_information(r.where):
        if isinstance(r, CDP.RcompUnit):
            from mcdp_posets.rcomp_units import make_rcompunit
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

        if isinstance(r, CDP.LoadPoset):
            return eval_poset_load(r, context)

        if isinstance(r, CDP.FinitePoset):
            return eval_space_finite_poset(r, context)

        if isinstance(r, (CDP.CodeSpecNoArgs, CDP.CodeSpec)):
            return eval_space_code_spec(r, context)

        # This should be removed...
        if isinstance(r, CDP.Unit):
            return r.value

        raise DPInternalError('Invalid value to eval_space: %s' % str(r))


def eval_space_code_spec(r, _context):
    from .eval_codespec_imp import eval_codespec
    res = eval_codespec(r, expect=Poset)
    return res

def eval_space_finite_poset(r, context):  # @UnusedVariable
    chains = unwrap_list(r.chains) 

    universe = set()
    relations = set()
    for c in chains:
        ops = get_odd_ops(c)
        elements = [_.identifier for _ in ops]
        universe.update(elements)
        
        for a, b in zip(elements, elements[1:]):
            relations.add((a, b))

    return FinitePoset(universe=universe, relations=relations)

def eval_poset_load(r, context):
    load_arg = r.name.value
    return context.load_poset(load_arg)


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
