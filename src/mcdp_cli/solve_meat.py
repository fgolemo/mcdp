# -*- coding: utf-8 -*-
from .query_interpretation import interpret_string
from .utils_mkdir import mkdirs_thread_safe
from contracts.utils import raise_desc, raise_wrapped
from decent_params.utils.script_utils import UserError
from mcdp_dp.dp_transformations import get_dp_bounds
from mcdp_dp.solver import generic_solve
from mcdp_dp.solver_iterative import solver_iterative
from mcdp_dp.tracer import Tracer
from mcdp_library.libraries import Librarian
from mcdp_posets import NotEqual, PosetProduct, UpperSets, get_types_universe
from mcdp_posets.poset import NotLeq
from mcdp_posets.types_universe import express_value_in_isomorphic_space
from mcdp_report.report import report_dp1, report_ndp1
from mocdp.comp.recursive_name_labeling import (get_imp_as_recursive_dict,
    label_with_recursive_names, ndp_make)
from reprep import Report
import os


class ExpectationsNotMet(Exception):
    pass

def solve_main(logger, config_dirs, maindir, cache_dir, model_name, lower, upper, out_dir,
               max_steps, query_strings,
       intervals, _exp_advanced, expect_nres, imp, expect_nimp, plot, do_movie,

       # expect_res=None,
       expect_res,
       make
       ):

    if out_dir is None:
        out = solve_get_output_dir(prefix='out/out')
    else:
        out = out_dir

    logger.info('Using output dir %r' % out)

    librarian = Librarian()
    for e in config_dirs:
        librarian.find_libraries(e)

    library = librarian.get_library_by_dir(maindir)
    if cache_dir is not None:
        library.use_cache_dir(cache_dir)

    ndp = library.load_ndp(model_name)
    basename = model_name

    if make:
        label_with_recursive_names(ndp)

    basename, dp = solve_get_dp_from_ndp(basename=basename, ndp=ndp,
                                         lower=lower, upper=upper)


    F = dp.get_fun_space()
    R = dp.get_res_space()
    UR = UpperSets(R)

    query = " ".join(query_strings)
    c = library.parse_constant(query)
    tu = get_types_universe()
    try:
        tu.check_leq(c.unit, F)
    except NotLeq as e:
        msg = 'The value given cannot be converted to functionality space.'
        raise_wrapped(UserError, e, msg, unit=c.unit, F=F, compact=True)
    fg = express_value_in_isomorphic_space(F, c.value, c.unit)

    logger.info('query: %s' % F.format(fg))

    tracer = Tracer(logger=logger)
    res, trace = solve_meat_solve(tracer, ndp, dp, fg, intervals, max_steps, _exp_advanced)

    nres = len(res.minimals)

    if expect_nres is not None:
        if nres != expect_nres:
            msg = 'Found wrong number of resources'
            raise_desc(ExpectationsNotMet, msg,
                       expect_nres=expect_nres, nres=nres)

    if imp:
        M = dp.get_imp_space()
        nimplementations = 0
        for r in res.minimals:
            ms = dp.get_implementations_f_r(fg, r)
            nimplementations += len(ms)
            s = 'r = %s ' % R.format(r)
            for j, m in enumerate(ms):
                # print('m = %s' % str(m))
                s += "\n  implementation %d of %d: m = %s " % (j + 1, len(ms), M.format(m))

                if make:
                    imp_dict = get_imp_as_recursive_dict(M, m)  # , ignore_hidden=False)
                    print('imp dict: %r' % imp_dict)
                    context = {}
                    artifact = ndp_make(ndp, imp_dict, context)

                    print('artifact: %s' % artifact)

            tracer.log(s)


        if expect_nimp is not None:
            if expect_nimp != nimplementations:
                msg = 'Found wrong number of implementations'
                raise_desc(ExpectationsNotMet, msg,
                           expect_nimp=expect_nimp,
                           nimplementations=nimplementations)

    if expect_res is not None:
        value = interpret_string(expect_res)
        tracer.log('value: %s' % value)
        res_expected = value.value
        tu = get_types_universe()
        # If it's a tuple of two elements, then we assume it's upper/lower bounds
        if isinstance(value.unit, PosetProduct):
            subs = value.unit.subs
            assert len(subs) == 2, subs

            lower_UR_expected, upper_UR_expected = subs
            lower_res_expected, upper_res_expected = value.value
            
            lower_bound = tu.get_embedding(lower_UR_expected, UR)[0](lower_res_expected)
            upper_bound = tu.get_embedding(upper_UR_expected, UR)[0](upper_res_expected)

            tracer.log('lower: %s <= %s' % (UR.format(lower_bound), UR.format(res)))
            tracer.log('upper: %s <= %s' % (UR.format(upper_bound), UR.format(res)))

            UR.check_leq(lower_bound, res)
            UR.check_leq(res, upper_bound)
        else:
            # only one element: equality
            UR_expected = value.unit
            tu.check_leq(UR_expected, UR)
            A_to_B, _B_to_A = tu.get_embedding(UR_expected, UR)

            res_expected_f = A_to_B(res_expected)
            try:
                UR.check_equal(res, res_expected_f)
            except NotEqual as e:
                raise_wrapped(ExpectationsNotMet, e, 'res is different',
                              res=res, res_expected=res_expected, compact=True)

    if plot:
        r = Report()
        if _exp_advanced:
            from mcdp_report.generic_report_utils import generic_report
            generic_report(r, dp, trace,
                           annotation=None, axis0=(0, 0, 0, 0))
        else:
            f = r.figure()
            from mcdp_report.generic_report_utils import generic_plot
            generic_plot(f, space=UR, value=res)
            from mcdp_report.generic_report_utils import generic_report_trace
            generic_report_trace(r, ndp, dp, trace, out, do_movie=do_movie)

        out_html = os.path.join(out, 'report.html')
        logger.info('writing to %r' % out_html)
        r.to_html(out_html)

        out_html = os.path.join(out, 'report_ndp1.html')
        r = report_ndp1(ndp)
        logger.info('writing to %r' % out_html)
        r.to_html(out_html)

        out_html = os.path.join(out, 'report_dp1.html')
        if imp:
            last_imp = m
            r = report_dp1(dp, imp=last_imp)
        else:
            r = report_dp1(dp)
        logger.info('writing to %r' % out_html)
        r.to_html(out_html)

def solve_meat_solve(trace, ndp, dp, fg, intervals, max_steps, _exp_advanced):
    R = dp.get_res_space()
    UR = UpperSets(R)

    if intervals:
        res = solver_iterative(dp, fg, trace)
    else:
        if not _exp_advanced:
            res = dp.solve_trace(fg, trace)
            rnames = ndp.get_rnames()
            x = ", ".join(rnames)
            # todo: add better formatting
            trace.log('Minimal resources needed: %s = %s' % (x, UR.format(res)))
        else:
            try:
                trace2 = generic_solve(dp, f=fg, max_steps=max_steps)
                trace.log('Iteration result: %s' % trace2.result)
                ss = trace2.get_s_sequence()
                S = trace2.S
                trace.log('Fixed-point iteration converged to: %s'
                      % S.format(ss[-1]))
                R = trace2.dp.get_res_space()
                UR = UpperSets(R)
                sr = trace2.get_r_sequence()
                rnames = ndp.get_rnames()
                x = ", ".join(rnames)
                trace.log('Minimal resources needed: %s = %s'
                      % (x, UR.format(sr[-1])))

                res = sr[-1]
            except:
                raise
    return res, trace
#
# def solve_read_model(dirs, param, library=None):
# #     GlobalConfig.global_load_dir("mocdp")
#
#     model_name = param
#     basename = model_name
#
#     if library is None:
#         from mcdp_library.library import MCDPLibrary
#
#         library = MCDPLibrary()
#         for d in dirs:
#             library.add_search_dir(d)
#
#     ndp = library.load_ndp(model_name)
#
#     return library, basename, ndp

def solve_get_dp_from_ndp(basename, ndp, lower, upper, flatten=True):
    if flatten:
        ndp = ndp.flatten()

    dp = ndp.get_dp()

    if upper is not None:
        _, dp = get_dp_bounds(dp, 1, upper)
        basename += '-u-%03d' % upper
        assert lower is None

    if lower is not None:
        dp, _ = get_dp_bounds(dp, lower, 1)
        basename += '-l-%03d' % lower
        assert upper is None

    return basename, dp

def solve_get_output_dir(prefix):
    last = prefix + '-last'
    for i in range(1000):
        candidate = prefix + '-%03d' % i
        if not os.path.exists(candidate):
            mkdirs_thread_safe(candidate)
            if os.path.lexists(last):  # not exists
                os.unlink(last)
            assert not os.path.lexists(last)
            os.symlink(candidate, last)
            return candidate
    assert False


