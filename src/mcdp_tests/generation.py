# -*- coding: utf-8 -*-
from contextlib import contextmanager
from mcdp_library.specs_def import SPEC_PRIMITIVEDPS, SPEC_VALUES, SPEC_POSETS,\
    SPEC_TEMPLATES, SPEC_MODELS

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
for_all_posets_dyn = make_accumulator() 

for_all_values = make_accumulator()
for_all_values_dyn = make_accumulator()

for_all_dps = make_accumulator()
for_all_dps_dyn = make_accumulator()

for_all_templates = make_accumulator()
for_all_templates_dyn = make_accumulator()

for_all_nameddps = make_accumulator()
for_all_nameddps_dyn = make_accumulator()

R = 'regular'
D = 'dynamic'

test_accumulators = {
    SPEC_MODELS: {
        R: for_all_nameddps,
        D: for_all_nameddps_dyn,
    },
    SPEC_TEMPLATES: {
        R: for_all_templates,
        D: for_all_templates_dyn,
    },
    SPEC_POSETS: {
        R: for_all_posets,
        D: for_all_posets_dyn,
    },
    SPEC_VALUES: {
        R: for_all_values,
        D: for_all_values_dyn,
    },
    SPEC_PRIMITIVEDPS: {
        R: for_all_dps,
        D: for_all_dps_dyn,
    },
}
    

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
