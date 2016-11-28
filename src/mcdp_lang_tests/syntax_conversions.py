# -*- coding: utf-8 -*-
from comptests.registrar import comptest, comptest_fails

from .utils2 import eval_rvalue_as_constant_same_exactly


@comptest_fails
def check_lang_conversion1():
    eval_rvalue_as_constant_same_exactly("(as Int) 1.0 [] ", "int:1")

@comptest_fails
def check_lang_conversion2():
    eval_rvalue_as_constant_same_exactly("(as Nat) 1.0 [] ", "nat:1")

@comptest_fails
def check_lang_conversion3():
    eval_rvalue_as_constant_same_exactly("(as R) nat:1 ", "1.0[]")



@comptest
def check_lang_conversion4():
    pass

@comptest
def check_lang_conversion5():
    pass


@comptest
def check_lang_conversion6():
    pass


@comptest
def check_lang_conversion7():
    pass

