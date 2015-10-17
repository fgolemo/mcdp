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

NewLimit = namedtuplewhere('NewLimit', 'value_with_unit')
ValueWithUnits = namedtuplewhere('ValueWithUnits', 'value unit')

Mult = namedtuplewhere('Mult', 'a b')
Plus = namedtuplewhere('Plus', 'a b')
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
