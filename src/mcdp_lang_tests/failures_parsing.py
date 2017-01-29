# -*- coding: utf-8 -*-
from comptests.registrar import comptest, comptest_fails

from .utils import assert_parsable_to_connected_ndp
from .utils2 import eval_rvalue_as_constant


@comptest
def ok_resource_mix():
    assert_parsable_to_connected_ndp("""
mcdp {
  provides f1 [dimensionless] 
  requires r1 [dimensionless]
  requires r2 [dimensionless]

  f1  <= 1 [] + (r1 * (r2 + r1)  )

}""")



@comptest_fails
def future_empty_set():
    eval_rvalue_as_constant("{} g")

@comptest
def bug_lift():
    assert_parsable_to_connected_ndp("""
mcdp {
  provides lift [N] 
  requires r1 [N^2]

  r1 >= (provided lift) ^ 2

}""")
