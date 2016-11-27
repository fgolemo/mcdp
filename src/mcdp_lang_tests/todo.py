from comptests.registrar import comptest, run_module_tests
from mcdp_lang_tests.utils2 import eval_rvalue_as_constant_same_exactly

@comptest
def check_nat_power():
    eval_rvalue_as_constant_same_exactly('3 ^ 2', 'Nat: 9')
    

@comptest
def check_nat_power_frac():
    eval_rvalue_as_constant_same_exactly('9 ^ (1/2)', 'Rcomp: 3.0')


if __name__ == '__main__': 
    run_module_tests()
    
    
    
