# -*- coding: utf-8 -*-
# operators
from collections import namedtuple

__all__ = ['CDPLanguage']

def namedtuplewhere(a, b):
    fields = b.split(" ")
    assert not 'where' in fields
    fields.append('where')
    base = namedtuple(a, fields)
    base.__new__.__defaults__ = (None,)
    F = base
    # make the name available
    g = globals()
    g[a] = F
    return F

def get_copy_with_where(x, where):
    d = x._asdict()
    del d['where']
    d['where'] = where
    T = type(x)
    x1 = T(**d)
    return x1

def remove_where_info(x):
    from compmake.jobs.dependencies import isnamedtupleinstance
    if not isnamedtupleinstance(x):
        return x
    d = x._asdict()
    for k, v in d.items():
        d[k] = remove_where_info(v)
    del d['where']
    d['where'] = None
    T = type(x)
    x1 = T(**d)
    return x1


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

    Mult = namedtuplewhere('Mult', 'a b')
    Plus = namedtuplewhere('Plus', 'a b')
    PlusN = namedtuplewhere('PlusN', 'ops')
    MultN = namedtuplewhere('MultN', 'ops')
    OpMax = namedtuplewhere('Max', 'a b')
    OpMin = namedtuplewhere('Min', 'a b')
    Resource = namedtuplewhere('Resource', 'dp s')
    Function = namedtuplewhere('Function', 'dp s')

    VariableRef = namedtuplewhere('VariableRef', 'name')

    # also plays like VariableRef
    NewFunction = namedtuplewhere('NewFunction', 'name')

    NewResource = namedtuplewhere('NewResource', 'name')
    Constraint = namedtuplewhere('Constraint', 'function rvalue')

    LoadCommand = namedtuplewhere('LoadCommand', 'load_arg')
    SetName = namedtuplewhere('SetName', 'name dp_rvalue')
    SetNameResource = namedtuplewhere('SetNameResource', 'name rvalue')
    SetNameConstant = namedtuplewhere('SetNameConstant', 'name constant_value')

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


