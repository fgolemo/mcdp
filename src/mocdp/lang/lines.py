from mocdp.lang.blocks import  ow
from pyparsing import (Combine, Literal,
    Suppress, Word, alphanums, alphas, oneOf, Forward, operatorPrecedence,
    opAssoc)
from collections import namedtuple

# operators
Mult = namedtuple('Mult', 'a b')
Resource = namedtuple('Resource', 'dp s')
NewFunction = namedtuple('NewFunction', 'name')
Constraint = namedtuple('Constraint', 'dp2 s2 rvalue')
LoadCommand = namedtuple('LoadCommand', 'name load_arg')

# shortcuts
S = Suppress
L = Literal
C = lambda x, b: x.setResultsName(b)


# identifier
idn = Combine(oneOf(list(alphas)) + Word('_' + alphanums))

load_expr = (ow + idn.setResultsName('dpname') + ow + S(L('='))
             + ow + S(L('load')) + ow + idn.setResultsName('load_arg'))

rvalue = Forward()
rvalue_resource = ow + C(idn, 'dp') + S(L('.')) + C(idn, 's') + ow
rvalue_new_function = ow + C(idn, 'new_function') + ow

operand = rvalue_new_function ^ rvalue_resource

rvalue_new_function.setParseAction(lambda _s, _loc, tokens:
                                   NewFunction(tokens['new_function']))
rvalue_resource.setParseAction(lambda _s, _loc, tokens:
                               Resource(tokens['dp'], tokens['s']))

def mult_parse_action(s, loc, tokens):  # @UnusedVariable
    t = tokens[0]
    assert t[1] == '*'
    return Mult(t[0], t[2])


def plus_parse_action(s, loc, tokens):  # @UnusedVariable
    pass

rvalue << operatorPrecedence(operand, [
#     ('-', 1, opAssoc.RIGHT, Unary.parse_action),
    ('*', 2, opAssoc.LEFT, mult_parse_action),
#     ('-', 2, opAssoc.LEFT, Binary.parse_action),
    ('+', 2, opAssoc.LEFT, plus_parse_action),
])

constraint_expr = (ow + C(idn, 'dp2') + S(L('.')) + C(idn, 's2') + ow +
                   S(L('>=')) + C(rvalue, 'rvalue'))

line_expr = load_expr ^ constraint_expr  # ^ simple_constraint_expr


def constraint_expr_parse(_s, _loc, tokens):
    return Constraint(tokens['dp2'], tokens['s2'], tokens['rvalue'])
    
constraint_expr.setParseAction(constraint_expr_parse)


def load_parse(s, loc, tokens):  # @UnusedVariable
    dpname = tokens['dpname']
    load_arg = tokens['load_arg']
    return LoadCommand(dpname, load_arg)

load_expr.setParseAction(load_parse)

def parse_line(line):
    from mocdp.lang.blocks import parse_wrap
    return parse_wrap(line_expr, line)[0]
