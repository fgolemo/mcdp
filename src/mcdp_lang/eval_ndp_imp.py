# -*- coding: utf-8 -*-
from contextlib import contextmanager
import sys

from contracts import contract
from contracts.utils import raise_desc, raise_wrapped
from mcdp_dp import (
    CatalogueDP, Conversion, JoinNDP, MeetNDualDP, get_conversion, make_series)
from mcdp_posets import (
    FiniteCollectionAsSpace, NotEqual, NotLeq, PosetProduct, get_types_universe)
from mocdp import ATTRIBUTE_NDP_MAKE_FUNCTION
from mocdp import logger
from mocdp.comp import (CompositeNamedDP, Connection, NamedDP, NotConnected,
    SimpleWrap, dpwrap)
from mocdp.comp.composite_makecanonical import cndp_makecanonical
from mocdp.comp.context import (CFunction, CResource, NoSuchMCDPType,
    get_name_for_fun_node, get_name_for_res_node)
from mocdp.comp.ignore_some_imp import ignore_some
from mocdp.comp.make_approximation_imp import make_approximation
from mocdp.exceptions import (DPInternalError, DPSemanticError,
    DPSemanticErrorNotConnected)
from mocdp.ndp.named_coproduct import NamedDPCoproduct

from .eval_codespec_imp_utils_instantiate import ImportFailure, import_name
from .eval_constant_imp import eval_constant
from .eval_ndp_approx import eval_ndp_approx_lower, eval_ndp_approx_upper
from .eval_space_imp import eval_space
from .eval_template_imp import eval_template
from .helpers import create_operation
from .namedtuple_tricks import recursive_print
from .parse_actions import add_where_information
from .parts import CDPLanguage
from .utils_lists import get_odd_ops, unwrap_list


CDP = CDPLanguage

@contract(returns=NamedDP)
def eval_ndp(r, context):  # @UnusedVariable
    with add_where_information(r.where):
        # TODO: remove
        if isinstance(r, CDP.VariableRef):
            try:
                return context.get_var2model(r.name)
            except NoSuchMCDPType as e:  # XXX: fixme
                msg = 'Cannot find name.'
                raise_wrapped(DPSemanticError, e, msg, compact=True)

        if isinstance(r, CDP.VariableRefNDPType):
            try:
                return context.get_var2model(r.name)
            except NoSuchMCDPType as e:
                msg = 'Cannot find name.'
                raise_wrapped(DPSemanticError, e, msg, compact=True)

        if isinstance(r, NamedDP):
            return r

        # XXX
        if isinstance(r, CDP.DPInstance):
            return eval_ndp(r.dp_rvalue, context)

        if isinstance(r, CDP.AbstractAway):
            ndp = eval_ndp(r.dp_rvalue, context)
            if isinstance(ndp, SimpleWrap):
                return ndp
            try:
                ndp.check_fully_connected()
            except NotConnected as e:
                msg = 'Cannot abstract away the design problem because it is not connected.'
                raise_wrapped(DPSemanticErrorNotConnected, e, msg, compact=True)

            ndpa = ndp.abstract()

            assert isinstance(ndpa, SimpleWrap)
            from mcdp_dp.opaque_dp import OpaqueDP
            ndpa.dp = OpaqueDP(ndpa.dp)

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
            CDP.BuildProblem: eval_build_problem,
            CDP.LoadNDP: eval_ndp_load,
            CDP.DPWrap : eval_ndp_dpwrap,
            CDP.MakeTemplate: eval_ndp_make_template,
            CDP.Coproduct:eval_ndp_coproduct,
            CDP.CoproductWithNames: eval_ndp_CoproductWithNames,
            CDP.ApproxDPModel: eval_ndp_approxdpmodel,
            CDP.FromCatalogue: eval_ndp_catalogue,
            CDP.Flatten: eval_ndp_flatten,
            CDP.DPInstanceFromLibrary: eval_ndp_instancefromlibrary,
            CDP.CodeSpecNoArgs: eval_ndp_code_spec,
            CDP.CodeSpec: eval_ndp_code_spec,
            CDP.MakeCanonical: eval_ndp_makecanonical,
            CDP.Specialize: eval_ndp_specialize,
            CDP.ApproxLower: eval_ndp_approx_lower,
            CDP.ApproxUpper: eval_ndp_approx_upper,
            CDP.AddMake: eval_ndp_addmake,
            CDP.IgnoreResources: eval_ndp_ignoreresources,
        }
        
        for klass, hook in cases.items():
            if isinstance(r, klass):
                return hook(r, context)

        if True:
            r = recursive_print(r)
            msg = 'eval_ndp(): cannot evaluate r as an NDP.'
            raise_desc(DPInternalError, msg, r=r)

def eval_ndp_ignoreresources(r, context):
    assert isinstance(r, CDP.IgnoreResources)
    rnames = [_.value for _ in unwrap_list(r.rnames)]
    ndp = eval_ndp(r.dp_rvalue, context)
    # print('ignoring %r' % rnames)
    return ignore_some(ndp, ignore_rnames=rnames, ignore_fnames=[])
    
def eval_ndp_addmake(r, context):
    assert isinstance(r, CDP.AddMake)
    ndp = eval_ndp(r.dp_rvalue, context)
    what = r.what.value
    function_name = r.code.function.value

    function = ImportedFunction(function_name)
    
    if not hasattr(ndp, ATTRIBUTE_NDP_MAKE_FUNCTION):
        setattr(ndp, ATTRIBUTE_NDP_MAKE_FUNCTION, [])

    res = getattr(ndp, ATTRIBUTE_NDP_MAKE_FUNCTION)
    res.append((what, function))
    return ndp

class ImportedFunction():
    def __init__(self, function_name):
        self.function_name = function_name
        self.sys_path = sys.path
        # check that it exists
        _check = self._import()
        
    def _import(self):
        with _sys_path_adjust(self.sys_path):
            try:
                function = import_name(self.function_name)
                return function
            except ImportFailure as e:
                msg = 'Could not import Python function name.'
                raise_wrapped(DPSemanticError, e, msg, function_name=self.function_name,
                              compact=True)

    def __call__(self, *args, **kwargs):
        function = self._import()
        return function(*args, **kwargs)


@contextmanager
def _sys_path_adjust(sys_path):

    previous = list(sys.path)
    sys.path = sys_path

    try:
        yield
    finally:
        sys.path = previous


def eval_ndp_specialize(r, context):
    assert isinstance(r, CDP.Specialize)

    params_ops = unwrap_list(r.params)
    if params_ops:
        keys = params_ops[::2]
        values = params_ops[1::2]
        keys = [_.value for _ in keys]
        if len(keys) != len(set(keys)):
            msg = 'Repeated parameters in specialize.'
            raise_desc(DPSemanticError, msg, keys=keys)
        values = [eval_ndp(_, context) for _ in values]
        d = dict(zip(keys, values))
        params = d
    else:
        params = {}

    template = eval_template(r.template, context)
    return template.specialize(params, context)

def eval_ndp_makecanonical(r, context):
    ndp = eval_ndp(r.dp_rvalue, context)
    return cndp_makecanonical(ndp)

def eval_ndp_code_spec(r, _context):
    from .eval_codespec_imp import eval_codespec
    res = eval_codespec(r, expect=NamedDP)
    return res


def eval_ndp_load(r, context):
    assert isinstance(r, CDP.LoadNDP)
    arg = r.load_arg
    assert isinstance(arg, (CDP.NDPName, CDP.NDPNameWithLibrary))

    if isinstance(arg, CDP.NDPNameWithLibrary):
        assert isinstance(arg.library, CDP.LibraryName), arg
        assert isinstance(arg.name, CDP.NDPName), arg
        libname = arg.library.value
        name = arg.name.value
        library = context.load_library(libname)
        return library.load_ndp(name)

    if isinstance(arg, CDP.NDPName):
        name = arg.value
        ndp = context.load_ndp(name)
        return ndp

    raise NotImplementedError(r)

def eval_ndp_instancefromlibrary(r, context):
    assert isinstance(r, CDP.DPInstanceFromLibrary)
    assert isinstance(r.dpname, (CDP.NDPName, CDP.NDPNameWithLibrary))
    arg = r.dpname

    if isinstance(arg, CDP.NDPNameWithLibrary):
        assert isinstance(arg.library, CDP.LibraryName), arg
        assert isinstance(arg.name, CDP.NDPName), arg

        libname = arg.library.value
        name = arg.name.value
        library = context.load_library(libname)
        return library.load_ndp(name)

    if isinstance(arg, CDP.NDPName):
        name = arg.value
        ndp = context.load_ndp(name)
        return ndp

    raise NotImplementedError(r)

def eval_ndp_flatten(r, context):
    ndp = eval_ndp(r.dp_rvalue, context)
    ndp = ndp.flatten()
    return ndp

def eval_ndp_coproduct(r, context):
    assert isinstance(r, CDP.Coproduct)
    ops = get_odd_ops(unwrap_list(r.ops))
    ndps = []
    for _, op in enumerate(ops):
        ndp = eval_ndp(op, context)
        ndps.append(ndp)

    return NamedDPCoproduct(tuple(ndps))


@contract(r=CDP.CoproductWithNames)
def eval_ndp_CoproductWithNames(r, context):
    assert isinstance(r, CDP.CoproductWithNames)
    elements = unwrap_list(r.elements)
    names = [_.value for _ in elements[0::2]]
    ndps = [eval_ndp(_, context) for _ in elements[1::2]]
    labels = tuple(names)
    return NamedDPCoproduct(tuple(ndps), labels=labels)


def eval_ndp_approxdpmodel(r, context):
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




@contract(r=CDP.DPWrap)
def eval_ndp_dpwrap(r, context):
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


def eval_ndp_catalogue(r, context):
    assert isinstance(r, CDP.FromCatalogue)
    # FIXME:need to check for re-ordering
    statements = unwrap_list(r.funres)
    fun = [x for x in statements if isinstance(x, CDP.FunStatement)]
    res = [x for x in statements if isinstance(x, CDP.ResStatement)]
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

    
    names = set([name for (name, _, _) in entries])
    M = FiniteCollectionAsSpace(names)
    # use integers
    # entries = [(float(i), b, c) for i, (_, b, c) in enumerate(entries)]

    fnames = [_.fname.value for  _ in fun]
    rnames = [_.rname.value for  _ in res]

    if len(Fs) == 1:
        F = Fs[0]
        fnames = fnames[0]
        entries = [(a, b[0], c) for (a, b, c) in entries]
    else:
        F = PosetProduct(tuple(Fs))

    if len(Rs) == 1:
        R = Rs[0]
        rnames = rnames[0]
        entries = [(a, b, c[0]) for (a, b, c) in entries]
    else:
        R = PosetProduct(tuple(Rs))

    dp = CatalogueDP(F=F, R=R, I=M, entries=tuple(entries))
    ndp = dpwrap(dp, fnames=fnames, rnames=rnames)
    return ndp


@contract(resource=CResource, function=CFunction)
def add_constraint(context, resource, function):
    R1 = context.get_rtype(resource)
    F2 = context.get_ftype(function)

    tu = get_types_universe()

    try:
        if tu.equal(R1, F2):
            c = Connection(dp1=resource.dp, s1=resource.s,
                           dp2=function.dp, s2=function.s)
            context.add_connection(c)
    
        elif tu.leq(R1, F2):
            ##  F2    ---- (<=) ----   =>  ----(<=)--- [R1_to_F2] ----
            ##   |     R1       F2          R1      R1             F2
            ##  R1
            R1_to_F2, _F2_to_R1 = tu.get_embedding(R1, F2)
            conversion = Conversion(R1_to_F2, _F2_to_R1)
    
            resource2 = create_operation(context=context, dp=conversion,
                                        resources=[resource], name_prefix='_conversion',
                                         op_prefix='_in', res_prefix='_out')
            c = Connection(dp1=resource2.dp, s1=resource2.s,
                           dp2=function.dp, s2=function.s)
            context.add_connection(c)
        elif tu.leq(F2, R1):
            ##  R1     ---- (<=) ----   =>  ----(<=)--- [F2_to_R1^L] ----
            ##   |h     R1       F2          R1      R1               F2
            ##  F2
            
            _F2_to_R1, R1_to_F2 = tu.get_embedding(F2, R1)
            conversion = Conversion(R1_to_F2, _F2_to_R1)
            resource2 = create_operation(context=context, dp=conversion,
                                        resources=[resource], name_prefix='_conversion',
                                         op_prefix='_in', res_prefix='_out')
            c = Connection(dp1=resource2.dp, s1=resource2.s,
                           dp2=function.dp, s2=function.s)
            context.add_connection(c)
        else:
            msg = 'Constraint between incompatible spaces.'
            raise_desc(DPSemanticError, msg, R1=R1, F2=F2)
    except NotImplementedError as e:
        msg = 'Problem while creating embedding.'
        raise_wrapped(DPInternalError, e, msg, resource=resource, function=function,
                      R1=R1, F2=F2)
        

def eval_statement(r, context):
    with add_where_information(r.where):
        from mcdp_lang.eval_resources_imp import eval_rvalue
        from mcdp_lang.eval_lfunction_imp import eval_lfunction

        if isinstance(r, Connection):
            context.add_connection(r)

        elif isinstance(r, CDP.Constraint):
            resource = eval_rvalue(r.rvalue, context)
            function = eval_lfunction(r.function, context)
            add_constraint(context, resource, function)

        elif isinstance(r, CDP.SetNameNDPInstance):
            name = r.name.value
            ndp = eval_ndp(r.dp_rvalue, context)
            context.add_ndp(name, ndp)

        elif isinstance(r, CDP.SetNameMCDPType):
            name = r.name.value
            right_side = r.right_side
            x = eval_ndp(right_side, context)
            context.set_var2model(name, x)

        elif isinstance(r, CDP.SetNameRValue):
            name = r.name.value
            right_side = r.right_side

            if name in context.constants:
                msg = 'Constant %r already set.' % name
                raise DPSemanticError(msg, where=r.where)

            if name in context.var2resource:
                msg = 'Resource %r already set.' % name
                raise DPSemanticError(msg, where=r.where)

            if name in context.var2function:
                msg = 'Name %r already used.' % name
                raise DPSemanticError(msg, where=r.where)

            from mcdp_lang.eval_constant_imp import NotConstant
            try:
                # from mcdp_lang.eval_constant_imp import eval_constant
                x = eval_constant(right_side, context)
                context.set_constant(name, x)
            except NotConstant:
                #  Cannot evaluate %r as constant
#                 try:
                    x = eval_rvalue(right_side, context)
#                     if False:
#                         mcdp_dev_warning('This might be very risky, but cute.')
#                         ndp = context.names[x.dp]
#                         if isinstance(ndp, SimpleWrap):
#                             if ndp.R_single:
#                                 ndp.Rname = name
#
#                         x = context.make_resource(x.dp, name)
                    # adding as resource
                    context.set_var2resource(name, x)
#                 except Exception as e:
#                     mcdp_dev_warning('fix this')
#                     print('Cannot evaluate %r as eval_rvalue: %s ' % (right_side, e))
#                     # XXX fix this
#                     x = eval_ndp(right_side, context)
#                     context.set_var2model(name, x)

        elif isinstance(r, CDP.SetNameFValue):
            name = r.name.value
            right_side = r.right_side

            if name in context.constants:
                msg = 'Constant %r already set.' % name
                raise DPSemanticError(msg, where=r.where)

            if name in context.var2resource:
                msg = 'Resource %r already set.' % name
                raise DPSemanticError(msg, where=r.where)

            if name in context.var2function:
                msg = 'Name %r already used.' % name
                raise DPSemanticError(msg, where=r.where)

            fv = eval_lfunction(right_side, context)
            context.set_var2function(name, fv)

        elif isinstance(r, CDP.ResStatement):
            # "requires r.rname [r.unit]"
            rname = r.rname.value
            if rname in context.rnames:
                msg = 'Repeated resource name %r.' % rname
                raise DPSemanticError(msg, where=r.rname.where)
            R = eval_space(r.unit, context)

            context.add_ndp_res_node(rname, R)

            return context.make_function(get_name_for_res_node(rname), rname)

        elif isinstance(r, CDP.FunStatement):
            fname = r.fname.value
            if fname in context.fnames:
                msg = 'Repeated function name %r.' % fname
                raise DPSemanticError(msg, where=r.fname.where)

            F = eval_space(r.unit, context)
            context.add_ndp_fun_node(fname, F)

            return context.make_resource(get_name_for_fun_node(fname), fname)

        elif isinstance(r, CDP.FunShortcut1):  # provides fname using name
            fname = r.fname.value
            with add_where_information(r.name.where):
                B = context.make_function(r.name.value, fname)
            F = context.get_ftype(B)
            A = eval_statement(CDP.FunStatement('-', r.fname, CDP.Unit(F)), context)
            add_constraint(context, resource=A, function=B)

        elif isinstance(r, CDP.ResShortcut1):  # requires rname for name
            # resource rname [r0]
            # rname >= name.rname
            with add_where_information(r.name.where):
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

        elif isinstance(r, CDP.IgnoreFun):
            # equivalent to f >= any-of(Minimals S)
            lf = eval_lfunction(r.fvalue, context)
            F = context.get_ftype(lf)
            values = F.get_minimal_elements()
            from mcdp_dp.dp_constant import ConstantMinimals
            dp = ConstantMinimals(F, values)
            ndp = SimpleWrap(dp, fnames=[], rnames='_out')
            name = context.new_name('_constant')
            context.add_ndp(name, ndp)
            r = context.make_resource(name, '_out')
            add_constraint(context, resource=r, function=lf)

        elif isinstance(r, CDP.IgnoreRes):
            # equivalent to r <= any-of(Maximals S)
            rv = eval_rvalue(r.rvalue, context)
            R = context.get_rtype(rv)
            try:
                values = R.get_maximal_elements()
            except NotImplementedError as e:
                msg = 'Could not call get_maximal_elements().'
                raise_wrapped(DPInternalError, e, msg, R=R)

            from mcdp_dp.dp_limit import LimitMaximals
            dp = LimitMaximals(R, values)
            ndp = SimpleWrap(dp, fnames='_limit', rnames=[])
            name = context.new_name('_limit')
            context.add_ndp(name, ndp)
            f = context.make_function(name, '_limit')
            add_constraint(context, resource=rv, function=f)
        else:
            msg = 'eval_statement(): cannot interpret.'
            r = recursive_print(r)
            raise_desc(DPInternalError, msg, r=r)

def eval_build_problem(r, context):
    context = context.child()

    statements = unwrap_list(r.statements)

    for s in statements:
        with add_where_information(s.where):
            try:
                eval_statement(s, context)
            except DPInternalError:
                logger.error(recursive_print(s))
                raise

    # take() optimization
    context.ifun_finish()
    context.ires_finish()
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
        dp = MeetNDualDP(n=len(its), P=P)

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


def eval_ndp_make_template(r, context):
    ndp = eval_ndp(r.dp_rvalue, context)
    from mocdp.comp.composite_templatize import ndp_templatize
    return ndp_templatize(ndp, mark_as_template=False)

