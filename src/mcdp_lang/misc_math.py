# -*- coding: utf-8 -*-
from contracts import contract
from contracts.utils import raise_desc
from mcdp_dp import sum_units
from mcdp_posets import Nat, RcompUnits, mult_table
from mocdp.comp.context import ValueWithUnits
from mocdp.exceptions import DPSemanticError
import functools
import warnings


class MultValue():

    def __init__(self, res):
        self.res = res

    def __call__(self, x):
        return x * self.res

    def __str__(self):
        return 'Mult(%s)' % self.res

# class MultValueMap(Map):
#     """ Implements _ -> _ * x on RCompUnits """
#
#     def __init__(self, F, R, constant):
#
#

@contract(S=RcompUnits)
def inv_unit(S):
    # S.units is a pint quantity
    unit = 1 / S.units
    string = '%s' % unit
    res = RcompUnits(1 / S.units, string)
    return res

def inv_constant(a):
    from mcdp_posets.rcomp import Rcomp
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


def mult_constants2(a, b):
    R = mult_table(a.unit, b.unit)
    value = a.value * b.value
    return ValueWithUnits(value=value, unit=R)

def mult_constantsN(seq):
    res = functools.reduce(mult_constants2, seq)
    # print('seq: %s res: %s' % (seq, res))
    return res


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
    return functools.reduce(plus_constants2, constants)
