# -*- coding: utf-8 -*-

from .namedtuple_tricks import namedtuplewhere

__all__ = ['CDPLanguage']


class CDPLanguage():

    GenericNonlinearity = namedtuplewhere('GenericNonlinearity', 'function op1 R_from_F')

    NewLimit = namedtuplewhere('NewLimit', 'value_with_unit')

    ValueWithUnits0 = namedtuplewhere('ValueWithUnits0', 'value unit')
    class ValueWithUnits(ValueWithUnits0):
        def __init__(self, value, unit):
            unit.belongs(value)
            CDPLanguage.ValueWithUnits0.__init__(self, value=value, unit=unit)

    MakeTemplate = namedtuplewhere('MakeTemplate', 'dp_rvalue')
    AbstractAway = namedtuplewhere('AbstractAway', 'dp_rvalue')
    Compact = namedtuplewhere('Compact', 'dp_rvalue')

    PlusN = namedtuplewhere('PlusN', 'ops')
    MultN = namedtuplewhere('MultN', 'ops')
    OpMax = namedtuplewhere('Max', 'a b')
    OpMin = namedtuplewhere('Min', 'a b')

    Resource = namedtuplewhere('Resource', 'dp s')
    Function = namedtuplewhere('Function', 'dp s')

    VariableRef = namedtuplewhere('VariableRef', 'name')

    NewResource = namedtuplewhere('NewResource', 'name')
    Constraint = namedtuplewhere('Constraint', 'function rvalue')

    LoadCommand = namedtuplewhere('LoadCommand', 'load_arg')
    SetName = namedtuplewhere('SetName', 'name dp_rvalue')

    SetNameGeneric = namedtuplewhere('SetNameGeneric', 'name right_side')

    FunStatement = namedtuplewhere('FunStatement', 'fname unit')
    ResStatement = namedtuplewhere('ResStatement', 'rname unit')

    LoadDP = namedtuplewhere('LoadDP', 'name')
    DPWrap = namedtuplewhere('DPWrap', 'fun res impl')
    PDPCodeSpec = namedtuplewhere('PDPCodeSpec', 'function arguments')

    InvMult = namedtuplewhere('InvMult', 'ops')
    FunShortcut1 = namedtuplewhere('FunShortcut1', 'fname name')
    ResShortcut1 = namedtuplewhere('ResShortcut1', 'rname name')
    FunShortcut2 = namedtuplewhere('FunShortcut2', 'fname lf')
    ResShortcut2 = namedtuplewhere('ResShortcut2', 'rname rvalue')
    MultipleStatements = namedtuplewhere('MultipleStatements', 'statements')
    
    IntegerFraction = namedtuplewhere('IntegerFraction', 'num den')

    Power = namedtuplewhere('Power', 'op1 exponent')


