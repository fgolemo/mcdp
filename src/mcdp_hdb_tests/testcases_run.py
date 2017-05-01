# -*- coding: utf-8 -*-
from contracts import contract

from comptests.registrar import comptest, run_module_tests, comptest_fails

from mcdp_hdb_tests.functoriality_diskrep_to_gitrep import check_translation_diskrep_to_gitrep
from mcdp_hdb_tests.functoriality_gitrepo_to_diskrep import check_translation_gitrep_to_diskrep
from mcdp_hdb_tests.functoriality_memdata_to_diskrep import check_translation_diskrep_to_memdata, check_translation_memdata_to_diskrep
from mcdp_hdb_tests.testcase_array_inside_yaml import testcases_arrays_inside_yaml
from mcdp_hdb_tests.testcase_arrayplus import testcases_arrayplus
from mcdp_hdb_tests.testcase_arrays import testcases_arrays
from mcdp_hdb_tests.testcase_minilibrary import testcases_minilibrary
from mcdp_hdb_tests.testcase_simpleuserdb import testcases_SimpleUserDB
from mcdp_hdb_tests.testcase_translatenone import testcases_TranslateNone
from mcdp_hdb_tests.testcases import DataTestCase


tcs = {}
tcs.update(testcases_arrays_inside_yaml())
tcs.update(testcases_arrays())
tcs.update(testcases_minilibrary())
tcs.update(testcases_TranslateNone())
tcs.update(testcases_SimpleUserDB())
tcs.update(testcases_arrayplus())

class HDBTestCaseWrapper(object):
    def __init__(self, k, tc):
        self.k = k
        self.tc = tc
        self.__name__ = 'hdb_testcase-' + k
    def __call__(self):
        return run_for_test_case(self.k, self.tc)

known_failures = """
hdb_testcase-array1-seq_delete0-vanilla               
hdb_testcase-array1-seq_delete_all-vanilla            
hdb_testcase-array_inside_yaml-seq_delete1-vanilla    
hdb_testcase-arrayplus-seq_delete0-vanilla            
hdb_testcase-arrayplus-seq_delete_all-vanilla         
hdb_testcase-arrayplus-seq_insert-vanilla             
hdb_testcase-commonops1-seq_set_hash-regular          
hdb_testcase-commonops1-seq_set_list-regular          
hdb_testcase-simpleuserdb-seq_set_hash-files_are_yaml 
hdb_testcase-simpleuserdb-seq_set_hash-vanilla        
hdb_testcase-simpleuserdb-seq_set_hash-with_hint      
hdb_testcase-simpleuserdb-seq_set_list-files_are_yaml 
hdb_testcase-simpleuserdb-seq_set_list-vanilla        
hdb_testcase-simpleuserdb-seq_set_list-with_hint
hdb_testcase-simpleuserdb-seq_set_struct-vanilla
hdb_testcase-simpleuserdb-seq_set_struct-with_hint
""".replace('\n',' ').split()

for k, tc in tcs.items():
    f = HDBTestCaseWrapper(k, tc)
    if f.__name__ in known_failures:
        comptest_fails(f)
    else:
        comptest(f)
    
@contract(tc=DataTestCase)
def run_for_test_case(name, tc):
    out = 'out/test_translation/testcases/%s' % name
    tc.run()
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
    r1 = check_translation_diskrep_to_memdata(schema, disk_rep0, disk_events, disk_rep, disk_map, 
                                         out=out_diskrep_to_memdata)
    
    _data_rep0_2 = r1['data_rep0']
    _data_rep1_2 = r1['data_rep']
    _data_events_2 = r1['data_events']
    
    r2 = check_translation_diskrep_to_gitrep(disk_rep0, disk_events, disk_rep,
                                              out=out_diskrep_to_memdata)
    repo = r2['repo']
    
    
    out_gitrep_to_diskrep = out + '/out_gitrep_to_diskrep'
    r3 = check_translation_gitrep_to_diskrep(repo, 'master', out_gitrep_to_diskrep)

    disk_rep0 = r3['disk_rep0']
    disk_rep = r3['disk_rep']
    disk_events = r3['disk_events']
    

if __name__ == '__main__':
    run_module_tests()
    