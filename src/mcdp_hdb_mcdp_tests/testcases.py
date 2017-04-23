# -*- coding: utf-8 -*-
from comptests.registrar import comptest
from mcdp_hdb_tests.testcases_run import HDBTestCaseWrapper

tcs = {}
tcs.update(testcases_CommonOperations1())


for k, tc in tcs.items():
    comptest(HDBTestCaseWrapper(k, tc))