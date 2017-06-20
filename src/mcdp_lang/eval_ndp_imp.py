# -*- coding: utf-8 -*-
from contextlib import contextmanager
from contracts import contract
from mcdp.constants import MCDPConstants
from mcdp.exceptions import (DPInternalError, DPSemanticError,
                             DPSemanticErrorNotConnected, MCDPExceptionWithWhere, mcdp_dev_warning,
                             DPNotImplementedError, DPSyntaxError)
from mcdp_dp import (CatalogueDP, Conversion, JoinNDP, MeetNDualDP, get_conversion, make_series, VariableNode,
                     ConstantMinimals, LimitMaximals, OpaqueDP, FunctionNode, ResourceNode)
from mcdp_posets import FiniteCollectionAsSpace, NotEqual, NotLeq, PosetProduct, get_types_universe
from mocdp.comp import (CompositeNamedDP, Connection, NamedDP, NotConnected,
                        SimpleWrap, dpwrap)
from mocdp.comp.composite_makecanonical import cndp_makecanonical
from mocdp.comp.context import (CFunction, CResource, NoSuchMCDPType,
                                get_name_for_fun_node, get_name_for_res_node, ModelBuildingContext,
                                check_good_name_for_regular_node, check_good_name_for_function,
                                check_good_name_for_resource)
from mocdp.comp.ignore_some_imp import ignore_some
from mocdp.comp.make_approximation_imp import make_approximation
from mocdp.comp.template_deriv import cndp_eversion
from mocdp.ndp.named_coproduct import NamedDPCoproduct
import sys
import warnings

from contracts.utils import raise_desc, raise_wrapped, check_isinstance, indent

from .eval_codespec_imp_utils_instantiate import ImportFailure, import_name
from .eval_constant_imp import eval_constant
from .eval_ndp_approx import eval_ndp_approx_lower, eval_ndp_approx_upper
from .eval_space_imp import eval_space
from .eval_template_imp import eval_template
from .eval_warnings import warn_language, MCDPWarnings
from .eval_warnings import warnings_copy_from_child_make_nested2
from .helpers import create_operation, get_valuewithunits_as_function, get_valuewithunits_as_resource
from .namedtuple_tricks import recursive_print
from .parse_actions import (add_where_information, decorate_add_where, raise_with_info,
                            parse_wrap)
from .parts import CDPLanguage
from .utils_lists import get_odd_ops, unwrap_list
from mcdp_lang.eval_uncertainty import eval_uncertain_constant


CDP = CDPLanguage


@decorate_add_where
@contract(returns=NamedDP)
def eval_ndp(r, context):
    check_isinstance(context, ModelBuildingContext)
    cases = {
        CDP.DPInstance: eval_ndp_dpinstance,
        CDP.Ellipsis: eval_ndp_ellipsis,
        CDP.VariableRef: eval_ndp_variableref,
        CDP.VariableRefNDPType: eval_ndp_VariableRefNDPType,
        CDP.AbstractAway: eval_ndp_abstractaway,
        CDP.Compact: eval_ndp_compact,
        CDP.BuildProblem: eval_build_problem,
        CDP.LoadNDP: eval_ndp_load,
        CDP.DPWrap: eval_ndp_dpwrap,
        CDP.MakeTemplate: eval_ndp_make_template,
        CDP.CoproductWithNames: eval_ndp_CoproductWithNames,
        CDP.ApproxDPModel: eval_ndp_approxdpmodel,
        CDP.FromCatalogue: eval_ndp_catalogue,
        CDP.Catalogue2: eval_ndp_catalogue2,
        CDP.Catalogue3: eval_ndp_catalogue3,
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
        CDP.Eversion: eval_eversion,
    }

    for klass, hook in cases.items():
        if isinstance(r, klass):
            return hook(r, context)

    if True:  # pragma: no cover
        r = recursive_print(r)
        msg = 'eval_ndp(): cannot evaluate r as an NDP.'
        raise_desc(DPInternalError, msg, r=r)


def eval_eversion(r, context):
    check_isinstance(r, CDP.Eversion)
    ndp = eval_ndp(r.ndp, context)
    name = r.dpname.value
    res = cndp_eversion(ndp, name)
    return res


def eval_ndp_dpinstance(r, context):
    return eval_ndp(r.dp_rvalue, context)


def eval_ndp_ellipsis(r, context):  # @UnusedVariable
    msg = 'Model is incomplete (the ellipsis operator "..." was used)'
    raise_desc(DPSemanticError, msg)


def eval_ndp_variableref(r, context):
    try:
        return context.get_var2model(r.name)
    except NoSuchMCDPType as e:  # XXX: fixme
        msg = 'Cannot find name.'
        raise_wrapped(DPSemanticError, e, msg, compact=True)


def eval_ndp_VariableRefNDPType(r, context):
    try:
        return context.get_var2model(r.name)
    except NoSuchMCDPType as e:
        msg = 'Cannot find name.'
        raise_wrapped(DPSemanticError, e, msg, compact=True)


def eval_ndp_abstractaway(r, context):
    ndp = eval_ndp(r.dp_rvalue, context)
    if isinstance(ndp, SimpleWrap):
        return ndp
    try:
        ndp.check_fully_connected()
    except NotConnected as e:
        msg = 'Cannot abstract away the design problem because it is not connected.'
        raise_wrapped(DPSemanticErrorNotConnected, e, msg, compact=True)

    ndpa = ndp.abstract()

    check_isinstance(ndpa, SimpleWrap)

    ndpa.dp = OpaqueDP(ndpa.dp)

    return ndpa


def eval_ndp_compact(r, context):
    ndp = eval_ndp(r.dp_rvalue, context)
    if isinstance(ndp, CompositeNamedDP):
        return ndp.compact()
    else:
        msg = 'Cannot compact primitive NDP.'
        raise_desc(DPSemanticError, msg, ndp=ndp.repr_long())


def eval_ndp_ignoreresources(r, context):
    check_isinstance(r, CDP.IgnoreResources)
    rnames = [_.value for _ in get_odd_ops(unwrap_list(r.rnames))]
    ndp = eval_ndp(r.dp_rvalue, context)
    return ignore_some(ndp, ignore_rnames=rnames, ignore_fnames=[])


def eval_ndp_addmake(r, context):
    check_isinstance(r, CDP.AddMake)
    ndp = eval_ndp(r.dp_rvalue, context)
    what = r.what.value
    function_name = r.code.function.value

    function = ImportedFunction(function_name)

    att = MCDPConstants.ATTRIBUTE_NDP_MAKE_FUNCTION
    if not hasattr(ndp, att):
        setattr(ndp, att, [])

    res = getattr(ndp, att)
    res.append((what, function))
    return ndp


class ImportedFunction(object):

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
    check_isinstance(r, CDP.Specialize)

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
    check_isinstance(r, CDP.LoadNDP)
    arg = r.load_arg
    check_isinstance(arg, (CDP.NDPName, CDP.NDPNameWithLibrary))

    try:
        if isinstance(arg, CDP.NDPNameWithLibrary):
            check_isinstance(arg.library, CDP.LibraryName), arg
            check_isinstance(arg.name, CDP.NDPName), arg
            libname = arg.library.value
            name = arg.name.value
            library = context.load_library(libname)

            context2 = context.child()
            res = library.load_ndp(name, context2)

            msg = 'While loading MCDP %r from library %r:' % (name, libname)
            warnings_copy_from_child_make_nested2(
                context, context2, r.where, msg)
            return res

        if isinstance(arg, CDP.NDPName):
            name = arg.value

            context2 = context.child()
            res = context2.load_ndp(name)
            msg = 'While loading MCDP %r:' % (name)
            warnings_copy_from_child_make_nested2(
                context, context2, r.where, msg)
            return res
    except DPSyntaxError as e:
        msg = 'Syntax error while loading %s:' % (name)
        s = str(e)
        print s
        msg += '\n\n' + indent(str(e), '   ')
        raise DPSemanticError(msg, where=arg.where)
        #raise_wrapped(DPSemanticError, e, msg, compact=True)

    if True:  # pragma: no cover
        msg = 'Unknown construct.'
        raise_desc(DPInternalError, msg, r=r)


def eval_ndp_instancefromlibrary(r, context):
    msg = 'Construct "new X" is deprecated in favor of "instance `X".'
    warn_language(r, MCDPWarnings.LANGUAGE_CONSTRUCT_DEPRECATED, msg, context)

    check_isinstance(r, CDP.DPInstanceFromLibrary)
    check_isinstance(r.dpname, (CDP.NDPName, CDP.NDPNameWithLibrary))
    arg = r.dpname

    if isinstance(arg, CDP.NDPNameWithLibrary):
        check_isinstance(arg.library, CDP.LibraryName), arg
        check_isinstance(arg.name, CDP.NDPName), arg

        libname = arg.library.value
        name = arg.name.value

        library = context.load_library(libname)

        context2 = context.child()
        res = library.load_ndp(name, context2)
        msg = 'While loading %r from library %r:' % (name, libname)
        warnings_copy_from_child_make_nested2(context, context2, r.where, msg)
        return res

    if isinstance(arg, CDP.NDPName):
        name = arg.value
        ndp = context.load_ndp(name)
        return ndp

    if True:  # pragma: no cover
        msg = 'Unknown construct.'
        raise_desc(DPInternalError, msg, r=r)


def eval_ndp_flatten(r, context):
    ndp = eval_ndp(r.dp_rvalue, context)
    ndp = ndp.flatten()
    return ndp


@contract(r=CDP.CoproductWithNames)
def eval_ndp_CoproductWithNames(r, context):
    check_isinstance(r, CDP.CoproductWithNames)
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
    # check_isinstance(x, ValueWithUnit)
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

    from .eval_primitivedp_imp import eval_primitivedp
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

    mcdp_dev_warning('Not sure about this')
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
    ftypes_expected = PosetProduct(
        tuple([eval_space(f.unit, context) for f in fun]))
    rtypes_expected = PosetProduct(
        tuple([eval_space(r.unit, context) for r in res]))

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
    check_isinstance(r, CDP.FromCatalogue)
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
            msg = 'Row with %d elements does not match expected of elements (%s fun, %s res)' % (
                len(items), len(fun), len(res))
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
                msg = 'Dimensionality problem: cannot convert %s to %s.' % (
                    Fhave.unit, F)
                ex = lambda msg: DPSemanticError(msg, where=cell.where)
                raise_wrapped(ex, e, msg, compact=True)

        for cell, Rhave, R in zip(rvalues0, rvalues, Rs):
            try:
                tu.check_leq(Rhave.unit, R)
            except NotLeq as e:
                msg = 'Dimensionality problem: cannot convert %s to %s.' % (
                    Rhave.unit, R)
                ex = lambda msg: DPSemanticError(msg, where=cell.where)
                raise_wrapped(ex, e, msg, compact=True)

        fvalues_ = [_.cast_value(F) for (_, F) in zip(fvalues, Fs)]
        rvalues_ = [_.cast_value(R)for (_, R) in zip(rvalues, Rs)]

        assert len(fvalues_) == len(fun)
        assert len(rvalues_) == len(res)

        entries.append((name, tuple(fvalues_), tuple(rvalues_)))

    names = set([name for (name, _, _) in entries])
    M = FiniteCollectionAsSpace(names)
    # use integers
    # entries = [(float(i), b, c) for i, (_, b, c) in enumerate(entries)]

    fnames = [_.fname.value for _ in fun]
    rnames = [_.rname.value for _ in res]

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


def eval_ndp_catalogue2(r, context):
    check_isinstance(r, CDP.Catalogue2)
    # FIXME:need to check for re-ordering
    statements = unwrap_list(r.funres)
    fun = [x for x in statements if isinstance(x, CDP.FunStatement)]
    res = [x for x in statements if isinstance(x, CDP.ResStatement)]
    Fs = [eval_space(_.unit, context) for _ in fun]
    Rs = [eval_space(_.unit, context) for _ in res]

    assert len(fun) + len(res) == len(statements), statements

    tu = get_types_universe()

    rows = unwrap_list(r.table)

    entries = []  # (name, f, r)

    for row in rows:
        check_isinstance(row, CDP.CatalogueRowMapsfromto)

        check_isinstance(row.functions, CDP.CatalogueFunc)
        row.mapsfrom
        row.impname
        row.impname.value
        row.mapsto
        check_isinstance(row.resources, CDP.CatalogueRes)

        fs = get_odd_ops(unwrap_list(row.functions.ops))
        rs = get_odd_ops(unwrap_list(row.resources.ops))

        for _ in list(fs) + list(rs):
            if isinstance(_, CDP.CatalogueEntryConstantUncertain):
                msg = 'Uncertain catalogue not implemented'
                raise DPNotImplementedError(msg, where=_.where)

        fs_evaluated = [eval_constant(_.constant, context) for _ in fs]
        rs_evaluated = [eval_constant(_.constant, context) for _ in rs]

        if len(Fs) == 0:
            # expect <>
            if len(fs) != 1 and fs_evaluated.value != ():
                msg = 'Because there are no functionalities, I expected simply "<>".'
                raise DPSemanticError(msg, where=row.functions.where)
        else:
            if len(fs_evaluated) != len(Fs):
                msg = 'Mismatch with number of functionalities.'
                raise DPSemanticError(msg, where=row.functions.where)

        if len(Rs) == 0:
            if len(rs) != 1 and rs_evaluated.value != ():
                msg = 'Because there are no resources, I expected simply "<>".'
                raise DPSemanticError(msg, where=row.resources.where)
        else:
            if len(rs_evaluated) != len(Rs):
                msg = 'Mismatch with number of resources.'
                raise DPSemanticError(msg, where=row.resources.where)

        for cell, Fhave, F in zip(fs, fs_evaluated, Fs):
            try:
                tu.check_leq(Fhave.unit, F)
            except NotLeq:
                msg = 'Dimensionality problem: cannot convert %s to %s.' % (
                    Fhave.unit, F)
                raise DPSemanticError(msg, where=cell.where)
#                 ex = lambda msg: DPSemanticError(msg, where=cell.where)
#                 raise_wrapped(ex, e, msg, compact=True)

        for cell, Rhave, R in zip(rs, rs_evaluated, Rs):
            try:
                tu.check_leq(Rhave.unit, R)
            except NotLeq:
                msg = 'Dimensionality problem: cannot convert %s to %s.' % (
                    Rhave.unit, R)
                raise DPSemanticError(msg, where=cell.where)
#                 ex = lambda msg: DPSemanticError(msg, where=cell.where)
#                 raise_wrapped(ex, e, msg, compact=True)

        fvalues_ = [_.cast_value(F) for (_, F) in zip(fs_evaluated, Fs)]
        rvalues_ = [_.cast_value(R) for (_, R) in zip(rs_evaluated, Rs)]

        assert len(fvalues_) == len(fun)
        assert len(rvalues_) == len(res)

        i = row.impname.value
        f = tuple(fvalues_)
        r = tuple(rvalues_)

        if len(Fs) == 0:
            f = ()
        if len(Rs) == 0:
            r = ()

        entries.append((i, f, r))

    names = set([name for (name, _, _) in entries])

    M = FiniteCollectionAsSpace(names)
    # use integers
    # entries = [(float(i), b, c) for i, (_, b, c) in enumerate(entries)]

    fnames = [_.fname.value for _ in fun]
    rnames = [_.rname.value for _ in res]

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


def eval_ndp_catalogue3(r, context):
    check_isinstance(r, CDP.Catalogue3)

    statements = unwrap_list(r.funres)
    fun = [x for x in statements if isinstance(x, CDP.FunStatement)]
    res = [x for x in statements if isinstance(x, CDP.ResStatement)]
    Fs = [eval_space(_.unit, context) for _ in fun]
    Rs = [eval_space(_.unit, context) for _ in res]

    assert len(fun) + len(res) == len(statements), statements

    tu = get_types_universe()

    rows = unwrap_list(r.table)

    entries = []  # (name, f, r)

    for i, row in enumerate(rows):
        check_isinstance(row, CDP.CatalogueRow3)

        check_isinstance(row.functions, CDP.CatalogueFunc)
        row.leftright
        check_isinstance(row.resources, CDP.CatalogueRes)

        fs = get_odd_ops(unwrap_list(row.functions.ops))
        rs = get_odd_ops(unwrap_list(row.resources.ops))

        for _ in list(fs) + list(rs):
            if isinstance(_, CDP.CatalogueEntryConstantUncertain):
                msg = 'Uncertain catalogue not implemented'
                raise DPNotImplementedError(msg, where=_.where)

        fs_evaluated = [eval_constant(_.constant, context) for _ in fs]
        rs_evaluated = [eval_constant(_.constant, context) for _ in rs]

        if len(Fs) == 0:
            # expect <>
            if len(fs) != 1 and fs_evaluated.value != ():
                msg = 'Because there are no functionalities, I expected simply "<>".'
                raise DPSemanticError(msg, where=row.functions.where)
        else:
            if len(fs_evaluated) != len(Fs):
                msg = 'Mismatch with number of functionalities.'
                raise DPSemanticError(msg, where=row.functions.where)

        if len(Rs) == 0:
            if len(rs) != 1 and rs_evaluated.value != ():
                msg = 'Because there are no resources, I expected simply "<>".'
                raise DPSemanticError(msg, where=row.resources.where)
        else:
            if len(rs_evaluated) != len(Rs):
                msg = 'Mismatch with number of resources.'
                raise DPSemanticError(msg, where=row.resources.where)

        for cell, Fhave, F in zip(fs, fs_evaluated, Fs):
            try:
                tu.check_leq(Fhave.unit, F)
            except NotLeq:
                msg = 'Dimensionality problem: cannot convert %s to %s.' % (
                    Fhave.unit, F)
                raise DPSemanticError(msg, where=cell.where)

        for cell, Rhave, R in zip(rs, rs_evaluated, Rs):
            try:
                tu.check_leq(Rhave.unit, R)
            except NotLeq:
                msg = 'Dimensionality problem: cannot convert %s to %s.' % (
                    Rhave.unit, R)
                raise DPSemanticError(msg, where=cell.where)

        fvalues_ = [_.cast_value(F) for (_, F) in zip(fs_evaluated, Fs)]
        rvalues_ = [_.cast_value(R) for (_, R) in zip(rs_evaluated, Rs)]

        assert len(fvalues_) == len(fun)
        assert len(rvalues_) == len(res)

        f = tuple(fvalues_)
        r = tuple(rvalues_)

        if len(Fs) == 0:
            f = ()
        if len(Rs) == 0:
            r = ()

        entries.append((i, f, r))

    names = set([name for (name, _, _) in entries])

    M = FiniteCollectionAsSpace(names)
    # use integers
    # entries = [(float(i), b, c) for i, (_, b, c) in enumerate(entries)]

    fnames = [_.fname.value for _ in fun]
    rnames = [_.rname.value for _ in res]

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
    check_isinstance(resource, CResource)
    check_isinstance(function, CFunction)

    R1 = context.get_rtype(resource)
    F2 = context.get_ftype(function)

    tu = get_types_universe()

    try:
        if tu.equal(R1, F2):
            c = Connection(dp1=resource.dp, s1=resource.s,
                           dp2=function.dp, s2=function.s)
            context.add_connection(c)
        else:
            # F2    ---- (<=) ----   becomes  ----(<=)--- [R1_to_F2] ----
            # |     R1       F2                R1      R1             F2
            # R1
            try:
                R1_to_F2, F2_to_R1 = tu.get_super_conversion(R1, F2)
                conversion = Conversion(R1_to_F2, F2_to_R1)
                assert tu.equal(R1, conversion.get_fun_space())
                assert tu.equal(F2, conversion.get_res_space())
                resource2 = create_operation(context=context, dp=conversion,
                                             resources=[resource], name_prefix='_conversion')
                c = Connection(dp1=resource2.dp, s1=resource2.s,
                               dp2=function.dp, s2=function.s)
                context.add_connection(c)
            except NotLeq as e:
                msg = 'Constraint between incompatible spaces.'
                msg += '\n  %s can be embedded in %s: %s ' % (
                    R1, F2, tu.leq(R1, F2))
                msg += '\n  %s can be embedded in %s: %s ' % (
                    F2, R1, tu.leq(F2, R1))
                raise_wrapped(
                    DPSemanticError, e, msg, R1=R1, F2=F2, compact=True)
    except NotImplementedError as e:  # pragma: no cover
        msg = 'Problem while creating embedding.'
        raise_wrapped(DPInternalError, e, msg, resource=resource, function=function,
                      R1=R1, F2=F2)


def add_variable(vname, P, where, context):
    if vname in context.variables:
        msg = 'Variable name %r already used once.' % vname
        raise DPSemanticError(msg, where=where)

    if vname in context.rnames:
        msg = 'Conflict between variable and resource name %r.' % vname
        raise DPSemanticError(msg, where=where)

    if vname in context.fnames:
        msg = 'Conflict between variable and functionality name %r.' % vname
        raise DPSemanticError(msg, where=where)

    if vname in context.var2resource:
        msg = 'The name %r is already used as a resource.' % vname
        raise DPSemanticError(msg, where=where)

    if vname in context.var2function:
        msg = 'The name %r is already used as a functionality.' % vname
        raise DPSemanticError(msg, where=where)

    try:
        check_good_name_for_regular_node(vname)
    except ValueError as e:
        msg = 'Invalid name: %s' % e
        raise DPSemanticError(msg, where=where)

    dp = VariableNode(P, vname)
    fname = '_' + vname
    rname = '_' + vname
    ndp = dpwrap(dp, fname, rname)
    context.add_ndp(vname, ndp)

    context.set_var2resource(vname, CResource(vname, rname))
    context.set_var2function(vname, CFunction(vname, fname))

    context.variables.add(vname)


def check_name_not_in_use(name, context, expr):
    if name in context.constants:
        msg = 'Constant %r already set.' % name
        raise DPSemanticError(msg, where=expr.where)

    if name in context.var2resource:
        msg = 'Resource %r already set.' % name
        raise DPSemanticError(msg, where=expr.where)

    if name in context.var2function:
        msg = 'Name %r already used.' % name
        raise DPSemanticError(msg, where=expr.where)


def eval_statement_SetNameConstant(r, context):
    check_isinstance(r, CDP.SetNameConstant)

    name = r.name.value
    right_side = r.right_side

    check_name_not_in_use(name, context, r)

    x = eval_constant(right_side, context)
    context.set_constant(name, x)


def eval_statement_SetNameUncertainConstant(r, context):
    check_isinstance(r, CDP.SetNameUncertainConstant)

    name = r.name.value
    right_side = r.right_side

    check_name_not_in_use(name, context, r)
    uc = eval_uncertain_constant(right_side, context)
    context.set_uncertain_constant(name, uc) 


def eval_statement_SetNameRValue(r, context):
    """ 
        This is a special case, because it is the place
        where the syntax is ambiguous.

            x = Nat: 1 + r

        could be interpreted with r being a functionality
        or a resource.

        By default it is parsed as SetNameRValue, and so we get here.

        We check whether it could be parsed as setname_fvalue,
        and warn about that.

    """
    from .eval_resources_imp import eval_rvalue
    from .eval_constant_imp import NotConstant
    from .syntax import Syntax

    check_isinstance(r, CDP.SetNameRValue)

    # Check to see if this could have been interpreted using
    #    setname_fvalue
    # Try to have an alternative parsing of the string as
    #     Syntax.setname_fvalue
    try:
        w = r.where
        s = w.string[w.character:w.character_end]
        alt = parse_wrap(Syntax.setname_fvalue, s)[0]
        # print('alternative: %s' % recursive_print(alt))
    except Exception as _:  # XXX: which one?
        # print "No, it does not parse: %s" % traceback.format_exc(e)
        alt = None

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

    try:
        x = eval_constant(right_side, context)
        context.set_constant(name, x)
        used_constant = True
    except NotConstant:
        used_constant = False
        try:
            x = eval_rvalue(right_side, context)
            ndp1 = context.names[x.dp]
            current = x.s
            updated = name
            try:
                ndp2 = ndp_rename_resource(
                    ndp1, current=current, updated=updated)
                context.names[x.dp] = ndp2
                x = CResource(x.dp, updated)
            except CouldNotRename:
                pass

            context.set_var2resource(name, x)
            used_rvalue = True

        except DPSemanticError:  # as e:
            #             if 'not declared' in str(e) and alt is not None:
            #                 # XXX: this seems not to be used anymore
            #                 # after we implemented the interpretation at the syntax level
            #                 msg = 'This should not happen...'
            #                 raise_wrapped(DPNotImplementedError, e, msg)
            #                 x = eval_lfunction(alt.right_side, context)
            #                 context.set_var2function(name, x)
            #                 used_rvalue = False
            #             else:
            raise

    if alt is not None:
        msg = ('This expression could be parsed both as a functionality '
               'and as a resource.')
        if used_constant:
            pass
        #             msg += ' I parsed it as a constant.'
        else:
            if used_rvalue:
                msg += ' I parsed it as a resource.'
            else:
                msg += ' I parsed it as a function.'

                warn_language(r, MCDPWarnings.LANGUAGE_AMBIGUOS_EXPRESSION,
                              msg, context)


def eval_statement_SetNameFvalue(r, context):
    check_isinstance(r, CDP.SetNameFValue)
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

    from .eval_lfunction_imp import eval_lfunction

    fv = eval_lfunction(right_side, context)

    ndp = context.names[fv.dp]
    # TODO: check that is not used anywhere

    current = fv.s
    updated = name
    try:
        ndp2 = ndp_rename_function(ndp, current=current, updated=updated)
        context.names[fv.dp] = ndp2
        fv = CFunction(fv.dp, updated)
    except CouldNotRename:
        pass

    context.set_var2function(name, fv)


class CouldNotRename(Exception):
    """ Raised by ndp_rename_function() if they could not rename 
        the function/resource.

        For example:
            - if it's a SimpleWrap with FunctionNode or ResourceNode
            - if it's a CompositedNamedDP
    """


@contract(ndp=NamedDP, current=str, updated=str)
def ndp_rename_function(ndp, current, updated):
    """ Returns a NamedDP with a renamed function. Only works
        with SimpleWrap + not FunctionNode or ResourceNode. In 
        case, it raises CouldNotRename() """
    fnames = ndp.get_fnames()
    if not current in fnames:  # pragma: no cover
        msg = 'Cannot find function %r in ndp.' % current
        raise_desc(
            DPInternalError, msg, current=current, updated=updated, ndp=ndp)

    if isinstance(ndp, SimpleWrap) and \
            not isinstance(ndp.dp, (FunctionNode, ResourceNode)):

        return ndp.get_copy_with_renamed_function(current, updated)
    else:
        raise CouldNotRename()

#     raise_desc(DPNotImplementedError, 'not implemented', ndp=ndp)


@contract(ndp=NamedDP, current=str, updated=str)
def ndp_rename_resource(ndp, current, updated):
    """ Returns a NamedDP with a renamed resource. """
    rnames = ndp.get_rnames()
    if not current in rnames:  # pragma: no cover
        msg = 'Cannot find %r in ndp.' % current
        raise_desc(
            DPInternalError, msg, current=current, updated=updated, ndp=ndp)

    if isinstance(ndp, SimpleWrap) and \
            not isinstance(ndp.dp, (FunctionNode, ResourceNode)):
        return ndp.get_copy_with_renamed_resource(current, updated)
    else:
        raise CouldNotRename()


def add_function(fname, F, context, r, repeated_ok=False):
    check_isinstance(fname, str)
    try:
        check_good_name_for_function(fname)
    except ValueError as e:
        msg = 'Invalid name for functionality: %s' % e
        raise DPSemanticError(msg, where=r.where)

    if fname in context.fnames:
        if not repeated_ok:
            msg = 'Repeated function name %r.' % fname
            raise DPSemanticError(msg, where=r.where)
        else:
            # check same or different
            warnings.warn('check same')
    else:
        context.add_ndp_fun_node(fname, F)
    return context.make_resource(get_name_for_fun_node(fname), fname)


def add_resource(rname, R, context, r, repeated_ok=False):
    check_isinstance(rname, str)
    try:
        check_good_name_for_resource(rname)
    except ValueError as e:
        msg = 'Invalid name for resource: %s' % e
        raise DPSemanticError(msg, where=r.where)

    if rname in context.rnames:
        if not repeated_ok:
            msg = 'Repeated resource name %r.' % rname
            raise DPSemanticError(msg, where=r.where)
        else:
            # check same or different
            warnings.warn('check same')
    else:
        context.add_ndp_res_node(rname, R)
    return context.make_function(get_name_for_res_node(rname), rname)


@decorate_add_where
def eval_statement(r, context):
    check_isinstance(context, ModelBuildingContext)
    from .eval_resources_imp import eval_rvalue
    from .eval_lfunction_imp import eval_lfunction

    invalid = (CDP.ConstraintInvalidRR,
               CDP.ConstraintInvalidFF,
               CDP.ConstraintInvalidSwapped)

    if isinstance(r, invalid):
        msg = 'This constraint is invalid. '

        if isinstance(r, CDP.ConstraintInvalidRR):
            msg += 'Both sides are resources.'
        if isinstance(r, CDP.ConstraintInvalidFF):
            msg += 'Both sides are functionalities.'
        if isinstance(r, CDP.ConstraintInvalidSwapped):
            msg += ('Functionality and resources are on the wrong side '
                    'of the inequality.')

        raise DPSemanticError(msg)

    if isinstance(r, Connection):
        context.add_connection(r)

    elif isinstance(r, CDP.Constraint):
        resource = eval_rvalue(r.rvalue, context)
        function = eval_lfunction(r.fvalue, context)
        try:
            add_constraint(context, resource, function)
        except MCDPExceptionWithWhere as e:
            _, _, tb = sys.exc_info()
            where = r.prep.where  # indicate preposition "<="
            raise_with_info(e, where, tb)

    elif isinstance(r, CDP.VarStatement):
        P = eval_space(r.unit, context)

        vnames = get_odd_ops(unwrap_list(r.vnames))
        for v in vnames:
            vname = v.value
            where = v.where
            add_variable(vname, P, where, context)

    elif isinstance(r, CDP.SetNameNDPInstance):
        name = r.name.value
        ndp = eval_ndp(r.dp_rvalue, context)
        if name in context.names:
            msg = 'Repeated identifier "%s".' % name
            raise DPSemanticError(msg, where=r.name.where)
        context.add_ndp(name, ndp)

    elif isinstance(r, CDP.SetNameMCDPType):
        name = r.name.value
        right_side = r.right_side
        x = eval_ndp(right_side, context)
        context.set_var2model(name, x)

    elif isinstance(r, CDP.SetNameRValue):
        return eval_statement_SetNameRValue(r, context)
    elif isinstance(r, CDP.SetNameConstant):
        return eval_statement_SetNameConstant(r, context)
    elif isinstance(r, CDP.SetNameFValue):
        return eval_statement_SetNameFvalue(r, context)
    elif isinstance(r, CDP.Implements):
        return eval_statement_implements(r, context)

    elif isinstance(r, CDP.IgnoreFun):
        # equivalent to f >= any-of(Minimals S)
        lf = eval_lfunction(r.fvalue, context)
        F = context.get_ftype(lf)
        values = F.get_minimal_elements()

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
        except NotImplementedError as e:  # pragma: no cover
            msg = 'Could not call get_maximal_elements().'
            raise_wrapped(DPInternalError, e, msg, R=R)

        dp = LimitMaximals(R, values)
        ndp = SimpleWrap(dp, fnames='_limit', rnames=[])
        name = context.new_name('_limit')
        context.add_ndp(name, ndp)
        f = context.make_function(name, '_limit')
        add_constraint(context, resource=rv, function=f)
    else:

        cases = {
            CDP.ResStatement: eval_statement_ResStatement,
            CDP.FunStatement: eval_statement_FunStatement,

            CDP.FunShortcut5: eval_statement_FunShortcut5,
            CDP.ResShortcut5: eval_statement_ResShortcut5,
            CDP.ResShortcut4: eval_statement_ResShortcut4,
            CDP.FunShortcut4: eval_statement_FunShortcut4,

            CDP.FunShortcut1m: eval_statement_FunShortcut1m,
            CDP.ResShortcut1m: eval_statement_ResShortcut1m,

            CDP.FunShortcut2: eval_statement_FunShortcut2,
            CDP.ResShortcut2: eval_statement_ResShortcut2,

            CDP.FunShortcut1: eval_statement_FunShortcut1,
            CDP.ResShortcut1: eval_statement_ResShortcut1,
            CDP.SetNameUncertainConstant: eval_statement_SetNameUncertainConstant,

        }

        for klass, hook in cases.items():
            if isinstance(r, klass):
                return hook(r, context)

        if True:  # pragma: no cover
            msg = 'eval_statement(): cannot interpret.'
            r2 = recursive_print(r)
            raise_desc(DPInternalError, msg, r=r2)  # where=r.where.__repr__())


def eval_statement_implements(r, context):
    interface = eval_ndp(r.interface, context)
    for fn in interface.get_fnames():
        F = interface.get_ftype(fn)
        add_function(fn, F, context, r=interface)

    for rn in interface.get_rnames():
        R = interface.get_rtype(rn)
        add_resource(rn, R, context, r=interface)


def eval_statement_FunShortcut1(r, context):
    # provides fname using name
    fname = r.fname.value
    with add_where_information(r.name.where):
        B = context.make_function(r.name.value, fname)
    F = context.get_ftype(B)
    A = add_function(r.fname.value, F, context, r=r.name, repeated_ok=True)
    add_constraint(context, resource=A, function=B)


def eval_statement_ResShortcut1(r, context):
    # requires rname for name
    with add_where_information(r.name.where):
        A = context.make_resource(r.name.value, r.rname.value)
    R = context.get_rtype(A)
    B = add_resource(r.rname.value, R, context, r=r.name, repeated_ok=True)
    add_constraint(context, resource=A, function=B)  # B >= A


def eval_statement_FunShortcut2(r, context):
    # provides rname <= (lf)
    from mcdp_lang.eval_lfunction_imp import eval_lfunction
    if isinstance(r.prep, CDP.leq):
        msg = 'This is deprecated, and should be "=".'
        warn_language(
            r.prep, MCDPWarnings.LANGUAGE_CONSTRUCT_DEPRECATED, msg, context)

    B = eval_lfunction(r.lf, context)
    check_isinstance(B, CFunction)
    F = context.get_ftype(B)
    A = add_function(r.fname.value, F, context, r)
    add_constraint(context, resource=A, function=B)


def eval_statement_ResShortcut2(r, context):
    # requires rname >= (rvalue)
    from mcdp_lang.eval_resources_imp import eval_rvalue

    if isinstance(r.prep, CDP.geq):
        msg = 'This is deprecated, and should be "=".'
        warn_language(
            r.prep, MCDPWarnings.LANGUAGE_CONSTRUCT_DEPRECATED, msg, context)

    A = eval_rvalue(r.rvalue, context)
    check_isinstance(A, CResource)
    R = context.get_rtype(A)
    B = add_resource(r.rname.value, R, context, r)
    # B >= A
    add_constraint(context, resource=A, function=B)


def eval_statement_ResShortcut1m(r, context):
    # requires rname1, rname2, ... for name
    rnames = get_odd_ops(unwrap_list(r.rnames))
    for rname in rnames:
        A = context.make_resource(r.name.value, rname.value)
        R = context.get_rtype(A)
        B = add_resource(rname.value, R, context, r=rname, repeated_ok=True)
        add_constraint(context, resource=A, function=B)


def eval_statement_FunShortcut1m(r, context):
    # provides fname1,fname2,... using name
    fnames = get_odd_ops(unwrap_list(r.fnames))
    for fname in fnames:
        B = context.make_function(r.name.value, fname.value)
        F = context.get_ftype(B)
        A = add_function(fname.value, F, context, r=fname, repeated_ok=True)
        add_constraint(context, resource=A, function=B)


def eval_statement_ResStatement(r, context):
    # provides r [Nat] 'comment'
    R = eval_space(r.unit, context)
    rname = r.rname
    return add_resource(rname.value, R, context, r=rname)


def eval_statement_FunStatement(r, context):
    # provides r [Nat] 'comment'
    F = eval_space(r.unit, context)
    fname = r.fname
    return add_function(fname.value, F, context, r=fname)


def eval_statement_ResShortcut5(r, context):
    # requires r1, r2 [Nat] 'comment'
    check_isinstance(r, CDP.ResShortcut5)
    R = eval_space(r.unit, context)

    rnames = get_odd_ops(unwrap_list(r.rnames))
    for rname in rnames:
        add_resource(rname.value, R, context, r=rname)


def eval_statement_FunShortcut5(r, context):
    check_isinstance(r, CDP.FunShortcut5)
    # provides f1, f2 [Nat] 'comment'
    F = eval_space(r.unit, context)

    fnames = get_odd_ops(unwrap_list(r.fnames))
    for fname in fnames:
        add_function(fname.value, F, context, r=fname)


def eval_build_problem(r, context0):
    context = context0.child()

    check_isinstance(r.statements, CDP.ModelStatements)
    statements = unwrap_list(r.statements.statements)

    for s in statements:
        eval_statement(s, context)

    from .eval_warnings import warnings_copy_from_child
    warnings_copy_from_child(context0, context)

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


def eval_statement_ResShortcut4(r, context):
    check_isinstance(r, CDP.ResShortcut4)
    # requires rname1, rname2
    rnames = get_odd_ops(unwrap_list(r.rnames))
    for _ in rnames:
        rname = _.value
        if rname in context.var2resource:
            A = context.var2resource[rname]
        elif rname in context.fnames:  # it's a function
            A = context.make_resource(get_name_for_fun_node(rname), rname)
        elif rname in context.constants:
            c = context.constants[rname]
            A = get_valuewithunits_as_resource(c, context)
        else:
            msg = 'Could not find required resource expression %r.' % rname
            raise DPSemanticError(msg, where=_.where)
        R = context.get_rtype(A)
        B = add_resource(rname, R, context, r)
        add_constraint(context, resource=A, function=B)  # B >= A


def eval_statement_FunShortcut4(r, context):
    # provides rname1, rname2
    check_isinstance(r, CDP.FunShortcut4)

    fnames = get_odd_ops(unwrap_list(r.fnames))
    for _ in fnames:
        fname = _.value
        if fname in context.var2function:
            B = context.var2function[fname]
        elif fname in context.rnames:  # it's a function
            B = context.make_function(get_name_for_res_node(fname), fname)
        elif fname in context.constants:
            c = context.constants[fname]
            B = get_valuewithunits_as_function(c, context)
        else:
            msg = 'Could not find required function expression %r.' % fname
            raise DPSemanticError(msg, where=_.where)
        F = context.get_ftype(B)
        A = add_function(fname, F, context, r)
        add_constraint(context, resource=A, function=B)  # B >= A
