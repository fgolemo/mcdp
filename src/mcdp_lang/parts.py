# -*- coding: utf-8 -*-
from .namedtuple_tricks import namedtuplewhere


__all__ = [
    'CDPLanguage',
]


class CDPLanguage(object):

    # any type of the kind  <name>(op1, ..., opn) 
    # min(), max(), etc.
    ProcName = namedtuplewhere('ProcName', 'name')
    GenericOperationName = namedtuplewhere('GenericOperationName', 'value')
    GenericOperationRes = namedtuplewhere('GenericOperationRes', 'name ops')
    GenericOperationFun = namedtuplewhere('GenericOperationFun', 'name ops')
    
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
    
    EmptySetKeyword= namedtuplewhere('EmptySetKeyword', 'keyword')
    EmptySet = namedtuplewhere('EmptySet', 'keyword space')
    
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

    # implements `ndp
    ImplementsKeyword = namedtuplewhere('ImplementsKeyword', 'keyword')
    Implements = namedtuplewhere('Implements', 'keyword interface')
    
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

    ConstantDivision = namedtuplewhere('ConstantDivision', 'op1 bar op2')
    PlusN = namedtuplewhere('PlusN', 'ops')
    MultN = namedtuplewhere('MultN', 'ops')
    RValueMinusN = namedtuplewhere('RValueMinusN', 'ops')
    FValueMinusN = namedtuplewhere('FValueMinusN', 'ops')
    Divide = namedtuplewhere('Divide', 'ops')
    
#     Coproduct = namedtuplewhere('Coproduct', 'ops')

    # elements: all strings, coproducts
    CoproductWithNamesChooseKeyword = namedtuplewhere('CoproductWithNamesChooseKeyword', 'keyword')
    CoproductWithNamesName = namedtuplewhere('CoproductWithNamesName', 'value')
    CoproductWithNames = namedtuplewhere('CoproductWithNames', 'keyword elements')

    OpMax = namedtuplewhere('OpMax', 'keyword a b')
    OpMin = namedtuplewhere('OpMin', 'keyword a b')

    OpMaxF = namedtuplewhere('OpMaxF', 'keyword a b')
    OpMinF = namedtuplewhere('OpMinF', 'keyword a b')

    DPName = namedtuplewhere('DPName', 'value')
    DPTypeName = namedtuplewhere('DPTypeName', 'value')

    Resource = namedtuplewhere('Resource', 'dp s keyword')
    Function = namedtuplewhere('Function', 'dp s keyword')

    VariableRefNDPType = namedtuplewhere('VariableRefNDPType', 'name')

    # required rname 
    NewResource = namedtuplewhere('NewResource', 'keyword name')
    # provided fname
    NewFunction = namedtuplewhere('NewFunction', 'keyword name')
    Constraint = namedtuplewhere('Constraint', 'fvalue rvalue prep')
    ConstraintInvalidRR = namedtuplewhere('ConstraintInvalidRR', 'rvalue1 rvalue2 prep')
    ConstraintInvalidFF = namedtuplewhere('ConstraintInvalidFF', 'fvalue1 fvalue2 prep')
    ConstraintInvalidSwapped = namedtuplewhere('ConstraintInvalidSwapped', 'fvalue rvalue prep')

    NatConstant = namedtuplewhere('NatConstant', 's1 s2 value')  # value = int, >=0
    RcompConstant = namedtuplewhere('RcompConstant', 'value')  # value = int, >=0
    IntConstant = namedtuplewhere('IntConstant', 's1 s2 value')  # value = int

    LoadNDP = namedtuplewhere('LoadNDP', 'keyword load_arg')
    LoadConstant = namedtuplewhere('LoadConstant', 'keyword load_arg')
    LoadPoset = namedtuplewhere('LoadPoset', 'keyword load_arg')
    LoadTemplate = namedtuplewhere('LoadTemplate', 'keyword load_arg')

    # an incomplete model
    Ellipsis = namedtuplewhere('Ellipsis', 'token')

    ConstantKeyword = namedtuplewhere('ConstantKeyword', 'keyword')
    
    SetNameGenericVar = namedtuplewhere('SetNameGenericVar', 'value')
    SetNameNDPInstance = namedtuplewhere('SetNameNDPInstance', 'keyword name eq dp_rvalue')
    SetNameMCDPType = namedtuplewhere('SetNameMCDPType', 'keyword name eq right_side')
    SetNameConstant = namedtuplewhere('SetNameConstant', 'keyword name eq right_side')
    SetNameUncertainConstant =  namedtuplewhere('SetNameUncertainConstant', 'keyword name eq right_side')
    SetNameRValue = namedtuplewhere('SetNameRValue', 'name eq right_side')
    SetNameFValue = namedtuplewhere('SetNameFValue', 'name eq right_side')

    # set-of(<space>)
    PowerSetKeyword = namedtuplewhere('PowerSetKeyword', 'keyword')
    PowerSet = namedtuplewhere('PowerSet', 'symbol p1 space p2')

    # natural numbers
    Nat = namedtuplewhere('Nat', 'symbol')
    Int = namedtuplewhere('Int', 'symbol')
    Rcomp = namedtuplewhere('Rcomp', 'symbol')
    
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
    OpenBraceKeyword = namedtuplewhere('OpenBraceKeyword', 'glyph')
    CloseBraceKeyword = namedtuplewhere('CloseBraceKeyword', 'glyph')
    FromLibraryKeyword = namedtuplewhere('FromLibraryKeyword', 'keyword')
    OpKeyword = namedtuplewhere('OpKeyword', 'keyword')  
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

    CatalogueEntryConstant = namedtuplewhere('CatalogueEntryConstant', 'constant')
    CatalogueEntryConstantUncertain = namedtuplewhere('CatalogueEntryConstantUncertain', 'constant_uncertain')
    CatalogueFunc = namedtuplewhere('CatalogueFun', 'ops')
    CatalogueRes = namedtuplewhere('CatalogueRes', 'ops')
    CatalogueRowMapsfromto = namedtuplewhere('CatalogueRowMapsfromto', 
                                             'functions mapsfrom impname mapsto resources')
    
    
    Catalogue2 = namedtuplewhere('Catalogue2', 'keyword lbrace funres table rbrace')

    CatalogueRow3 = namedtuplewhere('CatalogueRow3', 'functions leftright resources')
    Catalogue3 = namedtuplewhere('Catalogue3', 'keyword lbrace funres table rbrace')

    ApproxDPModel = namedtuplewhere('ApproxDPModel', 'keyword name perc abs max_value dp')

    # just prepositions
    leq = namedtuplewhere('leq', 'glyph')
    LSQ = namedtuplewhere('LSQ', 'glyph')
    RSQ = namedtuplewhere('RSQ', 'glyph')
    product = namedtuplewhere('product', 'glyph')
    geq = namedtuplewhere('geq', 'glyph')
    eq = namedtuplewhere('eq', 'glyph')
    plus = namedtuplewhere('plus', 'glyph')
    minus = namedtuplewhere('minus', 'glyph')
    plus_or_minus = namedtuplewhere('plus_or_minus', 'glyph')
    exponent = namedtuplewhere('exponent', 'glyph')
    times = namedtuplewhere('times', 'glyph')
    bar = namedtuplewhere('bar', 'glyph')
    sum = namedtuplewhere('sum', 'glyph')
    coprod = namedtuplewhere('coprod', 'glyph')
    DotPrep = namedtuplewhere('DotPrep', 'glyph')
    comma = namedtuplewhere('comma', 'glyph')
    LBRACE  = namedtuplewhere('LBRACE', 'glyph')
    RBRACE  = namedtuplewhere('RBRACE', 'glyph') 
    LBRACKET  = namedtuplewhere('LBRACKET', 'glyph')
    RBRACKET  = namedtuplewhere('RBRACKET', 'glyph') 
    LPAR  = namedtuplewhere('LPAR', 'glyph') 
    RPAR  = namedtuplewhere('RPAR', 'glyph')
    percent = namedtuplewhere('percent', 'glyph')
    asterisk = namedtuplewhere('asterisk', 'glyph')
    
    MAPSFROM  = namedtuplewhere('MAPSFROM', 'glyph')
    MAPSTO  = namedtuplewhere('MAPSTO', 'glyph')
    LEFTRIGHTARROW = namedtuplewhere('LEFTRIGHTARROW', 'glyph')
    
    # function name
    FName = namedtuplewhere('FName', 'value')
    # resource name
    RName = namedtuplewhere('RName', 'value')
    # constant name
    CName = namedtuplewhere('CName', 'value')
    # variable Name (can be used as either f or r)
    VName = namedtuplewhere('VName', 'value')
    
    # This is used in parsing when we cannot decide what to do with it
    # Later, it should be changed in one of the following
    VariableRef = namedtuplewhere('VariableRef', 'name')
    
    DerivResourceName = namedtuplewhere('DerivResourceName', 'value')
    DerivResourceRef = namedtuplewhere('DerivResourceRef', 'drname')
    
    DerivFunctionName = namedtuplewhere('DerivFunctionName', 'value')
    DerivFunctionRef = namedtuplewhere('DerivFunctionRef', 'dfname')
    ConstantRef = namedtuplewhere('ConstantRef', 'cname')
    
    # This  
    ActualVarRef = namedtuplewhere('ActualVarRef', 'vname')
    
    Collection = namedtuplewhere('Collection', 'elements')

    # upperset {0g,1g}
    UpperSetFromCollectionKeyword = namedtuplewhere('UpperSetFromCollectionKeyword', 'keyword')
    UpperSetFromCollection = namedtuplewhere('UpperSetFromCollection', 'keyword value')
    # lowerset {0g}
    LowerSetFromCollectionKeyword = namedtuplewhere('LowerSetFromCollectionKeyword', 'keyword')
    LowerSetFromCollection = namedtuplewhere('LowerSetFromCollection', 'keyword value')

    
    
    VarStatement = namedtuplewhere('VarStatement', 'keyword vnames lbracket unit rbracket comment')
    VarStatementKeyword = namedtuplewhere('VarStatementKeyword', 'keyword')
    
    PosetName = namedtuplewhere('PosetName', 'value')
    PosetNameWithLibrary = namedtuplewhere('PosetNameWithLibrary', 'library glyph name')

    LoadDP = namedtuplewhere('LoadDP', 'keyword name')

    DPWrap = namedtuplewhere('DPWrap', 'token statements prep impl')

    # Code specs
    ArgName = namedtuplewhere('ArgName', 'value')  # value = string
    ArgValue = namedtuplewhere('ArgValue', 'python_value')  # int, float, string
    CodeSpec = namedtuplewhere('CodeSpec', 'keyword function arguments')
    CodeSpecNoArgs = namedtuplewhere('CodeSpecNoArgs', 'keyword function')

    SpaceProduct = namedtuplewhere('SpaceProduct', 'lpar ops rpar')
    InvMult = namedtuplewhere('InvMult', 'ops')
    InvPlus = namedtuplewhere('InvPlus', 'ops')
    
    # provides r [Nat] 'comment'
    FunStatement = namedtuplewhere('FunStatement', 'keyword fname lbracket unit rbracket comment')
    # requires r [Nat] 'comment'
    ResStatement = namedtuplewhere('ResStatement', 'keyword rname lbracket unit rbracket comment')
    
    # provides x, y, z [Nat] 'comment'
    FunShortcut5 = namedtuplewhere('FunShortcut5', 'keyword fnames lbracket unit rbracket comment')
    # requires x, y, z [Nat] 'comment'
    ResShortcut5 = namedtuplewhere('ResShortcut5', 'keyword rnames lbracket unit rbracket comment')
    
    # requires r1, r2 
    ResShortcut4 = namedtuplewhere('ResShortcut4', 'requires rnames')
    # provides f1, f2
    FunShortcut4 = namedtuplewhere('FunShortcut4', 'requires fnames')
    # provides r using <box>
    FunShortcut1 = namedtuplewhere('FunShortcut1', 'provides fname prep_using name')
    # requires f for <box>
    ResShortcut1 = namedtuplewhere('ResShortcut1', 'requires rname prep_for name')
    # provides f1,f2 using <box>
    FunShortcut1m = namedtuplewhere('FunShortcut1m', 'provides fnames prep_using name')
    # requires r1,r2 for <box>
    ResShortcut1m = namedtuplewhere('ResShortcut1m', 'requires rnames prep_for name')
    # provides f1 <= <expression>  (now '=')
    FunShortcut2 = namedtuplewhere('FunShortcut2', 'keyword fname prep lf')
    # requires r1 >= <expression>  (now '=')
    ResShortcut2 = namedtuplewhere('ResShortcut2', 'keyword rname prep rvalue')
    
    IntegerFraction = namedtuplewhere('IntegerFraction', 'num den')

    PowerKeyword = namedtuplewhere('PowerKeyword', 'keyword')
    Power = namedtuplewhere('Power', 'keyword op1 exponent')
    PowerShort = namedtuplewhere('PowerShort', 'op1 glyph exponent')
    BuildProblem = namedtuplewhere('BuildProblem', 'keyword lbrace comment statements rbrace')

    ModelStatements = namedtuplewhere('ModelStatements', 'statements')

    # Finite posets
    # finite_poset { a <= b }
    FinitePosetKeyword = namedtuplewhere('FinitePosetKeyword', 'keyword')
    FinitePosetElement = namedtuplewhere('FinitePosetElement', 'identifier')
    FinitePosetChainLEQ = namedtuplewhere('FinitePosetChainLEQ', 'ops')
    FinitePosetChainGEQ = namedtuplewhere('FinitePosetChainGEQ', 'ops')
    FinitePoset = namedtuplewhere('FinitePoset', 'keyword lbrace chains rbrace')

    AddBottomKeyword = namedtuplewhere('AddBottomKeyword', 'keyword')
    AddBottom = namedtuplewhere('AddBottom', 'keyword poset')
    
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
    # solve_f( )
    SolveModelKeyword = namedtuplewhere('SolveModelKeyword', 'keyword')
    SolveModel = namedtuplewhere('SolveModel', 'keyword f model')

    # solve_r( <0 g>, `model )
    SolveRModelKeyword = namedtuplewhere('SolveRModelKeyword', 'keyword')
    SolveRModel = namedtuplewhere('SolveRModel', 'keyword r model')

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
    # unused 
    UncertainConstant = namedtuplewhere('UncertainConstant', 'keyword lower upper')

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

    # ignore_resources(a, b) mcdp { }
    IgnoreResourcesKeyword = namedtuplewhere('IgnoreResourcesKeyword', 'keyword')
    IgnoreResources = namedtuplewhere('IgnoreResources', 'keyword rnames dp_rvalue')

    # placeholders to use in documentation
    # [[label]]
    
    Placeholder = namedtuplewhere('Placeholder', 'label')
    
    Placeholder_ndp = Placeholder # namedtuplewhere('Placeholder_ndp', 'label')
    Placeholder_poset = Placeholder # namedtuplewhere('Placeholder_poset', 'label')
    Placeholder_primitivedp = Placeholder # namedtuplewhere('Placeholder_primitivedp', 'label')
    Placeholder_constant = Placeholder # namedtuplewhere('Placeholder_constant', 'label')
    Placeholder_dpname = Placeholder # namedtuplewhere('Placeholder_constant', 'label')
    Placeholder_rname = Placeholder # namedtuplewhere('Placeholder_constant', 'label')
    Placeholder_fname = Placeholder # namedtuplewhere('Placeholder_constant', 'label')
    Placeholder_libname = Placeholder # namedtuplewhere('Placeholder_constant', 'label')
    Placeholder_template = Placeholder # namedtuplewhere('Placeholder_template', 'label')
    Placeholder_collection = Placeholder # namedtuplewhere('Placeholder_collection', 'label')
    Placeholder_fvalue = Placeholder # namedtuplewhere('Placeholder_fvalue', 'label')
    Placeholder_rvalue = Placeholder # namedtuplewhere('Placeholder_rvalue', 'label')
    Placeholder_integer = Placeholder
    Placeholder_nonneg_integer = Placeholder
    Placeholder_integer_or_float = Placeholder
    Placeholder_index_label = Placeholder
    
    # deriv(name, <mcdp>) 
    DerivKeyword = namedtuplewhere('DerivKeyword', 'keyword')
    Deriv = namedtuplewhere('Deriv', 'keyword dpname ndp')
    
    # eversion(name, <mcdp>) 
    EversionKeyword = namedtuplewhere('EversionKeyword', 'keyword')
    Eversion = namedtuplewhere('Eversion', 'keyword dpname ndp')
    
    CommentStringSimple = namedtuplewhere('CommentStringSimple', 'value')
    CommentStringTriple = namedtuplewhere('CommentStringTriple', 'value')
    CommentModel = namedtuplewhere('CommentModel', 'comment_string')
    CommentFun = namedtuplewhere('CommentFun', 'comment_string')
    CommentCon = namedtuplewhere('CommentCon', 'comment_string')
    CommentRes = namedtuplewhere('CommentRes', 'comment_string')
    CommentVar = namedtuplewhere('CommentVar', 'comment_string')
    
    SpecialConstant = namedtuplewhere('SpecialConstant', 'constant_name')
    
    BetweenKeyword = namedtuplewhere('BetweenKeyword', 'keyword')
    BetweenAndKeyword = namedtuplewhere('BetweenAndKeyword', 'keyword')
    
    ConstantBetween = namedtuplewhere('ConstantBetween', 'between lower and_keyword upper')
    RValueBetween = namedtuplewhere('RValueBetween', 'between lower and_keyword upper')
    FValueBetween = namedtuplewhere('FValueBetween', 'between lower and_keyword upper')
    
    ConstantPlusOrMinus = namedtuplewhere('ConstantPlusOrMinus', 'median pm extent')
    RValuePlusOrMinus = namedtuplewhere('RValuePlusOrMinus', 'median pm extent')
    FValuePlusOrMinus = namedtuplewhere('FValuePlusOrMinus', 'median pm extent')
    
    ConstantPlusOrMinusPercent = namedtuplewhere('ConstantPlusOrMinusPercent', 'median pm perc percent')
    RValuePlusOrMinusPercent = namedtuplewhere('RValuePlusOrMinusPercent', 'median pm perc percent')
    FValuePlusOrMinusPercent = namedtuplewhere('FValuePlusOrMinusPercent', 'median pm perc percent')
    
    SumResources = namedtuplewhere('SumResources', 'sum rname required_by asterisk')
    SumFunctions = namedtuplewhere('SumFunctions', 'sum fname provided_by asterisk')
    

    