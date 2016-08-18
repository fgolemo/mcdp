#!/usr/bin/env python
import numpy as np
from reprep import Report
from mcdp_library.library import MCDPLibrary
from mcdp_ipython_utils.loading import solve_combinations
from mcdp_ipython_utils.plotting import plot_all_directions
from quickapp.quick_app import QuickApp

def go():
    lib = get_library()
    return process(lib)

def get_library():
    lib = MCDPLibrary()
    lib.use_cache_dir('_cached/drone_uncertain')
    lib.add_search_dir('.')
    return lib

def process(lib):
    ndp = lib.load_ndp('test1')
    print ndp.get_rnames()

    combinations = {
        "travel_distance": (np.linspace(1, 2, 5), "km"),
        "carry_payload": (100, "g"),
        "num_missions": ( 1000, "[]"),
    }

    result_like = dict(total_cost_ownership="USD", total_mass='kg')

    nu = 100
    data = solve_combinations(ndp, combinations, result_like, upper=nu, lower=None)
    return data

def report(data):
    what_to_plot_res = dict(total_cost_ownership="USD", total_mass='kg')
    what_to_plot_fun = dict(travel_distance="km", carry_payload="g")
    r = Report()

    plot_all_directions(r,
                        queries=data['queries'],
                        results=data['results'],
                        what_to_plot_res=what_to_plot_res,
                        what_to_plot_fun=what_to_plot_fun)
    
    return r

class DroneU(QuickApp):

    def define_options(self, params):
        pass

    def define_jobs_context(self, context):
        result = context.comp(go)
        r = context.comp(report, result)
        context.add_report(r, 'report')


if __name__ == '__main__':
    main = DroneU.get_sys_main()
    main()



