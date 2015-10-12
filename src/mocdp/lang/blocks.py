from contracts.interface import ContractSyntaxError, Where
from mocdp.comp.connection import Connection
from mocdp.configuration import get_conftools_nameddps
from pyparsing import (LineEnd, LineStart, Literal, OneOrMore, ParseException,
    ParseFatalException, ParserElement, SkipTo, Suppress, ZeroOrMore)
from mocdp.dp.dp_sum import Product
from mocdp.comp.wrap import dpwrap
from mocdp.posets.rcomp import Rcomp
from mocdp.dp.dp_identity import Identity
from contracts.utils import raise_desc, raise_wrapped


ParserElement.enablePackrat()

ParserElement.setDefaultWhitespaceChars('')

ow = Suppress(ZeroOrMore(Literal(' ')))
DPStart = Suppress(Literal('dp:'))

S = Suppress
EOL = S(LineEnd())
line = SkipTo(LineEnd(), failOn=LineStart() + LineEnd())

blockContent = OneOrMore(line)

comment_line = LineStart() + ow + Literal('#') + S(line) + EOL
indent = Literal(' ' * 4)
dp_model = ZeroOrMore(ow + EOL) + DPStart + EOL + \
        OneOrMore((S(LineStart() + indent) + line + EOL) |
                   S(comment_line))


def dp_model_parse_action(s, loc, tokens):

    lines = filter(None, [t.strip() for t in tokens])

    # remove comment line
    is_comment = lambda x: x[0] == '#'
    lines = [l for l in lines if not is_comment(l)]
    from mocdp.lang.lines import parse_line
    res = map(parse_line, lines)

    return interpret_commands(res)

def interpret_commands(res):
    from mocdp.lang.lines import Constraint
    library = get_conftools_nameddps()
    from mocdp.lang.lines import LoadCommand
    
    class Context():
        def __init__(self):
            self.names = {}
            self.connections = []
        def add_ndp(self, name, ndp):
            if name in self.names:
                raise ValueError('Already know %r' % name)
            self.names[name] = ndp
        def add_connection(self, c):
                
            if not c.dp1 in self.names:
                raise_desc(ValueError, 'Invalid connection', names=self.names, c=c)
            
            self.names[c.dp1].rindex(c.s1)

            if not c.dp2 in self.names:
                raise_desc(ValueError, 'Invalid connection', names=self.names, c=c)

            self.names[c.dp2].findex(c.s2)
                            
            self.connections.append(c)

        def new_name(self, prefix):
            for i in range(1, 10):
                cand = prefix + '%d' % i
                if not cand in self.names:
                    return cand
            assert False

    context = Context()
    
    for r in res:

        if not isinstance(r, (LoadCommand, Connection, Constraint)):
            raise ValueError(r)
        if isinstance(r, LoadCommand):
            name = r.name
            load_arg = r.load_arg
            _, ndp = library.instance_smarter(load_arg)
            context.add_ndp(name, ndp)

        if isinstance(r, Connection):
            context.add_connection(r)

        if isinstance(r, Constraint):
            resource = eval_rvalue(r.rvalue, context)
            c = Connection(dp1=resource.dp, s1=resource.s, dp2=r.dp2, s2=r.s2)
            context.add_connection(c)

    from mocdp.comp.connection import dpgraph
    try:
        return dpgraph(context.names, context.connections)
    except Exception as e:
        raise_wrapped(Exception, e, 'cannot create',
                      names=context.names, connection=context.connections)

# @contract(returns=Resource)
def eval_rvalue(rvalue, context):
    from mocdp.lang.lines import Resource
    from mocdp.lang.lines import Mult

    if isinstance(rvalue, Resource):
        return rvalue

    if isinstance(rvalue, Mult):
        a = eval_rvalue(rvalue.a, context)
        b = eval_rvalue(rvalue.b, context)
        F1 = Rcomp()
        F2 = Rcomp()
        R = Rcomp()
        ndp = dpwrap(Product(F1, F2, R), ['a', 'b'], 'res')
        name = context.new_name('mult')
        c1 = Connection(dp1=a.dp, s1=a.s, dp2=name, s2='a')
        c2 = Connection(dp1=b.dp, s1=b.s, dp2=name, s2='b')
        context.add_ndp(name, ndp)
        context.add_connection(c1)
        context.add_connection(c2)
        return Resource(name, 'res')

    from mocdp.lang.lines import NewFunction

    if isinstance(rvalue, NewFunction):
        F = Rcomp()
        ndp = dpwrap(Identity(F), rvalue.name, 'a')
        name = context.new_name('id')
        context.add_ndp(name, ndp)
        return Resource(name, 'a')

    raise ValueError(rvalue)

dp_model.setParseAction(dp_model_parse_action)

class DPSyntaxError(ContractSyntaxError):
    pass

def parse_wrap(expr, string):
    try:
        return expr.parseString(string, parseAll=True)
    except (ParseException, ParseFatalException) as e:
        where = Where(string, line=e.lineno, column=e.col)
        raise DPSyntaxError(str(e), where=where)

def parse_model(string):
    res = parse_wrap(dp_model, string)[0]

