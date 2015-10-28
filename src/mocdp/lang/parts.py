# -*- coding: utf-8 -*-

from .namedtuple_tricks import namedtuplewhere

__all__ = ['CDPLanguage']


class CDPLanguage():

    GenericNonlinearity = namedtuplewhere('GenericNonlinearity', 'function op1 R_from_F')

    NewLimit = namedtuplewhere('NewLimit', 'value_with_unit')

    ValueWithUnits0 = namedtuplewhere('ValueWithUnits0', 'value unit')
    class ValueWithUnits(ValueWithUnits0):
        def __init__(self, value, unit, where=None):
            unit.belongs(value)
            CDPLanguage.ValueWithUnits0.__init__(self, value=value, unit=unit, where=where)

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

    SetNameGenericVar = namedtuplewhere('SetNameGenericVar', 'value')
    SetNameGeneric = namedtuplewhere('SetNameGeneric', 'name right_side')

    # Just Keywords
    ProvideKeyword = namedtuplewhere('ProvideKeyword', 'keyword')
    RequireKeyword = namedtuplewhere('RequireKeyword', 'keyword')
    MCDPKeyword = namedtuplewhere('MCDPKeyword', 'keyword')

    FName = namedtuplewhere('FName', 'value')
    RName = namedtuplewhere('RName', 'value')
    Unit = namedtuplewhere('Unit', 'value')

    FunStatement = namedtuplewhere('FunStatement', 'keyword fname unit')
    ResStatement = namedtuplewhere('ResStatement', 'keyword rname unit')

    LoadDP = namedtuplewhere('LoadDP', 'name')
    DPWrap = namedtuplewhere('DPWrap', 'fun res impl')
    PDPCodeSpec = namedtuplewhere('PDPCodeSpec', 'function arguments')

    InvMult = namedtuplewhere('InvMult', 'ops')
    FunShortcut1 = namedtuplewhere('FunShortcut1', 'fname name')
    ResShortcut1 = namedtuplewhere('ResShortcut1', 'rname name')
    FunShortcut2 = namedtuplewhere('FunShortcut2', 'fname lf')
    ResShortcut2 = namedtuplewhere('ResShortcut2', 'rname rvalue')
#     MultipleStatements = namedtuplewhere('MultipleStatements', 'statements')
    
    IntegerFraction = namedtuplewhere('IntegerFraction', 'num den')

    Power = namedtuplewhere('Power', 'op1 exponent')
    BuildProblem = namedtuplewhere('BuildProblem', 'keyword statements')

list_types = {
}

for i in range(1, 30):
    args = ['e%d' % _ for _ in range(i)]
    ltype = namedtuplewhere('List%d' % i, " ".join(args))
    list_types[i] = ltype

def make_list(x, where=None):
    ltype = list_types[len(x)]
    res = ltype(*tuple(x), where=where)
#     print('res: %s' % str(res))
    return res

def unwrap_list(res):
    normal = []
    for k, v in res._asdict().items():
        if k == 'where': continue
        normal.append(v)
#     print('unwrapped to %r' % normal)
    return normal


