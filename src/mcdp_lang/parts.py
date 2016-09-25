# -*- coding: utf-8 -*-

from .namedtuple_tricks import namedtuplewhere

__all__ = [
    'CDPLanguage',
]


class CDPLanguage():

    # min(), max(), etc.
    ProcName = namedtuplewhere('ProcName', 'name')
    UnaryRvalue = namedtuplewhere('UnaryRvalue', 'proc rvalue')
    
    GenericNonlinearity = namedtuplewhere('GenericNonlinearity',
                                          'function op1 R_from_F')

    ValueExpr = namedtuplewhere('ValueExpr', 'value')

    # now only used for a hack
    Unit = namedtuplewhere('Unit', 'value')

    RcompUnit = namedtuplewhere('RcompUnit', 'pint_string')
    SimpleValue = namedtuplewhere('SimpleValue', 'value space')

    # Top <space>
    TopKeyword = namedtuplewhere('TopKeyword', 'keyword')
    Top = namedtuplewhere('Top', 'keyword space')
    # Bottom <space>
    Bottom = namedtuplewhere('Bottom', 'keyword space')
    BottomKeyword = namedtuplewhere('BottomKeyword', 'keyword')
    # Maximals <space>
    Maximals = namedtuplewhere('Maximals', 'keyword space')
    MaximalsKeyword = namedtuplewhere('MaximalsKeyword', 'keyword')
    # Minimals <space>
    Minimals = namedtuplewhere('Minimals', 'keyword space')
    MinimalsKeyword = namedtuplewhere('MinimalsKeyword', 'keyword')
    # ignore x provided by y
    # ignore x required by y
    IgnoreKeyword = namedtuplewhere('IgnoreKeyword', 'keyword')
    IgnoreFun = namedtuplewhere('IgnoreFun', 'keyword fvalue')
    IgnoreRes = namedtuplewhere('IgnoreRes', 'keyword rvalue')

    MakeTuple = namedtuplewhere('MakeTuple', 'open ops close')

    MakeTemplate = namedtuplewhere('MakeTemplate', 'keyword dp_rvalue')
    MakeCanonical = namedtuplewhere('MakeCanonical', 'keyword dp_rvalue')
    AbstractAway = namedtuplewhere('AbstractAway', 'keyword dp_rvalue')
    Compact = namedtuplewhere('Compact', 'keyword dp_rvalue')
    Flatten = namedtuplewhere('Flatten', 'keyword dp_rvalue')

    ApproxUpperKeyword = namedtuplewhere('ApproxUpperKeyword', 'keyword')
    ApproxLowerKeyword = namedtuplewhere('ApproxLowerKeyword', 'keyword')
    ApproxUpper = namedtuplewhere('ApproxUpper', 'keyword level ndp')
    ApproxLower = namedtuplewhere('ApproxLower', 'keyword level ndp')

    DPInstance = namedtuplewhere('DPInstance', 'keyword dp_rvalue')
    DPInstanceFromLibrary = namedtuplewhere('DPInstanceFromLibrary', 'keyword dpname')

    PlusN = namedtuplewhere('PlusN', 'ops')
    MultN = namedtuplewhere('MultN', 'ops')
    Divide = namedtuplewhere('Divide', 'ops')
    # all constants
    ConstantMinus = namedtuplewhere('ConstantMinus', 'ops')
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
    VariableRefNDPType = namedtuplewhere('VariableRefNDPType', 'name')

    NewResource = namedtuplewhere('NewResource', 'name')
    NewFunction = namedtuplewhere('NewFunction', 'name')
    Constraint = namedtuplewhere('Constraint', 'function rvalue prep')

    NatConstant = namedtuplewhere('NatConstant', 's1 s2 value')  # value = int, >=0
    IntConstant = namedtuplewhere('IntConstant', 's1 s2 value')  # value = int

    LoadNDP = namedtuplewhere('LoadNDP', 'keyword load_arg')
    LoadConstant = namedtuplewhere('LoadConstant', 'keyword load_arg')
    LoadPoset = namedtuplewhere('LoadPoset', 'keyword load_arg')
    LoadTemplate = namedtuplewhere('LoadTemplate', 'keyword load_arg')

    # an incomplete model
    Ellipsis = namedtuplewhere('Ellipsis', 'token')

    SetNameGenericVar = namedtuplewhere('SetNameGenericVar', 'value')
    SetNameNDPInstance = namedtuplewhere('SetNameNDPInstance', 'keyword name dp_rvalue')
    SetNameMCDPType = namedtuplewhere('SetNameMCDPType', 'keyword name eq right_side')
    SetNameRValue = namedtuplewhere('SetNameRValue', 'name eq right_side')
    SetNameFValue = namedtuplewhere('SetNameFValue', 'name eq right_side')

    # set-of(<space>)
    PowerSetKeyword = namedtuplewhere('PowerSetKeyword', 'keyword')
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
    TemplateName = namedtuplewhere('TemplateName', 'value')  # name in "new <name>"
    LibraryName = namedtuplewhere('LibraryName', 'value')  # name in "new <name>"
    NDPNameWithLibrary = namedtuplewhere('NDPNameWithLibrary', 'library glyph name')  # name in "new <name>"
    TemplateNameWithLibrary = namedtuplewhere('TemplateNameWithLibrary', 'library glyph name')  # name in "new <name>"
    ApproxKeyword = namedtuplewhere('ApproxKeyword', 'keyword')
    FlattenKeyword = namedtuplewhere('FlattenKeyword', 'keyword')
    SpecializeKeyword = namedtuplewhere('SpecializeKeyword', 'keyword')
    WithKeyword = namedtuplewhere('WithKeyword', 'keyword')
    TemplateSpec = namedtuplewhere('TemplateSpec', 'keyword params ndpt')

    DisambiguationFun = namedtuplewhere('DisambiguationFun', 'tag fvalue')
    DisambiguationFunTag = namedtuplewhere('DisambiguationFunTag', 'glyph')

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

    # upperset {0g,1g}
    UpperSetFromCollectionKeyword = namedtuplewhere('UpperSetFromCollectionKeyword', 'keyword')
    UpperSetFromCollection = namedtuplewhere('UpperSetFromCollection', 'keyword value')

    FunStatement = namedtuplewhere('FunStatement', 'keyword fname unit')
    ResStatement = namedtuplewhere('ResStatement', 'keyword rname unit')

    PosetName = namedtuplewhere('PosetName', 'value')
    PosetNameWithLibrary = namedtuplewhere('PosetNameWithLibrary', 'library glyph name')

    LoadDP = namedtuplewhere('LoadDP', 'keyword name')

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

    PowerKeyword = namedtuplewhere('PowerKeyword', 'keyword')
    Power = namedtuplewhere('Power', 'keyword op1 exponent')
    PowerShort = namedtuplewhere('PowerShort', 'op1 glyph exponent')
    BuildProblem = namedtuplewhere('BuildProblem', 'keyword statements')

    ModelStatements = namedtuplewhere('ModelStatements', 'statements')

    # Finite posets
    # finite_poset { a <= b }
    FinitePosetKeyword = namedtuplewhere('FinitePosetKeyword', 'keyword')
    FinitePosetElement = namedtuplewhere('FinitePosetElement', 'identifier')
    FinitePoset = namedtuplewhere('FinitePoset', 'keyword chains')

    # Single-element poset
    # S(tag)
    SingleElementPosetKeyword = namedtuplewhere('SingleElementPosetKeyword', 'keyword')
    SingleElementPosetTag = namedtuplewhere('SingleElementPosetTag', 'value')
    SingleElementPoset = namedtuplewhere('SingleElementPoset', 'keyword tag')

    # take( <>, <index>)
    TakeKeyword = namedtuplewhere('TakeKeyword', 'keyword')
    TupleIndexRes = namedtuplewhere('TupleIndexRes', 'keyword value index')
    TupleIndexFun = namedtuplewhere('TupleIndexFun', 'keyword value index')
    # take( <>, <label>)
#     TupleIndexLabel = namedtuplewhere('TupleIndexLabel', 'string')
#     TupleIndexLabelRes = namedtuplewhere('TupleIndexLabelRes', 'keyword value label')
#     TupleIndexLabelFun = namedtuplewhere('TupleIndexLabelFun', 'keyword value label')

    SpaceCustomValue = namedtuplewhere('SpaceCustomValue', 'space keyword custom_string')

    # solve( <0 g>, `model )
    SolveModelKeyword = namedtuplewhere('SolveModelKeyword', 'keyword')
    SolveModel = namedtuplewhere('SolveModel', 'keyword f model')

    # UpperSets(<space>)
    UpperSetsKeyword = namedtuplewhere('UpperSetsKeyword', 'keyword')
    MakeUpperSets = namedtuplewhere('MakeUpperSets', 'keyword space')
    # LowerSets(<space>)
    LowerSetsKeyword = namedtuplewhere('LowerSetsKeyword', 'keyword')
    MakeLowerSets = namedtuplewhere('MakeLowerSets', 'keyword space')

    # Uncertain(L, U)
    UncertainKeyword = namedtuplewhere('UncertainKeyword', 'keyword')
    UncertainRes = namedtuplewhere('UncertainRes', 'keyword lower upper')
    UncertainFun = namedtuplewhere('UncertainFun', 'keyword lower upper')

    # Interval(a, b)
    IntervalKeyword = namedtuplewhere('IntervalKeyword', 'keyword')
    SpaceInterval = namedtuplewhere('SpaceInterval', 'keyword a b')

    # product(a: x, b: X)
    ProductKeyword = namedtuplewhere('ProductKeyword', 'keyword')
    ProductWithLabelsLabel = namedtuplewhere('ProductWithLabelsLabel', 'label')
    ProductWithLabels = namedtuplewhere('ProductWithLabels', 'keyword entries')
    IndexLabel = namedtuplewhere('IndexLabel', 'label')
    ResourceLabelIndex = namedtuplewhere('ResourceLabelIndex', 'keyword rvalue label')
    FunctionLabelIndex = namedtuplewhere('FunctionLabelIndex', 'keyword fvalue label')

    # any-of({1,2})
    AnyOfKeyword = namedtuplewhere('AnyOfKeyword', 'keyword')
    AnyOfFun = namedtuplewhere('AnyOfFun', 'keyword value')
    AnyOfRes = namedtuplewhere('AnyOfRes', 'keyword value')

    # coproduct(space1, space2)
    SpaceCoproductKeyword = namedtuplewhere('SpaceCoproductKeyword', 'keyword')
    SpaceCoproduct = namedtuplewhere('SpaceCoproduct', 'keyword entries')


    # addmake(code module.func) mcdp { ... }
    # code = CodeSpecNoArgs = namedtuplewhere('CodeSpecNoArgs', 'keyword function')
    AddMakeKeyword = namedtuplewhere('AddMakeKeyword', 'keyword')
    AddMakeWhat = namedtuplewhere('AddMakeWhat', 'value')
    AddMake = namedtuplewhere('AddMake', 'keyword what code dp_rvalue')

    # approximating a resource
    ApproxKeyword = namedtuplewhere('ApproxKeyword', 'keyword')
    # approx(<rvalue>, 5g)
    ApproxStepRes = namedtuplewhere('ApproxRes', 'keyword rvalue step')

    # approxu(<rvalue>, 5g)
    ApproxUKeyword = namedtuplewhere('ApproxUKeyword', 'keyword')
    ApproxURes = namedtuplewhere('ApproxURes', 'keyword rvalue step')

    # from a import symbol1, symbol2
    # import symbol.a
#     ImportSymbolsKeywordFrom = namedtuplewhere('ImportSymbolsKeywordFrom', 'keyword')
#     ImportSymbolsKeywordImport = namedtuplewhere('ImportSymbolsKeywordImport', 'keyword')
#     ImportSymbolsLibname = namedtuplewhere('ImportSymbolsLibname', 'value')
#     ImportSymbolsSymbolname = namedtuplewhere('ImportSymbolsSymbolname', 'value')
#     ImportSymbols = namedtuplewhere('ImportSymbols', 'keyword1 libname keyword2 symbols')

    # assert_equal(v1, v2)
    # assert_leq(v1, v2)
    # assert_geq(v1, v2)
    # assert_lt(v1, v2)
    # assert_gt(v1, v2)
    # assert_nonempty(v1, v2)
    AssertEqualKeyword = namedtuplewhere('AssertEqualKeyword', 'keyword')
    AssertLEQKeyword = namedtuplewhere('AssertEqualKeyword', 'keyword')
    AssertGEQKeyword = namedtuplewhere('AssertEqualKeyword', 'keyword')
    AssertLTKeyword = namedtuplewhere('AssertEqualKeyword', 'keyword')
    AssertGTKeyword = namedtuplewhere('AssertEqualKeyword', 'keyword')
    AssertNonemptyKeyword = namedtuplewhere('AssertNonemptyKeyword', 'keyword')
    AssertEmptyKeyword = namedtuplewhere('AssertEmptyKeyword', 'keyword')

    AssertEqual = namedtuplewhere('AssertEqual', 'keyword v1 v2')
    AssertLEQ = namedtuplewhere('AssertLEQ', 'keyword v1 v2')
    AssertGEQ = namedtuplewhere('AssertGEQ', 'keyword v1 v2')
    AssertLT = namedtuplewhere('AssertLT', 'keyword v1 v2')
    AssertGT = namedtuplewhere('AssertGT', 'keyword v1 v2')
    AssertNonempty = namedtuplewhere('AssertNonempty', 'keyword value')
    AssertEmpty = namedtuplewhere('AssertEmpty', 'keyword value')


    ConstantMinusConstant = namedtuplewhere('ConstantMinusConstant', 'c1 c2')

    # ignore_resources(a, b) mcdp { }
    IgnoreResourcesKeyword = namedtuplewhere('IgnoreResourcesKeyword', 'keyword')
    IgnoreResources = namedtuplewhere('IgnoreResources', 'keyword rnames dp_rvalue')

