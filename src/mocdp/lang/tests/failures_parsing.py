# -*- coding: utf-8 -*-
from comptests.registrar import comptest_fails
from mocdp.lang.tests.utils import assert_parsable_to_connected_ndp
from mocdp.lang.tests.utils2 import eval_rvalue_as_constant


@comptest_fails
def bug_resource_mix():
    assert_parsable_to_connected_ndp("""
mcdp {
  provides f1 [R] 
  requires r1 [R]
  requires r2 [R]

  f1  <= 1 [] + (r1 * (r2 + r1)  )

}""")

@comptest_fails
def future_indexing_syntax():
    assert_parsable_to_connected_ndp("""
    mcdp {
       provides f [X x USD]
       requires cost [USD]

       cost >= f[1]
    }
""")


@comptest_fails
def future_comments_syntax():
    assert_parsable_to_connected_ndp('''
    mcdp {
       """ this is the comment """

      provides x [J] "This is a comment for the description"
    }
''')

@comptest_fails
def future_empty_set():
    eval_rvalue_as_constant("{} g")

@comptest_fails
def bug_lift():
    assert_parsable_to_connected_ndp("""
mcdp {
  provides lift [N] 
  requires r1 [N^2]

  r1 >= (provided lift) ^ 2

}""")
