# -*- coding: utf-8 -*-
import functools
import warnings

from contracts import contract
from contracts.utils import check_isinstance, raise_desc
from mcdp_maps.SumN_xxx_Map import sum_units
from mcdp_posets import Nat, RcompUnits, mult_table, Rcomp, express_value_in_isomorphic_space
from mcdp_posets.nat import Nat_mult_uppersets_continuous
from mcdp_posets.rcomp_units import (R_dimensionless, mult_table_seq,
    RbicompUnits)
from mocdp.comp.context import ValueWithUnits
from mocdp.exceptions import DPSemanticError


@contract(S=RcompUnits)
def inv_unit(S):
    # S.units is a pint quantity
    unit = 1 / S.units
    string = '%s' % unit
    res = RcompUnits(1 / S.units, string)
    return res

def inv_constant(a):
    if a.unit == Nat():
        raise NotImplementedError('division by natural number')
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
        check_isinstance(p, (Nat, RcompUnits))


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
                return Rcomp
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

def plus_constants2(a, b):
    R = a.unit
    Fs = [a.unit, b.unit]
    values = [a.value, b.value]
    res = sum_units(Fs, values, R)
    return ValueWithUnits(value=res, unit=R)

def plus_constantsN(constants):
    print('plus_constantsN: %s' % constants)
    return functools.reduce(plus_constants2, constants)
