# -*- coding: utf-8 -*-
from comptests.registrar import comptest
from mcdp_lang.tests.utils2 import eval_rvalue_as_constant


@comptest
def check_sums1():
    eval_rvalue_as_constant('int:2 + int:4 ')


@comptest
def check_sums2():
    eval_rvalue_as_constant('nat:3 + int:2')


@comptest
def check_sums3():
    eval_rvalue_as_constant('int:2 + nat:3')
