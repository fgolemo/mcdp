from comptests.registrar import comptest
from mcdp_lang.tests.utils2 import eval_rvalue_as_constant_same

same = eval_rvalue_as_constant_same

@comptest
def check_tuples1():

    same("1 g + 1 kg", "1001 g")

@comptest
def check_tuples2():

    same("<1g, 5J>[1]", "5 J")

@comptest
def check_tuples3():
    pass

@comptest
def check_tuples4():
    pass

@comptest
def check_tuples5():
    pass

@comptest
def check_tuples6():
    pass

@comptest
def check_tuples7():
    pass

@comptest
def check_tuples8():
    pass

@comptest
def check_tuples9():
    pass

