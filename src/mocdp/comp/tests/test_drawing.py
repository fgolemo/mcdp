from mocdp.unittests.generation import for_all_nameddps_dyn
from mocdp.dp_report.report import report_dp1
from mocdp.posets.rcomp import Rcomp
from reprep import Report



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
    print funsp
    print ressp
    if not is_scalar(funsp) or not is_scalar(ressp):
        return

    solutions = context.comp(solve_ndp, ndp)
    r = context.comp(report_solutions, ndp, solutions)
    context.add_report(r, 'report_solutions')

def unzip(iterable):
    return zip(*iterable)

def report_solutions(ndp, solutions):
    r = Report()
    
    f, rmin = unzip(solutions)
    
    with r.plot() as pylab:
        def gety(x):
            return list(x.minimals)[0]
        y = map(gety, rmin)
        print f
        print y

        def get_finite_part(a, b):
            def is_finite(x):
                return isinstance(x, float)
            return unzip([(f, r) for (f, r) in zip(a, b) if is_finite(r)])

        f0, y0 = get_finite_part(f, y)
        print f0
        print y0

        pylab.plot(f0, y0)

    return r

def solve_ndp(ndp, n=10):
    dp = ndp.get_dp()
    funsp = dp.get_fun_space()
    chain = funsp.get_test_chain(n=n)
    results = map(dp.solve, chain)
    return zip(chain, results)

        
        
        
def is_scalar(space):
    return isinstance(space, Rcomp)
