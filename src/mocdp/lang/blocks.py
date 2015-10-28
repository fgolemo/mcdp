# -*- coding: utf-8 -*-

from conf_tools import (ConfToolsException, SemanticMistakeKeyNotFound,
    instantiate_spec)
from contracts import contract, describe_value
from contracts.utils import indent, raise_desc, raise_wrapped, check_isinstance
from mocdp.comp import (CompositeNamedDP, Connection, Context, NamedDP,
    NotConnected, SimpleWrap, dpwrap)
from mocdp.configuration import get_conftools_dps, get_conftools_nameddps
from mocdp.dp import (Constant, GenericUnary, Identity, InvMult2, Limit, Max,
    Max1, Min, PrimitiveDP, ProductN)
from mocdp.dp.dp_sum import SumN
from mocdp.exceptions import DPInternalError, DPSemanticError
from mocdp.lang.parse_actions import plus_constantsN
from mocdp.lang.parts import CDPLanguage, unwrap_list
from mocdp.posets import (NotBelongs, NotEqual, NotLeq, PosetProduct, Rcomp,
    get_types_universe, mult_table, mult_table_seq)
from mocdp.comp.context import CFunction, CResource


CDP = CDPLanguage
#

def add_constraint(context, resource, function):
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
        resource = context.make_resource(name, '_out')

    else:
        # print('Spaces are equal: %s and %s' % (R1, F2))
        pass

    c = Connection(dp1=resource.dp, s1=resource.s,
                   dp2=function.dp, s2=function.s)
    context.add_connection(c)
    
def eval_statement(r, context):

    if isinstance(r, Connection):
        context.add_connection(r)
    
    elif isinstance(r, CDP.Constraint):
        resource = eval_rvalue(r.rvalue, context)
        function = eval_lfunction(r.function, context)
        add_constraint(context, resource, function)
    
    elif isinstance(r, CDP.SetName):
        name = r.name
        ndp = eval_dp_rvalue(r.dp_rvalue, context)
        context.add_ndp(name, ndp)
        
    elif isinstance(r, CDP.SetNameGeneric):
        name = r.name.value
        right_side = r.right_side

        if name in context.constants:
            msg = 'Constant %r already set.' % name
            raise DPSemanticError(msg, where=r.where)

        if name in context.var2resource:
            msg = 'Resource %r already set.' % name
            raise DPSemanticError(msg, where=r.where)

        try:
            res = eval_constant(right_side, context)
            context.set_constant(name, res)
        except NotConstant:
            # print('Cannot evaluate %r as constant: %s ' % (right_side, e))
            rvalue = eval_rvalue(right_side, context)
            # print('adding as resource')
            context.set_var2resource(name, rvalue)

    elif isinstance(r, CDP.ResStatement):
        # requires r.rname [r.unit]
        F = r.unit.value
        rname = r.rname.value
        ndp = dpwrap(Identity(F), rname, rname)
        context.add_ndp_res(rname, ndp)
        return context.make_function(context.get_name_for_res_node(rname), rname)
    
    elif isinstance(r, CDP.FunStatement):
        F = r.unit.value
        fname = r.fname.value
        ndp = dpwrap(Identity(F), fname, fname)
        context.add_ndp_fun(fname, ndp)
        return context.make_resource(context.get_name_for_fun_node(fname), fname)
    
    elif isinstance(r, CDP.FunShortcut1):  # provides fname using name
        fname = r.fname.value
        B = context.make_function(r.name, fname)
        F = context.get_ftype(B)
        A = eval_statement(CDP.FunStatement('-', r.fname, CDP.Unit(F)), context)
        add_constraint(context, resource=A, function=B)

    elif isinstance(r, CDP.ResShortcut1):  # requires rname for name
        # resource rname [r0]
        # rname >= name.rname
        rname = r.rname.value
        A = context.make_resource(r.name, rname)
        R = context.get_rtype(A)
        B = eval_statement(CDP.ResStatement('-', r.rname, CDP.Unit(R)), context)
        # B >= A
        add_constraint(context, resource=A, function=B)

    elif isinstance(r, CDP.ResShortcut1m):  # requires rname for name

        for rname in unwrap_list(r.rnames):
            A = context.make_resource(r.name, rname.value)
            R = context.get_rtype(A)
            B = eval_statement(CDP.ResStatement('-', rname, CDP.Unit(R)), context)
            add_constraint(context, resource=A, function=B)

    elif isinstance(r, CDP.FunShortcut1m):  # requires rname for name

        for fname in unwrap_list(r.fnames):
            B = context.make_function(r.name, fname.value)
            F = context.get_ftype(B)
            A = eval_statement(CDP.FunStatement('-', fname, CDP.Unit(F)), context)
            add_constraint(context, resource=A, function=B)

    elif isinstance(r, CDP.FunShortcut2):  # provides rname <= (lf)
        B = eval_lfunction(r.lf, context)
        assert isinstance(B, CFunction)
        F = context.get_ftype(B)
        A = eval_statement(CDP.FunStatement('-', r.fname, CDP.Unit(F)), context)
        add_constraint(context, resource=A, function=B)
#         eval_statement(CDP.Constraint(function=B, rvalue=A, prep=None), context)

    elif isinstance(r, CDP.ResShortcut2):  # requires rname >= (rvalue)
        A = eval_rvalue(r.rvalue, context)
        assert isinstance(A, CResource)
        R = context.get_rtype(A)
        B = eval_statement(CDP.ResStatement('-', r.rname, CDP.Unit(R)), context)
        # B >= A
        add_constraint(context, resource=A, function=B)
#         eval_statement(CDP.Constraint(function=B, rvalue=A, prep=None), context)

        # ndp = eval_dp_rvalue(r.rvalue, context)
#     elif isinstance(r, CDP.MultipleStatements):
#         for s in r.statements:
#             eval_statement(s, context)
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
        if isinstance(r, CDP.BuildProblem):
            special_list = r.statements
            statements = unwrap_list(special_list)
            return interpret_commands(statements)

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

            fnames = [f.fname.value for f in fun]
            rnames = [r.rname.value for r in res]

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
            ftypes_expected = PosetProduct(tuple([f.unit.value for f in fun]))
            rtypes_expected = PosetProduct(tuple([r.unit.value for r in res]))

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
#         print('function: %s' % function)
#         print('arguments: %s' % arguments)
        check_isinstance(function, str)
        res = instantiate_spec([function, arguments])
        return res
            
    raise DPInternalError('Invalid pdp rvalue: %s' % str(r))

@contract(returns=CFunction)
def eval_lfunction(lf, context):
    if isinstance(lf, CDP.Function):
        if not lf.dp in context.names:
            msg = 'Unknown dp (%r.%r)' % (lf.dp, lf.s)
            raise DPSemanticError(msg, where=lf.where)

#         warnings.warn('Not sure if this was necessary')
#         if context.is_new_resource(lf.dp):
#             msg = 'Cannot use the name %s of an external interface function.' % lf.__repr__()
#             raise DPSemanticError(msg, where=lf.where)

        return context.make_function(dp=lf.dp, s=lf.s)

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

        res = context.make_function(name, '_input')
        return res



    if isinstance(lf, CDP.NewResource):
        rname = lf.name
        try:
            dummy_ndp = context.get_ndp_res(rname)
        except ValueError as e:
            msg = 'New resource name %r not declared.' % rname
            msg += '\n%s' % str(e)
            raise DPSemanticError(msg, where=lf.where)

        return context.make_function(context.get_name_for_res_node(rname),
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

        return context.make_function(n, sn)

    msg = 'Cannot eval_lfunction(%s)' % lf.__repr__()
    raise DPInternalError(msg)

@contract(returns=CResource)
def eval_rvalue(rvalue, context):
    # wants Resource or NewFunction
    try:
        if isinstance(rvalue, CDP.Resource):
            return context.make_resource(dp=rvalue.dp, s=rvalue.s)
        
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
            return context.make_resource(name, nres)

        if isinstance(rvalue, CDP.MultN):
            return eval_MultN_as_rvalue(rvalue, context)

        if isinstance(rvalue, CDP.PlusN):
            return eval_PlusN_as_rvalue(rvalue, context)

        if isinstance(rvalue, CDP.OpMax):

            if isinstance(rvalue.a, CDP.ValueWithUnits0):
                b = eval_rvalue(rvalue.b, context)
                # print('a is constant')
                name = context.new_name('max1')
                ndp = dpwrap(Max1(rvalue.a.unit, rvalue.a.value), '_in', '_out')
                context.add_ndp(name, ndp)
                c = Connection(dp1=b.dp, s1=b.s, dp2=name, s2='_in')
                context.add_connection(c)
                return context.make_resource(name, '_out')

            a = eval_rvalue(rvalue.a, context)

            if isinstance(rvalue.b, CDP.ValueWithUnits0):
                # print('using straight')
                name = context.new_name('max1')
                ndp = dpwrap(Max1(rvalue.b.unit, rvalue.b.value), '_in', '_out')
                context.add_ndp(name, ndp)
                c = Connection(dp1=a.dp, s1=a.s, dp2=name, s2='_in')
                context.add_connection(c)
                return context.make_resource(name, '_out')

            b = eval_rvalue(rvalue.b, context)

            F1 = context.get_rtype(a)
            F2 = context.get_rtype(b)

#             print context.names[a.dp].repr_long()
#             print context.names[b.dp].repr_long()
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
            # XXX: stuff here
            if isinstance(unit, Rcomp):
                if isinstance(value, int):
                    value = float(value)
            try:
                unit.belongs(value)
            except NotBelongs as e:
                raise_wrapped(DPSemanticError, e, "Value is not in the give space.")
                
            return get_valuewithunits_as_resource(rvalue, context)
        
        if isinstance(rvalue, CDP.VariableRef):
            if rvalue.name in context.constants:
                return eval_rvalue(context.constants[rvalue.name], context)

            elif rvalue.name in context.var2resource:
                return context.var2resource[rvalue.name]

            try:
                dummy_ndp = context.get_ndp_fun(rvalue.name)
            except ValueError as e:
                msg = 'New function name %r not declared.' % rvalue.name
                msg += '\n%s' % str(e)
                raise DPSemanticError(msg, where=rvalue.where)

            s = dummy_ndp.get_rnames()[0]
            return context.make_resource(context.get_name_for_fun_node(rvalue.name), s)

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

            return context.make_resource(name, rname)

        msg = 'Cannot evaluate %s as rvalue.' % rvalue.__repr__()
        raise ValueError(msg)
    except DPSemanticError as e:
        if e.where is None:
            raise DPSemanticError(str(e), where=rvalue.where)
        raise e

class NotConstant(Exception):
    pass

@contract(returns=CDP.ValueWithUnits)
def eval_constant(op, context):
    """ 
        Raises NotConstant if not constant. 
        Returns ValueWithUnits
    """
    
    if isinstance(op, (CDP.Resource)):
        raise NotConstant(str(op))

    if isinstance(op, (CDP.OpMax, CDP.OpMin, CDP.Power)):
        # TODO: can implement optimization
        raise NotConstant(str(op))

    if isinstance(op, CDP.ValueWithUnits):
        return op

    if isinstance(op, CDP.VariableRef):
        if op.name in context.constants:
            return context.constants[op.name]

        if op.name in context.var2resource:
            res = context.var2resource[op.name]
            msg = 'This is a resource.'
            raise_desc(NotConstant, msg, res=res)
            
        try:
            x = context.get_ndp_fun(op.name)
        except ValueError:
            pass
        else:
            raise_desc(NotConstant, 'Corresponds to new function.', x=x)

        msg = 'Variable ref %r unknown.' % op.name
        raise DPSemanticError(msg, where=op.where)

    if isinstance(op, CDP.GenericNonlinearity):
        raise NotConstant(op)
    
    if isinstance(op, CDP.PlusN):
        return eval_PlusN_as_constant(op, context)

    if isinstance(op, CDP.MultN):
        return eval_MultN_as_constant(op, context)

    msg = 'Cannot evaluate %s as constant.' % op.__repr__()
    raise ValueError(msg)

def eval_PlusN_as_constant(x, context):
    return eval_PlusN(x, context, wants_constant=True)

def eval_MultN_as_constant(x, context):
    return eval_MultN(x, context, wants_constant=True)

def eval_MultN_as_rvalue(x, context):
    res = eval_MultN(x, context, wants_constant=False)
    if isinstance(res, CDP.ValueWithUnits):
        return get_valuewithunits_as_resource(res, context)
    else:
        return res

def eval_PlusN_as_rvalue(x, context):
    res = eval_PlusN(x, context, wants_constant=False)
    if isinstance(res, CDP.ValueWithUnits):
        return get_valuewithunits_as_resource(res, context)
    else:
        return res


def flatten_multN(ops):
    res = []
    for op in ops:
        if isinstance(op, CDP.MultN):
            res.extend(flatten_multN(unwrap_list(op.ops)))
        else:
            res.append(op)
    return res


def eval_MultN(x, context, wants_constant):
    """ Raises NotConstant if wants_constant is True. """
    from mocdp.lang.parse_actions import mult_constantsN 

    assert isinstance(x, CDP.MultN)

    ops = flatten_multN(unwrap_list(x.ops))
    assert len(ops) > 1

    constants = []
    resources = []

    for op in ops:

        try:
            x = eval_constant(op, context)
            assert isinstance(x, CDP.ValueWithUnits)
            constants.append(x)
        except NotConstant as e:
            if wants_constant:
                msg = 'Product not constant because one op is not constant.'
                raise_wrapped(NotConstant, e, msg, op=op)
            x = eval_rvalue(op, context)
            assert isinstance(x, CResource)
            resources.append(x)

    # it's a constant value
    if len(resources) == 0:
        return mult_constantsN(constants)
    if len(resources) == 1:
        c = mult_constantsN(constants)
        return get_mult_op(context, r=resources[0], c=c)
    else:
        # there are some resources
        resources_types = [context.get_rtype(_) for _ in resources]

        # create multiplication for the resources
        R = mult_table_seq(resources_types)

        dp = ProductN(tuple(resources_types), R)

        r = create_operation(context, dp, resources,
                             name_prefix='_prod', op_prefix='_factor',
                             res_prefix='_result')

        if not constants:
            return r
        else:
            c = mult_constantsN(constants)
            return get_mult_op(context, r, c)

@contract(r=CDP.Resource, c=CDP.ValueWithUnits)
def get_mult_op(context, r, c):
    from mocdp.lang.parse_actions import MultValue
    from mocdp.dp_report.gg_ndp import format_unit
    function = MultValue(c.value)
    rtype = context.get_rtype(r)
    setattr(function, '__name__', '× %s %s' % (c.unit.format(c.value),
                                               format_unit(c.unit)))

    F = rtype
    R = mult_table(rtype, c.unit)
    dp = GenericUnary(F, R, function)

    r2 = create_operation(context, dp, resources=[r],
                          name_prefix='_mult', op_prefix='_x',
                          res_prefix='_y')
    return r2


def flatten_plusN(ops):
    res = []
    for op in ops:
        if isinstance(op, CDP.PlusN):
            res.extend(flatten_plusN(unwrap_list(op.ops)))
        else:
            res.append(op)
    return res

def eval_PlusN(x, context, wants_constant):
    """ Raises NotConstant if wants_constant is True. """
    assert isinstance(x, CDP.PlusN)
    assert len(x.ops) > 1

    ops = flatten_plusN(unwrap_list(x.ops))

    constants = []
    resources = []

    for op in ops:
        try:
            x = eval_constant(op, context)
            assert isinstance(x, CDP.ValueWithUnits)
            constants.append(x)
        except NotConstant as e:
            if wants_constant:
                msg = 'Product not constant because one op is not constant.'
                raise_wrapped(NotConstant, e, msg, op=op)
            x = eval_rvalue(op, context)
            assert isinstance(x, CResource)
            resources.append(x)

    # it's a constant value
    if len(resources) == 0:
        return plus_constantsN(constants)
    elif len(resources) == 1:
        c = plus_constantsN(constants)
        return get_plus_op(context, r=resources[0], c=c)
    else:
        # there are some resources
        resources_types = [context.get_rtype(_) for _ in resources]

        # create multiplication for the resources
        R = resources_types[0]

        dp = SumN(tuple(resources_types), R)

        r = create_operation(context, dp, resources,
                             name_prefix='_sum', op_prefix='_term',
                             res_prefix='_result')

        if not constants:
            return r
        else:
            c = plus_constantsN(constants)
            return get_plus_op(context, r=r, c=c)


def get_plus_op(context, r, c):
    from mocdp.lang.parse_actions import PlusValue
    from mocdp.dp_report.gg_ndp import format_unit

    function = PlusValue(c.value)
    setattr(function, '__name__', '+ %s %s' % (c.unit.format(c.value),
                                               format_unit(c.unit)))
    rtype = context.get_rtype(r)

    F = rtype
    R = rtype
    dp = GenericUnary(F, R, function)  # XXX

    r2 = create_operation(context, dp, resources=[r],
                          name_prefix='_plus', op_prefix='_x',
                          res_prefix='_y')

    return r2
    
    
@contract(resources='seq')
def create_operation(context, dp, resources, name_prefix, op_prefix, res_prefix):
    name = context.new_name(name_prefix)
    name_result = context.new_res_name(res_prefix)

    connections = []
    fnames = []
    for i, r in enumerate(resources):
        ni = context.new_fun_name('%s%s' % (op_prefix, i))
        c = Connection(dp1=r.dp, s1=r.s, dp2=name, s2=ni)
        fnames.append(ni)
        connections.append(c)

    if len(fnames) == 1:
        fnames = fnames[0]

    ndp = dpwrap(dp, fnames, name_result)
    context.add_ndp(name, ndp)

    for c in connections:
        context.add_connection(c)

    res = context.make_resource(name, name_result)
    return res


@contract(v=CDP.ValueWithUnits)
def get_valuewithunits_as_resource(v, context):
    dp = Constant(R=v.unit, value=v.value)
    nres = context.new_res_name('c')
    ndp = dpwrap(dp, [], nres)
    context.add_ndp(nres, ndp)
    return context.make_resource(nres, nres)

