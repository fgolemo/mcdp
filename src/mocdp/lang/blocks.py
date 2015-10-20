# -*- coding: utf-8 -*-
from .parts import (AbstractAway, Constraint, Function, LoadCommand, NewLimit,
    NewResource, OpMax, OpMin, Plus, Resource, SetName, ValueWithUnits)
from conf_tools import (ConfToolsException, SemanticMistakeKeyNotFound,
    instantiate_spec)
from contracts import contract, describe_value
from contracts.utils import indent, raise_desc, raise_wrapped
from mocdp.comp.connection import Connection
from mocdp.comp.interfaces import CompositeNamedDP, NamedDP, NotConnected
from mocdp.comp.wrap import SimpleWrap, dpwrap
from mocdp.configuration import get_conftools_dps, get_conftools_nameddps
from mocdp.dp import (Constant, Identity, Limit, Max, Min, PrimitiveDP, Product,
    Sum)
from mocdp.dp.dp_generic_unary import GenericUnary
from mocdp.dp.dp_sum import ProductN, SumN
from mocdp.exceptions import DPInternalError, DPSemanticError
from mocdp.lang.parts import GenericNonlinearity, MakeTemplate, MultN, PlusN
from mocdp.lang.syntax import (DPWrap, FunStatement, LoadDP, PDPCodeSpec,
    ResStatement)
from mocdp.posets import NotBelongs, PosetProduct
from mocdp.posets.rcomp import Rcomp, mult_table, mult_table_seq
import warnings

class Context():
    def __init__(self):
        self.names = {}  # name -> ndp
        self.connections = []

        self.fnames = []
        self.rnames = []

    def info(self, s):
        # print(s)
        pass

    def add_ndp(self, name, ndp):
        self.info('Adding name %r = %r' % (name, ndp))
        if name in self.names:
            # where?
            raise DPSemanticError('Repeated identifier %r.' % name)
        self.names[name] = ndp

    def get_name_for_fun_node(self, name):
        return '_fun_%s' % name

    def add_ndp_fun(self, fname, ndp):
        name = self.get_name_for_fun_node(fname)
        self.info('Adding new function %r as %r.' % (str(name), fname))
        self.add_ndp(name, ndp)
        self.fnames.append(fname)

    def is_new_function(self, name):
        assert name in self.names
        return '_fun_' in name

    def is_new_resource(self, name):
        assert name in self.names
        return '_res_' in name

    def get_name_for_res_node(self, name):
        return '_res_%s' % name

    def add_ndp_res(self, rname, ndp):
        name = self.get_name_for_res_node(rname)
        self.info('Adding new resource %r as %r ' % (str(name), rname))
        self.add_ndp(name, ndp)
        self.rnames.append(rname)

        # self.newresources[rname] = ndp

    def iterate_new_functions(self):
        for fname in self.fnames:
            name = self.get_name_for_fun_node(fname)
            ndp = self.names[name]
            yield fname, name, ndp

    def iterate_new_resources(self):
        for rname in self.rnames:
            name = self.get_name_for_res_node(rname)
            ndp = self.names[name]
            yield rname, name, ndp
    # for fname, name, ndp in context.iterate_new_functions():


    def get_ndp_res(self, rname):
        name = self.get_name_for_res_node(rname)
        if not name in self.names:
            raise ValueError('Resource name %r (%r) not found in %s.' % (rname, name, list(self.names)))
        return self.names[name]

    def get_ndp_fun(self, fname):
        name = self.get_name_for_fun_node(fname)
        if not name in self.names:
            raise ValueError('Function name %r (%r) not found in %s.' % (fname, name, list(self.names)))
        return self.names[name]

    def add_connection(self, c):
        self.info('Adding connection %r' % str(c))
        if not c.dp1 in self.names:
            raise_desc(DPSemanticError, 'Invalid connection: %r not found.' % c.dp1,
                       names=self.names, c=c)

        if not c.dp2 in self.names:
            raise_desc(DPSemanticError, 'Invalid connection: %r not found.' % c.dp2,
                       names=self.names, c=c)

        warnings.warn('redo this check')

        if self.is_new_function(c.dp2):
            raise_desc(DPSemanticError, "Cannot add connection to external interface %r." % c.dp1,
                        c=c)

        if self.is_new_resource(c.dp1):
            raise_desc(DPSemanticError, "Cannot add connection to external interface %r." % c.dp2,
                        c=c)

        ndp1 = self.names[c.dp1]
        ndp2 = self.names[c.dp2]

        rnames = ndp1.get_rnames()
        if not c.s1 in rnames:
            msg = "Resource %r does not exist (known: %s)" % (c.s1, ", ".join(rnames))
            raise_desc(DPSemanticError, msg, known=rnames)

        fnames = ndp2.get_fnames()
        if not c.s2 in fnames:
            msg = "Function %r does not exist (known: %s)" % (c.s2, ", ".join(fnames))
            raise_desc(DPSemanticError, msg, known=rnames)


        R1 = ndp1.get_rtype(c.s1)
        F2 = ndp2.get_ftype(c.s2)
        if not (R1 == F2):
            msg = 'Connection between different spaces'
            raise_desc(DPSemanticError, msg, F2=F2, R1=R1)

        self.connections.append(c)

    def new_name(self, prefix):
        for i in range(1, 1000):
            cand = prefix + '%d' % i
            if not cand in self.names:
                return cand
        assert False, 'cannot find name? %r' % cand

    def _fun_name_exists(self, fname):
        for ndp in self.names.values():
            if fname in ndp.get_fnames():
                return True
        return False

    def _res_name_exists(self, rname):
        for ndp in self.names.values():
            if rname in ndp.get_rnames():
                return True
        return False

    def new_fun_name(self, prefix):
        for i in range(1, 1000):
            cand = prefix + '%d' % i
            if not self._fun_name_exists(cand):
                return cand
        assert False, 'cannot find name? %r' % cand

    def new_res_name(self, prefix):
        for i in range(1, 10000):
            cand = prefix + '%d' % i
            if not self._res_name_exists(cand):
                return cand
        assert False, 'cannot find name? %r' % cand

    @contract(a=Resource)
    def get_rtype(self, a):
        """ Gets the type of a resource, raises DPSemanticError if not present. """
        if not a.dp in self.names:
            msg = "Cannot find resource %r." % a
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

    # if not context.names:
    #    raise DPSemanticError('Empty model')

    return CompositeNamedDP(context=context)

def get_missing_connections(context):
    connected_fun = set()  # contains (name, f)
    connected_res = set()  # contains (name, f)
    for c in context.connections:
        connected_fun.add((c.dp2, c.s2))
        connected_res.add((c.dp1, c.s1))

    available_fun = set()
    available_res = set()
    # look for the open connections
    for n, ndp in context.names.items():

        if not context.is_new_function(n):
            for fn in ndp.get_fnames():
                available_fun.add((n, fn))

        if not context.is_new_resource(n):
            for rn in ndp.get_rnames():
                available_res.add((n, rn))

#     print('context.connections: %s' % context.connections)
#     print('context.newfunctions: %s' % context.newfunctions)
#     print('context.newresources: %s' % context.newresources)
#     print ('available_fun: %s' % available_fun)
#     print ('available_res: %s' % available_res)
#     print ('connected_fun: %s' % connected_fun)
#     print ('connected_res: %s' % connected_res)

    unconnected_fun = available_fun - connected_fun
    unconnected_res = available_res - connected_res

#     print('context.connections: %s' % context.connections)
#     print('context.newfunctions: %s' % context.newfunctions)
#     print('context.newresources: %s' % context.newresources)
#     print ('available_fun: %s' % available_fun)
#     print ('available_res: %s' % available_res)
#     print ('connected_fun: %s' % connected_fun)
#     print ('connected_res: %s' % connected_res)
#     print ('unconnected_res: %s' % unconnected_res)
#     print ('unconnected_fun: %s' % unconnected_fun)

    return unconnected_fun, unconnected_res

def check_missing_connections(context):
    """ Checks that all resources and functions are connected. """

    unconnected_fun, unconnected_res = get_missing_connections(context)

    s = ""
    if unconnected_fun:
        s += "There are some unconnected functions:"
        for n, fn in unconnected_fun:
            s += '\n- function %r of dp %r' % (fn, n)
            msg = 'One way to fix this is to add an explicit function:\n'
            fn2 = 'f'
            fix = "provides %s [unit]" % fn2
            if context.is_new_resource(n):
                ref = n
            else:
                ref = '%s.%s' % (n, fn)
            fix += '\n' + "%s >= %s" % (ref, fn2)
            msg += indent(fix, '    ')
            s += '\n' + indent(msg, 'help: ')

    if unconnected_res:
        s += "\nThere are some unconnected resources:"
        for n, rn in unconnected_res:
            s += '\n- resource %s of dp %r' % (rn, n)
            msg = 'One way to fix this is to add an explicit resource:\n'
            rn2 = 'r'
            fix = "requires %s [unit]" % rn2
            if context.is_new_function(n):
                ref = n
            else:
                ref = '%s.%s' % (n, rn)
            # todo: omit '.' if n is
            fix += '\n' + "%s >= %s" % (rn2, ref)
            msg += indent(fix, '    ')
            s += '\n' + indent(msg, 'help: ')


    # This should count as unconnected:
# cdp {
#     a = template cdp {}
#     b = template cdp {}
# }
    for name, ndp in context.names.items():
        # anything that has both zero functions and zero resources is unconnected
        rnames = ndp.get_rnames()
        fnames = ndp.get_fnames()
        if not rnames and not fnames:
            s += "\nBlock %r has no functions or resources." % name

    if s:
        raise NotConnected(s)
    

@contract(returns=NamedDP)
def eval_dp_rvalue(r, context):  # @UnusedVariable
    try:
        library = get_conftools_nameddps()
        if isinstance(r, NamedDP):
            return r

        if isinstance(r, LoadCommand):
            load_arg = r.load_arg
            try:
                _, ndp = library.instance_smarter(load_arg)
            except ConfToolsException as e:
                msg = 'Cannot load predefined DP %s.' % load_arg.__repr__()
                raise_wrapped(DPSemanticError, e, msg)

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
            try:
                w = SimpleWrap(dp=dp, fnames=fnames, rnames=rnames)
            except ValueError as e:
                raise DPSemanticError(str(e), r.where)

            return w

        if isinstance(r, AbstractAway):
            ndp = eval_dp_rvalue(r.dp_rvalue, context)
            if isinstance(ndp, SimpleWrap):
                return ndp
            try:
                ndp.check_fully_connected()
            except NotConnected as e:
                msg = 'Cannot abstract away the design problem because it is not connected.'
                raise_wrapped(DPSemanticError, e, msg, compact=True)

            ndpa = ndp.abstract()
            return ndpa

        if isinstance(r, MakeTemplate):
            ndp = eval_dp_rvalue(r.dp_rvalue, context)

            fnames = ndp.get_fnames()
            ftypes = ndp.get_ftypes(fnames)
            rnames = ndp.get_rnames()
            rtypes = ndp.get_rtypes(rnames)

            if len(fnames) == 1:
                fnames = fnames[0]
                F = ftypes[0]
            else:
                F = PosetProduct(tuple(ftypes))

            if len(rnames) == 1:
                rnames = rnames[0]
                R = rtypes[0]
            else:
                R = PosetProduct(tuple(rtypes))

            from mocdp.comp.template_imp import Dummy

            dp = Dummy(F, R)
            res = SimpleWrap(dp, fnames, rnames)
            return res

    except DPSemanticError as e:
        if e.where is None:
            e.where = r.where
        raise e

    raise ValueError('Invalid dprvalue: %s' % str(r))

@contract(returns=PrimitiveDP)
def eval_pdp(r, context):  # @UnusedVariable
    if isinstance(r, LoadDP):
        name = r.name
        try:
            _, dp = get_conftools_dps().instance_smarter(name)
        except SemanticMistakeKeyNotFound as e:
            raise DPSemanticError(str(e), r.where)

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
            raise DPSemanticError(msg, where=lf.where)

        if context.is_new_resource(lf.dp):
            msg = 'Cannot use the name of an external interface function.'
            raise DPSemanticError(msg, where=lf.where)

        return lf

    if isinstance(lf, NewResource):
        rname = lf.name
        try:
            dummy_ndp = context.get_ndp_res(rname)
        except ValueError as e:
            msg = 'New resource name %r not declared.' % rname
            msg += '\n%s' % str(e)
            raise DPSemanticError(msg, where=lf.where)

        return Function(context.get_name_for_res_node(rname),
                        dummy_ndp.get_fnames()[0])

    if isinstance(lf, NewLimit):
        vu = lf.value_with_unit
        value = vu.value
        F = vu.unit
        # TODO: special conversion int -> float
        try:
            F.belongs(value)
        except NotBelongs as e:
            msg = 'Invalid value provided.'
            raise_wrapped(DPSemanticError, e, msg)

        dp = Limit(F, value)
        n = context.new_name('lim')
        sn = context.new_fun_name('l')
        ndp = dpwrap(dp, sn, [])
        context.add_ndp(n, ndp)

        return Function(n, sn)
        
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
            nres = context.new_res_name(nres)
            na = context.new_fun_name(na)
            nb = context.new_fun_name(nb)

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

            return add_binary(dp, nprefix, na, nb, nres)

        if isinstance(rvalue, PlusN):
            ops = rvalue.ops
            assert len(ops) > 1
            R = None
            op_rs = []
            for op in ops:
                op_r = eval_rvalue(op, context)
                op_rs.append(op_r)
                op_R = context.get_rtype(op_r)
                if R is not None:
                    if not (R == op_R):
                        msg = 'Incompatible units: %s and %s' % (R, op_R)
                        raise_desc(DPSemanticError, msg, rvalue=rvalue)
                R = op_R

            dp = SumN(R, len(ops))

            nres = context.new_res_name('sum')
            fnames = []
            for i, op in enumerate(ops):
                ni = context.new_fun_name('s%s' % i)
                fnames.append(ni)

            ndp = dpwrap(dp, fnames, nres)
            name = context.new_name('sum')
            context.add_ndp(name, ndp)

            for i, op in enumerate(ops):
                c = Connection(dp1=op_rs[i].dp, s1=op_rs[i].s, dp2=name, s2=fnames[i])
                context.add_connection(c)
            
            return Resource(name, nres)

        if isinstance(rvalue, MultN):
            ops = rvalue.ops
            assert len(ops) > 1
            R = None
            op_rs = []
            op_Fs = []
            for op in ops:
                op_r = eval_rvalue(op, context)
                op_rs.append(op_r)
                op_R = context.get_rtype(op_r)
                op_Fs.append(op_R)

            R = mult_table_seq(op_Fs)
            dp = ProductN(tuple(op_Fs), R)

            nres = context.new_res_name('prod')
            fnames = []
            for i, op in enumerate(ops):
                ni = context.new_fun_name('s%s' % i)
                fnames.append(ni)

            ndp = dpwrap(dp, fnames, nres)
            name = context.new_name('prod')
            context.add_ndp(name, ndp)

            for i, op in enumerate(ops):
                c = Connection(dp1=op_rs[i].dp, s1=op_rs[i].s, dp2=name, s2=fnames[i])
                context.add_connection(c)

            return Resource(name, nres)


        if isinstance(rvalue, OpMax):
            a, F1, b, F2 = eval_ops(rvalue)
            if not (F1 == F2):
                msg = 'Incompatible units: %s and %s' % (F1, F2)
                raise DPSemanticError(msg, where=rvalue.where)

            dp = Max(F1)
            nprefix, na, nb, nres = 'opmax', 'm0', 'm1', 'max'

            return add_binary(dp, nprefix, na, nb, nres)

        if isinstance(rvalue, OpMin):
            a, F1, b, F2 = eval_ops(rvalue)
            if not (F1 == F2):
                msg = 'Incompatible units: %s and %s' % (F1, F2)
                raise DPSemanticError(msg, where=rvalue.where)

            dp = Min(F1)
            nprefix, na, nb, nres = 'opmin', 'm0', 'm1', 'min'

            return add_binary(dp, nprefix, na, nb, nres)

        if isinstance(rvalue, ValueWithUnits):
            # implicit conversion from int to float
            unit = rvalue.unit
            value = rvalue.value
            if isinstance(unit, Rcomp):
                if isinstance(value, int):
                    value = float(value)
            try:
                unit.belongs(value)
            except NotBelongs as e:
                raise_wrapped(DPSemanticError, e, "Value is not in the give space.")

            dp = Constant(unit, value)
            nres = context.new_res_name('c')
            ndp = dpwrap(dp, [], nres)
            context.add_ndp(nres, ndp)
            return Resource(nres, nres)

        if isinstance(rvalue, NewFunction):
            fname = rvalue.name

            try:
                dummy_ndp = context.get_ndp_fun(fname)
            except ValueError as e:
                msg = 'New function name %r not declared.' % fname
                msg += '\n%s' % str(e)
                raise DPSemanticError(msg, where=rvalue.where)

            s = dummy_ndp.get_rnames()[0]
            return Resource(context.get_name_for_fun_node(fname), s)

        if isinstance(rvalue, GenericNonlinearity):
            op_r = eval_rvalue(rvalue.op1, context)
            function = rvalue.function
            R_from_F = rvalue.R_from_F
            F = context.get_rtype(op_r)
            R = R_from_F(F)

            dp = GenericUnary(F=F, R=R, function=function)

            fnames = context.new_fun_name('s')
            name = context.new_name(function.__name__)
            rname = context.new_res_name('res')

            ndp = dpwrap(dp, fnames, rname)
            context.add_ndp(name, ndp)

            c = Connection(dp1=op_r.dp, s1=op_r.s, dp2=name, s2=fnames)

            context.add_connection(c)

            return Resource(name, rname)




        raise ValueError(rvalue)
    except DPSemanticError as e:
        if e.where is None:
            raise DPSemanticError(str(e), where=rvalue.where)
        raise e

