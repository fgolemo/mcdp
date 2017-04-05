from contracts import contract

from comptests.registrar import comptest, run_module_tests
from mcdp_hdb_tests.functoriality_memdata_to_diskrep import \
    check_translation_diskrep_to_memdata, check_translation_memdata_to_diskrep
from mcdp_hdb_tests.testcases import testcases_SimpleUserDB, DataTestCase,\
    testcases_TranslateNone
from mcdp_hdb_tests.functoriality_diskrep_to_gitrep import check_translation_diskrep_to_gitrep


tcs = {}
tcs.update(testcases_SimpleUserDB())
tcs.update(testcases_TranslateNone())

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
    out_memdata_to_diskrep = out + '/out_memdata_to_diskrep'
    r = check_translation_memdata_to_diskrep(schema, data_rep0, memdata_events, data_rep1, disk_map, 
                          out=out_memdata_to_diskrep)
    
    
    disk_rep0 = r['disk_rep0']
    disk_events = r['disk_events']
    disk_rep = r['disk_rep']
    out_diskrep_to_memdata = out + '/out_diskrep_to_memdata'
    check_translation_diskrep_to_memdata(schema, disk_rep0, disk_events, disk_rep, disk_map, 
                                         out=out_diskrep_to_memdata)
    
    
    r2 = check_translation_diskrep_to_gitrep(disk_rep0, disk_events, disk_rep,
                                              out=out_diskrep_to_memdata)
    

if __name__ == '__main__':
    run_module_tests()
    