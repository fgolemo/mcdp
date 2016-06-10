from comptests import (comptests_for_all, comptests_for_all_dynamic,
    comptests_for_some)
from comptests.registrar import comptests_for_some_dynamic
from mocdp.configuration import (get_conftools_dps, get_conftools_nameddps,
    get_conftools_posets)

library_posets = get_conftools_posets()
library_dps = get_conftools_dps()

library_nameddps = get_conftools_nameddps()

for_all_posets = comptests_for_all(library_posets)
for_some_posets = comptests_for_some(library_posets)
for_all_dps = comptests_for_all(library_dps)

for_all_nameddps = comptests_for_all(library_nameddps)

for_all_nameddps_dyn = comptests_for_all_dynamic(library_nameddps)

for_all_dps_dyn = comptests_for_all_dynamic(library_dps)
for_all_nameddps_dyn = comptests_for_all_dynamic(library_nameddps)
for_some_dps = comptests_for_some(library_dps)
for_some_dps_dyn = comptests_for_some_dynamic(library_dps)

def make_accumulator():
    def g(x):
        g.registered.append(x)
    g.registered = []
    return g

for_all_source_mcdp = make_accumulator()

