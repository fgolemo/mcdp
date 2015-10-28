# -*- coding: utf-8 -*-

from .namedtuple_tricks import namedtuplewhere
from contracts.interface import Where
from contracts.utils import raise_desc, raise_wrapped
from mocdp.exceptions import DPInternalError

__all__ = ['CDPLanguage']


class CDPLanguage():

    GenericNonlinearity = namedtuplewhere('GenericNonlinearity', 'function op1 R_from_F')

    NewLimit = namedtuplewhere('NewLimit', 'value_with_unit')

    ValueExpr = namedtuplewhere('ValueExpr', 'value')
    UnitExpr = namedtuplewhere('UnitExpr', 'value')
    SimpleValue = namedtuplewhere('SimpleValue', 'value unit')

    MakeTemplate = namedtuplewhere('MakeTemplate', 'keyword dp_rvalue')
    AbstractAway = namedtuplewhere('AbstractAway', 'keyword dp_rvalue')
    Compact = namedtuplewhere('Compact', 'keyword dp_rvalue')

    PlusN = namedtuplewhere('PlusN', 'ops glyphs')
    MultN = namedtuplewhere('MultN', 'ops glyphs')
    OpMax = namedtuplewhere('Max', 'keyword a b')
    OpMin = namedtuplewhere('Min', 'keyword a b')

    DPName = namedtuplewhere('DPName', 'value')

    Resource = namedtuplewhere('Resource', 'dp s keyword')
    Function = namedtuplewhere('Function', 'dp s keyword')

    VariableRef = namedtuplewhere('VariableRef', 'name')

    NewResource = namedtuplewhere('NewResource', 'name')
    Constraint = namedtuplewhere('Constraint', 'function rvalue prep')

    LoadCommand = namedtuplewhere('LoadCommand', 'keyword load_arg')
    SetName = namedtuplewhere('SetName', 'keyword name dp_rvalue')

    SetNameGenericVar = namedtuplewhere('SetNameGenericVar', 'value')
    SetNameGeneric = namedtuplewhere('SetNameGeneric', 'name eq right_side')

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
    ImplementedbyKeyword = namedtuplewhere('ImplementedbyKeyword', 'keyword')
    LoadKeyword = namedtuplewhere('LoadKeyword', 'keyword')
    CodeKeyword = namedtuplewhere('CodeKeyword', 'keyword')
    OpKeyword = namedtuplewhere('OpKeyword', 'keyword')  # Max
    DPWrapToken = namedtuplewhere('DPWrapToken', 'keyword')
    FuncName = namedtuplewhere('FuncName', 'value')  # python function name
    # just prepositions
    leq = namedtuplewhere('leq', 'glyph')
    geq = namedtuplewhere('geq', 'glyph')
    eq = namedtuplewhere('eq', 'glyph')
    plus = namedtuplewhere('plus', 'glyph')
    times = namedtuplewhere('times', 'glyph')
    DotPrep = namedtuplewhere('DotPrep', 'glyph')

    FName = namedtuplewhere('FName', 'value')
    RName = namedtuplewhere('RName', 'value')
    Unit = namedtuplewhere('Unit', 'value')

    FunStatement = namedtuplewhere('FunStatement', 'keyword fname unit')
    ResStatement = namedtuplewhere('ResStatement', 'keyword rname unit')

    LoadDP = namedtuplewhere('LoadDP', 'keyword name')
    DPWrap = namedtuplewhere('DPWrap', 'token statements prep impl')
    PDPCodeSpec = namedtuplewhere('PDPCodeSpec', 'keyword function arguments')

    InvMult = namedtuplewhere('InvMult', 'ops')
    FunShortcut1 = namedtuplewhere('FunShortcut1', 'provides fname prep_using name')
    ResShortcut1 = namedtuplewhere('ResShortcut1', 'requires rname prep_for name')

    FunShortcut1m = namedtuplewhere('FunShortcut1m', 'provides fnames prep_using name')
    ResShortcut1m = namedtuplewhere('ResShortcut1m', 'requires rnames prep_for name')
    FunShortcut2 = namedtuplewhere('FunShortcut2', 'keyword fname leq lf')
    ResShortcut2 = namedtuplewhere('ResShortcut2', 'keyword rname geq rvalue')
    
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


def is_a_special_list(x):
    return 'List' in type(x).__name__

def make_list(x, where=None):
    try:
        if not len(x):
#             if not where:
#                 raise ValueError(x)
            return list_types[0](dummy='dummy', where=where)
    
        ltype = list_types[len(x)]
        w1 = x[0].where
        w2 = x[-1].where
        if w1 is None or w2 is None:
            for y in x:
                if y.where is None:
                    print y
            raise_desc(ValueError, 'Cannot create list', x=x)
        w3 = Where(string=w1.string,
                      character=w1.character,
                      character_end=w2.character_end)

        res = ltype(*tuple(x), where=w3)
        return res
    except BaseException as e:
        msg = 'Cannot create list'
        raise_wrapped(DPInternalError, e, msg, x=x, where=where)

def unwrap_list(res):
    if isinstance(res, list_types[0]):
        return []
    normal = []
    for k, v in res._asdict().items():
        if k == 'where': continue
        normal.append(v)
    return normal



