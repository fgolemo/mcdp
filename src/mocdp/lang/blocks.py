# -*- coding: utf-8 -*-

from .parse_actions import plus_constantsN
from .parts import CDPLanguage, unwrap_list
from conf_tools import (ConfToolsException, SemanticMistakeKeyNotFound,
    instantiate_spec)
from contracts import contract, describe_value
from contracts.utils import check_isinstance, indent, raise_desc, raise_wrapped
from mocdp.comp import (CompositeNamedDP, Connection, Context, NamedDP,
    NotConnected, SimpleWrap, dpwrap)
from mocdp.comp.context import CFunction, CResource, ValueWithUnits
from mocdp.configuration import get_conftools_dps, get_conftools_nameddps
from mocdp.dp import (
    Constant, GenericUnary, Identity, InvMult2, InvPlus2, Limit, Max, Max1, Min,
    PrimitiveDP, ProductN, SumN)
from mocdp.dp.dp_generic_unary import WrapAMap
from mocdp.dp.dp_series_simplification import make_series
from mocdp.exceptions import DPInternalError, DPSemanticError
from mocdp.lang.parse_actions import inv_constant
from mocdp.posets import (NotBelongs, NotEqual, NotLeq, PosetProduct, Rcomp,
    Space, get_types_universe, mult_table, mult_table_seq)
from mocdp.posets.finite_set import FiniteCollection, FiniteCollectionsInclusion
from mocdp.dp.dp_catalogue import CatalogueDP
from mocdp.posets.any import Any


CDP = CDPLanguage
#

@contract(resource=CResource, function=CFunction)
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
        name = r.name.value
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
            x = eval_constant(right_side, context)
            context.set_constant(name, x)
        except NotConstant:
            # print('Cannot evaluate %r as constant: %s ' % (right_side, e))
            try:
                x = eval_rvalue(right_side, context)
                # print('adding as resource')
                context.set_var2resource(name, x)
            except:
                x = eval_dp_rvalue(right_side, context)
                context.set_var2model(name, x)

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
        B = context.make_function(r.name.value, fname)
        F = context.get_ftype(B)
        A = eval_statement(CDP.FunStatement('-', r.fname, CDP.Unit(F)), context)
        add_constraint(context, resource=A, function=B)

    elif isinstance(r, CDP.ResShortcut1):  # requires rname for name
        # resource rname [r0]
        # rname >= name.rname
        A = context.make_resource(r.name.value, r.rname.value)
        R = context.get_rtype(A)
        B = eval_statement(CDP.ResStatement('-', r.rname, CDP.Unit(R)), context)
        add_constraint(context, resource=A, function=B)  # B >= A

    elif isinstance(r, CDP.ResShortcut1m):  # requires rname1, rname2, ... for name
        for rname in unwrap_list(r.rnames):
            A = context.make_resource(r.name.value, rname.value)
            R = context.get_rtype(A)
            B = eval_statement(CDP.ResStatement('-', rname, CDP.Unit(R)), context)
            add_constraint(context, resource=A, function=B)

    elif isinstance(r, CDP.FunShortcut1m):  # provides fname1,fname2,... using name
        for fname in unwrap_list(r.fnames):
            B = context.make_function(r.name.value, fname.value)
            F = context.get_ftype(B)
            A = eval_statement(CDP.FunStatement('-', fname, CDP.Unit(F)), context)
            add_constraint(context, resource=A, function=B)

    elif isinstance(r, CDP.FunShortcut2):  # provides rname <= (lf)
        B = eval_lfunction(r.lf, context)
        assert isinstance(B, CFunction)
        F = context.get_ftype(B)
        A = eval_statement(CDP.FunStatement('-', r.fname, CDP.Unit(F)), context)
        add_constraint(context, resource=A, function=B)

    elif isinstance(r, CDP.ResShortcut2):  # requires rname >= (rvalue)
        A = eval_rvalue(r.rvalue, context)
        assert isinstance(A, CResource)
        R = context.get_rtype(A)
        B = eval_statement(CDP.ResStatement('-', r.rname, CDP.Unit(R)), context)
        # B >= A
        add_constraint(context, resource=A, function=B)

    else:
        raise DPInternalError('Cannot interpret %s' % describe_value(r))
    
def interpret_commands(res, context):
    context = context.child()
    
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
    

@contract(r=CDP.DPWrap)
def eval_dp_rvalue_dpwrap(r, context):
    tu = get_types_universe()

    statements = unwrap_list(r.statements)
    fun = [x for x in statements if isinstance(x, CDP.FunStatement)]
    res = [x for x in statements if isinstance(x, CDP.ResStatement)]

    assert len(fun) + len(res) == len(statements), statements
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

    dp_F = dp.get_fun_space()
    dp_R = dp.get_res_space()

    # Check that the functions are the same
    want_Fs = tuple([f.unit.value for f in fun])
    if len(want_Fs) == 1:
        want_F = want_Fs[0]
    else:
        want_F = PosetProduct(want_Fs)

    want_Rs = tuple([r.unit.value for r in res])
    if len(want_Rs) == 1:
        want_R = want_Rs[0]
    else:
        want_R = PosetProduct(want_Rs)

    dp_prefix = get_conversion(want_F, dp_F)
    dp_postfix = get_conversion(dp_R, want_R)

    if dp_prefix is not None:
        dp = make_series(dp_prefix, dp)

    if dp_postfix is not None:
        dp = make_series(dp, dp_postfix)

    try:
        w = SimpleWrap(dp=dp, fnames=use_fnames, rnames=use_rnames)
    except ValueError as e:
        raise DPSemanticError(str(e), r.where)

    ftypes = w.get_ftypes(fnames)
    rtypes = w.get_rtypes(rnames)
    ftypes_expected = PosetProduct(tuple([f.unit.value for f in fun]))
    rtypes_expected = PosetProduct(tuple([r.unit.value for r in res]))

    try:

        tu.check_equal(ftypes, ftypes_expected)
        tu.check_equal(rtypes, rtypes_expected)
    except NotEqual as e:
        msg = 'The types in the description do not match.'
        raise_wrapped(DPSemanticError, e, msg,
                      dp=dp,
                   ftypes=ftypes,
                   ftypes_expected=ftypes_expected,
                   rtypes=rtypes,
                   rtypes_expected=rtypes_expected, compact=True)

    return w

def eval_dp_rvalue_coproduct(r, context):
    assert isinstance(r, CDP.Coproduct)
    ops = get_odd_ops(unwrap_list(r.ops))
    ndps = []
    for _, op in enumerate(ops):
        ndp = eval_dp_rvalue(op, context)
        ndps.append(ndp)
    from mocdp.comp.interfaces import NamedDPCoproduct
    return NamedDPCoproduct(tuple(ndps))

def eval_dp_rvalue_catalogue(r, context):
    assert isinstance(r, CDP.FromCatalogue)
    # FIXME:need to check for re-ordering
    statements = unwrap_list(r.funres)
    fun = [x for x in statements if isinstance(x, CDP.FunStatement)]
    res = [x for x in statements if isinstance(x, CDP.ResStatement)]
    Fs = [_.unit.value for _ in fun]
    Rs = [_.unit.value for _ in res]

    assert len(fun) + len(res) == len(statements), statements
    tu = get_types_universe()
    table = r.table
    rows = unwrap_list(table.rows)
    entries = []
    for row in rows:
        items = unwrap_list(row)
        name = items[0].value
        expected = 1 + len(fun) + len(res)
        if len(items) != expected:
            msg = 'Row does not match number of elements (%s fun, %s res)' % (len(fun), len(res))
            raise DPSemanticError(msg, where=items[-1].where)
        fvalues0 = items[1:1+len(fun)]
        rvalues0 = items[1 + len(fun):1 + len(fun) + len(res)]

        fvalues = [eval_constant(_, context) for _ in fvalues0]
        rvalues = [eval_constant(_, context) for _ in rvalues0]

        for cell, Fhave, F in zip(fvalues0, fvalues, Fs):
            try:
                tu.check_leq(Fhave.unit, F)
            except NotLeq as e:
                msg = 'Dimensionality problem: cannot convert %s to %s.' % (Fhave.unit, F)
                ex = lambda msg: DPSemanticError(msg, where=cell.where)
                raise_wrapped(ex, e, msg, compact=True)
            
        for cell, Rhave, R in zip(rvalues0, rvalues, Rs):
            try:
                tu.check_leq(Rhave.unit, R)
            except NotLeq as e:
                msg = 'Dimensionality problem: cannot convert %s to %s.' % (Rhave.unit, R)
                ex = lambda msg: DPSemanticError(msg, where=cell.where)
                raise_wrapped(ex, e, msg, compact=True)

        fvalues_ = [convert_vu(_.value, _.unit, F, context) for (_, F) in zip(fvalues, Fs)]
        rvalues_ = [convert_vu(_.value, _.unit, R, context) for (_, R) in zip(rvalues, Rs)]

        assert len(fvalues_) == len(fun)
        assert len(rvalues_) == len(res)

        entries.append((name, tuple(fvalues_), tuple(rvalues_)))

    M = Any()
    # use integers
#     entries = [(float(i), b, c) for i, (_, b, c) in enumerate(entries)]

    fnames = [_.fname.value for  _ in fun]
    rnames = [_.rname.value for  _ in res]

    if len(Fs) > 1:
        F = PosetProduct(tuple(Fs))
    else:
        F = Fs[0]
        fnames = fnames[0]
        entries = [(a, b[0], c) for (a, b, c) in entries]

    if len(Rs) > 1:
        R = PosetProduct(tuple(Rs))
    else:
        R = Rs[0]
        rnames = rnames[0]
        entries = [(a, b, c[0]) for (a, b, c) in entries]

    dp = CatalogueDP(F=F, R=R, M=M, entries=tuple(entries))



    ndp = dpwrap(dp, fnames=fnames, rnames=rnames)
    return ndp

@contract(returns=NamedDP)
def eval_dp_rvalue(r, context):  # @UnusedVariable
    try:
        if isinstance(r, CDP.BuildProblem):
            special_list = r.statements
            statements = unwrap_list(special_list)
            return interpret_commands(statements, context)

        if isinstance(r, CDP.VariableRef):
            return context.get_var2model(r.name)

        if isinstance(r, CDP.FromCatalogue):
            return eval_dp_rvalue_catalogue(r, context)

        if isinstance(r, CDP.Coproduct):
            return eval_dp_rvalue_coproduct(r, context)

        if isinstance(r, NamedDP):
            return r

        if isinstance(r, CDP.LoadCommand):
            library = get_conftools_nameddps()
            load_arg = r.load_arg.value
            try:
                _, ndp = library.instance_smarter(load_arg)
            except ConfToolsException as e:
                msg = 'Cannot load predefined DP %s.' % load_arg.__repr__()
                raise_wrapped(DPSemanticError, e, msg)

            return ndp

        if isinstance(r, CDP.DPWrap):
            return eval_dp_rvalue_dpwrap(r, context)

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

def get_conversion(A, B):
    """ Returns None if there is no need. """
    tu = get_types_universe()
    try:
        tu.check_leq(A, B)
    except NotLeq as e:
        msg = 'Wrapping with incompatible units.'
        raise_wrapped(DPSemanticError, e, msg, A=A, B=B)

    if tu.equal(A, B):
        conversion = None
    else:
        A_to_B, _ = tu.get_embedding(A, B)
        conversion = WrapAMap(A_to_B)

    return conversion

@contract(returns=PrimitiveDP)
def eval_pdp(r, context):  # @UnusedVariable
    if isinstance(r, CDP.LoadDP):
        name = r.name.value
        try:
            _, dp = get_conftools_dps().instance_smarter(name)
        except SemanticMistakeKeyNotFound as e:
            raise DPSemanticError(str(e), r.where)

        return dp

    if isinstance(r, CDP.PDPCodeSpec):
        function = r.function.value
        arguments = r.arguments
        check_isinstance(function, str)
        res = instantiate_spec([function, arguments])
        return res
            
    raise DPInternalError('Invalid pdp rvalue: %s' % str(r))

@contract(returns=CFunction)
def eval_lfunction(lf, context):
    if isinstance(lf, CDP.Function):
        return context.make_function(dp=lf.dp.value, s=lf.s.value)

    if isinstance(lf, CDP.InvMult):
        ops = get_odd_ops(unwrap_list(lf.ops))
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

    if isinstance(lf, CDP.InvPlus):
        ops = get_odd_ops(unwrap_list(lf.ops))
        if len(ops) != 2:
            raise DPInternalError('Only 2 expected')

        fs = []

        for op_i in ops:
            fi = eval_lfunction(op_i, context)
            fs.append(fi)

        assert len(fs) == 2

        Fs = map(context.get_ftype, fs)
        # R = plus_table(Fs[0], Fs[1])
        R = Fs[0]

        dp = InvPlus2(R, tuple(Fs))
        ndp = dpwrap(dp, '_input', ['_f0', '_f1'])

        name = context.new_name('_invplus')
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
        A = eval_constant(lf.value_with_unit, context)
        dp = Limit(A.unit, A.value)
        n = context.new_name('lim')
        sn = context.new_fun_name('l')
        ndp = dpwrap(dp, sn, [])
        context.add_ndp(n, ndp)

        return context.make_function(n, sn)

    msg = 'Cannot eval_lfunction(%s)' % lf.__repr__()
    raise DPInternalError(msg)

class DoesNotEvalToResource(Exception):
    """ also called rvalue """

@contract(returns=CResource)
def eval_rvalue(rvalue, context):
    """
        raises DoesNotEvalToResource
    """
    # wants Resource or NewFunction
    try:
        if isinstance(rvalue, CDP.Divide):
            return eval_divide_as_rvalue(rvalue, context)

        if isinstance(rvalue, CDP.Resource):
            return context.make_resource(dp=rvalue.dp.value, s=rvalue.s.value)
        
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

            if isinstance(rvalue.a, CDP.SimpleValue):
                b = eval_rvalue(rvalue.b, context)
                # print('a is constant')
                name = context.new_name('max1')
                ndp = dpwrap(Max1(rvalue.a.unit, rvalue.a.value), '_in', '_out')
                context.add_ndp(name, ndp)
                c = Connection(dp1=b.dp, s1=b.s, dp2=name, s2='_in')
                context.add_connection(c)
                return context.make_resource(name, '_out')

            a = eval_rvalue(rvalue.a, context)

            if isinstance(rvalue.b, CDP.SimpleValue):
                name = context.new_name('max1')
                ndp = dpwrap(Max1(rvalue.b.unit.value, rvalue.b.value.value), '_in', '_out')
                context.add_ndp(name, ndp)
                c = Connection(dp1=a.dp, s1=a.s, dp2=name, s2='_in')
                context.add_connection(c)
                return context.make_resource(name, '_out')

            b = eval_rvalue(rvalue.b, context)

            F1 = context.get_rtype(a)
            F2 = context.get_rtype(b)

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

        if isinstance(rvalue, CDP.SimpleValue):
            # implicit conversion from int to float
            unit = rvalue.unit.value
            value = rvalue.value.value
            # XXX: stuff here
            if isinstance(unit, Rcomp):
                if isinstance(value, int):
                    value = float(value)
            try:
                unit.belongs(value)
            except NotBelongs as e:
                raise_wrapped(DPSemanticError, e, "Value is not in the give space.")
                
            c = ValueWithUnits(value, unit)
            return get_valuewithunits_as_resource(c, context)
        
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

        msg = 'Cannot evaluate as resource.'
        raise_desc(DoesNotEvalToResource, msg, rvalue=rvalue)
    except DPSemanticError as e:
        if e.where is None:
            raise DPSemanticError(str(e), where=rvalue.where)
        raise e

class NotConstant(Exception):
    pass

@contract(returns=Space)
def eval_unit(x, context):  # @UnusedVariable

    if isinstance(x, CDP.Unit):
        S = x.value
        assert isinstance(S, Space), S
        return S
    
    msg = 'Cannot evaluate %s as unit.' % x.__repr__()
    raise ValueError(msg)
    
def eval_constant_divide(op, context):
    ops = get_odd_ops(unwrap_list(op.ops))
    if len(ops) != 2:
        raise DPSemanticError('divide by more than two')

    constants = [eval_constant(_, context) for _ in ops]
    invs = [inv_constant(_) for _ in constants]
    from mocdp.lang.parse_actions import mult_constantsN
    return mult_constantsN(invs)

@contract(unit1=Space, unit2=Space)
def convert_vu(value, unit1, unit2, context):  # @UnusedVariable
    tu = get_types_universe()
    A_to_B, _ = tu.get_embedding(unit1, unit2)
    return A_to_B(value)

    
def eval_constant_collection(op, context):
    ops = get_odd_ops(unwrap_list(op.elements))
    if len(ops) == 0:
        raise DPSemanticError('empty list')
    elements = [eval_constant(_, context) for _ in ops]

    e0 = elements[0]

    u0 = e0.unit
    elements = [convert_vu(_.value, _.unit, u0, context) for _ in elements]

    value = FiniteCollection(set(elements), u0)
    unit = FiniteCollectionsInclusion(u0)
    vu = ValueWithUnits(value, unit)

    return vu

@contract(returns=ValueWithUnits)
def eval_constant(op, context):
    """ 
        Raises NotConstant if not constant. 
        Returns ValueWithUnits
    """
    if isinstance(op, CDP.Divide):
        return eval_constant_divide(op, context)
    
    if isinstance(op, CDP.Collection):
        return eval_constant_collection(op, context)

    if isinstance(op, (CDP.Resource)):
        raise NotConstant(str(op))

    if isinstance(op, (CDP.OpMax, CDP.OpMin, CDP.Power)):
        # TODO: can implement optimization
        raise NotConstant(str(op))

    if isinstance(op, CDP.SimpleValue):
        assert isinstance(op.unit, CDP.Unit), op

        F = eval_unit(op.unit, context)
        assert isinstance(F, Space), op
        v = op.value.value
        if isinstance(v, int) and isinstance(F, Rcomp):
            v = float(v)

        try:
            F.belongs(v)
        except NotBelongs as e:
            msg = 'Not in space'
            raise_wrapped(DPSemanticError, e, msg, F=F, v=v)
        return ValueWithUnits(unit=F, value=v)

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

    msg = 'Cannot evaluate %s as constant.' % type(op).__name__
    raise_desc(NotConstant, msg, op=op)

def eval_PlusN_as_constant(x, context):
    return eval_PlusN(x, context, wants_constant=True)

def eval_MultN_as_constant(x, context):
    return eval_MultN(x, context, wants_constant=True)

def eval_MultN_as_rvalue(x, context):
    res = eval_MultN(x, context, wants_constant=False)
    if isinstance(res, ValueWithUnits):
        return get_valuewithunits_as_resource(res, context)
    else:
        return res

def eval_divide_as_rvalue(op, context):
    ops = get_odd_ops(unwrap_list(op.ops))
    
    try:
        c2 = eval_constant(ops[1], context)
    except NotConstant as e:
        msg = 'Cannot divide by a non-constant.'
        raise_wrapped(DPSemanticError, e, msg, ops[0])
    
    try:
        c1 = eval_constant(ops[0], context)
        # also the first one is a constant
        from mocdp.lang.parse_actions import mult_constantsN
        return mult_constantsN([inv_constant(c1), inv_constant(c2)])

    except NotConstant:
        pass
    
    # then eval as resource
    r = eval_rvalue(ops[0], context)
    c2_inv = inv_constant(c2)
    res = get_mult_op(context, r=r, c=c2_inv)
    return res
    
    
     
def eval_PlusN_as_rvalue(x, context):
    res = eval_PlusN(x, context, wants_constant=False)
    if isinstance(res, ValueWithUnits):
        return get_valuewithunits_as_resource(res, context)
    else:
        return res


def flatten_multN(ops):
    res = []
    for op in ops:
        if isinstance(op, CDP.MultN):
            res.extend(flatten_multN(get_odd_ops(unwrap_list(op.ops))))
        else:
            res.append(op)
    return res


def eval_MultN(x, context, wants_constant):
    """ Raises NotConstant if wants_constant is True. """
    from mocdp.lang.parse_actions import mult_constantsN 

    assert isinstance(x, CDP.MultN)

    ops = flatten_multN(get_odd_ops(unwrap_list(x.ops)))
    assert len(ops) > 1

    constants = []
    resources = []

    for op in ops:

        try:
            x = eval_constant(op, context)
            assert isinstance(x, ValueWithUnits)
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

@contract(r=CResource, c=ValueWithUnits)
def get_mult_op(context, r, c):
    from mocdp.lang.parse_actions import MultValue
    function = MultValue(c.value)
    rtype = context.get_rtype(r)
#     setattr(function, '__name__', '× %s %s' % (c.unit.format(c.value),
#                                                format_unit(c.unit)))
    setattr(function, '__name__', '× %s' % (c.unit.format(c.value)))

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
            res.extend(flatten_plusN(get_odd_ops(unwrap_list(op.ops))))
        else:
            res.append(op)
    return res

def get_odd_ops(l):
    """ Returns odd elements from l. """
    res = []
    for i, x in enumerate(l):
        if i % 2 == 0:
            res.append(x)
    return res

def eval_PlusN(x, context, wants_constant):
    """ Raises NotConstant if wants_constant is True. """
    assert isinstance(x, CDP.PlusN)
    assert len(x.ops) > 1

    ops = flatten_plusN(get_odd_ops(unwrap_list(x.ops)))
    constants = []
    resources = []

    for op in ops:
        try:
            x = eval_constant(op, context)
            assert isinstance(x, ValueWithUnits)
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

@contract(r=CResource, c=ValueWithUnits)
def get_plus_op(context, r, c):
    from mocdp.lang.parse_actions import PlusValue

    rtype = context.get_rtype(r)

    F = rtype
    R = rtype
    function = PlusValue(F=F, R=R, c=c)
    setattr(function, '__name__', '+ %s' % (c.unit.format(c.value)))
    dp = GenericUnary(F, R, function)  # XXX
    # TODO: dp = WrapAMap(map)

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


@contract(v=ValueWithUnits)
def get_valuewithunits_as_resource(v, context):
    dp = Constant(R=v.unit, value=v.value)
    nres = context.new_res_name('c')
    ndp = dpwrap(dp, [], nres)
    context.add_ndp(nres, ndp)
    return context.make_resource(nres, nres)

