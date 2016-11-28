#!/usr/bin/env python
# -*- coding: utf-8 -*-
from mcdp_ipython_utils.loading import solve_queries
from mcdp_ipython_utils.plotting import plot_all_directions
from mcdp_library.library import MCDPLibrary
from reprep import Report
import numpy as np

def go():
 
    model_name = 'droneC'
    queries = []
    def add(q):
        queries.append(q)

    n = 10
    endurance = np.linspace(1, 20, n)
    payload = np.linspace(5, 50, n)

    for endurance, payload in zip(endurance, payload):
        q = {
            "num_missions": (1000, "[]"),
            "extra_power": (5, "W"),
            "extra_payload": (payload, "g"),
            "endurance": (endurance, "minutes"),
        }
        add(q)

    result_like = dict(total_cost="CHF", total_mass='kg')
    what_to_plot_res = result_like
    what_to_plot_fun = dict(extra_payload="g", endurance="minutes")

    lib = MCDPLibrary()
    lib.add_search_dir('.')
    ndp = lib.load_ndp(model_name)

    data = solve_queries(ndp, queries, result_like)

    r = Report()

    plot_all_directions(r,
                        queries=data['queries'],
                        results=data['results'],
                        what_to_plot_res=what_to_plot_res,
                        what_to_plot_fun=what_to_plot_fun)
    fn = 'out/droneC_c1.html'
    print('writing to %r' % fn)
    r.to_html(fn)



if __name__ == '__main__':
    # go()
    go()



