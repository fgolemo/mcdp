#!/usr/bin/env python
import numpy as np
from reprep import Report
from mcdp_library.library import MCDPLibrary
from mcdp_ipython_utils.loading import solve_combinations
from mcdp_ipython_utils.plotting import plot_all_directions

def get_library():
    lib = MCDPLibrary()
    lib.use_cache_dir('_cached/drone_uncertain')
    lib.add_search_dir('.')
    return lib

def go(lib):
    ndp = lib.load_ndp('test1')
    print ndp.get_rnames()

    combinations = {
        "travel_distance": (np.linspace(1, 2, 5), "km"),
        "carry_payload": (100, "g"),
        "num_missions": ( 1000, "[]"),
    }

    result_like = dict(total_cost_ownership="USD", total_mass='kg')
    what_to_plot_res = result_like
    what_to_plot_fun = dict(travel_distance="km", carry_payload="g")

    nu = 100
    data = solve_combinations(ndp, combinations, result_like, upper=nu, lower=None)

    r = Report()

    plot_all_directions(r, queries=data['queries'], results=data['results'],
                        what_to_plot_res=what_to_plot_res,
                        what_to_plot_fun=what_to_plot_fun)
    
    fn = 'out/drone_uncertainty/go1.html'
    print('Writing on %s' % fn)
    r.to_html(fn)

#
# def go2(lib):
#     model_name = 'batteries_squash'
#     combinations = {
#         "capacity": (np.linspace(50, 3000, 10), "Wh"),
#         "missions": (1000, "[]"),
#     }
#     result_like = dict(cost="USD", mass='kg')
#     what_to_plot_res = result_like
#     what_to_plot_fun = dict(capacity="Wh", missions="[]")
#
#     ndp = lib.load_ndp(model_name)
#
#     data = solve_combinations(ndp, combinations, result_like)
#
#     r = Report()
#
#     plot_all_directions(r, queries=data['queries'], results=data['results'],
#                         what_to_plot_res=what_to_plot_res,
#                         what_to_plot_fun=what_to_plot_fun)
#     r.to_html('out/batteries_squash-c2.html')

if __name__ == '__main__':
    lib = get_library()
    go(lib)
    # go2(lib)



