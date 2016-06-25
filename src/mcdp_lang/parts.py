# -*- coding: utf-8 -*-

from .namedtuple_tricks import namedtuplewhere

__all__ = [
    'CDPLanguage',
]


class CDPLanguage():

    GenericNonlinearity = namedtuplewhere('GenericNonlinearity', 'function op1 R_from_F')

    ValueExpr = namedtuplewhere('ValueExpr', 'value')

    # now only used for a hack
    Unit = namedtuplewhere('Unit', 'value')

    RcompUnit = namedtuplewhere('RcompUnit', 'pint_string')
    SimpleValue = namedtuplewhere('SimpleValue', 'value space')
    Top = namedtuplewhere('Top', 'keyword space')
    Bottom = namedtuplewhere('Bottom', 'keyword space')
    MakeTuple = namedtuplewhere('MakeTuple', 'open ops close')

    MakeTemplate = namedtuplewhere('MakeTemplate', 'keyword dp_rvalue')
    MakeCanonical = namedtuplewhere('MakeCanonical', 'keyword dp_rvalue')
    AbstractAway = namedtuplewhere('AbstractAway', 'keyword dp_rvalue')
    Compact = namedtuplewhere('Compact', 'keyword dp_rvalue')
    Flatten = namedtuplewhere('Flatten', 'keyword dp_rvalue')

    DPInstance = namedtuplewhere('DPInstance', 'keyword dp_rvalue')
    DPInstanceFromLibrary = namedtuplewhere('DPInstanceFromLibrary', 'keyword dpname')

    PlusN = namedtuplewhere('PlusN', 'ops')
    MultN = namedtuplewhere('MultN', 'ops')
    Divide = namedtuplewhere('Divide', 'ops')
    Coproduct = namedtuplewhere('Coproduct', 'ops')

    # elements: all strings, coproducts
    CoproductWithNamesChooseKeyword = namedtuplewhere('CoproductWithNamesChooseKeyword', 'keyword')
    CoproductWithNamesName = namedtuplewhere('CoproductWithNamesName', 'value')
    CoproductWithNames = namedtuplewhere('CoproductWithNames', 'keyword elements')

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

    LoadNDP = namedtuplewhere('LoadNDP', 'keyword load_arg')
    LoadConstant = namedtuplewhere('LoadConstant', 'keyword load_arg')
    LoadPoset = namedtuplewhere('LoadPoset', 'keyword load_arg')
    LoadTemplate = namedtuplewhere('LoadTemplate', 'keyword load_arg')

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
    ProvidedKeyword = namedtuplewhere('ProvidedKeyword', 'keyword')
    RequiredKeyword = namedtuplewhere('RequiredKeyword', 'keyword')
    MCDPKeyword = namedtuplewhere('MCDPKeyword', 'keyword')
    SubKeyword = namedtuplewhere('SubKeyword', 'keyword')
    TopKeyword = namedtuplewhere('TopKeyword', 'keyword')
    BottomKeyword = namedtuplewhere('BottomKeyword', 'keyword')
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
    FromLibraryKeyword = namedtuplewhere('FromLibraryKeyword', 'keyword')
    OpKeyword = namedtuplewhere('OpKeyword', 'keyword')  # Max
    DPWrapToken = namedtuplewhere('DPWrapToken', 'keyword')
    FuncName = namedtuplewhere('FuncName', 'value')  # python function name
    NDPName = namedtuplewhere('NDPName', 'value')  # name in "new <name>"
    ApproxKeyword = namedtuplewhere('ApproxKeyword', 'keyword')
    FlattenKeyword = namedtuplewhere('FlattenKeyword', 'keyword')
    SpecializeKeyword = namedtuplewhere('SpecializeKeyword', 'keyword')
    WithKeyword = namedtuplewhere('WithKeyword', 'keyword')
    TemplateSpec = namedtuplewhere('TemplateSpec', 'keyword params ndpt')

    Specialize = namedtuplewhere('Specialize', 'keyword template params')
    TemplateParamName = namedtuplewhere('TemplateParamName', 'value')

    # catalogue =
    FromCatalogueKeyword = namedtuplewhere('FromCatalogueKeyword', 'keyword')  # python function name

    ImpName = namedtuplewhere('ImpName', 'value')
    CatalogueRow = namedtuplewhere('CatalogeRow', 'cells')
    CatalogueTable = namedtuplewhere('CatalogueTable', 'rows')
    FromCatalogue = namedtuplewhere('FromCatalogue', 'keyword funres table')

    ApproxDPModel = namedtuplewhere('ApproxDPModel', 'keyword name perc abs max_value dp')

    # just prepositions
    leq = namedtuplewhere('leq', 'glyph')
    LSQ = namedtuplewhere('LSQ', 'glyph')
    RSQ = namedtuplewhere('RSQ', 'glyph')
    product = namedtuplewhere('product', 'glyph')
    geq = namedtuplewhere('geq', 'glyph')
    eq = namedtuplewhere('eq', 'glyph')
    plus = namedtuplewhere('plus', 'glyph')
    exponent = namedtuplewhere('exponent', 'glyph')
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

    PosetName = namedtuplewhere('PosetName', 'value')
    LoadDP = namedtuplewhere('LoadDP', 'keyword name')
    LoadPoset = namedtuplewhere('LoadPoset', 'keyword name')

    DPWrap = namedtuplewhere('DPWrap', 'token statements prep impl')

    # Code specs
    ArgName = namedtuplewhere('ArgName', 'value')  # value = string
    ArgValue = namedtuplewhere('ArgValue', 'python_value')  # int, float, string
    CodeSpec = namedtuplewhere('CodeSpec', 'keyword function arguments')
    CodeSpecNoArgs = namedtuplewhere('CodeSpecNoArgs', 'keyword function')

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

    Power = namedtuplewhere('Power', 'op1 glyph exponent')
    BuildProblem = namedtuplewhere('BuildProblem', 'keyword statements')

    # Finite posets
    FinitePosetKeyword = namedtuplewhere('FinitePosetKeyword', 'keyword')
    FinitePosetElement = namedtuplewhere('FinitePosetElement', 'identifier')
    FinitePoset = namedtuplewhere('FinitePoset', 'keyword chains')

    TakeKeyword = namedtuplewhere('TakeKeyword', 'keyword')

    TupleIndex = namedtuplewhere('TupleIndex', 'keyword value index')

    SpaceCustomValue = namedtuplewhere('SpaceCustomValue', 'space keyword custom_string')

    # solve( <0 g>, `model )
    SolveModel = namedtuplewhere('SolveModel', 'keyword f model')

    # UpperSets(<space>)
    UpperSetsKeyword = namedtuplewhere('UpperSetsKeyword', 'keyword')
    MakeUpperSets = namedtuplewhere('MakeUpperSets', 'keyword space')

    # Uncertain(L, U)
    UncertainKeyword = namedtuplewhere('UncertainKeyword', 'keyword')
    UncertainRes = namedtuplewhere('UncertainRes', 'keyword lower upper')
    UncertainFun = namedtuplewhere('UncertainFun', 'keyword lower upper')

