# -*- coding: utf-8 -*-
from .parts import Constraint, LoadCommand, SetName
from conf_tools.code_specs import instantiate_spec
from contracts import contract, describe_value
from contracts.utils import raise_desc, indent, raise_wrapped
from mocdp.comp.connection import Connection
from mocdp.comp.interfaces import NamedDP
from mocdp.comp.wrap import SimpleWrap, dpwrap
from mocdp.configuration import get_conftools_dps, get_conftools_nameddps
from mocdp.dp.dp_identity import Identity
from mocdp.dp.dp_max import Max, Min
from mocdp.dp.dp_sum import Product, Sum
from mocdp.dp.primitive import PrimitiveDP
from mocdp.lang.parts import Function, NewResource, OpMax, OpMin, Plus, Resource
from mocdp.lang.syntax import (DPSyntaxError, DPWrap, FunStatement, LoadDP,
    PDPCodeSpec, ResStatement)
from mocdp.posets.rcomp import mult_table
from mocdp.exceptions import DPSemanticError, DPInternalError
from contracts.syntax import e

class Context():
    def __init__(self):
        self.names = {}  # name -> ndp
        # for a new function or new resource, the ndp shows up twice
        # both in "names" as well as newfunctions, newresources
        self.newfunctions = {}  # name -> ndp
        self.newresources = {}  # name -> ndp
        self.connections = []

    def info(self, s):
#         print(s)
        pass

    def add_ndp(self, name, ndp):
        self.info('Adding name %r = %r' % (name, ndp))
        if name in self.names:
            # where?
            raise DPSemanticError('Repeated identifier %r.' % name)
        self.names[name] = ndp

    def add_ndp_fun(self, name, ndp):
        self.info('Adding new function %r' % str(name))
        self.add_ndp(name, ndp)
        self.newfunctions[name] = ndp

    def add_ndp_res(self, name, ndp):
        self.info('Adding new resource %r' % str(name))
        self.add_ndp(name, ndp)
        self.newresources[name] = ndp

    def add_connection(self, c):
        self.info('Adding connection %r' % str(c))
        if not c.dp1 in self.names:
            raise_desc(DPSemanticError, 'Invalid connection: %r not found.' % c.dp1,
                       names=self.names, c=c)

        if c.dp2 in self.newfunctions:
            raise_desc(DPSemanticError, "Cannot add connection to external interface %r." % c.dp1,
                       newfunctions=self.newfunctions, c=c)

        if c.dp1 in self.newresources:
            raise_desc(DPSemanticError, "Cannot add connection to external interface %r." % c.dp2,
                       newresources=self.newresources, c=c)

        self.names[c.dp1].rindex(c.s1)

        if not c.dp2 in self.names:
            raise_desc(DPSemanticError, 'Invalid connection: %r not found.' % c.dp2,
                       names=self.names, c=c)

        self.names[c.dp2].findex(c.s2)

        self.connections.append(c)

    def new_name(self, prefix):
        for i in range(1, 10):
            cand = prefix + '%d' % i
            if not cand in self.names:
                return cand
        assert False

    @contract(a=Resource)
    def get_rtype(self, a):
        """ Gets the type of a resource, raises DPSemanticError if not present. """
        if not a.dp in self.names:
            msg = "Cannot find dp %r." % a
            raise DPSemanticError(msg)
        dp = self.names[a.dp]
        if not a.s in dp.get_rnames():
            msg = "Design problem %r does not have resource %r." % (a.dp, a.s)
            raise DPSemanticError(msg)
        return dp.get_rtype(a.s)


def interpret_commands(res):
    context = Context()
    
    for r in res:
        try:
            if isinstance(r, Connection):
                context.add_connection(r)


            elif isinstance(r, Constraint):
                resource = eval_rvalue(r.rvalue, context)
                function = eval_lfunction(r.function, context)
                c = Connection(dp1=resource.dp, s1=resource.s,
                               dp2=function.dp, s2=function.s)
                context.add_connection(c)

            elif isinstance(r, SetName):
                name = r.name
                ndp = eval_dp_rvalue(r.dp_rvalue, context)
                context.add_ndp(name, ndp)

            elif isinstance(r, ResStatement):
                F = r.unit
                ndp = dpwrap(Identity(F), r.rname, r.rname)
                context.add_ndp_res(r.rname, ndp)

            elif isinstance(r, FunStatement):
                F = r.unit
                ndp = dpwrap(Identity(F), r.fname, r.fname)
                context.add_ndp_fun(r.fname, ndp)

            else:
                raise DPInternalError('Cannot interpret %s' % describe_value(r))
        except DPSemanticError as e:
            if e.where is None:
                raise DPSemanticError(str(e), where=r.where)
            raise
            
    check_missing_connections(context)

    if not context.names:
        raise DPSemanticError('Empty model')

    from mocdp.comp.connection import dpgraph
    return dpgraph(context.names, context.connections, split=[])


def check_missing_connections(context):
    """ Checks that all resources and functions are connected. """

    # now look for unconnected functions and resources
    connected_fun = set()  # contains (name, f)
    connected_res = set()  # contains (name, f)
    for c in context.connections:
        connected_fun.add((c.dp2, c.s2))
        connected_res.add((c.dp1, c.s1))
        
    available_fun = set()
    available_res = set()
    # look for the open connections
    for n, ndp in context.names.items():
        if n in context.newfunctions or n in context.newresources:
            continue
        for fn in ndp.get_fnames():
            available_fun.add((n, fn))
        for rn in ndp.get_rnames():
            available_res.add((n, rn))

#     print ('available_fun: %s' % available_fun)
#     print ('available_res: %s' % available_res)
#     print ('connected_fun: %s' % connected_fun)
#     print ('connected_res: %s' % connected_res)

    unconnected_fun = available_fun - connected_fun
    unconnected_res = available_res - connected_res
#     print ('unconnected_res: %s' % unconnected_res)
#     print ('unconnected_fun: %s' % unconnected_fun)

    s = ""
    if unconnected_fun:
        s += "There are some unconnected functions:"
        for n, fn in unconnected_fun:
            s += '\n- function %r of dp %r' % (fn, n)
            msg = 'One way to fix this is to add an explicit function:\n'
            fn2 = fn + '_'
            fix = "provides %s [unit]" % fn2
            fix += '\n' + "%s.%s >= %s" % (fn, n, fn2)
            msg += indent(fix, '    ')
            s += '\n' + indent(msg, 'help: ')

    if unconnected_res:
        s += "There are some unconnected resources:"
        for n, rn in unconnected_res:
            s += '\n- resource %s of dp %r' % (rn, n)
            msg = 'One way to fix this is to add an explicit resource:\n'
            rn2 = rn + '_'
            fix = "requires %s [unit]" % rn2
            fix += '\n' + "%s >= %s.%s" % (rn2, n, rn)
            msg += indent(fix, '    ')
            s += '\n' + indent(msg, 'help: ')

    if s:
        raise DPSemanticError(s)

@contract(returns=NamedDP)
def eval_dp_rvalue(r, context):  # @UnusedVariable
    library = get_conftools_nameddps()
    if isinstance(r, NamedDP):
        return r

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
def eval_pdp(r, context):  # @UnusedVariable
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

@contract(returns=Function)
def eval_lfunction(lf, context):
    if isinstance(lf, Function):
        if not lf.dp in context.names:
            msg = 'Unknown dp (%r.%r)' % (lf.dp, lf.s)
            raise DPSyntaxError(msg, where=lf.where)

        if lf.dp in context.newresources:
            msg = 'Cannot use the name of an external interface function.'
            raise DPSemanticError(msg, where=lf.where)

        return lf

    if isinstance(lf, NewResource):
        if not lf.name in context.names:
            msg = 'New resource name %r not declared.' % lf.name
            msg += '\n known names: %s' % list(context.names)
            raise DPSyntaxError(msg, where=lf.where)
        return Function(lf.name, context.names[lf.name].get_fnames()[0])

    raise ValueError(lf)

# @contract(returns=Resource)
def eval_rvalue(rvalue, context):
    try:
        from .parts import Mult, NewFunction

        if isinstance(rvalue, Resource):
            if not rvalue.dp in context.names:
                msg = 'Unknown dp (%r.%r)' % (rvalue.dp, rvalue.s)
                raise DPSemanticError(msg, where=rvalue.where)


            ndp = context.names[rvalue.dp]
            if not rvalue.s in ndp.get_rnames():
                msg = 'Unknown resource %r.' % (rvalue.s)
                msg += '\nThe design problem %r evaluates to:' % rvalue.dp
                msg += '\n' + indent(ndp.repr_long(), '  ')
                raise DPSemanticError(msg, where=rvalue.where)

            return rvalue

        def eval_ops(rvalue):
            """ Returns a, F1, b, F2 """
            a = eval_rvalue(rvalue.a, context)
            b = eval_rvalue(rvalue.b, context)
            F1 = context.get_rtype(a)
            F2 = context.get_rtype(b)
            return a, F1, b, F2

        def add_binary(dp, nprefix, na, nb, nres):
            ndp = dpwrap(dp, [na, nb], nres)
            name = context.new_name(nprefix)
            c1 = Connection(dp1=a.dp, s1=a.s, dp2=name, s2=na)
            c2 = Connection(dp1=b.dp, s1=b.s, dp2=name, s2=nb)
            context.add_ndp(name, ndp)
            context.add_connection(c1)
            context.add_connection(c2)
            return Resource(name, nres)

        if isinstance(rvalue, Mult):
            a, F1, b, F2 = eval_ops(rvalue)

            try:
                R = mult_table(F1, F2)
            except ValueError as e:
                msg = 'CDP is very strongly typed...'
                raise_wrapped(DPInternalError, e, msg)

            dp = Product(F1, F2, R)
            nprefix, na, nb, nres = 'times', 'p0', 'p1', 'product'

            return add_binary(dp, nprefix, na, nb, nres)


        if isinstance(rvalue, Plus):
            a, F1, b, F2 = eval_ops(rvalue)
            if not F1 == F2:
                msg = 'Incompatible units: %s and %s' % (F1, F2)
                raise_desc(DPSemanticError, msg, rvalue=rvalue)

            dp = Sum(F1)
            nprefix, na, nb, nres = 'add', 's0', 's1', 'sum'

            # TODO: this will raise an exception
            # nprefix, na, nb, nres = 'add', 'p0', 'p1', 'sum'

            return add_binary(dp, nprefix, na, nb, nres)

        if isinstance(rvalue, OpMax):
            a, F1, b, F2 = eval_ops(rvalue)
            if not (F1 == F2):
                msg = 'Incompatible units: %s and %s' % (F1, F2)
                raise DPSyntaxError(msg, where=rvalue.where)

            dp = Max(F1)
            nprefix, na, nb, nres = 'opmax', 'm0', 'm1', 'max'

            return add_binary(dp, nprefix, na, nb, nres)

        if isinstance(rvalue, OpMin):
            a, F1, b, F2 = eval_ops(rvalue)
            if not (F1 == F2):
                msg = 'Incompatible units: %s and %s' % (F1, F2)
                raise DPSyntaxError(msg, where=rvalue.where)

            dp = Min(F1)
            nprefix, na, nb, nres = 'opmin', 'm0', 'm1', 'min'

            return add_binary(dp, nprefix, na, nb, nres)

        if isinstance(rvalue, NewFunction):
            n = rvalue.name
            if not n in context.names:
                msg = 'New function name %r not declared.' % n
                msg += '\n known names: %s' % list(context.names)
                raise DPSyntaxError(msg, where=rvalue.where)
            s = context.names[n].get_rnames()[0]
            return Resource(n, s)

        raise ValueError(rvalue)
    except DPSemanticError as e:
        if e.where is None:
            raise DPSemanticError(str(e), where=rvalue.where)
        raise e

