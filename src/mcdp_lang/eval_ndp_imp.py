# -*- coding: utf-8 -*-
from .eval_constant_imp import eval_constant
from .eval_space_imp import eval_space
from .parts import CDPLanguage
from .utils_lists import get_odd_ops, unwrap_list
from contracts import contract, describe_value
from contracts.utils import raise_desc, raise_wrapped
from mcdp_lang.parse_actions import add_where_information
from mcdp_posets import Any, NotEqual, NotLeq, PosetProduct, get_types_universe
from mocdp.comp import (CompositeNamedDP, Connection, NamedDP, NotConnected,
    SimpleWrap, dpwrap)
from mocdp.comp.context import (CFunction, CResource, NoSuchMCDPType,
    get_name_for_fun_node, get_name_for_res_node)
from mocdp.dp.conversion import get_conversion
from mocdp.dp.dp_approximation import make_approximation
from mocdp.dp.dp_catalogue import CatalogueDP
from mocdp.dp.dp_series_simplification import make_series
from mocdp.exceptions import DPInternalError, DPSemanticError
from mocdp.ndp.named_coproduct import NamedDPCoproduct
from mocdp.dp.dp_max import JoinNDP, MeetNDual



CDP = CDPLanguage

@contract(returns=NamedDP)
def eval_ndp(r, context):  # @UnusedVariable
    with add_where_information(r.where):

        if isinstance(r, CDP.BuildProblem):
            return eval_build_problem(r, context)

        # TODO: remove
        if isinstance(r, CDP.VariableRef):
            try:
                return context.get_var2model(r.name)
            except NoSuchMCDPType as e:
                msg = 'Cannot find name.'
                raise_wrapped(DPSemanticError, e, msg, compact=True)

        if isinstance(r, CDP.DPVariableRef):
            try:
                return context.get_var2model(r.name)
            except NoSuchMCDPType as e:
                msg = 'Cannot find name.'
                raise_wrapped(DPSemanticError, e, msg, compact=True)

        if isinstance(r, CDP.DPInstance):
            return eval_ndp(r.dp_rvalue, context)

        if isinstance(r, NamedDP):
            return r

        if isinstance(r, CDP.LoadCommand):
            load_arg = r.load_arg.value
            return eval_dp_rvalue_load(load_arg, context)

        if isinstance(r, CDP.DPWrap):
            return eval_dp_rvalue_dpwrap(r, context)

        if isinstance(r, CDP.AbstractAway):
            ndp = eval_ndp(r.dp_rvalue, context)
            if isinstance(ndp, SimpleWrap):
                return ndp
            try:
                ndp.check_fully_connected()
            except NotConnected as e:
                msg = 'Cannot abstract away the design problem because it is not connected.'
                raise_wrapped(DPSemanticError, e, msg, compact=True)

            ndpa = ndp.abstract()
            return ndpa

        if isinstance(r, CDP.Compact):
            ndp = eval_ndp(r.dp_rvalue, context)
            if isinstance(ndp, CompositeNamedDP):
                return ndp.compact()
            else:
                msg = 'Cannot compact primitive NDP.'
                raise_desc(DPSemanticError, msg, ndp=ndp.repr_long())

        if isinstance(r, CDP.Ellipsis):
            msg = 'Model is incomplete (the ellipsis operator "..." was used)'
            raise_desc(DPSemanticError, msg)
            
        cases = {
            CDP.MakeTemplate: eval_make_template,
            CDP.Coproduct:eval_dp_rvalue_coproduct,
            CDP.CoproductWithNames: eval_dp_rvalue_CoproductWithNames,
            CDP.ApproxDPModel: eval_dp_rvalue_approxdpmodel,
            CDP.FromCatalogue: eval_dp_rvalue_catalogue,
            CDP.Flatten: eval_dp_rvalue_flatten,
            CDP.DPInstanceFromLibrary: eval_dp_rvalue_instancefromlibrary,
            CDP.CodeSpecNoArgs: eval_ndp_code_spec,
            CDP.CodeSpec: eval_ndp_code_spec,
            CDP.MakeCanonical: eval_ndp_makecanonical,
        }
        
        for klass, hook in cases.items():
            if isinstance(r, klass):
                return hook(r, context)
        
   
    raise_desc(DPInternalError, 'Invalid dprvalue.', r=r)


def eval_ndp_makecanonical(r, context):
    ndp = eval_ndp(r.dp_rvalue, context)
    print ndp
    raise NotImplementedError


def eval_ndp_code_spec(r, _context):
    from .eval_codespec_imp import eval_codespec
    res = eval_codespec(r, expect=NamedDP)
    return res

def eval_dp_rvalue_instancefromlibrary(r, context):
    name = r.dpname.value
    ndp = eval_dp_rvalue_load(name, context)
    return ndp


def eval_dp_rvalue_flatten(r, context):
    ndp = eval_ndp(r.dp_rvalue, context)

    ndp = ndp.flatten()

#     from mocdp.comp.connection import get_connection_graph
#     G = get_connection_graph(ndp.get_name2ndp(), ndp.get_connections())
    if isinstance(ndp, CompositeNamedDP):
        from mocdp.comp.connection import choose_connection_to_cut1
        choose_connection_to_cut1(connections=ndp.get_connections(), name2dp=ndp.get_name2ndp())
    # print ndp
    return ndp

def eval_dp_rvalue_coproduct(r, context):
    assert isinstance(r, CDP.Coproduct)
    ops = get_odd_ops(unwrap_list(r.ops))
    ndps = []
    for _, op in enumerate(ops):
        ndp = eval_ndp(op, context)
        ndps.append(ndp)

    return NamedDPCoproduct(tuple(ndps))

@contract(r=CDP.CoproductWithNames)
def eval_dp_rvalue_CoproductWithNames(r, context):
    assert isinstance(r, CDP.CoproductWithNames)
    elements = r.elements
    names = [_.value for _ in elements[0::2]]
    ndps = [eval_ndp(_, context) for _ in elements[1::2]]
    labels = tuple(names)
    return NamedDPCoproduct(tuple(ndps), labels=labels)

def eval_dp_rvalue_approxdpmodel(r, context):
    # name of function or resource
    name = r.name.value
    approx_perc = float(r.perc.value)
    
    approx_abs = float(r.abs.value.value)
    approx_abs_S = eval_space(r.abs.space, context)  # should be real
    ndp0 = eval_ndp(r.dp, context)
    x = eval_constant(r.max_value, context)
    # assert isinstance(x, ValueWithUnit)
    max_value = x.value
    max_value_S = x.unit
    return make_approximation(name=name, approx_perc=approx_perc,
                              approx_abs=approx_abs, approx_abs_S=approx_abs_S,
                              max_value=max_value, max_value_S=max_value_S,
                              ndp=ndp0)


def eval_dp_rvalue_load(load_arg, context):
    return context.load_ndp(load_arg)


@contract(r=CDP.DPWrap)
def eval_dp_rvalue_dpwrap(r, context):
    tu = get_types_universe()

    statements = unwrap_list(r.statements)
    fun = [x for x in statements if isinstance(x, CDP.FunStatement)]
    res = [x for x in statements if isinstance(x, CDP.ResStatement)]

    assert len(fun) + len(res) == len(statements), statements
    impl = r.impl

    from mcdp_lang.eval_primitivedp_imp import eval_primitivedp
    dp = eval_primitivedp(impl, context)

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
#     from mcdp_lang.eval_space_imp import eval_space
    want_Fs = tuple([eval_space(f.unit, context) for f in fun])
    if len(want_Fs) == 1:
        want_F = want_Fs[0]
    else:
        want_F = PosetProduct(want_Fs)

    want_Rs = tuple([eval_space(r.unit, context) for r in res])
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
    ftypes_expected = PosetProduct(tuple([eval_space(f.unit, context) for f in fun]))
    rtypes_expected = PosetProduct(tuple([eval_space(r.unit, context) for r in res]))

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


def eval_dp_rvalue_catalogue(r, context):
    assert isinstance(r, CDP.FromCatalogue)
    # FIXME:need to check for re-ordering
    statements = unwrap_list(r.funres)
    fun = [x for x in statements if isinstance(x, CDP.FunStatement)]
    res = [x for x in statements if isinstance(x, CDP.ResStatement)]
#     from mcdp_lang.eval_space_imp import eval_space
    Fs = [eval_space(_.unit, context) for _ in fun]
    Rs = [eval_space(_.unit, context) for _ in res]

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
            msg = 'Row with %d elements does not match expected of elements (%s fun, %s res)' % (len(items), len(fun), len(res))
            # msg += ' items: %s' % str(items)
            raise DPSemanticError(msg, where=items[-1].where)
        fvalues0 = items[1:1 + len(fun)]
        rvalues0 = items[1 + len(fun):1 + len(fun) + len(res)]

#         from mcdp_lang.eval_constant_imp import eval_constant
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

        from mcdp_lang.eval_math import convert_vu
        fvalues_ = [convert_vu(_.value, _.unit, F, context) for (_, F) in zip(fvalues, Fs)]
        rvalues_ = [convert_vu(_.value, _.unit, R, context) for (_, R) in zip(rvalues, Rs)]

        assert len(fvalues_) == len(fun)
        assert len(rvalues_) == len(res)

        entries.append((name, tuple(fvalues_), tuple(rvalues_)))

    M = Any()
    # use integers
    # entries = [(float(i), b, c) for i, (_, b, c) in enumerate(entries)]

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


@contract(resource=CResource, function=CFunction)
def add_constraint(context, resource, function):
    R1 = context.get_rtype(resource)
    F2 = context.get_ftype(function)

    tu = get_types_universe()


    if not tu.equal(R1, F2):

#         try:
#             tu.check_equal(R1, F2)
#         except NotEqual as e:
#             pass
#         else:
#             assert False

        try:
            tu.check_leq(R1, F2)
        except NotLeq as e:
            msg = 'Constraint between incompatible spaces.'
            raise_wrapped(DPSemanticError, e, msg, compact=True)

        conversion = get_conversion(R1, F2)

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
#     from mcdp_lang.eval_space_imp import eval_space
    from mcdp_lang.eval_resources_imp import eval_rvalue
    from mcdp_lang.eval_lfunction_imp import eval_lfunction

    if isinstance(r, Connection):
        context.add_connection(r)

    elif isinstance(r, CDP.Constraint):
        resource = eval_rvalue(r.rvalue, context)
        function = eval_lfunction(r.function, context)
        add_constraint(context, resource, function)

    elif isinstance(r, CDP.SetName):
        name = r.name.value
        ndp = eval_ndp(r.dp_rvalue, context)
        context.add_ndp(name, ndp)

    elif isinstance(r, CDP.SetMCDPType):
        name = r.name.value
        right_side = r.right_side
        x = eval_ndp(right_side, context)
        context.set_var2model(name, x)

    elif isinstance(r, CDP.SetNameGeneric):
        name = r.name.value
        right_side = r.right_side

        if name in context.constants:
            msg = 'Constant %r already set.' % name
            raise DPSemanticError(msg, where=r.where)

        if name in context.var2resource:
            msg = 'Resource %r already set.' % name
            raise DPSemanticError(msg, where=r.where)

        from mcdp_lang.eval_constant_imp import NotConstant
        try:
            # from mcdp_lang.eval_constant_imp import eval_constant
            x = eval_constant(right_side, context)
            context.set_constant(name, x)
        except NotConstant:
            # print('Cannot evaluate %r as constant: %s ' % (right_side, e))
            try:
                x = eval_rvalue(right_side, context)
                # print('adding as resource')
                context.set_var2resource(name, x)
            except Exception as e:
                print('Cannot evaluate %r as eval_rvalue: %s ' % (right_side, e))
                # XXX fix this
                x = eval_ndp(right_side, context)
                context.set_var2model(name, x)

    elif isinstance(r, CDP.ResStatement):
        # requires r.rname [r.unit]

        R = eval_space(r.unit, context)
        rname = r.rname.value
        context.add_ndp_res_node(rname, R)
        
        return context.make_function(get_name_for_res_node(rname), rname)

    elif isinstance(r, CDP.FunStatement):
        F = eval_space(r.unit, context)
        fname = r.fname.value

        context.add_ndp_fun_node(fname, F)

        return context.make_resource(get_name_for_fun_node(fname), fname)

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

def eval_build_problem(r, context):
    context = context.child()

    statements = unwrap_list(r.statements)

    for s in statements:
        with add_where_information(s.where):
            eval_statement(s, context)

    # at this point we need to fix the case where there might be multiple
    # functions / resources
    fix_functions_with_multiple_connections(context)
    fix_resources_with_multiple_connections(context)

    return CompositeNamedDP.from_context(context)

def fix_functions_with_multiple_connections(context):
    # tuples (ndp, res)
    from mocdp.comp.connection import find_functions_with_multiple_connections
    res = find_functions_with_multiple_connections(context.connections)
    for id_ndp, fname in res:
        matches = lambda c: c.dp2 == id_ndp and c.s2 == fname
        its = [c for c in context.connections if matches(c)]
        assert len(its) >= 2

        for c in its:
            context.connections.remove(c)

        P = context.get_ftype(CFunction(id_ndp, fname))
        new_name = context.new_name('_join_fname')
        dp = JoinNDP(n=len(its), P=P)

        new_connections = []
        fnames = []
        rname = '_a'
        for i, c in enumerate(its):
            fn = '_%s_%d' % (fname, i)
            fnames.append(fn)
            c2 = Connection(dp1=c.dp1, s1=c.s1, dp2=new_name, s2=fn)
            new_connections.append(c2)

        ndp = dpwrap(dp, fnames, rname)
        context.add_ndp(new_name, ndp)
        for c2 in new_connections:
            context.add_connection(c2)

        cc = Connection(dp1=new_name, s1=rname, dp2=id_ndp, s2=fname)
        context.add_connection(cc)


def fix_resources_with_multiple_connections(context):
    # tuples (ndp, res)
    from mocdp.comp.connection import find_resources_with_multiple_connections
    res = find_resources_with_multiple_connections(context.connections)
    for id_ndp, rname in res:
        matches = lambda c: c.dp1 == id_ndp and c.s1 == rname
        its = [c for c in context.connections if matches(c)]
        assert len(its) >= 2

        for c in its:
            context.connections.remove(c)

        P = context.get_rtype(CResource(id_ndp, rname))
        new_name = context.new_name('_join_fname')
        dp = MeetNDual(n=len(its), P=P)

        new_connections = []
        rnames = []
        for i, c in enumerate(its):
            rn = '_%s_%d' % (rname, i)
            rnames.append(rn)
            c2 = Connection(dp1=new_name, s1=rn, dp2=c.dp2, s2=c.s2)
            new_connections.append(c2)

        fname = '_a'
        ndp = dpwrap(dp, fname, rnames)
        context.add_ndp(new_name, ndp)
        for c2 in new_connections:
            context.add_connection(c2)

        # [ id_ndp : rname ] -> [ new_name ]
        cc = Connection(dp2=new_name, s2=fname, dp1=id_ndp, s1=rname)
        context.add_connection(cc)

def eval_make_template(r, context):
    ndp = eval_ndp(r.dp_rvalue, context)
    from mocdp.comp.composite_templatize import ndp_templatize
    return ndp_templatize(ndp)

