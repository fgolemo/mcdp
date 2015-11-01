# -*- coding: utf-8 -*-
from .parse_actions import *  # @UnusedWildImport
from mocdp.lang.helpers import square
from mocdp.posets import make_rcompunit
from mocdp.posets.rcomp_units import R_dimensionless
from pyparsing import (
    CaselessLiteral, Combine, Forward, Group, Literal, NotAny, OneOrMore,
    Optional, Or, ParserElement, Suppress, Word, ZeroOrMore, alphanums, alphas,
    nums, oneOf, opAssoc, operatorPrecedence, nestedExpr)
import math

ParserElement.enablePackrat()

def sp(a, b):
    spa(a, b)
    return a


class Syntax():
    keywords = ['load', 'compact', 'required', 'provides', 'abstract',
                      'dp', 'cdp', 'mcdp', 'template', 'sub', 'for',
                      'provided', 'requires', 'implemented-by', 'using', 'by']
    reserved = oneOf(keywords)

    # ParserElement.setDefaultWhitespaceChars('')

    # shortcuts
    S = Suppress
    L = Literal
    O = Optional
    # "call"
    C = lambda x, b: x.setResultsName(b)

    # optional whitespace
    ow = S(ZeroOrMore(L(' ')))
    # EOL = S(LineEnd())
    # line = SkipTo(LineEnd(), failOn=LineStart() + LineEnd())

    # identifier
    idn = (Combine(oneOf(list(alphas)) + Optional(Word('_' + alphanums)))).setResultsName('idn')

    unit_base = Word(alphas + '$' + ' ')
    unit_power = L('^') + O(L(' ')) + Word(nums)
    unit_simple = unit_base + O(unit_power)
    unit_connector = L('/') | L('*')

    unit_expr = Combine(unit_simple + ZeroOrMore(unit_connector + unit_simple))


    spa(unit_expr, lambda t: CDP.Unit(make_rcompunit(t[0])))

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

    unitst = S(L('[')) + C(unit_expr, 'unit') + S(L(']'))

    PROVIDES = sp(L('provides'), lambda t: CDP.ProvideKeyword(t[0]))
    REQUIRES = sp(L('requires'), lambda t: CDP.RequireKeyword(t[0]))
    
    USING = sp(L('using'), lambda t: CDP.UsingKeyword(t[0]))
    FOR = sp(L('for'), lambda t: CDP.ForKeyword(t[0]))

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
    number_with_unit3 = sp(integer_or_float + unit_expr,
                           lambda t: CDP.SimpleValue(t[0], t[1]))
    number_with_unit = number_with_unit1 ^ number_with_unit2 ^ number_with_unit3

    # load battery
    LOAD = sp(L('load'), lambda t: CDP.LoadKeyword(t[0]))

    # TODO: change
    ndpname = sp(idn.copy(), lambda t: CDP.FuncName(t[0]))  # XXX

    load_expr = sp(LOAD - ndpname, lambda t: CDP.LoadCommand(t[0], t[1]))

    dp_rvalue = Forward()
    # <dpname> = ...

    SUB = sp(L('sub'), lambda t: CDP.SubKeyword(t[0]))

    dpname = sp(idn.copy(), lambda t: CDP.DPName(t[0]))

    setsub_expr = sp(SUB - dpname - S(L('=')) - C(dp_rvalue, 'dp_rvalue'),
                     lambda t: CDP.SetName(t[0], t[1], t[2]))


    rvalue = Forward()
    fvalue = Forward()

    setname_rightside = rvalue ^ dp_rvalue

    EQ = sp(L('='), lambda t: CDP.eq(t[0]))
    DOT = sp(L('.'), lambda t: CDP.DotPrep(t[0]))
    PLUS = sp(L('+'), lambda t: CDP.plus(t[0]))
    TIMES = sp(L('*'), lambda t: CDP.times(t[0]))
    BAR = sp(L('/'), lambda t: CDP.bar(t[0]))
 
    setname_generic_var = sp(idn.copy(),
                              lambda t: CDP.SetNameGenericVar(t[0]))

    setname_generic = sp(setname_generic_var + EQ + setname_rightside,
                         lambda t: CDP.SetNameGeneric(t[0], t[1], t[2]))


    variable_ref = sp(NotAny(reserved) + C(idn.copy(), 'variable_ref_name'),
                      lambda t: CDP.VariableRef(t['variable_ref_name']))

    constant_value = Forward()
    

#     par = nestedExpr(opener='(', closer=')', content=constant_value)

#     par = S(L("(")) + number_with_unit + S(L(")"))
    constant_value << number_with_unit ^ variable_ref

    # ^ divide_constants)




    rvalue_resource_simple = sp(dpname + DOT - rname,
                                lambda t: CDP.Resource(s=t[2], keyword=t[1], dp=t[0]))

    REQUIRED_BY = sp(L('required') - L('by'),
                    lambda _: CDP.RequiredByKeyword('required by'))

    PROVIDED_BY = sp(L('provided') - L('by'),
                    lambda _: CDP.ProvidedByKeyword('provided by'))

                     
    rvalue_resource_fancy = sp(rname + REQUIRED_BY - dpname,
                               lambda t: CDP.Resource(s=t[0], keyword=t[1], dp=t[2]))

    rvalue_resource = rvalue_resource_simple ^ rvalue_resource_fancy

    rvalue_new_function = C(idn.copy(), 'new_function')
    spa(rvalue_new_function, lambda t: CDP.VariableRef(t['new_function']))

    lf_new_resource = C(idn.copy(), 'new_resource')
    spa(lf_new_resource, lambda t: CDP.NewResource(t['new_resource']))

    lf_new_limit = C(Group(number_with_unit), 'limit')
    spa(lf_new_limit, lambda t: CDP.NewLimit(t['limit'][0]))

    unary = {
        'sqrt': lambda op1: CDP.GenericNonlinearity(math.sqrt, op1, lambda F: F),
        'square': lambda op1: CDP.GenericNonlinearity(square, op1, lambda F: F),
    }
    unary_op = Or([L(x) for x in unary])
    unary_expr = (C(unary_op, 'opname') - S(L('('))
                    + C(rvalue, 'op1')) - S(L(')'))

    spa(unary_expr, lambda t: Syntax.unary[t['opname']](t['op1']))


    binary = {
        'max': CDP.OpMax,
        'min': CDP.OpMin,
    }

    opname = sp(Or([L(x) for x in binary]), lambda t: CDP.OpKeyword(t[0]))

    binary_expr = (opname - S(L('(')) +
                    C(rvalue, 'op1') - S(L(','))
                    + C(rvalue, 'op2')) - S(L(')'))


    spa(binary_expr, lambda t: Syntax.binary[t[0].keyword](a=t['op1'], b=t['op2'], keyword=t[0]))

    operand = rvalue_new_function ^ rvalue_resource ^ binary_expr ^ unary_expr ^ constant_value


    simple = sp(dpname + DOT - fname,
               lambda t: CDP.Function(dp=t[0], s=t[2], keyword=t[1]))

    fancy = sp(fname + PROVIDED_BY - dpname,
                lambda t: CDP.Function(dp=t[2], s=t[0], keyword=t[1]))

    fvalue_operand = lf_new_limit ^ simple ^ fancy ^ lf_new_resource ^ (S(L('(')) - (lf_new_limit ^ simple ^ fancy ^ lf_new_resource) - S(L(')')))

    # Fractions

    integer_fraction = sp(C(integer, 'num') + S(L('/')) + C(integer, 'den'),
                          lambda t: CDP.IntegerFraction(t['num'], t['den']))


    power_expr = sp((S(L('pow')) - S(L('(')) +
                    C(rvalue, 'op1') - S(L(','))
                    + C(integer_fraction, 'exponent')) - S(L(')')),
                    power_expr_parse)


    GEQ = sp(L('>='), lambda t: CDP.geq(t[0]))
    LEQ = sp(L('<='), lambda t: CDP.leq(t[0]))

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


    line_expr = (load_expr ^ constraint_expr ^ constraint_expr2 ^
                 (setname_generic ^ setsub_expr)
                 ^ fun_statement ^ res_statement ^ fun_shortcut1 ^ fun_shortcut2
                 ^ res_shortcut1 ^ res_shortcut2 ^ res_shortcut3 ^ fun_shortcut3)


    CDPTOKEN = sp(L('cdp') | L('mcdp'), lambda t: CDP.MCDPKeyword(t[0]))

    dp_model_statements = sp(ZeroOrMore(S(ow) + line_expr),
                             lambda t: make_list(list(t)))

    dp_model = sp(CDPTOKEN - S(L('{')) - dp_model_statements - S(L('}')),
                  lambda t: CDP.BuildProblem(keyword=t[0], statements=t[1]))

    funcname = sp(Combine(idn + ZeroOrMore(L('.') - idn)), lambda t: CDP.FuncName(t[0]))
    CODE = sp(L('code'), lambda t: CDP.CodeKeyword(t[0]))

    code_spec = sp(CODE - funcname,
                   lambda t: CDP.PDPCodeSpec(keyword=t[0], function=t[1], arguments={}))

    pdpname = sp(idn.copy(), lambda t: CDP.FuncName(t[0]))
    load_pdp = sp(LOAD - pdpname,
                  lambda t: CDP.LoadDP(t[0], t[1]))

    pdp_rvalue = load_pdp ^ code_spec

    DPTOKEN = sp(L('dp'), lambda t: CDP.DPWrapToken(t[0]))

    simple_dp_model_stats = sp(ZeroOrMore(S(ow) + fun_statement ^ res_statement),
                               lambda t: make_list(list(t)))

    IMPLEMENTEDBY = sp(L('implemented-by'), lambda t: CDP.ImplementedbyKeyword(t[0]))

    simple_dp_model = sp(DPTOKEN - S(L('{')) -
                       simple_dp_model_stats -
                       IMPLEMENTEDBY - pdp_rvalue -
                       S(L('}')),
                         lambda t: CDP.DPWrap(token=t[0], statements=t[1], prep=t[2], impl=t[3]))


    COMPACT = sp(L('compact'), lambda t: CDP.CompactKeyword(t[0]))
    TEMPLATE = sp(L('template'), lambda t: CDP.TemplateKeyword(t[0]))
    ABSTRACT = sp(L('abstract'), lambda t: CDP.AbstractKeyword(t[0]))
    COPROD = sp(L('^'), lambda t: CDP.coprod(t[0]))

    abstract_expr = sp(ABSTRACT - dp_rvalue, 
                       lambda t: CDP.AbstractAway(t[0], t[1]))

    
    compact_expr = sp(COMPACT - dp_rvalue,
                       lambda t: CDP.Compact(t[0], t[1]))

    template_expr = sp(TEMPLATE - dp_rvalue,
                       lambda t: CDP.MakeTemplate(t[0], t[1]))

    dp_operand = (load_expr | simple_dp_model | dp_model | abstract_expr |
                  template_expr | compact_expr | variable_ref)

    dp_rvalue << operatorPrecedence(dp_operand, [
    #     ('-', 1, opAssoc.RIGHT, Unary.parse_action),
        (COPROD, 2, opAssoc.LEFT, coprod_parse_action),
    ])

    rvalue << operatorPrecedence(operand, [
    #     ('-', 1, opAssoc.RIGHT, Unary.parse_action),
        (TIMES, 2, opAssoc.LEFT, mult_parse_action),
        (BAR, 2, opAssoc.LEFT, divide_parse_action),
    #     ('-', 2, opAssoc.LEFT, Binary.parse_action),
        (PLUS, 2, opAssoc.LEFT, plus_parse_action),
    ])


    fvalue << operatorPrecedence(fvalue_operand, [
    #     ('-', 1, opAssoc.RIGHT, Unary.parse_action),
        ('*', 2, opAssoc.LEFT, mult_inv_parse_action),
        ('+', 2, opAssoc.LEFT, plus_inv_parse_action),
    #     ('-', 2, opAssoc.LEFT, Binary.parse_action),
    #     ('+', 2, opAssoc.LEFT, plus_parse_action),
    ])


#     divide_constants = sp(constant_value + BAR + constant_value,
#                               lambda t: CDP.Divide(make_list([t[0], t[1], t[2]])))

