# -*- coding: utf-8 -*-

from .namedtuple_tricks import namedtuplewhere

__all__ = ['CDPLanguage']


class CDPLanguage():

    GenericNonlinearity = namedtuplewhere('GenericNonlinearity', 'function op1 R_from_F')

    NewLimit = namedtuplewhere('NewLimit', 'value_with_unit')

    ValueExpr = namedtuplewhere('ValueExpr', 'value')
    Unit = namedtuplewhere('Unit', 'value')
    SimpleValue = namedtuplewhere('SimpleValue', 'value unit')
    MakeTupleConstants = namedtuplewhere('MakeTupleConstants', 'open ops close')

    MakeTemplate = namedtuplewhere('MakeTemplate', 'keyword dp_rvalue')
    AbstractAway = namedtuplewhere('AbstractAway', 'keyword dp_rvalue')
    Compact = namedtuplewhere('Compact', 'keyword dp_rvalue')

    DPInstance = namedtuplewhere('DPInstance', 'keyword dp_rvalue')
    PlusN = namedtuplewhere('PlusN', 'ops')
    MultN = namedtuplewhere('MultN', 'ops')
    Divide = namedtuplewhere('Divide', 'ops')
    Coproduct = namedtuplewhere('Coproduct', 'ops')
    OpMax = namedtuplewhere('Max', 'keyword a b')
    OpMin = namedtuplewhere('Min', 'keyword a b')

    DPName = namedtuplewhere('DPName', 'value')
    DPTypeName = namedtuplewhere('DPTypeName', 'value')

    Resource = namedtuplewhere('Resource', 'dp s keyword')
    Function = namedtuplewhere('Function', 'dp s keyword')

    VariableRef = namedtuplewhere('VariableRef', 'name')
    DPVariableRef = namedtuplewhere('DPVariableRef', 'name')

    NewResource = namedtuplewhere('NewResource', 'name')
    NewFunction = namedtuplewhere('NewFunction', 'name')
    Constraint = namedtuplewhere('Constraint', 'function rvalue prep')

    NatConstant = namedtuplewhere('NatConstant', 's1 s2 value')  # value = int, >=0
    IntConstant = namedtuplewhere('IntConstant', 's1 s2 value')  # value = int

    LoadCommand = namedtuplewhere('LoadCommand', 'keyword load_arg')
    SetName = namedtuplewhere('SetName', 'keyword name dp_rvalue')
    SetMCDPType = namedtuplewhere('SetMCDPType', 'keyword name eq right_side')

    # an incomplete model
    Ellipsis = namedtuplewhere('Ellipsis', 'token')

    SetNameGenericVar = namedtuplewhere('SetNameGenericVar', 'value')
    SetNameGeneric = namedtuplewhere('SetNameGeneric', 'name eq right_side')

    PowerSet = namedtuplewhere('PowerSet', 'symbol p1 space p2')
    # natural numbers
    Nat = namedtuplewhere('Nat', 'symbol')
    Int = namedtuplewhere('Int', 'symbol')
    # Just Keywords
    ProvideKeyword = namedtuplewhere('ProvideKeyword', 'keyword')
    RequireKeyword = namedtuplewhere('RequireKeyword', 'keyword')
    MCDPKeyword = namedtuplewhere('MCDPKeyword', 'keyword')
    SubKeyword = namedtuplewhere('SubKeyword', 'keyword')
    TopKeyword = namedtuplewhere('TopKeyword', 'keyword')
    MCDPTypeKeyword = namedtuplewhere('MCDPTypeKeyword', 'keyword')
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
    InstanceKeyword = namedtuplewhere('InstanceKeyword', 'keyword')
    OpenBraceKeyword = namedtuplewhere('OpenBraceKeyword', 'keyword')
    CloseBraceKeyword = namedtuplewhere('CloseBraceKeyword', 'keyword')
    OpKeyword = namedtuplewhere('OpKeyword', 'keyword')  # Max
    DPWrapToken = namedtuplewhere('DPWrapToken', 'keyword')
    FuncName = namedtuplewhere('FuncName', 'value')  # python function name
    ApproxKeyword = namedtuplewhere('ApproxKeyword', 'keyword')


    # catalogue =
    FromCatalogueKeyword = namedtuplewhere('FromCatalogueKeyword', 'keyword')  # python function name

    ImpName = namedtuplewhere('ImpName', 'value')
    CatalogueRow = namedtuplewhere('CatalogeRow', 'cells')
    CatalogueTable = namedtuplewhere('CatalogueTable', 'rows')
    FromCatalogue = namedtuplewhere('FromCatalogue', 'keyword funres table')

    ApproxDPModel = namedtuplewhere('ApproxDPModel', 'name perc abs max_value dp')

    # just prepositions
    leq = namedtuplewhere('leq', 'glyph')
    product = namedtuplewhere('product', 'glyph')
    geq = namedtuplewhere('geq', 'glyph')
    eq = namedtuplewhere('eq', 'glyph')
    plus = namedtuplewhere('plus', 'glyph')
    times = namedtuplewhere('times', 'glyph')
    bar = namedtuplewhere('bar', 'glyph')
    coprod = namedtuplewhere('coprod', 'glyph')
    DotPrep = namedtuplewhere('DotPrep', 'glyph')
    comma = namedtuplewhere('comma', 'glyph')
    open_brace = namedtuplewhere('open_brace', 'glyph')
    close_brace = namedtuplewhere('close_brace', 'glyph')

    FName = namedtuplewhere('FName', 'value')
    RName = namedtuplewhere('RName', 'value')
    Collection = namedtuplewhere('Collection', 'elements')
    UpperSetFromCollection = namedtuplewhere('UpperSetFromCollection', 'value')

    FunStatement = namedtuplewhere('FunStatement', 'keyword fname unit')
    ResStatement = namedtuplewhere('ResStatement', 'keyword rname unit')

    LoadDP = namedtuplewhere('LoadDP', 'keyword name')
    DPWrap = namedtuplewhere('DPWrap', 'token statements prep impl')

    ArgName = namedtuplewhere('ArgName', 'value')  # value = string
    PDPCodeSpec = namedtuplewhere('PDPCodeSpec', 'keyword function arguments')
    PDPCodeSpecNoArgs = namedtuplewhere('PDPCodeSpecNoArgs', 'keyword function')

    SpaceProduct = namedtuplewhere('SpaceProduct', 'ops')
    InvMult = namedtuplewhere('InvMult', 'ops')
    InvPlus = namedtuplewhere('InvPlus', 'ops')
    FunShortcut1 = namedtuplewhere('FunShortcut1', 'provides fname prep_using name')
    ResShortcut1 = namedtuplewhere('ResShortcut1', 'requires rname prep_for name')

    FunShortcut1m = namedtuplewhere('FunShortcut1m', 'provides fnames prep_using name')
    ResShortcut1m = namedtuplewhere('ResShortcut1m', 'requires rnames prep_for name')
    FunShortcut2 = namedtuplewhere('FunShortcut2', 'keyword fname leq lf')
    ResShortcut2 = namedtuplewhere('ResShortcut2', 'keyword rname geq rvalue')
    
    IntegerFraction = namedtuplewhere('IntegerFraction', 'num den')

    Power = namedtuplewhere('Power', 'op1 exponent')
    BuildProblem = namedtuplewhere('BuildProblem', 'keyword statements')




