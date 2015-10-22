# -*- coding: utf-8 -*-
from .parts import (AbstractAway, Constraint, DPWrap, FunStatement, Function,
    LoadCommand, LoadDP, MakeTemplate, NewFunction, NewLimit, NewResource, OpMax,
    OpMin, PDPCodeSpec, ResStatement, Resource, SetName, ValueWithUnits)
from .utils import parse_action
from contracts import contract
from contracts.interface import Where
from contracts.utils import indent, raise_desc, raise_wrapped
from mocdp.exceptions import DPInternalError, DPSemanticError, DPSyntaxError
from mocdp.lang.parts import GenericNonlinearity, MultN, PlusN, FunShortcut1, \
    ResShortcut1, FunShortcut2, ResShortcut2, SetNameResource, InvMult, \
    MultipleStatements, Compact
from mocdp.posets.rcomp import (R_Cost, R_Current, R_Energy, R_Power, R_Time,
    R_Voltage, R_Weight, R_dimensionless, mult_table)
from mocdp.posets.space import NotBelongs, Space
from pyparsing import (CaselessLiteral, Combine, Forward, Group, Literal,
    Optional, Or, ParseException, ParseFatalException, ParserElement, Suppress,
    Word, ZeroOrMore, alphanums, alphas, nums, oneOf, opAssoc,
    operatorPrecedence, OneOrMore)
import functools
import math


ParserElement.enablePackrat()

# ParserElement.setDefaultWhitespaceChars('')

# shortcuts
S = Suppress
L = Literal
O = Optional
# "call"
C = lambda x, b: x.setResultsName(b)

def spa(x, b):
    @parse_action
    def p(tokens, loc, s):
        where = Where(s, loc)
        try:
            res = b(tokens)
        except DPSemanticError as e:
            if e.where is None:
                e.where = where
            raise DPSemanticError(str(e), where=where)
        except BaseException as e:
            raise_wrapped(DPInternalError, e, "Error while parsing.",
                          where=where.__str__(), tokens=tokens)

        if hasattr(res, 'where'):
            res.where = where
        return res
    x.setParseAction(p)

# optional whitespace
ow = S(ZeroOrMore(L(' ')))
# EOL = S(LineEnd())
# line = SkipTo(LineEnd(), failOn=LineStart() + LineEnd())


# identifier
idn = Combine(oneOf(list(alphas)) + Optional(Word('_' + alphanums)))


# Simple DPs being wrapped
#
# f name (unit)
# f name (unit)
# wraps name

units = {
    'J': R_Energy,
    's': R_Time,
    'A': R_Current,
    'V': R_Voltage,
    'g': R_Weight,
    'W': R_Power,
    '$': R_Cost,
    'R': R_dimensionless,
}
unit_expr = oneOf(list(units))
spa(unit_expr, lambda t: units[t[0]])

# numbers
number = Word(nums)
point = Literal('.')
e = CaselessLiteral('E')
plusorminus = Literal('+') | Literal('-')
integer = Combine(O(plusorminus) + number)
# Note that '42' is not a valid float...
floatnumber = (Combine(integer + point + O(number) + O(e + integer)) |
                Combine(integer + e + integer))

def convert_int(tokens):
    assert(len(tokens) == 1)
    return int(tokens[0])

integer.setParseAction(convert_int)
floatnumber.setParseAction(lambda tokens: float(tokens[0]))

integer_or_float = integer ^ floatnumber

unitst = S(L('[')) - C(unit_expr, 'unit') - S(L(']'))

PROVIDES = S(L('provides'))
REQUIRES = S(L('requires'))
USING = S(L('using'))
FOR = S(L('for'))

fun_statement = PROVIDES + C(idn, 'fname') + unitst
spa(fun_statement, lambda t: FunStatement(t['fname'], t['unit']))

res_statement = REQUIRES + C(idn, 'rname') + unitst
spa(res_statement, lambda t: ResStatement(t['rname'], t['unit']))

empty_unit = S(L('[')) + S(L(']'))
spa(empty_unit, lambda _: dict(unit=R_dimensionless))
number_with_unit = C(integer_or_float, 'value') + unitst ^ empty_unit  # C(empty_unit, 'unit')

def number_with_unit_parse(t):
    value = t[0]
    units = t[1]
    from mocdp.posets.rcomp import Rcomp
    if isinstance(value, int) and isinstance(units, Rcomp):
        value = float(value)
    try:
        units.belongs(value)
    except NotBelongs as e:
        msg = 'Value %r does not belong to %s.' % (value, units)
        raise_desc(DPSemanticError, msg)
    res = ValueWithUnits(value, units)
    return res

spa(number_with_unit, number_with_unit_parse)

# load battery
load_expr = S(L('load')) - C(idn, 'load_arg')
spa(load_expr, lambda t: LoadCommand(t['load_arg']))

dp_rvalue = Forward()
# <dpname> = ...
setname_expr = (C(idn, 'dpname') + S(L('='))) + C(dp_rvalue, 'dp_rvalue')
spa(setname_expr, lambda t: SetName(t['dpname'], t['dp_rvalue']))


rvalue = Forward()
fvalue = Forward()

setname_resource = (C(idn, 'name') + S(L('='))) + C(rvalue, 'rvalue')
spa(setname_resource, lambda t: SetNameResource(t['name'], t['rvalue']))


rvalue_resource_simple = C(idn, 'dp') + S(L('.')) - C(idn, 's')

prep = (S(L('required')) - S(L('by'))) | S(L('of'))
rvalue_resource_fancy = C(idn, 's') + prep - C(idn, 'dp')
rvalue_resource = rvalue_resource_simple ^ rvalue_resource_fancy
spa(rvalue_resource, lambda t: Resource(t['dp'], t['s']))

rvalue_new_function = C(idn, 'new_function')
spa(rvalue_new_function, lambda t: NewFunction(t['new_function']))

lf_new_resource = C(idn, 'new_resource')
spa(lf_new_resource, lambda t: NewResource(t['new_resource']))

lf_new_limit = C(Group(number_with_unit), 'limit')
spa(lf_new_limit, lambda t: NewLimit(t['limit'][0]))

def square(x):
    return x * x

unary = {
    'sqrt': lambda op1: GenericNonlinearity(math.sqrt, op1, lambda F: F),
    'square': lambda op1: GenericNonlinearity(square, op1, lambda F: F),
}
unary_op = Or([L(x) for x in unary])
unary_expr = (C(unary_op, 'opname') - S(L('('))
                + C(rvalue, 'op1')) - S(L(')'))

spa(unary_expr, lambda t: unary[t['opname']](t['op1']))


binary = {
    'max': OpMax,
    'min': OpMin,
}

opname = Or([L(x) for x in binary])
binary_expr = (C(opname, 'opname') - S(L('(')) +
                C(rvalue, 'op1') - S(L(','))
                + C(rvalue, 'op2')) - S(L(')'))


spa(binary_expr, lambda t: binary[t['opname']](t['op1'], t['op2']))

operand = rvalue_new_function ^ rvalue_resource ^ binary_expr ^ unary_expr ^ number_with_unit

# comment_line = S(LineStart()) + ow + L('#') + line + S(EOL)
# comment_line = ow + Literal('#') + line + S(EOL)


simple = (C(idn, 'dp2') + S(L('.')) - C(idn, 's2'))
fancy = (C(idn, 's2') + S(L('provided')) - S(L('by')) - C(idn, 'dp2'))

spa(simple, lambda t: Function(t['dp2'], t['s2']))
spa(fancy, lambda t: Function(t['dp2'], t['s2']))


fvalue_operand = lf_new_limit ^ simple ^ fancy ^ lf_new_resource ^ (S(L('(')) - (lf_new_limit ^ simple ^ fancy ^ lf_new_resource) - S(L(')')))

GEQ = S(L('>=')) 
LEQ = S(L('<='))

constraint_expr = C(fvalue, 'lf') + GEQ - C(rvalue, 'rvalue')
spa(constraint_expr, lambda t: Constraint(t['lf'], t['rvalue']))

constraint_expr2 = C(rvalue, 'rvalue') + LEQ - C(fvalue, 'lf')
spa(constraint_expr2, lambda t: Constraint(t['lf'], t['rvalue']))



fun_shortcut1 = PROVIDES + C(idn, 'fname') + USING + C(idn, 'name')
res_shortcut1 = REQUIRES + C(idn, 'rname') + FOR + C(idn, 'name')

fun_shortcut2 = PROVIDES + C(idn, 'fname') + LEQ - C(fvalue, 'lf')
res_shortcut2 = REQUIRES + C(idn, 'rname') + GEQ - C(rvalue, 'rvalue')

fun_shortcut3 = PROVIDES + C(Group(idn + OneOrMore(S(L(',')) + idn)), 'fnames') + USING + C(idn, 'name')
res_shortcut3 = REQUIRES + C(Group(idn + OneOrMore(S(L(',')) + idn)), 'rnames') + FOR + C(idn, 'name')



spa(fun_shortcut1, lambda t: FunShortcut1(t['fname'], t['name']))
spa(res_shortcut1, lambda t: ResShortcut1(t['rname'], t['name']))

spa(fun_shortcut2, lambda t: FunShortcut2(t['fname'], t['lf']))
spa(res_shortcut2, lambda t: ResShortcut2(t['rname'], t['rvalue']))

def res_shortcut3_parse(tokens):
    name = tokens['name']
    res = []
    for rname in tokens['rnames']:
        res.append(ResShortcut1(rname, name))
    return MultipleStatements(res)

def fun_shortcut3_parse(tokens):
    name = tokens['name']
    res = []
    for fname in tokens['fnames']:
        res.append(FunShortcut1(fname, name))
    return MultipleStatements(res)



spa(fun_shortcut3, fun_shortcut3_parse)

spa(res_shortcut3, res_shortcut3_parse)

line_expr = (load_expr ^ constraint_expr ^ constraint_expr2 ^ setname_expr ^ setname_resource
             ^ fun_statement ^ res_statement ^ fun_shortcut1 ^ fun_shortcut2
             ^ res_shortcut1 ^ res_shortcut2 ^ res_shortcut3 ^ fun_shortcut3)


dp_model = S(L('cdp')) - S(L('{')) - ZeroOrMore(S(ow) + line_expr) - S(L('}'))


funcname = Combine(idn + ZeroOrMore(L('.') - idn))
code_spec = S(L('code')) - C(funcname, 'function')
spa(code_spec, lambda t: PDPCodeSpec(function=t['function'], arguments={}))



load_pdp = S(L('load')) - C(idn, 'name')
spa(load_pdp, lambda t: LoadDP(t['name']))

pdp_rvalue = load_pdp ^ code_spec


simple_dp_model = (S(L('dp')) - S(L('{')) -
                   C(Group(ZeroOrMore(fun_statement)), 'fun') -
                   C(Group(ZeroOrMore(res_statement)), 'res') -
                   S(L('implemented-by')) - C(pdp_rvalue, 'pdp_rvalue') -
                   S(L('}')))
spa(simple_dp_model, lambda t: DPWrap(list(t[0]), list(t[1]), t[2]))


abstract_expr = S(L('abstract')) - C(dp_rvalue, 'dp_rvalue')
spa(abstract_expr, lambda t: AbstractAway(t['dp_rvalue']))

compact_expr = S(L('compact')) - C(dp_rvalue, 'dp_rvalue')
spa(compact_expr, lambda t: Compact(t['dp_rvalue']))

template_expr = S(L('template')) - C(dp_rvalue, 'dp_rvalue')
spa(template_expr, lambda t: MakeTemplate(t['dp_rvalue']))

# dp_rvalue << (load_expr | simple_dp_model) ^ dp_model
dp_rvalue << (load_expr | simple_dp_model | dp_model | abstract_expr |
              template_expr | compact_expr)


@parse_action
def mult_parse_action(tokens):
    tokens = list(tokens[0])

    ops = []
    for i, t in enumerate(tokens):
        if i % 2 == 0:
            ops.append(t)
        else:
            assert t == '*'

    assert len(ops) > 1

    constants = [op for op in ops if isinstance(op, ValueWithUnits)]
    nonconstants = [op for op in ops if not isinstance(op, ValueWithUnits)]

    if constants:
        # compile time optimization
        def mult(a, b):
            R = mult_table(a.unit, b.unit)
            value = a.value * b.value
            return ValueWithUnits(value=value, unit=R)
        res = functools.reduce(mult, constants)

        if len(nonconstants) == 0:
            return res

        if len(nonconstants) == 1:
            op1 = nonconstants[0]
        else:
            assert len(nonconstants) > 1
            op1 = MultN(nonconstants)
        function = MultValue(res.value)

        from mocdp.dp_report.gg_ndp import format_unit
        setattr(function, '__name__', '× %s %s' % (res.unit.format(res.value),
                                                   format_unit(res.unit)))
        R_from_F = MultType(res.unit)
        return GenericNonlinearity(function=function, op1=op1, R_from_F=R_from_F)

    return MultN(ops)

class MultType():
    def __init__(self, factor):
        self.factor = factor
    def __call__(self, F):
        return mult_table(F, self.factor)

class MultValue():
    def __init__(self, res):
        self.res = res
    def __call__(self, x):
        return x * self.res

@parse_action
def plus_parse_action(tokens):
    tokens = list(tokens[0])

    ops = []
    for i, t in enumerate(tokens):
        if i % 2 == 0:
            ops.append(t)
        else:
            assert t == '+'
            
    def simplify(op):
        if isinstance(op, GenericNonlinearity) and isinstance(op.function, PlusValue):
            value = op.function.value
            unit = op.factor
            vu = ValueWithUnits(value=value, unit=unit)
            return [op.op1, vu]
        else:
            return [op]
    newops = []
    for op in ops:
        newops.extend(simplify(op))

    ops = newops

    constants = [op for op in ops if isinstance(op, ValueWithUnits)]
    nonconstants = [op for op in ops if not isinstance(op, ValueWithUnits)]

    if constants:
        # compile time optimization
        def add(a, b):
            R = add_table(a.unit, b.unit)
            value = a.value + b.value
            return ValueWithUnits(value=value, unit=R)
        res = functools.reduce(add, constants)
        if len(nonconstants) == 0:
            return res

        if len(nonconstants) == 1:
            op1 = nonconstants[0]
        else:
            assert len(nonconstants) > 1
            op1 = PlusN(nonconstants)
        function = PlusValue(res.value)
        from mocdp.dp_report.gg_ndp import format_unit
        setattr(function, '__name__', '+ %s %s' % (res.unit.format(res.value),
                                                   format_unit(res.unit)))
        R_from_F = PlusType(res.unit)
        return GenericNonlinearity(function=function, op1=op1, R_from_F=R_from_F)

    return PlusN(ops)

def add_table(F1, F2):
    if not F1 == F2:
        msg = 'Incompatible units for addition.'
        raise_desc(DPSemanticError, msg, F1=F1, F2=F2)
    return F1

class PlusType():
    @contract(factor=Space)
    def __init__(self, factor):
        self.factor = factor
    def __call__(self, F):
        return add_table(F, self.factor)

class PlusValue():
    def __init__(self, value):
        self.value = value
    def __call__(self, x):
        return x + self.value

rvalue << operatorPrecedence(operand, [
#     ('-', 1, opAssoc.RIGHT, Unary.parse_action),
    ('*', 2, opAssoc.LEFT, mult_parse_action),
#     ('-', 2, opAssoc.LEFT, Binary.parse_action),
    ('+', 2, opAssoc.LEFT, plus_parse_action),
])

@parse_action
def mult_inv_parse_action(tokens):
    tokens = list(tokens[0])

    ops = []
    for i, t in enumerate(tokens):
        if i % 2 == 0:
            ops.append(t)
        else:
            assert t == '*'

    assert len(ops) > 1
    assert len(ops) == 2
    return InvMult(ops)


fvalue << operatorPrecedence(fvalue_operand, [
#     ('-', 1, opAssoc.RIGHT, Unary.parse_action),
    ('*', 2, opAssoc.LEFT, mult_inv_parse_action),
#     ('-', 2, opAssoc.LEFT, Binary.parse_action),
#     ('+', 2, opAssoc.LEFT, plus_parse_action),
])


#
# def boxit(s):
#     lines = s.split('\n')
#     W = max(map(len, lines))
# #     c = ['┌', '┐', '└', '┘']
#     s = '┌' + '┄' * (W + 2) + '┐'
#     s += '\n' + '┆ ' + ' ' * (W) + ' ┆'
#
#     for l in lines:
#         s += '\n┆ ' + l.ljust(W, '-') + ' ┆'
#     s += '\n' + '┆ ' + ' ' * (W) + ' ┆'
#     s += '\n' + '└' + '┄' * (W + 2) + '┘'
#
#     return s

def parse_wrap(expr, string):
    # Nice trick: the removE_comments doesn't change the number of lines
    # it only truncates them...
    string0 = remove_comments(string)

    # m = boxit
    m = lambda x: x
    try:
        return expr.parseString(string0, parseAll=True)
    except (ParseException, ParseFatalException) as e:
        # ... so we can use "string" here.
        where = Where(string, line=e.lineno, column=e.col)
        raise DPSyntaxError(str(e), where=where)
    except DPSemanticError as e:
        msg = "User error while interpreting the model:"
        msg += "\n\n" + indent(m(string), '  ') + '\n'
        raise_wrapped(DPSemanticError, e, msg, compact=True)
    except DPInternalError as e:
        msg = "Internal error while evaluating the spec:"
        msg += "\n\n" + indent(m(string), '  ') + '\n'
        raise_wrapped(DPInternalError, e, msg, compact=False)
    
def remove_comments(s):
    lines = s.split("\n")
    def remove_comment(line):
        if '#' in line:
            return line[:line.index('#')]
        else:
            return line
    return "\n".join(map(remove_comment, lines))

# @contract(returns=NamedDP)
def parse_ndp(string):
    v = parse_wrap(dp_rvalue, string)[0]
    from mocdp.lang.blocks import Context, eval_dp_rvalue
    context = Context()
    res = eval_dp_rvalue(v, context)
    # I'm not sure what happens to the context
    # if context.names # error ??

    from mocdp.comp.interfaces import NamedDP
    assert isinstance(res, NamedDP), res
    return res

def parse_line(line):
    return parse_wrap(line_expr, line)[0]

@parse_action
def dp_model_parse_action(tokens):
    res = list(tokens)
    # if not res:
    #    raise DPSemanticError('Empty model')
    from mocdp.lang.blocks import interpret_commands
    return interpret_commands(res)

dp_model.setParseAction(dp_model_parse_action)


