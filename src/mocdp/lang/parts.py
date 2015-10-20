# -*- coding: utf-8 -*-
# operators
from collections import namedtuple

def namedtuplewhere(a, b):
    base = namedtuple(a, b)
    class F(base):
        def __init__(self, *args, **kwargs):
            base.__init__(self, *args, **kwargs)
            self.where = None
    F.__name__ = a
    return F

GenericNonlinearity = namedtuplewhere('GenericNonlinearity', 'function op1 R_from_F')

NewLimit = namedtuplewhere('NewLimit', 'value_with_unit')

ValueWithUnits0 = namedtuplewhere('ValueWithUnits0', 'value unit')
class ValueWithUnits(ValueWithUnits0):
    def __init__(self, value, unit):
        unit.belongs(value)
        ValueWithUnits0.__init__(self, value=value, unit=unit)

MakeTemplate = namedtuplewhere('MakeTemplate', 'dp_rvalue')
AbstractAway = namedtuplewhere('AbstractAway', 'dp_rvalue')

Mult = namedtuplewhere('Mult', 'a b')
Plus = namedtuplewhere('Plus', 'a b')
PlusN = namedtuplewhere('PlusN', 'ops')
MultN = namedtuplewhere('MultN', 'ops')
OpMax = namedtuplewhere('Max', 'a b')
OpMin = namedtuplewhere('Min', 'a b')
Resource = namedtuplewhere('Resource', 'dp s')
Function = namedtuplewhere('Function', 'dp s')

NewFunction = namedtuplewhere('NewFunction', 'name')
NewResource = namedtuplewhere('NewResource', 'name')
Constraint = namedtuplewhere('Constraint', 'function rvalue')

LoadCommand = namedtuplewhere('LoadCommand', 'load_arg')
SetName = namedtuplewhere('SetName', 'name dp_rvalue')

FunStatement = namedtuplewhere('FunStatement', 'fname unit')
ResStatement = namedtuplewhere('ResStatement', 'rname unit')

LoadDP = namedtuplewhere('LoadDP', 'name')
DPWrap = namedtuplewhere('DPWrap', 'fun res impl')
PDPCodeSpec = namedtuplewhere('PDPCodeSpec', 'function arguments')


FunShortcut1 = namedtuplewhere('FunShortcut1', 'fname name')
ResShortcut1 = namedtuplewhere('ResShortcut1', 'rname name')
FunShortcut2 = namedtuplewhere('FunShortcut2', 'fname lf')
ResShortcut2 = namedtuplewhere('ResShortcut2', 'rname rvalue')
