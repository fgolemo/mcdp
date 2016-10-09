# -*- coding: utf-8 -*-
from .parts import CDPLanguage
from contracts.utils import raise_desc
from mcdp_posets import (FiniteCollectionsInclusion, LowerSets, PosetProduct,
    UpperSets, express_value_in_isomorphic_space)
from mocdp import logger
from mocdp.comp.context import ValueWithUnits
from mocdp.exceptions import DPSemanticError, DPUserAssertion

def assert_generic(r, context, which):
    """ a : v1 < v2
        b : v1 = v2
        b : v1 = v2
    """
    from .eval_constant_imp import eval_constant

    
    v1 = eval_constant(r.v1, context)
    v2 = eval_constant(r.v2, context)
    
    # put v2 in v1's space
    P = v1.unit
    value1 = v1.value
    value2 = express_value_in_isomorphic_space(v2.unit, v2.value, v1.unit)
    
    t = {}
    t['equal'] = P.equal(value1, value2)
    t['leq'] = P.leq(value1, value2)
    t['geq'] = P.leq(value2, value1)
    t['lt'] = t['leq'] and not t['equal']
    t['gt'] = t['geq'] and not t['equal']
     
    if not which in t:
        raise ValueError(t)
    
    result = t[which]
    if result:
        return passed_value()
    
    else: # assertion
        msg = 'Assertion %r failed.' % which
        raise_desc(DPUserAssertion, msg, v1=v1, v2=v2)
    
         
CDP = CDPLanguage
def eval_assert_equal(r, context):
    assert isinstance(r, CDP.AssertEqual)
    return assert_generic(r, context, 'equal')

def eval_assert_leq(r, context):
    assert isinstance(r, CDP.AssertLEQ)
    return assert_generic(r, context, 'leq')

def eval_assert_geq(r, context):
    assert isinstance(r, CDP.AssertGEQ)
    return assert_generic(r, context, 'geq')

def eval_assert_gt(r, context):
    assert isinstance(r, CDP.AssertGT)
    return assert_generic(r, context, 'gt')

def eval_assert_lt(r, context):
    assert isinstance(r, CDP.AssertLT)
    return assert_generic(r, context, 'lt')

def eval_assert_nonempty(r, context):
    from .eval_constant_imp import eval_constant
    assert isinstance(r, CDP.AssertNonempty)
    v = eval_constant(r.value, context)

    seq = get_sequence(v)
    check = len(seq) > 0

    if check:
        logger.info(v.__repr__())
        return passed_value()

    msg = 'Assertion assert_nonempty() failed.'
    raise_desc(DPUserAssertion, msg, v=v)

def eval_assert_empty(r, context):
    from .eval_constant_imp import eval_constant
    assert isinstance(r, CDP.AssertEmpty)
    v = eval_constant(r.value, context)
    seq = get_sequence(v)
    check = len(seq) == 0

    if check:
        logger.info(v.__repr__())
        return passed_value()

    msg = 'Assertion assert_nonempty() failed.'
    raise_desc(DPUserAssertion, msg, v=v)


def get_sequence(vu):
    if isinstance(vu.unit, UpperSets):
        return vu.value.minimals
    elif isinstance(vu.unit, LowerSets):
        return vu.value.maximals
    elif isinstance(vu.unit, FiniteCollectionsInclusion):
        return vu.value.elements
    else:
        msg = 'Could not get sequence from element %s.' % type(vu.unit)
        raise_desc(DPSemanticError, msg, vu=vu)


def passed_value():
    return ValueWithUnits((), PosetProduct(()))
