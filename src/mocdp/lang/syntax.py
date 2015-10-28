# -*- coding: utf-8 -*-
from .parse_actions import *  # @UnusedWildImport
from mocdp.lang.helpers import square
from mocdp.posets import R_dimensionless, make_rcompunit
from pyparsing import (
    CaselessLiteral, Combine, Forward, Group, Literal, NotAny, OneOrMore,
    Optional, Or, ParserElement, Suppress, Word, ZeroOrMore, alphanums, alphas,
    nums, oneOf, opAssoc, operatorPrecedence)
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

    unit1 = Word(alphas + '$' + ' ')
    unit2 = L('/')
    unit3 = L('^') + L('2')
    unit4 = L('*')  # any
    unit_expr = Combine(OneOrMore(unit1 ^ unit2 ^ unit3 ^ unit4))


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

    integer_or_float = integer ^ floatnumber

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

    empty_unit = S(L('[')) + S(L(']'))
    spa(empty_unit, lambda _: dict(unit=R_dimensionless))
    number_with_unit = C(integer_or_float, 'value') + C(unit_expr, 'unit') ^ unitst ^ empty_unit
    number_with_unit = ((C(integer_or_float, 'value') + unitst) ^
                        (C(integer_or_float, 'value') + C(unit_expr, 'unit')))

    spa(number_with_unit, number_with_unit_parse)

    # load battery
    load_expr = S(L('load')) - C(idn.copy(), 'load_arg')
    spa(load_expr, lambda t: CDP.LoadCommand(t['load_arg']))

    dp_rvalue = Forward()
    # <dpname> = ...

    SUB = sp(L('sub'), lambda t: CDP.SubKeyword(t[0]))

    setsub_expr = sp(SUB - C(idn.copy(), 'dpname') - S(L('=')) - C(dp_rvalue, 'dp_rvalue'),
                     lambda t: CDP.SetName(t[0], t[1], t[2]))


    rvalue = Forward()
    fvalue = Forward()

    setname_rightside = rvalue

    setname_generic_var = idn.copy()
    spa(setname_generic_var, lambda t: CDP.SetNameGenericVar(t[0]))
    setname_generic = (C(setname_generic_var, 'name') + S(L('='))) + C(setname_rightside, 'right_side')
    spa(setname_generic, lambda t: CDP.SetNameGeneric(t[0], t[1]))


    variable_ref = NotAny(reserved) + C(idn.copy(), 'variable_ref_name')
    spa(variable_ref, lambda t: CDP.VariableRef(t['variable_ref_name']))

    constant_value = number_with_unit ^ variable_ref


    rvalue_resource_simple = sp(C(idn.copy(), 'dp') + L('.') - C(idn.copy(), 's'),
                                lambda t: CDP.Resource(s=t[2], keyword=t[1], dp=t[0]))

    REQUIRED_BY = sp(L('required') - L('by'),
                    lambda _: CDP.RequiredByKeyword('required by'))

    PROVIDED_BY = sp(L('provided') - L('by'),
                    lambda _: CDP.ProvidedByKeyword('provided by'))

                     
    rvalue_resource_fancy = sp(C(idn.copy(), 's') + REQUIRED_BY - C(idn.copy(), 'dp'),
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

    # comment_line = S(LineStart()) + ow + L('#') + line + S(EOL)
    # comment_line = ow + Literal('#') + line + S(EOL)


    DOT = sp(L('.'), lambda t: CDP.DotPrep(t[0]))
    
    simple = sp(C(idn.copy(), 'dp2') + DOT - C(idn.copy(), 's2'),
               lambda t: CDP.Function(dp=t['dp2'], s=t['s2'], keyword=t[1])  )
    fancy = sp(C(idn.copy(), 's2') + PROVIDED_BY - C(idn.copy(), 'dp2'),
                lambda t: CDP.Function(dp=t['dp2'], s=t['s2'], keyword=t[1]))

    fvalue_operand = lf_new_limit ^ simple ^ fancy ^ lf_new_resource ^ (S(L('(')) - (lf_new_limit ^ simple ^ fancy ^ lf_new_resource) - S(L(')')))

    # Fractions

    integer_fraction = C(integer, 'num') + S(L('/')) + C(integer, 'den')
    spa(integer_fraction, lambda t: CDP.IntegerFraction(t['num'], t['den']))


    power_expr = (S(L('pow')) - S(L('(')) +
                    C(rvalue, 'op1') - S(L(','))
                    + C(integer_fraction, 'exponent')) - S(L(')'))

    
    spa(power_expr, power_expr_parse)
#     spa(power_expr, lambda t: CDP.Power(op1=t['op1'], exponent=t['exponent']))



    GEQ = sp(L('>='), lambda t: CDP.geq(t[0]))
    LEQ = sp(L('<='), lambda t: CDP.leq(t[0]))

    constraint_expr = C(fvalue, 'lf') + GEQ - C(rvalue, 'rvalue')
    spa(constraint_expr, lambda t: CDP.Constraint(function=t['lf'],
                                                  rvalue=t['rvalue'], prep=t[1]))

    constraint_expr2 = C(rvalue, 'rvalue') + LEQ - C(fvalue, 'lf')
    spa(constraint_expr2, lambda t: CDP.Constraint(function=t['lf'],
                                                   rvalue=t['rvalue'], prep=t[1]))



    fun_shortcut1 = sp(PROVIDES + fname + USING + idn.copy(),
                       lambda t: CDP.FunShortcut1(provides=t[0],
                                                  fname=t[1],
                                                  prep_using=t[2],
                                                  name=t[3]))

    res_shortcut1 = sp(REQUIRES + rname + FOR + idn,
                       lambda t: CDP.ResShortcut1(t[0], t[1], t[2], t[3]))

    fun_shortcut2 = sp(PROVIDES + fname + LEQ - fvalue,
                       lambda t: CDP.FunShortcut2(t[0], t[1], t[2], t[3]))

    res_shortcut2 = sp(REQUIRES + rname + GEQ - rvalue,
                       lambda t: CDP.ResShortcut2(t[0], t[1], t[2], t[3]))

    fun_shortcut3 = sp(PROVIDES + C(Group(fname + OneOrMore(S(L(',')) + fname)), 'fnames')
                       + USING + C(idn.copy(), 'name'),
                       lambda t: CDP.FunShortcut1m(provides=t[0],
                             fnames=make_list(list(t['fnames'])),
                             prep_using=t[2],
                             name=t['name']))

    res_shortcut3 = sp(REQUIRES + C(Group(rname + OneOrMore(S(L(',')) + rname)), 'rnames')
                       + FOR + C(idn.copy(), 'name'),
                       lambda t: CDP.ResShortcut1m(requires=t[0],
                             rnames=make_list(list(t['rnames'])),
                             prep_for=t[2],
                             name=t['name']))


    line_expr = (load_expr ^ constraint_expr ^ constraint_expr2 ^
                 (setname_generic ^ setsub_expr)
                 ^ fun_statement ^ res_statement ^ fun_shortcut1 ^ fun_shortcut2
                 ^ res_shortcut1 ^ res_shortcut2 ^ res_shortcut3 ^ fun_shortcut3)


    CDPTOKEN = L('cdp') | L('mcdp')
    spa(CDPTOKEN, lambda t: CDP.MCDPKeyword(t[0]))

    dp_model_statements = ZeroOrMore(S(ow) + line_expr)
    spa(dp_model_statements, lambda t: make_list(t))

    dp_model = CDPTOKEN - S(L('{')) - dp_model_statements - S(L('}'))
    spa(dp_model, lambda t: CDP.BuildProblem(keyword=t[0], statements=t[1]))

    funcname = Combine(idn + ZeroOrMore(L('.') - idn))
    code_spec = sp(S(L('code')) - C(funcname, 'function'),
                   lambda t: CDP.PDPCodeSpec(function=t['function'][0], arguments={}))


    load_pdp = S(L('load')) - C(idn.copy(), 'name')
    spa(load_pdp, lambda t: CDP.LoadDP(t['name']))

    pdp_rvalue = load_pdp ^ code_spec


    simple_dp_model = (S(L('dp')) - S(L('{')) -
                       C(Group(ZeroOrMore(fun_statement)), 'fun') -
                       C(Group(ZeroOrMore(res_statement)), 'res') -
                       S(L('implemented-by')) - C(pdp_rvalue, 'pdp_rvalue') -
                       S(L('}')))
    spa(simple_dp_model, lambda t: CDP.DPWrap(list(t[0]), list(t[1]), t[2]))


    COMPACT = sp(L('compact'), lambda t: CDP.CompactKeyword(t[0]))
    TEMPLATE = sp(L('template'), lambda t: CDP.TemplateKeyword(t[0]))
    ABSTRACT = sp(L('abstract'), lambda t: CDP.AbstractKeyword(t[0]))

    abstract_expr = sp(ABSTRACT - dp_rvalue, 
                       lambda t: CDP.AbstractAway(t[0], t[1]))

    
    compact_expr = sp(COMPACT - dp_rvalue,
                       lambda t: CDP.Compact(t[0], t[1]))

    template_expr = sp(TEMPLATE - dp_rvalue,
                       lambda t: CDP.MakeTemplate(t[0], t[1]))

    # dp_rvalue << (load_expr | simple_dp_model) ^ dp_model
    dp_rvalue << (load_expr | simple_dp_model | dp_model | abstract_expr |
                  template_expr | compact_expr)

    rvalue << operatorPrecedence(operand, [
    #     ('-', 1, opAssoc.RIGHT, Unary.parse_action),
        ('*', 2, opAssoc.LEFT, mult_parse_action),
    #     ('-', 2, opAssoc.LEFT, Binary.parse_action),
        ('+', 2, opAssoc.LEFT, plus_parse_action),
    ])


    fvalue << operatorPrecedence(fvalue_operand, [
    #     ('-', 1, opAssoc.RIGHT, Unary.parse_action),
        ('*', 2, opAssoc.LEFT, mult_inv_parse_action),
    #     ('-', 2, opAssoc.LEFT, Binary.parse_action),
    #     ('+', 2, opAssoc.LEFT, plus_parse_action),
    ])


