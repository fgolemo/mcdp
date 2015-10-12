from .parts import Constraint, LoadCommand, SetName
from conf_tools.code_specs import instantiate_spec
from contracts import contract, describe_value
from contracts.utils import raise_desc, raise_wrapped
from mocdp.comp.connection import Connection
from mocdp.comp.interfaces import NamedDP
from mocdp.comp.wrap import SimpleWrap, dpwrap
from mocdp.configuration import get_conftools_dps, get_conftools_nameddps
from mocdp.dp.dp_identity import Identity
from mocdp.dp.dp_sum import Product, Sum
from mocdp.dp.primitive import PrimitiveDP
from mocdp.lang.syntax import (DPSyntaxError, DPWrap, FunStatement, LoadDP,
    PDPCodeSpec, ResStatement)
from mocdp.posets.rcomp import mult_table
from mocdp.lang.parts import Plus

class Context():
    def __init__(self):
        self.names = {}
        self.connections = []
        self.newfunctions = {}
        self.newresources = {}

    def info(self, s):
        print(s)
        pass

    def add_ndp(self, name, ndp):
        self.info('Adding name %r = %r' % (name, ndp))
        if name in self.names:
            raise ValueError('Already know %r' % name)
        self.names[name] = ndp

    def add_connection(self, c):
        self.info('Adding connection %r' % str(c))
        if not c.dp1 in self.names:
            raise_desc(ValueError, 'Invalid connection: %r not found.' % c.dp1,
                       names=self.names, c=c)

        self.names[c.dp1].rindex(c.s1)

        if not c.dp2 in self.names:
            raise_desc(ValueError, 'Invalid connection: %r not found.' % c.dp2,
                       names=self.names, c=c)

        self.names[c.dp2].findex(c.s2)

        self.connections.append(c)

    def new_name(self, prefix):
        for i in range(1, 10):
            cand = prefix + '%d' % i
            if not cand in self.names:
                return cand
        assert False

def interpret_commands(res):
    context = Context()
    
    for r in res:
        if isinstance(r, Connection):
            context.add_connection(r)

        elif isinstance(r, Constraint):
            resource = eval_rvalue(r.rvalue, context)
            c = Connection(dp1=resource.dp, s1=resource.s, dp2=r.dp2, s2=r.s2)
            context.add_connection(c)
            
        elif isinstance(r, SetName):
            name = r.name
            ndp = eval_dp_rvalue(r.dp_rvalue, context)
            context.add_ndp(name, ndp)

        elif isinstance(r, ResStatement):
            print('ignoring %r' % str(r))
            pass

        elif isinstance(r, FunStatement):
            F = r.unit
            ndp = dpwrap(Identity(F), r.fname, 'a')
            context.add_ndp(r.fname, ndp)

        else:
            raise ValueError('Cannot interpret %s' % describe_value(r))

    from mocdp.comp import dpgraph
    try:
        return dpgraph(context.names, context.connections)
    except Exception as e:
        raise_wrapped(Exception, e, 'cannot create',
                      names=context.names, connection=context.connections)

@contract(returns=NamedDP)
def eval_dp_rvalue(r, context):  # @UnusedVariable
    library = get_conftools_nameddps()
    if isinstance(r, LoadCommand):
        load_arg = r.load_arg
        _, ndp = library.instance_smarter(load_arg)
        return ndp

    if isinstance(r, DPWrap):
        fun = r.fun
        res = r.res
        impl = r.impl

        dp = eval_pdp(impl, context)

        fnames = [f.fname for f in fun]
        rnames = [r.rname for r in res]
        if len(fnames) == 1: fnames = fnames[0]
        if len(rnames) == 1: rnames = rnames[0]
        return SimpleWrap(dp=dp, fnames=fnames, rnames=rnames)

    raise ValueError('Invalid dprvalue: %s' % str(r))

@contract(returns=PrimitiveDP)
def eval_pdp(r, context):
    if isinstance(r, LoadDP):
        name = r.name
        _, dp = get_conftools_dps().instance_smarter(name)
        return dp

    if isinstance(r, PDPCodeSpec):
        function = r.function
        arguments = r.arguments
        res = instantiate_spec([function, arguments])
        return res
            
    raise ValueError('Invalid pdp rvalue: %s' % str(r))

# @contract(returns=Resource)
def eval_rvalue(rvalue, context):
    from .parts import Resource, Mult, NewFunction

    if isinstance(rvalue, Resource):
        if not rvalue.dp in context.names:
            msg = 'Unknown dp (%r.%r)' % (rvalue.dp, rvalue.s)
            raise DPSyntaxError(msg, where=rvalue.where)
        return rvalue

    if isinstance(rvalue, Mult):
        a = eval_rvalue(rvalue.a, context)
        b = eval_rvalue(rvalue.b, context)
        F1 = context.names[a.dp].get_rtype(a.s)
        F2 = context.names[b.dp].get_rtype(b.s)
        R = mult_table(F1, F2)
        ndp = dpwrap(Product(F1, F2, R), ['a', 'b'], 'res')
        name = context.new_name('mult')
        c1 = Connection(dp1=a.dp, s1=a.s, dp2=name, s2='a')
        c2 = Connection(dp1=b.dp, s1=b.s, dp2=name, s2='b')
        context.add_ndp(name, ndp)
        context.add_connection(c1)
        context.add_connection(c2)
        return Resource(name, 'res')

    if isinstance(rvalue, Plus):
        a = eval_rvalue(rvalue.a, context)
        b = eval_rvalue(rvalue.b, context)
        F1 = context.names[a.dp].get_rtype(a.s)
        F2 = context.names[b.dp].get_rtype(b.s)
        if not F1 == F2:
            msg = 'Incompatible units: %s and %s' % (F1, F2)
            raise DPSyntaxError(msg, where=rvalue.where)
        # todo: create new signal names
        ndp = dpwrap(Sum(F1), ['p0', 'p1'], 'sum')

        name = context.new_name('sum')
        c1 = Connection(dp1=a.dp, s1=a.s, dp2=name, s2='p0')
        c2 = Connection(dp1=b.dp, s1=b.s, dp2=name, s2='p1')
        context.add_ndp(name, ndp)
        context.add_connection(c1)
        context.add_connection(c2)
        return Resource(name, 'sum')

    if isinstance(rvalue, NewFunction):
        if not rvalue.name in context.names:
            msg = 'New function name %r not declared.' % rvalue.name
            msg += '\n known names: %s' % list(context.names)
            raise DPSyntaxError(msg, where=rvalue.where)
        return Resource(rvalue.name, 'a')

    raise ValueError(rvalue)


