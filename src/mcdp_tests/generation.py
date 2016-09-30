
def make_accumulator():
    def g(x):
        g.registered.append(x)
        return x
    g.registered = []
    return g

for_all_source_mcdp = make_accumulator()

for_all_posets = make_accumulator()
for_all_values = make_accumulator()
for_all_dps = make_accumulator()
for_all_templates = make_accumulator()

for_all_nameddps = make_accumulator()

for_all_nameddps_dyn = make_accumulator()
for_all_dps_dyn = make_accumulator()
for_all_nameddps_dyn = make_accumulator()


