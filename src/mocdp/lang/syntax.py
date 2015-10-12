
from .parts import Constraint, LoadCommand, Mult, NewFunction, Resource
from contracts import contract
from contracts.interface import ContractSyntaxError, Where
from mocdp.comp.interfaces import NamedDP
from pyparsing import (Combine, Forward, LineEnd, LineStart, Literal,
    ParseException, ParseFatalException, ParserElement, SkipTo, Suppress, Word,
    ZeroOrMore, alphanums, alphas, oneOf, opAssoc, operatorPrecedence,
    OneOrMore)
from mocdp.lang.parts import SetName
from mocdp.lang.utils import parse_action



ParserElement.enablePackrat()

# ParserElement.setDefaultWhitespaceChars('')

# shortcuts
S = Suppress
L = Literal
C = lambda x, b: x.setResultsName(b)
def spa(x, b):
    @parse_action
    def p(tokens):
#         print('s: %r' % _s)
#         print('loc: %s' % _loc)
#         print('tokens: %r' % tokens)
        return b(tokens)
    x.setParseAction(p)



ow = S(ZeroOrMore(L(' ')))
EOL = S(LineEnd())
line = SkipTo(LineEnd(), failOn=LineStart() + LineEnd())


# identifier
idn = Combine(oneOf(list(alphas)) + Word('_' + alphanums))

# load battery
load_expr = S(L('load')) + C(idn, 'load_arg')
spa(load_expr, lambda t: LoadCommand(t['load_arg']))

dp_rvalue = Forward()
# <dpname> = ...
setname_expr = C(idn, 'dpname') + S(L('=')) + C(dp_rvalue, 'rvalue')
spa(setname_expr, lambda t: SetName(t['dpname'], t['rvalue']))

rvalue = Forward()
rvalue_resource = C(idn, 'dp') + S(L('.')) + C(idn, 's')
spa(rvalue_resource, lambda t: Resource(t['dp'], t['s']))

rvalue_new_function = C(idn, 'new_function')
spa(rvalue_new_function, lambda t: NewFunction(t['new_function']))

operand = rvalue_new_function ^ rvalue_resource

# comment_line = S(LineStart()) + ow + L('#') + line + S(EOL)
comment_line = ow + Literal('#') + line + S(EOL)


constraint_expr = (C(idn, 'dp2') + S(L('.')) + C(idn, 's2') +
                   S(L('>=')) + C(rvalue, 'rvalue'))

line_expr = load_expr ^ constraint_expr ^ setname_expr


dp_statement = S(comment_line) ^ line_expr

dp_model = S(L('dp')) + S(L('{')) + OneOrMore(dp_statement) + S(L('}'))


dp_rvalue << load_expr ^ dp_model


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

#     lines = filter(None, [t.strip() for t in tokens])
#
#     # remove comment line
#     is_comment = lambda x: x[0] == '#'
#     lines = [l for l in lines if not is_comment(l)]
#     res = map(parse_line, lines)

    res = list(tokens)
    from mocdp.lang.blocks import interpret_commands
    return interpret_commands(res)

dp_model.setParseAction(dp_model_parse_action)


