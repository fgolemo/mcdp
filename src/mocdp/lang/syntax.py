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


class Syntax():
    keywords = ['load', 'compact', 'required', 'provides', 'abstract',
                      'dp', 'cdp', 'mcdp', 'template', 'sub']
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
    idn = Combine(oneOf(list(alphas)) + Optional(Word('_' + alphanums)))

    unit1 = Word(alphas + '$' + ' ')
    unit2 = L('/')
    unit3 = L('^') + L('2')
    unit4 = L('*')  # any
    unit_expr = Combine(OneOrMore(unit1 ^ unit2 ^ unit3 ^ unit4))


    spa(unit_expr, lambda t:  make_rcompunit(t[0]))

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

    PROVIDES = S(L('provides'))
    REQUIRES = S(L('requires'))
    USING = S(L('using'))
    FOR = S(L('for'))

    fun_statement = PROVIDES + C(idn, 'fname') + unitst
    spa(fun_statement, lambda t: CDP.FunStatement(t['fname'], t['unit']))

    res_statement = REQUIRES + C(idn, 'rname') + unitst
    spa(res_statement, lambda t: CDP.ResStatement(t['rname'], t['unit']))

    empty_unit = S(L('[')) + S(L(']'))
    spa(empty_unit, lambda _: dict(unit=R_dimensionless))
    number_with_unit = C(integer_or_float, 'value') + C(unit_expr, 'unit') ^ unitst ^ empty_unit
    number_with_unit = ((C(integer_or_float, 'value') + unitst) ^
                        (C(integer_or_float, 'value') + C(unit_expr, 'unit')))

    spa(number_with_unit, number_with_unit_parse)

    # load battery
    load_expr = S(L('load')) - C(idn, 'load_arg')
    spa(load_expr, lambda t: CDP.LoadCommand(t['load_arg']))

    dp_rvalue = Forward()
    # <dpname> = ...
    setsub_expr = S(L('sub')) - C(idn, 'dpname') - S(L('=')) - C(dp_rvalue, 'dp_rvalue')
    spa(setsub_expr, lambda t: CDP.SetName(t['dpname'], t['dp_rvalue']))


    rvalue = Forward()
    fvalue = Forward()

    setname_rightside = rvalue
    setname_generic = (C(idn, 'name') + S(L('='))) + C(setname_rightside, 'right_side')
    spa(setname_generic, lambda t: CDP.SetNameGeneric(t['name'], t['right_side']))

#     setname_resource = (C(idn, 'name') + S(L('='))) + C(rvalue, 'rvalue')
#     spa(setname_resource, lambda t: CDP.SetNameResource(t['name'], t['rvalue']))
# 
#     setname_value = (C(idn, 'setname_value') + S(L('='))) + C(constant_value, 'constant_value')
#     spa(setname_value, lambda t: CDP.SetNameConstant(t['setname_value'], t['constant_value']))


    variable_ref = NotAny(reserved) + C(idn, 'variable_ref_name')
    spa(variable_ref, lambda t: CDP.VariableRef(t['variable_ref_name']))

    constant_value = number_with_unit ^ variable_ref



    rvalue_resource_simple = C(idn, 'dp') + S(L('.')) - C(idn, 's')

    prep = (S(L('required')) - S(L('by'))) | S(L('of'))
    rvalue_resource_fancy = C(idn, 's') + prep - C(idn, 'dp')
    rvalue_resource = rvalue_resource_simple ^ rvalue_resource_fancy
    spa(rvalue_resource, lambda t: CDP.Resource(t['dp'], t['s']))

    rvalue_new_function = C(idn, 'new_function')
    spa(rvalue_new_function, lambda t: CDP.VariableRef(t['new_function']))

    lf_new_resource = C(idn, 'new_resource')
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

    opname = Or([L(x) for x in binary])
    binary_expr = (C(opname, 'opname') - S(L('(')) +
                    C(rvalue, 'op1') - S(L(','))
                    + C(rvalue, 'op2')) - S(L(')'))


    spa(binary_expr, lambda t: Syntax.binary[t['opname']](t['op1'], t['op2']))

    operand = rvalue_new_function ^ rvalue_resource ^ binary_expr ^ unary_expr ^ constant_value

    # comment_line = S(LineStart()) + ow + L('#') + line + S(EOL)
    # comment_line = ow + Literal('#') + line + S(EOL)


    simple = (C(idn, 'dp2') + S(L('.')) - C(idn, 's2'))
    fancy = (C(idn, 's2') + S(L('provided')) - S(L('by')) - C(idn, 'dp2'))

    spa(simple, lambda t: CDP.Function(t['dp2'], t['s2']))
    spa(fancy, lambda t: CDP.Function(t['dp2'], t['s2']))


    fvalue_operand = lf_new_limit ^ simple ^ fancy ^ lf_new_resource ^ (S(L('(')) - (lf_new_limit ^ simple ^ fancy ^ lf_new_resource) - S(L(')')))

    # Fractions

    integer_fraction = C(integer, 'num') + S(L('/')) + C(integer, 'den')
    spa(integer_fraction, lambda t: CDP.IntegerFraction(t['num'], t['den']))


    power_expr = (S(L('pow')) - S(L('(')) +
                    C(rvalue, 'op1') - S(L(','))
                    + C(integer_fraction, 'exponent')) - S(L(')'))

    
    spa(power_expr, power_expr_parse)
#     spa(power_expr, lambda t: CDP.Power(op1=t['op1'], exponent=t['exponent']))



    GEQ = S(L('>='))
    LEQ = S(L('<='))

    constraint_expr = C(fvalue, 'lf') + GEQ - C(rvalue, 'rvalue')
    spa(constraint_expr, lambda t: CDP.Constraint(t['lf'], t['rvalue']))

    constraint_expr2 = C(rvalue, 'rvalue') + LEQ - C(fvalue, 'lf')
    spa(constraint_expr2, lambda t: CDP.Constraint(t['lf'], t['rvalue']))



    fun_shortcut1 = PROVIDES + C(idn, 'fname') + USING + C(idn, 'name')
    res_shortcut1 = REQUIRES + C(idn, 'rname') + FOR + C(idn, 'name')

    fun_shortcut2 = PROVIDES + C(idn, 'fname') + LEQ - C(fvalue, 'lf')
    res_shortcut2 = REQUIRES + C(idn, 'rname') + GEQ - C(rvalue, 'rvalue')

    fun_shortcut3 = PROVIDES + C(Group(idn + OneOrMore(S(L(',')) + idn)), 'fnames') + USING + C(idn, 'name')
    res_shortcut3 = REQUIRES + C(Group(idn + OneOrMore(S(L(',')) + idn)), 'rnames') + FOR + C(idn, 'name')



    spa(fun_shortcut1, lambda t: CDP.FunShortcut1(t['fname'], t['name']))
    spa(res_shortcut1, lambda t: CDP.ResShortcut1(t['rname'], t['name']))

    spa(fun_shortcut2, lambda t: CDP.FunShortcut2(t['fname'], t['lf']))
    spa(res_shortcut2, lambda t: CDP.ResShortcut2(t['rname'], t['rvalue']))


    spa(fun_shortcut3, fun_shortcut3_parse)

    spa(res_shortcut3, res_shortcut3_parse)

    line_expr = (load_expr ^ constraint_expr ^ constraint_expr2 ^
                 (setname_generic ^ setsub_expr)
                 ^ fun_statement ^ res_statement ^ fun_shortcut1 ^ fun_shortcut2
                 ^ res_shortcut1 ^ res_shortcut2 ^ res_shortcut3 ^ fun_shortcut3)


    CDPTOKEN = S(L('cdp')) | S(L('mcdp'))
    dp_model = CDPTOKEN - S(L('{')) - ZeroOrMore(S(ow) + line_expr) - S(L('}'))
    spa(dp_model, dp_model_parse_action)

    funcname = Combine(idn + ZeroOrMore(L('.') - idn))
    code_spec = S(L('code')) - C(funcname, 'function')
    spa(code_spec, lambda t: CDP.PDPCodeSpec(function=t['function'], arguments={}))



    load_pdp = S(L('load')) - C(idn, 'name')
    spa(load_pdp, lambda t: CDP.LoadDP(t['name']))

    pdp_rvalue = load_pdp ^ code_spec


    simple_dp_model = (S(L('dp')) - S(L('{')) -
                       C(Group(ZeroOrMore(fun_statement)), 'fun') -
                       C(Group(ZeroOrMore(res_statement)), 'res') -
                       S(L('implemented-by')) - C(pdp_rvalue, 'pdp_rvalue') -
                       S(L('}')))
    spa(simple_dp_model, lambda t: CDP.DPWrap(list(t[0]), list(t[1]), t[2]))


    abstract_expr = S(L('abstract')) - C(dp_rvalue, 'dp_rvalue')
    spa(abstract_expr, lambda t: CDP.AbstractAway(t['dp_rvalue']))

    compact_expr = S(L('compact')) - C(dp_rvalue, 'dp_rvalue')
    spa(compact_expr, lambda t: CDP.Compact(t['dp_rvalue']))

    template_expr = S(L('template')) - C(dp_rvalue, 'dp_rvalue')
    spa(template_expr, lambda t: CDP.MakeTemplate(t['dp_rvalue']))

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


