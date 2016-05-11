#!/usr/bin/env python
from mcdp_ipython_utils.loading import solve_queries
from mcdp_ipython_utils.plotting import plot_all_directions
from mcdp_library.library import MCDPLibrary
from reprep import Report
import numpy as np

def go():
    fn = 'out/actuation_c1.html'
 
    model_name = 'actuation'
    queries = []
    def add(q):
        queries.append(q)

    n = 10
    lifts = np.linspace(0, 10.0, n)

    for lift,  in zip(lifts):
        q = {
            "lift": (lift, "N"),
        }
        add(q)

    result_like = dict(power="W", cost='$')
    
    what_to_plot_res = result_like
    
    what_to_plot_fun = dict(lift="N")


    lib = MCDPLibrary()
    lib = lib.add_search_dir('.')
    _, ndp = lib.load_ndp(model_name)

    data = solve_queries(ndp, queries, result_like)

    r = Report()

    plot_all_directions(r,
                        queries=data['queries'],
                        results=data['results'],
                        what_to_plot_res=what_to_plot_res,
                        what_to_plot_fun=what_to_plot_fun)
    print('writing to %r' % fn)
    r.to_html(fn)



if __name__ == '__main__':
    # go()
    go()



