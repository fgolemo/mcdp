from comptests import (comptests_for_all, comptests_for_all_dynamic,
    comptests_for_all_pairs, comptests_for_all_pairs_dynamic, comptests_for_some,
    comptests_for_some_pairs)
from example_package import (get_conftools_example_class1,
    get_conftools_example_class2)
from mocdp.configuration import get_conftools_posets, get_conftools_dps
from comptests.registrar import comptests_for_some_dynamic

library_posets = get_conftools_posets()
library_dps = get_conftools_dps()

for_all_posets = comptests_for_all(library_posets)
for_some_posets = comptests_for_some(library_posets)
for_all_dps = comptests_for_all(library_dps)
for_some_dps = comptests_for_some(library_dps)
for_some_dps_dyn = comptests_for_some_dynamic(library_dps)

#
# for_some_class1 = comptests_for_some(library_class1)
# for_some_class1_class2 = comptests_for_some_pairs(library_class1, library_class2)
#
# for_all_class1_class2 = comptests_for_all_pairs(library_class1, library_class2)
# for_all_class1_dynamic = comptests_for_all_dynamic(library_class1)
# for_all_class1_class2_dynamic = comptests_for_all_pairs_dynamic(library_class1, library_class2)
