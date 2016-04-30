# -*- coding: utf-8 -*-
from conf_tools import GlobalConfig
from contracts.utils import raise_desc
from decent_params import UserError
from mocdp.dp.dp_transformations import get_dp_bounds
from mocdp.dp.solver import generic_solve
from mocdp.dp.solver_iterative import solver_iterative
from mocdp.dp.tracer import Tracer
from mocdp.posets import PosetProduct, UpperSets, get_types_universe
from reprep import Report
import os
from mcdp_library.library import MCDPLibrary
from cdpview.utils_mkdir import mkdirs_thread_safe


class ExpectationsNotMet(Exception):
    pass

def solve_main(logger, config_dirs, model_name, lower, upper, out_dir,
               max_steps, query_strings,
       intervals, _exp_advanced, expect_nres, imp, expect_nimp, plot, do_movie):

    if out_dir is None:
        out = solve_get_output_dir(prefix='out')
    else:
        out = out_dir

    logger.info('Using output dir %r' % out)

    _library, basename, ndp = solve_read_model(dirs=config_dirs, param=model_name)

    basename, dp = solve_get_dp_from_ndp(basename=basename, ndp=ndp,
                                   lower=lower, upper=upper)

    fnames = ndp.get_fnames()

    F = dp.get_fun_space()
    R = dp.get_res_space()
    UR = UpperSets(R)

    fg = solve_interpret_query_strings(query_strings=query_strings, fnames=fnames, F=F)

    logger.info('query: %s' % F.format(fg))

    res, trace = solve_meat_solve(logger, ndp, dp, fg, intervals, max_steps, _exp_advanced)

    nres = len(res.minimals)

    if expect_nres is not None:
        if nres != expect_nres:
            msg = 'Found wrong number of resources'
            raise_desc(ExpectationsNotMet, msg,
                       expect_nres=expect_nres, nres=nres)

    if imp:
        M = dp.get_imp_space_mod_res()
        nimplementations = 0
        for r in res.minimals:
            ms = dp.get_implementations_f_r(f=fg, r=r)
            nimplementations += len(ms)
            s = 'r = %s ' % R.format(r)
            for j, m in enumerate(ms):
                # print('m = %s' % str(m))
                s += "\n  implementation %d: m = %s " % (j + 1, M.format(m))
            print(s)
        if expect_nimp is not None:
            if expect_nimp != nimplementations:
                msg = 'Found wrong number of implementations'
                raise_desc(ExpectationsNotMet, msg,
                           expect_nimp=expect_nimp,
                           nimplementations=nimplementations)

#     pp = '-'.join(params)
#     for forbidden in ['-', ' ', '{', '}', ':']:
#         pp = pp.replace(forbidden, '')
#
#     d = basename + '-' + pp
#     outd = os.path.join(out, d)

    if plot:
        r = Report()
        if _exp_advanced:
            from mocdp.dp_report.generic_report_utils import generic_report
            generic_report(r, dp, trace,
                           annotation=None, axis0=(0, 0, 0, 0))
        else:
            f = r.figure()
            from mocdp.dp_report.generic_report_utils import generic_plot
            generic_plot(f, space=UR, value=res)
            from mocdp.dp_report.generic_report_utils import generic_report_trace
            generic_report_trace(r, ndp, dp, trace, out, do_movie=do_movie)

        out_html = os.path.join(out, 'report.html')
        logger.info('writing to %r' % out_html)
        r.to_html(out_html)


def solve_meat_solve(logger, ndp, dp, fg, intervals, max_steps, _exp_advanced):
    R = dp.get_res_space()
    UR = UpperSets(R)

    if intervals:
        trace = Tracer()
        res = solver_iterative(dp, fg, trace)
    else:
        if not _exp_advanced:
            trace = Tracer()
            res = dp.solve_trace(fg, trace)
            rnames = ndp.get_rnames()
            x = ", ".join(rnames)
            logger.info('Minimal resources needed: %s = %s' % (x, UR.format(res)))

        else:
            try:
                trace = generic_solve(dp, f=fg, max_steps=max_steps)
                logger.info('Iteration result: %s' % trace.result)
                ss = trace.get_s_sequence()
                S = trace.S
                logger.info('Fixed-point iteration converged to: %s'
                      % S.format(ss[-1]))
                R = trace.dp.get_res_space()
                UR = UpperSets(R)
                sr = trace.get_r_sequence()
                rnames = ndp.get_rnames()
                x = ", ".join(rnames)
                logger.info('Minimal resources needed: %s = %s'
                      % (x, UR.format(sr[-1])))
            except:
                raise
    return res, trace


def solve_interpret_query_strings(query_strings, fnames, F):
    from .query_interpretation import interpret_params
    from .query_interpretation import interpret_params_1string

    if len(query_strings) > 1:
        fg = interpret_params(query_strings, fnames, F)
    elif len(query_strings) == 1:
        p = query_strings[0]
        fg = interpret_params_1string(p, F)
    else:
        tu = get_types_universe()
        if tu.equal(F, PosetProduct(())):
            fg = ()
        else:
            msg = 'Please specify query parameter.'
            raise_desc(UserError, msg, F=F)
    return fg

def solve_read_model(dirs, param):
    GlobalConfig.global_load_dir("mocdp")

    model_name = param
    basename = model_name

    library = MCDPLibrary()
    for d in dirs:
        library = library.add_search_dir(d)

    library, ndp = library.load_ndp(model_name)

    return library, basename, ndp

def solve_get_dp_from_ndp(basename, ndp, lower, upper):
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
            if os.path.exists(last):
                os.unlink(last)
            os.symlink(candidate, last)
            return candidate
    assert False


