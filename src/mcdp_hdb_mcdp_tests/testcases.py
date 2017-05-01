# -*- coding: utf-8 -*-
from comptests.registrar import comptest, comptest_fails, run_module_tests
from mcdp_hdb_tests.testcases_run import HDBTestCaseWrapper
from mcdp_hdb_mcdp_tests.testcases_operations1 import testcases_CommonOperations1

tcs = {}
tcs.update(testcases_CommonOperations1())
    
known_failures = """
operations1-seq_set_hash-regular               
operations1-seq_set_list-regular
""".replace('\n',' ').split()

for k, tc in tcs.items():
    f = HDBTestCaseWrapper(k, tc)
    if k in known_failures:
        comptest_fails(f)
    else:
        comptest(f)
        

if __name__ == '__main__':
    run_module_tests()
    
    
    
    