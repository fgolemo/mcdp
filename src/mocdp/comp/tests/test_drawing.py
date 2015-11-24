from mocdp.dp_report.report import report_dp1
from mocdp.posets import Rcomp
from mocdp.unittests.generation import for_all_nameddps_dyn
from reprep import Report
import numpy as np

# @for_all_nameddps_dyn
# def html_report(context, _id_dp, ndp):
#     r = context.comp(report_syntax_hl, ndp)
#     context.add_report(r, 'syntax_hl')
#
# def report_syntax_hl(ndp):
#     r = Report()
#     h = ast_to_html(s, complete_document=Flase)
#
#     return r


@for_all_nameddps_dyn
def nameddp1_report(context, _id_dp, ndp):
    dp = ndp.get_dp()
    r = context.comp(report_dp1, dp)
    context.add_report(r, 'nameddp1')

@for_all_nameddps_dyn
def nameddp1_solve(context, _, ndp):
    dp = ndp.get_dp()
    funsp = dp.get_fun_space()
    ressp = dp.get_res_space()

    if not is_scalar(funsp) or not is_scalar(ressp):
        return

    solutions = context.comp(solve_ndp, ndp, n=30)
    r = context.comp(report_solutions, ndp, solutions)
    context.add_report(r, 'report_solutions')

def unzip(iterable):
    return zip(*iterable)

def report_solutions(ndp, solutions):
    r = Report()
    
    fnames = ndp.get_fnames()
    rnames = ndp.get_rnames()
    assert len(fnames) == 1
    assert len(rnames) == 1
    xl = '%s (%s)' % (fnames[0], ndp.get_ftype(fnames[0]))
    yl = '%s (%s)' % (rnames[0], ndp.get_rtype(rnames[0]))


    f, rmin = unzip(solutions)
    
    with r.plot() as pylab:
        def gety(x):
            return list(x.minimals)[0]
        y = map(gety, rmin)
        print f
        print y

        def is_finite(r):
            return isinstance(r, float)

        def get_finite_part(a, b):
            return unzip([(f, r) for (f, r) in zip(a, b)
                          if is_finite(r)
                          and is_finite(f)])

        def get_unfeasible_f(a, b):
            return [f for (f, r) in zip(a, b) if not is_finite(r) and
                    is_finite(f)  # no top
                    ]

        f0, y0 = get_finite_part(f, y)
        print f0, y0
        fu = get_unfeasible_f(f, y)

        pylab.plot(f0, y0, 'k.')
        pylab.plot(fu, 0 * np.array(fu), 'rs')
        pylab_xlabel_unicode(pylab, xl)
        pylab_ylabel_unicode(pylab, yl)

    return r


def pylab_xlabel_unicode(pylab, xl):
    try:
        pylab.xlabel(xl)
    except UnicodeDecodeError as e:
        print('Cannot set label %s %r: %s' % (xl, xl, e))


def pylab_ylabel_unicode(pylab, yl):
    try:
        pylab.ylabel(yl)
    except UnicodeDecodeError as e:
        print('Cannot set label %s %r: %s' % (yl, yl, e))


def solve_ndp(ndp, n=20):
    dp = ndp.get_dp()
    funsp = dp.get_fun_space()
    chain = funsp.get_test_chain(n=n)
    results = map(dp.solve, chain)
    return zip(chain, results)

        
        
        
def is_scalar(space):
    return isinstance(space, Rcomp)
