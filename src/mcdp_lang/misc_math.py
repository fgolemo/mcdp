# -*- coding: utf-8 -*-
import functools
import warnings

from contracts import contract
from contracts.utils import check_isinstance, raise_desc
from mcdp_maps.SumN_xxx_Map import sum_units
from mcdp_posets import Nat, RcompUnits, mult_table, Rcomp, express_value_in_isomorphic_space
from mcdp_posets.nat import Nat_mult_uppersets_continuous, Nat_add
from mcdp_posets.rcomp_units import (R_dimensionless, mult_table_seq,
    RbicompUnits, rcomp_add,inverse_of_unit)
from mocdp.comp.context import ValueWithUnits
from mocdp.exceptions import DPSemanticError, DPNotImplementedError
from mcdp_posets.poset import NotLeq

inv_unit = inverse_of_unit
# 
# @contract(S=RcompUnits)
# def inv_unit(S):
#     # S.units is a pint quantity
#     unit = 1 / S.units
#     string = ('%s' % unit).encode('utf-8')
#     res = RcompUnits(1 / S.units, string)
#     return res

@contract(returns=ValueWithUnits, a =ValueWithUnits)
def inv_constant(a):
    if a.unit == Nat():
        raise DPNotImplementedError('division by natural number')
        warnings.warn('Please think more about this. Now 1/N -> 1.0/N')
        unit = Rcomp()
    else:
        unit = inv_unit(a.unit)

    if a.value == 0:
        raise DPSemanticError('Division by zero')
    # TODO: what about integers?
    value = 1.0 / a.value
    return ValueWithUnits(value=value, unit=unit)

@contract(a=ValueWithUnits, b=ValueWithUnits)
def vu_rcomp_mult_constants2(a, b):
    """ Multiplies two ValueWithUnits that are also RcompUnits """
    check_isinstance(a.unit, RcompUnits)
    check_isinstance(b.unit, RcompUnits)
    R = mult_table(a.unit, b.unit)
    value = a.value * b.value
    return ValueWithUnits(value=value, unit=R)

@contract(seq='seq($ValueWithUnits)')
def generic_mult_constantsN(seq):
    """ Multiplies a sequence of constants that could be either Nat, Rcomp, or RCompUnits """
    for c in seq:
        if isinstance(c.unit, RbicompUnits):
            assert c.value < 0
            msg = 'Cannot multiply by negative number %s.' % c
            raise_desc(DPSemanticError, msg)

    posets = [_.unit for _ in seq]
    for p in posets:
        check_isinstance(p, (Nat, Rcomp, RcompUnits))

    promoted, R = generic_mult_table(posets)
    
    if isinstance(R, Nat):
        values = [_.value for _ in seq]
        from functools import reduce
        res = reduce(Nat_mult_uppersets_continuous, values)
        return ValueWithUnits(res, R) 
    else:
        res = 1.0
        for vu, F2 in zip(seq, promoted):
            value2 = express_value_in_isomorphic_space(vu.unit, vu.value, F2)
            if F2.equal(value2, F2.get_top()):
                res = R.get_top()
                break
            res *= value2
        return ValueWithUnits(res, R)
        # XXX needs to check overflow
    return res

def generic_mult_table(seq):
    """ A generic mult table that knows how to take care of Nat and Rcomp as well. """
    seq = list(seq)
    for s in seq:
        check_isinstance(s, (Nat, Rcomp, RcompUnits))
        
    # If there are some RcompUnits, then Nat and Rcomp 
    # will be promoted to Rcomp dimensionless
    any_reals = any(isinstance(_, RcompUnits) for _ in seq)
    any_rcomp = any(isinstance(_, Rcomp) for _ in seq)
    if any_reals:
        # compute the promoted ones
        def get_promoted(s):
            if isinstance(s, (Rcomp, Nat)):
                return R_dimensionless
            else:
                return s
    
        # this is all RcompUnits
        promoted = map(get_promoted, seq)
    
        # now we can use mult_table
        return promoted, mult_table_seq(promoted)
    elif any_rcomp:
        # promote Nat to Rcomp
        def get_promoted(s):
            if isinstance(s,  Nat):
                return Rcomp()
            else:
                assert isinstance(s, Rcomp)
                return s
    
        # this is all RcompUnits
        promoted = map(get_promoted, seq)
    
        # now we can use mult_table
        return promoted, Rcomp()
    else: # it's all Nats
        return seq, Nat()

def add_table(F1, F2):
    if not F1 == F2:
        msg = 'Incompatible units for addition.'
        raise_desc(DPSemanticError, msg, F1=F1, F2=F2)
    return F1

class ConstantsNotCompatibleForAddition(Exception):
    pass

def plus_constants2(a, b):
    """ raises ConstantsNotCompatibleForAddition """
    
    A = a.unit
    B = b.unit
    
    if isinstance(A, RcompUnits) and isinstance(B, RcompUnits):
        return plus_constants2_rcompunits(a, b)
    
    if isinstance(A, RcompUnits) and isinstance(B, (Rcomp, Nat)):
        try:
            b2A = b.cast_value(A)
        except NotLeq:
            msg = 'Cannot sum %s and %s.' % (A, B)
            raise_desc(ConstantsNotCompatibleForAddition, msg)
        b2 = ValueWithUnits(b2A, A)
        return plus_constants2_rcompunits(a, b2)
    
    if isinstance(B, RcompUnits) and isinstance(A, (Rcomp, Nat)):
        try:
            a2B = a.cast_value(B)
        except NotLeq:
            msg = 'Cannot sum %s and %s.' % (A, B)
            raise_desc(ConstantsNotCompatibleForAddition, msg)
        a2 = ValueWithUnits(a2B, B)
        return plus_constants2_rcompunits(a2, b)

    if isinstance(B, Rcomp) and isinstance(A, Rcomp):
        res = rcomp_add(a.value, b.value)
        return ValueWithUnits(value=res, unit=Rcomp())

    if isinstance(B, Rcomp) and isinstance(A, Nat):
        a2v = a.cast_value(B)
        res = rcomp_add(a2v, b.value)
        return ValueWithUnits(value=res, unit=Rcomp())
  
    if isinstance(A, Rcomp) and isinstance(B, Nat):
        b2v = b.cast_value(A)
        res = rcomp_add(a.value, b2v)
        return ValueWithUnits(value=res, unit=Rcomp())

    if isinstance(B, Nat) and isinstance(A, Nat):
        res = Nat_add(a.value, b.value)
        return ValueWithUnits(value=res, unit=Nat())
        
    msg = 'Cannot add %r and %r' % (a, b)
    raise DPNotImplementedError(msg)

@contract(a=ValueWithUnits, b=ValueWithUnits)
def plus_constants2_rcompunits(a, b):
    """ raises ConstantsNotCompatibleForAddition """
    check_isinstance(a.unit, RcompUnits)
    check_isinstance(b.unit, RcompUnits)
    R = a.unit
    Fs = [a.unit, b.unit]
    values = [a.value, b.value]
    res = sum_units(Fs, values, R)
    return ValueWithUnits(value=res, unit=R)

def plus_constantsN(constants):
    """ raises ConstantsNotCompatibleForAddition """
    return functools.reduce(plus_constants2, constants)
