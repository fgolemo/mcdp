# -*- coding: utf-8 -*-
from .parse_actions import *  # @UnusedWildImport
from mocdp.lang.helpers import square
from mocdp.posets import R_dimensionless
from pyparsing import (
    CaselessLiteral, Combine, Forward, Group, Literal, NotAny, OneOrMore,
    Optional, Or, ParserElement, Suppress, Word, ZeroOrMore, alphanums, alphas,
    nums, oneOf, opAssoc, operatorPrecedence)
import math

ParserElement.enablePackrat()

def sp(a, b):
    spa(a, b)
    return a


def VariableRef_make(t):
    name = t[0]
    if not isinstance(name, str):
        raise ValueError(t)
    res = CDP.VariableRef(name)
    return res

class Syntax():
    keywords = [
        'load', 'compact', 'required', 'provides', 'abstract',
        'dp', 'cdp', 'mcdp', 'template', 'sub', 'for', 'instance',
        'provided', 'requires', 'implemented-by', 'using', 'by',
        'catalogue', 'set-of', 'mcdp-type', 'dptype', 'instance',
    ]

    # shortcuts
    S = Suppress
    L = Literal
    O = Optional

    PRODUCT = sp(L('x') | L('×'), lambda t: CDP.product(t[0]))
    COMMA = sp(L(','), lambda t: CDP.comma(t[0]))
    PROVIDES = sp(L('provides'), lambda t: CDP.ProvideKeyword(t[0]))
    REQUIRES = sp(L('requires'), lambda t: CDP.RequireKeyword(t[0]))
    USING = sp(L('using'), lambda t: CDP.UsingKeyword(t[0]))
    FOR = sp(L('for'), lambda t: CDP.ForKeyword(t[0]))
    # load battery
    LOAD = sp(L('load'), lambda t: CDP.LoadKeyword(t[0]))
    SUB = sp(L('sub'), lambda t: CDP.SubKeyword(t[0]))
    MCDPTYPE = sp(L('mcdp-type') ^ L('mcdp') ^ L('dptype'), lambda t: CDP.MCDPTypeKeyword(t[0]))

    INSTANCE = sp(Combine(L('instance') + O(L('of'))), lambda t: CDP.InstanceKeyword(t[0]))

    # 'MATHEMATICAL LEFT ANGLE BRACKET' (U+27E8) ⟨
    # 'MATHEMATICAL RIGHT ANGLE BRACKET'   ⟩

    OPEN_BRACE = sp(L('<') ^ L('⟨'), lambda t: CDP.OpenBraceKeyword(t[0]))
    CLOSE_BRACE = sp(L('>') ^ L('⟩'), lambda t: CDP.CloseBraceKeyword(t[0]))
    REQUIRED_BY = sp(L('required') - L('by'),
                    lambda _: CDP.RequiredByKeyword('required by'))

    PROVIDED_BY = sp(L('provided') - L('by'),
                    lambda _: CDP.ProvidedByKeyword('provided by'))
    GEQ = sp(L('>=') | L('≥') | L('⊇') | L('≽') | L('⊒'), lambda t: CDP.geq(t[0]))
    LEQ = sp(L('<=') | L('≤') | L('⊆') | L('≼') | L('⊑'), lambda t: CDP.leq(t[0]))

    EQ = sp(L('='), lambda t: CDP.eq(t[0]))
    DOT = sp(L('.'), lambda t: CDP.DotPrep(t[0]))
    PLUS = sp(L('+'), lambda t: CDP.plus(t[0]))
    TIMES = sp(L('*'), lambda t: CDP.times(t[0]))
    BAR = sp(L('/'), lambda t: CDP.bar(t[0]))
    DPTOKEN = sp(L('dp'), lambda t: CDP.DPWrapToken(t[0]))
    IMPLEMENTEDBY = sp(L('implemented-by'), lambda t: CDP.ImplementedbyKeyword(t[0]))
    CDPTOKEN = sp(L('cdp') | L('mcdp'), lambda t: CDP.MCDPKeyword(t[0]))

    FROMCATALOGUE = sp(L('catalogue'), lambda t:CDP.FromCatalogueKeyword(t[0]))
    COMPACT = sp(L('compact'), lambda t: CDP.CompactKeyword(t[0]))
    TEMPLATE = sp(L('template'), lambda t: CDP.TemplateKeyword(t[0]))
    ABSTRACT = sp(L('abstract'), lambda t: CDP.AbstractKeyword(t[0]))
    COPROD = sp(L('^'), lambda t: CDP.coprod(t[0]))
    CODE = sp(L('code'), lambda t: CDP.CodeKeyword(t[0]))

    # "call"
    C = lambda x, b: x.setResultsName(b)

    # optional whitespace
    ow = S(ZeroOrMore(L(' '))) 
    # identifier
    idn = (NotAny(oneOf(keywords)) + Combine(oneOf(list(alphas)) + Optional(Word('_' + alphanums)))).setResultsName('idn')
 
    disallowed = oneOf(keywords + ['x'])
    unit_base = NotAny(oneOf(keywords + ['x'])) + Word(alphas + '$')

    unit_power = L('^') + Word(nums)
    unit_simple = unit_base + O(unit_power)
    unit_connector = L('/') | L('*')
 
    pint_unit = sp((unit_simple + ZeroOrMore(unit_connector + unit_simple)),
                   parse_pint_unit)

    space_expr = Forward() 

    power_set_expr = sp((L('℘') | L('set-of')) - L('(') + space_expr + L(')'),
                        lambda t: CDP.PowerSet(t[0], t[1],
                                               t[2], t[3]))
#
#     power_set_expr2 = sp((Combine(L('set') + L('of'))) + space_expr ,
#                         lambda t: CDP.PowerSet(t[0], t[1],
#                                                t[2], t[3]))

    space_operand = (pint_unit ^ power_set_expr)

    space_expr << operatorPrecedence(space_operand, [
                (PRODUCT, 2, opAssoc.LEFT, space_product_parse_action),
    ])

    # numbers
    number = Word(nums)
    point = Literal('.')
    e = CaselessLiteral('E')
    plusorminus = Literal('+') | Literal('-')
    integer = Combine(O(plusorminus) + number)
    # Note that '42' is not a valid float...
    floatnumber = (Combine(integer + point + O(number) + O(e + integer)) |
                    Combine(integer + e + integer))

    spa(integer, lambda t: int(t[0]))
    spa(floatnumber, lambda t: float(t[0]))

    integer_or_float = sp(integer ^ floatnumber,
                          lambda t: CDP.ValueExpr(t[0]))

    unitst = S(L('[')) + C(space_expr, 'unit') + S(L(']'))

    fname = sp(idn.copy(), lambda t: CDP.FName(t[0]))
    rname = sp(idn.copy(), lambda t: CDP.RName(t[0]))

    fun_statement = sp(PROVIDES + C(fname, 'fname') + unitst,
                       lambda t: CDP.FunStatement(t[0], t[1], t[2]))

    res_statement = sp(REQUIRES + C(rname, 'rname') + unitst,
                       lambda t: CDP.ResStatement(t[0], t[1], t[2]))

    number_with_unit1 = sp(integer_or_float + unitst,
                           lambda t: CDP.SimpleValue(t[0], t[1]))

    dimensionless = sp(L('[') + L(']'), lambda _: CDP.Unit(R_dimensionless))
    number_with_unit2 = sp(integer_or_float + dimensionless,
                           lambda t: CDP.SimpleValue(t[0], t[1]))
    number_with_unit3 = sp(integer_or_float + space_expr,
                           lambda t: CDP.SimpleValue(t[0], t[1]))
    number_with_unit = number_with_unit1 ^ number_with_unit2 ^ number_with_unit3

    # TODO: change
    ndpname = sp(idn.copy(), lambda t: CDP.FuncName(t[0]))  # XXX

    load_expr = sp(LOAD - ndpname, lambda t: CDP.LoadCommand(t[0], t[1]))

    dp_rvalue = Forward()
    # <dpname> = ...

    dpname = sp(idn.copy(), lambda t: CDP.DPName(t[0]))
    dptypename = sp(idn.copy(), lambda t: CDP.DPTypeName(t[0]))

    dpinstance_from_type = sp((INSTANCE + dp_rvalue) ^ (INSTANCE + L('(') + dp_rvalue + L(")")),
                              lambda t: CDP.DPInstance(t[0], t[1]))

    dpinstance_expr = (dpinstance_from_type ^ dp_rvalue)

    setsub_expr = sp(SUB - dpname - S(L('=')) - dpinstance_expr,
                     lambda t: CDP.SetName(t[0], t[1], t[2]))

    setmcdptype_expr = sp(MCDPTYPE - dptypename - L('=') - dp_rvalue,
                     lambda t: CDP.SetMCDPType(t[0], t[1], t[2], t[3]))

    rvalue = Forward()
    fvalue = Forward()

    setname_rightside = rvalue ^ dp_rvalue
 
    setname_generic_var = sp(idn.copy(),
                              lambda t: CDP.SetNameGenericVar(t[0]))

    setname_generic = sp(setname_generic_var + EQ + setname_rightside,
                         lambda t: CDP.SetNameGeneric(t[0], t[1], t[2]))

    variable_ref = sp(idn.copy(), VariableRef_make)
    dp_variable_ref = sp(idn.copy(), lambda t: CDP.DPVariableRef(t[0]))
    
    constant_value = Forward()
    tuple_of_constants = sp(OPEN_BRACE + constant_value +
                            ZeroOrMore(COMMA + constant_value) + CLOSE_BRACE,
                            lambda t: CDP.MakeTupleConstants(t[0], make_list(list(t)[1:-1]), t[-1]))
    
    collection_of_constants = sp(S(L('{')) + constant_value +
                                 ZeroOrMore(COMMA + constant_value) + S(L('}')),
                                 lambda t: CDP.Collection(make_list(list(t))))

    constant_value << (number_with_unit ^ variable_ref ^ collection_of_constants ^ tuple_of_constants)

    rvalue_resource_simple = sp(dpname + DOT - rname,
                                lambda t: CDP.Resource(s=t[2], keyword=t[1], dp=t[0]))
                     
    rvalue_resource_fancy = sp(rname + REQUIRED_BY - dpname,
                               lambda t: CDP.Resource(s=t[0], keyword=t[1], dp=t[2]))

    rvalue_resource = rvalue_resource_simple ^ rvalue_resource_fancy

    rvalue_new_function = sp(idn.copy(), VariableRef_make)

    lf_new_resource = sp(idn.copy(),
                         lambda t: CDP.NewResource(t[0]))

    lf_new_limit = sp(C(Group(number_with_unit), 'limit'),
                      lambda t: CDP.NewLimit(t['limit'][0]))

    unary = {
        'sqrt': lambda op1: CDP.GenericNonlinearity(math.sqrt, op1, lambda F: F),
        'square': lambda op1: CDP.GenericNonlinearity(square, op1, lambda F: F),
    }

    unary_op = Or([L(x) for x in unary])
    unary_expr = sp((C(unary_op, 'opname') - S(L('('))
                    + C(rvalue, 'op1')) - S(L(')')),
                    lambda t: Syntax.unary[t['opname']](t['op1']))

    binary = {
        'max': CDP.OpMax,
        'min': CDP.OpMin,
    }

    opname = sp(Or([L(x) for x in binary]), lambda t: CDP.OpKeyword(t[0]))

    binary_expr = sp((opname - S(L('(')) +
                    C(rvalue, 'op1') - S(L(','))
                    + C(rvalue, 'op2')) - S(L(')')) ,
                   lambda t: Syntax.binary[t[0].keyword](a=t['op1'], b=t['op2'], keyword=t[0]))

    operand = rvalue_new_function ^ rvalue_resource ^ binary_expr ^ unary_expr ^ constant_value


    simple = sp(dpname + DOT - fname,
               lambda t: CDP.Function(dp=t[0], s=t[2], keyword=t[1]))

    fancy = sp(fname + PROVIDED_BY - dpname,
                lambda t: CDP.Function(dp=t[2], s=t[0], keyword=t[1]))

    fvalue_operand = lf_new_limit ^ simple ^ fancy ^ lf_new_resource ^ (S(L('(')) - (lf_new_limit ^ simple ^ fancy ^ lf_new_resource) - S(L(')')))

    # Fractions

    integer_fraction = sp(C(integer, 'num') + S(L('/')) + C(integer, 'den'),
                          lambda t: CDP.IntegerFraction(t['num'], t['den']))

    power_expr = sp((S(L('pow')) - S(L('(')) + C(rvalue, 'op1') - S(L(','))
                    + C(integer_fraction, 'exponent')) - S(L(')')),
                    power_expr_parse)

    constraint_expr = sp(C(fvalue, 'lf') + GEQ - C(rvalue, 'rvalue'),
                         lambda t: CDP.Constraint(function=t['lf'],
                                                  rvalue=t['rvalue'], prep=t[1]))

    constraint_expr2 = sp(C(rvalue, 'rvalue') + LEQ - C(fvalue, 'lf'),
                          lambda t: CDP.Constraint(function=t['lf'],
                                                   rvalue=t['rvalue'], prep=t[1]))

    fun_shortcut1 = sp(PROVIDES + fname + USING + dpname,
                       lambda t: CDP.FunShortcut1(provides=t[0],
                                                  fname=t[1],
                                                  prep_using=t[2],
                                                  name=t[3]))

    res_shortcut1 = sp(REQUIRES + rname + FOR + dpname,
                       lambda t: CDP.ResShortcut1(t[0], t[1], t[2], t[3]))

    fun_shortcut2 = sp(PROVIDES + fname + LEQ - fvalue,
                       lambda t: CDP.FunShortcut2(t[0], t[1], t[2], t[3]))

    res_shortcut2 = sp(REQUIRES + rname + GEQ - rvalue,
                       lambda t: CDP.ResShortcut2(t[0], t[1], t[2], t[3]))

    fun_shortcut3 = sp(PROVIDES + C(Group(fname + OneOrMore(S(L(',')) + fname)), 'fnames')
                       + USING + dpname,
                       lambda t: funshortcut1m(provides=t[0],
                             fnames=make_list(list(t['fnames'])),
                             prep_using=t[2],
                             name=t[3]))

    res_shortcut3 = sp(REQUIRES + C(Group(rname + OneOrMore(S(L(',')) + rname)), 'rnames')
                       + FOR + dpname,
                       lambda t: resshortcut1m(requires=t[0],
                             rnames=make_list(list(t['rnames'])),
                             prep_for=t[2],
                             name=t[3]))

    line_expr = (constraint_expr ^ constraint_expr2 ^
                 (setname_generic ^ setsub_expr ^ setmcdptype_expr)
                 ^ fun_statement ^ res_statement ^ fun_shortcut1 ^ fun_shortcut2
                 ^ res_shortcut1 ^ res_shortcut2 ^ res_shortcut3 ^ fun_shortcut3)

    dp_model_statements = sp(ZeroOrMore(S(ow) + line_expr),
                             lambda t: make_list(list(t)))

    dp_model = sp(CDPTOKEN - S(L('{')) - dp_model_statements - S(L('}')),
                  lambda t: CDP.BuildProblem(keyword=t[0], statements=t[1]))

    funcname = sp(Combine(idn + ZeroOrMore(L('.') - idn)), lambda t: CDP.FuncName(t[0]))

    code_spec = sp(CODE - funcname,
                   lambda t: CDP.PDPCodeSpec(keyword=t[0], function=t[1], arguments={}))

    pdpname = sp(idn.copy(), lambda t: CDP.FuncName(t[0]))
    load_pdp = sp(LOAD - pdpname, lambda t: CDP.LoadDP(t[0], t[1]))

    pdp_rvalue = load_pdp ^ code_spec

    simple_dp_model_stats = sp(ZeroOrMore(S(ow) + fun_statement ^ res_statement),
                               lambda t: make_list(list(t)))

    simple_dp_model = sp(DPTOKEN -
                         S(L('{')) -
                         simple_dp_model_stats -
                         IMPLEMENTEDBY -
                         pdp_rvalue -
                         S(L('}')),
                         lambda t: CDP.DPWrap(token=t[0], statements=t[1],
                                              prep=t[2], impl=t[3]))

    entry = rvalue
    imp_name = sp(idn.copy(), lambda t: CDP.ImpName(t[0]))
    col_separator = L('|') ^ L('│')  # box drawing
    catalogue_row = sp(imp_name +  # S(L('[')) + entry +
                       ZeroOrMore(S(col_separator) + entry),  # + S(L(']')),
                       lambda t: make_list(list(t)))

    catalogue_table = sp(OneOrMore(catalogue_row),
                         lambda t: CDP.CatalogueTable(make_list(list(t))))

    catalogue_dp = sp(FROMCATALOGUE -
                      S(L('{')) -
                      simple_dp_model_stats -
                      catalogue_table -
                      S(L('}')),
                      lambda t: CDP.FromCatalogue(t[0], t[1], t[2]))

    abstract_expr = sp(ABSTRACT - dp_rvalue, 
                       lambda t: CDP.AbstractAway(t[0], t[1]))
    
    compact_expr = sp(COMPACT - dp_rvalue,
                       lambda t: CDP.Compact(t[0], t[1]))

    template_expr = sp(TEMPLATE - dp_rvalue,
                       lambda t: CDP.MakeTemplate(t[0], t[1]))

    dp_operand = (load_expr | simple_dp_model | dp_model | abstract_expr |
                  template_expr | compact_expr | dp_variable_ref | catalogue_dp)

    dp_rvalue << operatorPrecedence(dp_operand, [
    #     ('-', 1, opAssoc.RIGHT, Unary.parse_action),
        (COPROD, 2, opAssoc.LEFT, coprod_parse_action),
    ])

    rvalue << operatorPrecedence(operand, [
        (TIMES, 2, opAssoc.LEFT, mult_parse_action),
        (BAR, 2, opAssoc.LEFT, divide_parse_action),
        (PLUS, 2, opAssoc.LEFT, plus_parse_action),
    ])

    fvalue << operatorPrecedence(fvalue_operand, [
        ('*', 2, opAssoc.LEFT, mult_inv_parse_action),
        ('+', 2, opAssoc.LEFT, plus_inv_parse_action),
    ])

#     divide_constants = sp(constant_value + BAR + constant_value,
#                               lambda t: CDP.Divide(make_list([t[0], t[1], t[2]])))

