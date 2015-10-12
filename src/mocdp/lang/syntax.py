
from .parts import Constraint, LoadCommand, Mult, NewFunction, Resource
from contracts import contract
from contracts.interface import ContractSyntaxError, Where, describe_value
from mocdp.comp.interfaces import NamedDP
from pyparsing import (Combine, Forward, LineEnd, LineStart, Literal,
    ParseException, ParseFatalException, ParserElement, SkipTo, Suppress, Word,
    ZeroOrMore, alphanums, alphas, oneOf, opAssoc, operatorPrecedence,
    OneOrMore, Group, Optional)
from mocdp.lang.parts import SetName
from mocdp.lang.utils import parse_action
from collections import namedtuple



ParserElement.enablePackrat()

# ParserElement.setDefaultWhitespaceChars('')

# shortcuts
S = Suppress
L = Literal
C = lambda x, b: x.setResultsName(b)
def spa(x, b):
    @parse_action
    def p(tokens):
        return b(tokens)
    x.setParseAction(p)



ow = S(ZeroOrMore(L(' ')))
EOL = S(LineEnd())
line = SkipTo(LineEnd(), failOn=LineStart() + LineEnd())


# identifier
idn = Combine(oneOf(list(alphas)) + Optional(Word('_' + alphanums)))

# load battery
load_expr = S(L('load')) + C(idn, 'load_arg')
spa(load_expr, lambda t: LoadCommand(t['load_arg']))

dp_rvalue = Forward()
# <dpname> = ...
setname_expr = C(idn, 'dpname') + S(L('=')) + C(dp_rvalue, 'rvalue')
spa(setname_expr, lambda t: SetName(t['dpname'], t['rvalue']))

rvalue = Forward()
rvalue_resource_simple = C(idn, 'dp') + S(L('.')) + C(idn, 's')
rvalue_resource_fancy =C(idn, 's') + S(L('required')) + S(L('by')) + C(idn, 'dp') 
rvalue_resource = rvalue_resource_simple | rvalue_resource_fancy
spa(rvalue_resource, lambda t: Resource(t['dp'], t['s']))

rvalue_new_function = C(idn, 'new_function')
spa(rvalue_new_function, lambda t: NewFunction(t['new_function']))

operand = rvalue_new_function ^ rvalue_resource

# comment_line = S(LineStart()) + ow + L('#') + line + S(EOL)
comment_line = ow + Literal('#') + line + S(EOL)


simple = (C(idn, 'dp2') + S(L('.')) + C(idn, 's2'))
fancy = (C(idn, 's2') + S(L('provided')) + S(L('by')) + C(idn, 'dp2'))
signal_rvalue = simple | fancy | (S(L('(')) + (simple | fancy) + S(L(')')))

constraint_expr = (
                signal_rvalue
                   +                 
                   S(L('>=')) + C(rvalue, 'rvalue')
                )   

line_expr = load_expr ^ constraint_expr ^ setname_expr


dp_statement = S(comment_line) ^ line_expr

dp_model = S(L('cdp')) + S(L('{')) + OneOrMore(dp_statement) + S(L('}'))


# Simple DPs being wrapped
#
# f name (unit)
# f name (unit)
# wraps name

FunStatement = namedtuple('FunStatement', 'fname unit')
ResStatement = namedtuple('ResStatement', 'rname unit')
# ImplStatement = namedtuple('ImplStatement', 'name')
LoadDP = namedtuple('LoadDP', 'name')
DPWrap = namedtuple('DPWrap', 'fun res impl')
PDPCodeSpec = namedtuple('PDPCodeSpec', 'function arguments')
funcname = Combine(idn + ZeroOrMore(L('.') + idn))
code_spec = S(L('code')) + C(funcname, 'function')
spa(code_spec, lambda t: PDPCodeSpec(function=t['function'], arguments={}))

unitst = S(L('(')) + C(idn, 'unit') + S(L(')'))

fun_statement = S(L('f')) ^ S(L('provides')) + C(idn, 'fname') + unitst
spa(fun_statement, lambda t: FunStatement(t['fname'], t['unit']))

res_statement = S(L('r')) ^ S(L('requires')) + C(idn, 'rname') + unitst
spa(res_statement, lambda t: ResStatement(t['rname'], t['unit']))

load_pdp = S(L('load')) + C(idn, 'name')
spa(load_pdp, lambda t: LoadDP(t['name']))

pdp_rvalue = load_pdp ^ code_spec


simple_dp_model = (S(L('dp')) + S(L('{')) +
                   C(Group(OneOrMore(fun_statement)), 'fun') +
                   C(Group(OneOrMore(res_statement)), 'res') +
                   S(L('implemented-by')) + C(pdp_rvalue, 'pdp_rvalue') +
                   S(L('}')))
spa(simple_dp_model, lambda t: DPWrap(list(t[0]), list(t[1]), t[2]))


dp_rvalue << (load_expr | simple_dp_model) ^ dp_model


@parse_action
def mult_parse_action(tokens):  # @UnusedVariable
    t = tokens[0]
    assert t[1] == '*'
    return Mult(t[0], t[2])

@parse_action
def plus_parse_action(tokens):  # @UnusedVariable
    assert False

rvalue << operatorPrecedence(operand, [
#     ('-', 1, opAssoc.RIGHT, Unary.parse_action),
    ('*', 2, opAssoc.LEFT, mult_parse_action),
#     ('-', 2, opAssoc.LEFT, Binary.parse_action),
    ('+', 2, opAssoc.LEFT, plus_parse_action),
])


spa(constraint_expr, lambda t: Constraint(t['dp2'], t['s2'], t['rvalue']))


class DPSyntaxError(ContractSyntaxError):
    pass

def parse_wrap(expr, string):
    try:
        return expr.parseString(string, parseAll=True)
    except (ParseException, ParseFatalException) as e:
        where = Where(string, line=e.lineno, column=e.col)
        raise DPSyntaxError(str(e), where=where)

@contract(returns=NamedDP)
def parse_model(string):
    res = parse_wrap(dp_model, string)[0]
    return res

def parse_line(line):
    return parse_wrap(line_expr, line)[0]

@parse_action
def dp_model_parse_action(tokens):
    res = list(tokens)
    from mocdp.lang.blocks import interpret_commands
    return interpret_commands(res)

dp_model.setParseAction(dp_model_parse_action)


