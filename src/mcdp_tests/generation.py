from mocdp import logger

def make_accumulator():
    def g(x):
        g.registered.append(x)
        return x
    g.registered = []
    return g

for_all_source_mcdp = make_accumulator()

for_all_posets0 = make_accumulator()

def for_all_posets(f):
    f0 = for_all_posets0(f)
    def f1(id_poset, poset):
        try:
            return f0(id_poset, poset)
        except:
            logger.error('poset: %r' % poset)
            logger.error('poset: %s' % type(poset))
            raise
    return f1

for_all_values = make_accumulator()
for_all_dps = make_accumulator()
for_all_templates = make_accumulator()

for_all_nameddps = make_accumulator()

for_all_nameddps_dyn = make_accumulator()
for_all_dps_dyn = make_accumulator()
for_all_nameddps_dyn = make_accumulator()


