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
# 
# def for_all_posets(f):
#     @for_all_posets0
#     def f1(id_poset, poset):
#         try:
#             return f(id_poset, poset)
#         except:
#             logger.error('poset: %r' % poset)
#             logger.error('poset: %s' % type(poset))
#             raise
#     return f1

# for_all_posets.registered = for_all_posets0.registered

for_all_values = make_accumulator()
for_all_dps = make_accumulator()
for_all_templates = make_accumulator()

for_all_nameddps = make_accumulator()

for_all_nameddps_dyn = make_accumulator()
for_all_dps_dyn = make_accumulator()
for_all_nameddps_dyn = make_accumulator()
# 
# @decorator
# def primitive_dp_test(f):
#     print('decorating %s' % f)
#     from mocdp import logger
#     def f0(id_dp, dp):
#         try:
#             return f(id_dp, dp)
#         except:
#             logger.error('Test failure for DP: %s' % dp.__repr__())
#             logger.error(dp.repr_long())
#             raise
#     return f0
    

@contextmanager
def primitive_dp_test(id_dp, dp):
    from mocdp import logger
    try:
        yield
    except:
        logger.error('Test failure for DP %r' % id_dp)
        logger.error('__repr__():\n%s' % dp.__repr__())
        logger.error('repr_long():\n%s' % dp.repr_long())
        raise
    
    

