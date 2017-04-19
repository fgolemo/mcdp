# -*- coding: utf-8 -*-
from contextlib import contextmanager

def make_accumulator():
    def g(x):
        g.registered.append(x)
        return x
    g.registered = []
    return g

for_all_source_all = make_accumulator() # all of the below
for_all_source_mcdp = make_accumulator()
for_all_source_mcdp_poset = make_accumulator()
for_all_source_mcdp_template = make_accumulator()
for_all_source_mcdp_value = make_accumulator()
for_all_posets = make_accumulator() 
for_all_values = make_accumulator()
for_all_dps = make_accumulator()
for_all_templates = make_accumulator()
for_all_nameddps = make_accumulator()
for_all_nameddps_dyn = make_accumulator()
for_all_dps_dyn = make_accumulator()
for_all_nameddps_dyn = make_accumulator() 
    

@contextmanager
def primitive_dp_test(id_dp, dp):
    from mcdp import logger
    try:
        yield
    except:
        logger.error('Test failure for DP %r' % id_dp)
        logger.error('__repr__():\n%s' % dp.__repr__())
        logger.error('repr_long():\n%s' % dp.repr_long())
        raise
    
    

