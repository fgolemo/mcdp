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

    MakeTemplate = namedtuplewhere('MakeTemplate', 'keyword dp_rvalue')
    AbstractAway = namedtuplewhere('AbstractAway', 'keyword dp_rvalue')
    Compact = namedtuplewhere('Compact', 'keyword dp_rvalue')

    PlusN = namedtuplewhere('PlusN', 'ops')
    MultN = namedtuplewhere('MultN', 'ops')
    OpMax = namedtuplewhere('Max', 'keyword a b')
    OpMin = namedtuplewhere('Min', 'keyword a b')

    DPName = namedtuplewhere('DPName', 'value')

    Resource = namedtuplewhere('Resource', 'dp s keyword')
    Function = namedtuplewhere('Function', 'dp s keyword')

    VariableRef = namedtuplewhere('VariableRef', 'name')

    NewResource = namedtuplewhere('NewResource', 'name')
    Constraint = namedtuplewhere('Constraint', 'function rvalue prep')

    LoadCommand = namedtuplewhere('LoadCommand', 'load_arg')
    SetName = namedtuplewhere('SetName', 'keyword name dp_rvalue')

    SetNameGenericVar = namedtuplewhere('SetNameGenericVar', 'value')
    SetNameGeneric = namedtuplewhere('SetNameGeneric', 'name right_side')

    # Just Keywords
    ProvideKeyword = namedtuplewhere('ProvideKeyword', 'keyword')
    RequireKeyword = namedtuplewhere('RequireKeyword', 'keyword')
    MCDPKeyword = namedtuplewhere('MCDPKeyword', 'keyword')
    SubKeyword = namedtuplewhere('SubKeyword', 'keyword')
    CompactKeyword = namedtuplewhere('CompactKeyword', 'keyword')
    AbstractKeyword = namedtuplewhere('AbstractKeyword', 'keyword')
    TemplateKeyword = namedtuplewhere('TemplateKeyword', 'keyword')
    ForKeyword = namedtuplewhere('ForKeyword', 'keyword')
    UsingKeyword = namedtuplewhere('UsingKeyword', 'keyword')
    RequiredByKeyword = namedtuplewhere('RequiredByKeyword', 'keyword')
    ProvidedByKeyword = namedtuplewhere('ProvidedByKeyword', 'keyword')
    OpKeyword = namedtuplewhere('OpKeyword', 'keyword')  # Max
    # just prepositions
    leq = namedtuplewhere('leq', 'glyph')
    geq = namedtuplewhere('geq', 'glyph')
    DotPrep = namedtuplewhere('DotPrep', 'glyph')

    FName = namedtuplewhere('FName', 'value')
    RName = namedtuplewhere('RName', 'value')
    Unit = namedtuplewhere('Unit', 'value')

    FunStatement = namedtuplewhere('FunStatement', 'keyword fname unit')
    ResStatement = namedtuplewhere('ResStatement', 'keyword rname unit')

    LoadDP = namedtuplewhere('LoadDP', 'name')
    DPWrap = namedtuplewhere('DPWrap', 'fun res impl')
    PDPCodeSpec = namedtuplewhere('PDPCodeSpec', 'function arguments')

    InvMult = namedtuplewhere('InvMult', 'ops')
    FunShortcut1 = namedtuplewhere('FunShortcut1', 'provides fname prep_using name')
    ResShortcut1_ = namedtuplewhere('ResShortcut1', 'requires rname prep_for name')

    class ResShortcut1(ResShortcut1_):
        def __init__(self, requires, rname, prep_for, name):
            if not isinstance(rname, CDPLanguage.RName):
                raise ValueError(rname)
            CDPLanguage.ResShortcut1_.__init__(self, requires, rname, prep_for, name)

    FunShortcut1m = namedtuplewhere('FunShortcut1m', 'provides fnames prep_using name')
    ResShortcut1m = namedtuplewhere('ResShortcut1m', 'requires rnames prep_for name')
    FunShortcut2 = namedtuplewhere('FunShortcut2', 'keyword fname leq lf')
    ResShortcut2 = namedtuplewhere('ResShortcut2', 'keyword rname geq rvalue')
#     MultipleStatements = namedtuplewhere('MultipleStatements', 'statements')
    
    IntegerFraction = namedtuplewhere('IntegerFraction', 'num den')

    Power = namedtuplewhere('Power', 'op1 exponent')
    BuildProblem = namedtuplewhere('BuildProblem', 'keyword statements')

list_types = {
}

for i in range(1, 100):
    args = ['e%d' % _ for _ in range(i)]
    ltype = namedtuplewhere('List%d' % i, " ".join(args))
    list_types[i] = ltype

list_types[0] = namedtuplewhere('List0', 'dummy')

def make_list(x, where=None):
    if not len(x):
        return list_types[0](dummy='dummy', where=where)

    ltype = list_types[len(x)]
    res = ltype(*tuple(x), where=where)
    return res

def unwrap_list(res):
    if isinstance(res, list_types[0]):
        return []
    normal = []
    for k, v in res._asdict().items():
        if k == 'where': continue
        normal.append(v)
    return normal


