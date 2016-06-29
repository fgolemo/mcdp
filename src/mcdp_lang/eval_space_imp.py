# -*- coding: utf-8 -*-
from .parse_actions import add_where_information
from .parts import CDPLanguage
from .utils_lists import get_odd_ops, unwrap_list
from contracts import contract
from mcdp_posets import (
    FiniteCollectionsInclusion, FinitePoset, Int, Nat, Poset, PosetProduct,
    Space, UpperSets)
from mocdp.exceptions import DPInternalError
from mocdp.comp.context import ValueWithUnits
from mcdp_posets.interval import GenericInterval
from mcdp_posets.poset_product_with_labels import PosetProductWithLabels

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

        if isinstance(r, CDP.MakeUpperSets):
            return eval_space_makeuppersets(r, context)

        cases = {
            CDP.SpaceInterval: eval_space_interval,
            CDP.ProductWithLabels : eval_space_productwithlabels,
        }

        for klass, hook in cases.items():
            if isinstance(r, klass):
                return hook(r, context)
                            
        # This should be removed...
        if isinstance(r, CDP.Unit):
            return r.value

        raise DPInternalError('Invalid value to eval_space: %s' % str(r))

def eval_space_productwithlabels(r, context):
    assert isinstance(r, CDP.ProductWithLabels)
    entries = unwrap_list(r.entries)
    labels = [_.label for _ in entries[::2]]
    spaces = [eval_space(_, context) for _ in entries[1::2]]
    return PosetProductWithLabels(subs=spaces, labels=labels)


def express_vu_in_isomorphic_space(vb, va):
    """ Returns vb in va's units """
    from mcdp_posets.types_universe import express_value_in_isomorphic_space
    value = express_value_in_isomorphic_space(vb.unit, vb.value, va.unit)
    return ValueWithUnits(value=value, unit=va.unit)


def eval_space_interval(r, context):
    from mcdp_lang.eval_constant_imp import eval_constant
    va = eval_constant(r.a, context)
    vb = eval_constant(r.b, context)
    vb2 = express_vu_in_isomorphic_space(vb, va)
    P = GenericInterval(va.unit, va.value, vb2.value)
    return P

def eval_space_makeuppersets(r, context):
    P = eval_space(r.space, context)
    return UpperSets(P)

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

