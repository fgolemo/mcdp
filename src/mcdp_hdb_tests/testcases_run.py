from contracts import contract

from comptests.registrar import comptest, run_module_tests
from mcdp_hdb_tests.test_translation import check_translation
from mcdp_hdb_tests.testcases import testcases_SimpleUserDB, DataTestCase


tcs = {}
tcs.update(testcases_SimpleUserDB())

class X():
    def __init__(self, k, tc):
        self.k = k
        self.tc = tc
        self.__name__ = k
    def __call__(self):
        return run_for_test_case(self.k, self.tc)

for k, tc in tcs.items():
    comptest(X(k, tc))
    
@contract(tc=DataTestCase)
def run_for_test_case(name, tc):
    out = 'out/test_translation/testcases/%s' % name
    data_rep0 = tc.get_data1()
    data_rep1 = tc.get_data2()
    schema = tc.get_schema()
    memdata_events = tc.get_events()
    disk_map = tc.get_disk_map()
    check_translation(schema, data_rep0, memdata_events, data_rep1, disk_map, out)

if __name__ == '__main__':
    run_module_tests()
    