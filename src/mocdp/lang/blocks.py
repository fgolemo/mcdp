# -*- coding: utf-8 -*-

from conf_tools import (ConfToolsException, SemanticMistakeKeyNotFound,
    instantiate_spec)
from contracts import contract, describe_value
from contracts.utils import indent, raise_desc, raise_wrapped
from mocdp.comp import (CompositeNamedDP, Connection, Context, NamedDP,
    NotConnected, SimpleWrap, dpwrap)
from mocdp.configuration import get_conftools_dps, get_conftools_nameddps
from mocdp.dp import (Constant, GenericUnary, Identity, InvMult2, Limit, Max,
    Max1, Min, PrimitiveDP, Product, ProductN, Sum, SumN)
from mocdp.dp.dp_sum import SumUnitsNotCompatible, check_sum_units_compatible
from mocdp.exceptions import DPInternalError, DPSemanticError
from mocdp.lang.parts import CDPLanguage
from mocdp.posets import (NotBelongs, NotLeq, PosetProduct, Rcomp,
    get_types_universe, mult_table, mult_table_seq)
from mocdp.posets.space import NotEqual


CDP = CDPLanguage


def eval_statement(r, context):

    if isinstance(r, Connection):
        context.add_connection(r)
    
    elif isinstance(r, CDP.Constraint):
        resource = eval_rvalue(r.rvalue, context)
        function = eval_lfunction(r.function, context)

        R1 = context.get_rtype(resource)
        F2 = context.get_ftype(function)
        
        tu = get_types_universe()

        if not tu.equal(R1, F2):
            try:
                tu.check_leq(R1, F2)
            except NotLeq as e:
                msg = 'Constraint between incompatible spaces.'
                raise_wrapped(DPSemanticError, e, msg)

            map1, _map2 = tu.get_embedding(R1, F2)

            conversion = GenericUnary(R1, F2, map1)
            conversion_ndp = dpwrap(conversion, '_in', '_out')

            name = context.new_name('_conversion')
            context.add_ndp(name, conversion_ndp)

            c1 = Connection(dp1=resource.dp, s1=resource.s,
                       dp2=name, s2='_in')
            context.add_connection(c1)
            resource = CDP.Resource(name, '_out')

        else:
            # print('Spaces are equal: %s and %s' % (R1, F2))
            pass

        c = Connection(dp1=resource.dp, s1=resource.s,
                       dp2=function.dp, s2=function.s)
        context.add_connection(c)
    
    elif isinstance(r, CDP.SetName):
        name = r.name
        ndp = eval_dp_rvalue(r.dp_rvalue, context)
        context.add_ndp(name, ndp)
        
    elif isinstance(r, CDP.SetNameResource):
        name = r.name
        rvalue = eval_rvalue(r.rvalue, context)
        context.var2resource[name] = rvalue

    elif isinstance(r, CDP.SetNameConstant):
        if r.name in context.constants:
            msg = 'Constant %r already set.' % r.name
            raise DPSemanticError(msg, where=r.where)
        context.constants[r.name] = r.constant_value

    elif isinstance(r, CDP.ResStatement):
        # requires r.rname [r.unit]
        F = r.unit
        ndp = dpwrap(Identity(F), r.rname, r.rname)
        context.add_ndp_res(r.rname, ndp)
        return CDP.Function(context.get_name_for_res_node(r.rname), r.rname)
    
    elif isinstance(r, CDP.FunStatement):
        F = r.unit
        ndp = dpwrap(Identity(F), r.fname, r.fname)
        context.add_ndp_fun(r.fname, ndp)
        return CDP.Resource(context.get_name_for_fun_node(r.fname), r.fname)
    
    elif isinstance(r, CDP.FunShortcut1):  # provides fname using name
        B = CDP.Function(r.name, r.fname)
        F = context.get_ftype(B)
        A = eval_statement(CDP.FunStatement(r.fname, F), context)
        eval_statement(CDP.Constraint(function=B, rvalue=A), context)

    elif isinstance(r, CDP.ResShortcut1):  # requires rname for name
        # resource rname [r0]
        # rname >= name.rname
        A = CDP.Resource(r.name, r.rname)
        R = context.get_rtype(A)
        B = eval_statement(CDP.ResStatement(r.rname, R), context)
        # B >= A
        eval_statement(CDP.Constraint(function=B, rvalue=A), context)
        # eval_rvalue wants Resource or NewFunction
        # eval_lfunction wants Function or NewResource

    elif isinstance(r, CDP.FunShortcut2):  # provides rname <= (lf)
        B = eval_lfunction(r.lf, context)
        assert isinstance(B, CDP.Function)
        F = context.get_ftype(B)
        A = eval_statement(CDP.FunStatement(r.fname, F), context)
        eval_statement(CDP.Constraint(function=B, rvalue=A), context)

    elif isinstance(r, CDP.ResShortcut2):  # requires rname >= (rvalue)
        A = eval_rvalue(r.rvalue, context)
        assert isinstance(A, CDP.Resource)
        R = context.get_rtype(A)
        B = eval_statement(CDP.ResStatement(r.rname, R), context)
        # B >= A
        eval_statement(CDP.Constraint(function=B, rvalue=A), context)

        # ndp = eval_dp_rvalue(r.rvalue, context)
    elif isinstance(r, CDP.MultipleStatements):
        for s in r.statements:
            eval_statement(s, context)
    else:
        raise DPInternalError('Cannot interpret %s' % describe_value(r))
    
def interpret_commands(res):
    context = Context()
    
    for r in res:
        try:
            eval_statement(r, context)
        except DPSemanticError as e:
            if e.where is None:
                raise DPSemanticError(str(e), where=r.where)
            raise

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

        if isinstance(r, NamedDP):
            return r

        if isinstance(r, CDP.LoadCommand):
            library = get_conftools_nameddps()
            load_arg = r.load_arg
            try:
                _, ndp = library.instance_smarter(load_arg)
            except ConfToolsException as e:
                msg = 'Cannot load predefined DP %s.' % load_arg.__repr__()
                raise_wrapped(DPSemanticError, e, msg)

            return ndp

        if isinstance(r, CDP.DPWrap):
            fun = r.fun
            res = r.res
            impl = r.impl

            dp = eval_pdp(impl, context)

            fnames = [f.fname for f in fun]
            rnames = [r.rname for r in res]

            if len(fnames) == 1:
                use_fnames = fnames[0]
            else:
                use_fnames = fnames
            if len(rnames) == 1:
                use_rnames = rnames[0]
            else:
                use_rnames = rnames

            try:
                w = SimpleWrap(dp=dp, fnames=use_fnames, rnames=use_rnames)
            except ValueError as e:
                raise DPSemanticError(str(e), r.where)

            ftypes = w.get_ftypes(fnames)
            rtypes = w.get_rtypes(rnames)
            ftypes_expected = PosetProduct(tuple([f.unit for f in fun]))
            rtypes_expected = PosetProduct(tuple([r.unit for r in res]))

            try:
                tu = get_types_universe()
                tu.check_equal(ftypes, ftypes_expected)
                tu.check_equal(rtypes, rtypes_expected)
            except NotEqual as e:
                msg = 'The types in the description do not match.'
                raise_wrapped(DPSemanticError, e, msg,
                           ftypes=ftypes,
                           ftypes_expected=ftypes_expected,
                           rtypes=rtypes,
                           rtypes_expected=rtypes_expected, compact=True)

            return w

        if isinstance(r, CDP.AbstractAway):
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

        if isinstance(r, CDP.MakeTemplate):
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
        
        if isinstance(r, CDP.Compact):
            ndp = eval_dp_rvalue(r.dp_rvalue, context)
            if isinstance(ndp, CompositeNamedDP):
                return ndp.compact()
            else:
                msg = 'Cannot compact primitive NDP.'
                raise_desc(DPSemanticError, msg, ndp=ndp.repr_long())

    except DPSemanticError as e:
        if e.where is None:
            e.where = r.where
        raise e

    raise DPInternalError('Invalid dprvalue: %s' % str(r))

@contract(returns=PrimitiveDP)
def eval_pdp(r, context):  # @UnusedVariable
    if isinstance(r, CDP.LoadDP):
        name = r.name
        try:
            _, dp = get_conftools_dps().instance_smarter(name)
        except SemanticMistakeKeyNotFound as e:
            raise DPSemanticError(str(e), r.where)

        return dp

    if isinstance(r, CDP.PDPCodeSpec):
        function = r.function
        arguments = r.arguments
        res = instantiate_spec([function, arguments])
        return res
            
    raise DPInternalError('Invalid pdp rvalue: %s' % str(r))

@contract(returns=CDP.Function)
def eval_lfunction(lf, context):
    if isinstance(lf, CDP.Function):
        if not lf.dp in context.names:
            msg = 'Unknown dp (%r.%r)' % (lf.dp, lf.s)
            raise DPSemanticError(msg, where=lf.where)

#         warnings.warn('Not sure if this was necessary')
#         if context.is_new_resource(lf.dp):
#             msg = 'Cannot use the name %s of an external interface function.' % lf.__repr__()
#             raise DPSemanticError(msg, where=lf.where)

        return lf

    if isinstance(lf, CDP.InvMult):
        ops = lf.ops
        if len(ops) != 2:
            raise DPInternalError('Only 2 expected')

        fs = []

        for op_i in ops:
            fi = eval_lfunction(op_i, context)
            fs.append(fi)

        assert len(fs) == 2



        Fs = map(context.get_ftype, fs)
        R = mult_table(Fs[0], Fs[1])


        dp = InvMult2(R, tuple(Fs))
        ndp = dpwrap(dp, '_input', ['_f0', '_f1'])



        name = context.new_name('_invmult')
        context.add_ndp(name, ndp)

        c1 = Connection(dp2=fs[0].dp, s2=fs[0].s, dp1=name, s1='_f0')
        c2 = Connection(dp2=fs[1].dp, s2=fs[1].s, dp1=name, s1='_f1')
        context.add_connection(c1)
        context.add_connection(c2)

        res = CDP.Function(name, '_input')
        return res



    if isinstance(lf, CDP.NewResource):
        rname = lf.name
        try:
            dummy_ndp = context.get_ndp_res(rname)
        except ValueError as e:
            msg = 'New resource name %r not declared.' % rname
            msg += '\n%s' % str(e)
            raise DPSemanticError(msg, where=lf.where)

        return CDP.Function(context.get_name_for_res_node(rname),
                        dummy_ndp.get_fnames()[0])

    if isinstance(lf, CDP.NewLimit):
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

        return CDP.Function(n, sn)

    msg = 'Cannot eval_lfunction(%s)' % lf.__repr__()
    raise DPInternalError(msg)

# @contract(returns=Resource)
def eval_rvalue(rvalue, context):
    # wants Resource or NewFunction
    try:
        
        if isinstance(rvalue, CDP.Resource):
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
            return CDP.Resource(name, nres)

        if isinstance(rvalue, CDP.Mult):
            a, F1, b, F2 = eval_ops(rvalue)

            try:
                R = mult_table(F1, F2)
            except ValueError as e:
                msg = 'CDP is very strongly typed...'
                raise_wrapped(DPInternalError, e, msg)

            dp = Product(F1, F2, R)
            nprefix, na, nb, nres = 'times', 'p0', 'p1', 'product'

            return add_binary(dp, nprefix, na, nb, nres)


        if isinstance(rvalue, CDP.Plus):
            a, F1, b, F2 = eval_ops(rvalue)
            if not F1 == F2:
                msg = 'Incompatible units: %s and %s' % (F1, F2)
                raise_desc(DPSemanticError, msg, rvalue=rvalue)

            dp = Sum(F1)
            nprefix, na, nb, nres = 'add', 's0', 's1', 'sum'

            return add_binary(dp, nprefix, na, nb, nres)

        if isinstance(rvalue, CDP.PlusN):
            ops = rvalue.ops
            assert len(ops) > 1
            op_rs = []
            op_Rs = []
            for op in ops:
                op_r = eval_rvalue(op, context)
                op_rs.append(op_r)
                op_R = context.get_rtype(op_r)
                op_Rs.append(op_R)

            try:
                check_sum_units_compatible(tuple(op_Rs))
            except SumUnitsNotCompatible as e:
                msg = 'Incompatible units found: %s' % str(e)
                raise DPSemanticError(msg, where=rvalue.where)
                # raise_wrapped(DPSemanticError, e, msg, rvalue=rvalue)
            except BaseException as e:
                raise_wrapped(DPInternalError, e, '', op_Rs=op_Rs)

            dp = SumN(tuple(op_Rs), op_Rs[0])

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
            
            return CDP.Resource(name, nres)

        if isinstance(rvalue, CDP.MultN):
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

            return CDP.Resource(name, nres)


        if isinstance(rvalue, CDP.OpMax):

            if isinstance(rvalue.a, CDP.ValueWithUnits0):
                b = eval_rvalue(rvalue.b, context)
                # print('a is constant')
                name = context.new_name('max1')
                ndp = dpwrap(Max1(rvalue.a.unit, rvalue.a.value), '_in', '_out')
                context.add_ndp(name, ndp)
                c = Connection(dp1=b.dp, s1=b.s, dp2=name, s2='_in')
                context.add_connection(c)
                return CDP.Resource(name, '_out')

            a = eval_rvalue(rvalue.a, context)

            if isinstance(rvalue.b, CDP.ValueWithUnits0):
                # print('using straight')
                name = context.new_name('max1')
                ndp = dpwrap(Max1(rvalue.b.unit, rvalue.b.value), '_in', '_out')
                context.add_ndp(name, ndp)
                c = Connection(dp1=a.dp, s1=a.s, dp2=name, s2='_in')
                context.add_connection(c)
                return CDP.Resource(name, '_out')

            b = eval_rvalue(rvalue.b, context)

            F1 = context.get_rtype(a)
            F2 = context.get_rtype(b)

            print context.names[a.dp].repr_long()
            print context.names[b.dp].repr_long()
            if not (F1 == F2):
                msg = 'Incompatible units for Max(): %s and %s' % (F1, F2)
                msg += '%s and %s' % (type(F1), type(F2))
                raise DPSemanticError(msg, where=rvalue.where)

            dp = Max(F1)
            nprefix, na, nb, nres = 'opmax', 'm0', 'm1', 'max'

            return add_binary(dp, nprefix, na, nb, nres)

        if isinstance(rvalue, CDP.OpMin):
            a, F1, b, F2 = eval_ops(rvalue)
            if not (F1 == F2):
                msg = 'Incompatible units: %s and %s' % (F1, F2)
                raise DPSemanticError(msg, where=rvalue.where)

            dp = Min(F1)
            nprefix, na, nb, nres = 'opmin', 'm0', 'm1', 'min'

            return add_binary(dp, nprefix, na, nb, nres)

        if isinstance(rvalue, CDP.ValueWithUnits):
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
            return CDP.Resource(nres, nres)

        if isinstance(rvalue, CDP.VariableRef):
            if rvalue.name in context.constants:
                return eval_rvalue(context.constants[rvalue.name], context)
            else:
                msg = 'Variable %r not found' % rvalue.name
                raise DPSemanticError(msg, where=rvalue.where)

        if isinstance(rvalue, CDP.NewFunction):
            fname = rvalue.name

            if rvalue.name in context.constants:
                return eval_rvalue(context.constants[rvalue.name], context)

            if fname in context.var2resource:
                return context.var2resource[fname]

            try:
                dummy_ndp = context.get_ndp_fun(fname)
            except ValueError as e:
                msg = 'New function name %r not declared.' % fname
                msg += '\n%s' % str(e)
                raise DPSemanticError(msg, where=rvalue.where)

            s = dummy_ndp.get_rnames()[0]
            return CDP.Resource(context.get_name_for_fun_node(fname), s)

        if isinstance(rvalue, CDP.GenericNonlinearity):
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

            return CDP.Resource(name, rname)

        msg = 'Cannot evaluate %s as rvalue.' % rvalue.__repr__()
        raise ValueError(msg)
    except DPSemanticError as e:
        if e.where is None:
            raise DPSemanticError(str(e), where=rvalue.where)
        raise e

