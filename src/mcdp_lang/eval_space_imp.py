# -*- coding: utf-8 -*-
from .namedtuple_tricks import recursive_print
from .parse_actions import add_where_information
from .parts import CDPLanguage
from .utils_lists import get_odd_ops, unwrap_list
from contracts import contract
from contracts.utils import raise_desc
from mcdp_posets import (
    FiniteCollectionsInclusion, FinitePoset, GenericInterval, Int, LowerSets,
    Nat, Poset, PosetCoproduct, PosetProduct, PosetProductWithLabels, Space,
    UpperSets)
from mocdp.comp.context import ValueWithUnits
from mocdp.exceptions import DPInternalError

CDP = CDPLanguage

@contract(returns=Space)
def eval_space(r, context):
    with add_where_information(r.where):
        cases = {
            CDP.RcompUnit: eval_space_rcompunit,
            CDP.SpaceProduct: eval_space_spaceproduct,
            CDP.SpaceCoproduct: eval_space_spacecoproduct,
            CDP.PowerSet: eval_space_powerset,
            CDP.LoadPoset: eval_poset_load,
            CDP.FinitePoset: eval_space_finite_poset,
            CDP.CodeSpecNoArgs: eval_space_code_spec,
            CDP.CodeSpec: eval_space_code_spec,
            CDP.MakeUpperSets: eval_space_makeuppersets,
            CDP.MakeLowerSets: eval_space_makelowersets,
            CDP.SpaceInterval: eval_space_interval,
            CDP.ProductWithLabels: eval_space_productwithlabels,
            CDP.SingleElementPoset: eval_space_single_element_poset,
            CDP.Nat: lambda r, context: Nat(),  # @UnusedVariable
            CDP.Int: lambda r, context: Int(),  # @UnusedVariable
        }

        for klass, hook in cases.items():
            if isinstance(r, klass):
                return hook(r, context)
                            
        # This should be removed...
        if isinstance(r, CDP.Unit):
            return r.value

        msg = 'eval_space(): Cannot interpret as a space.'
        r = recursive_print(r)
        raise_desc(DPInternalError, msg, r=r)

def eval_space_single_element_poset(r, context):  # @UnusedVariable
    assert isinstance(r, CDP.SingleElementPoset)
    tag = r.tag.value
    universe = set([tag])
    return FinitePoset(universe=universe, relations=[])
    
def eval_space_rcompunit(r, context):  # @UnusedVariable
    from mcdp_posets.rcomp_units import make_rcompunit
    return make_rcompunit(r.pint_string)
 
def eval_space_spaceproduct(r, context):
    ops = get_odd_ops(unwrap_list(r.ops))
    Ss = [eval_space(_, context) for _ in ops]
    return PosetProduct(tuple(Ss))
                        

def eval_space_spacecoproduct(r, context):
    assert isinstance(r, CDP.SpaceCoproduct)
    ops = unwrap_list(r.entries)
    Ss = [eval_space(_, context) for _ in ops]
    return PosetCoproduct(tuple(Ss))


def eval_space_powerset(r, context):
    P = eval_space(r.space, context)
    return FiniteCollectionsInclusion(P)


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


def eval_space_makelowersets(r, context):
    P = eval_space(r.space, context)
    return LowerSets(P)


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
    if isinstance(r.name, CDP.PosetName):
        load_arg = r.name.value
        return context.load_poset(load_arg)
    if isinstance(r.name, CDP.PosetNameWithLibrary):
        libname = r.name.library
        name = r.name.name
        library = context.load_library(libname)
        return library.load_poset(name)
    raise NotImplementedError(r.name)
