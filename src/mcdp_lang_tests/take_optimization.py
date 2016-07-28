from comptests.registrar import comptest
from mcdp_lang.parse_interface import parse_ndp
from mcdp_lang_tests.utils import assert_parsable_to_connected_ndp


@comptest
def check_take_optim1():
    ndp = parse_ndp(""" 
    mcdp {
    
        provides f [s x J] 
        
        requires r1 [s]
        requires r2 [J]
        
        required r1 >= take(provided f, 0)
        required r2 >= take(provided f, 1) 
    }
    
    """)

@comptest
def check_take_optim2():
    ndp = parse_ndp("""
    
    mcdp {
    
        requires r [s x J] 
        
        provides f1 [s]
        provides f2 [J]
        
        provided f1 <= take(required r, 0)
        provided f2 <= take(required r, 1) 
    }
    
    """)

@comptest
def check_take_optim3():
    assert_parsable_to_connected_ndp("""
    
    mcdp {
    
        requires r [s x J] 
        
        provides f1 [s]
        
        provided f1 <= take(required r, 0)
         
    }
    
    """)

@comptest
def check_take_optim4():
    pass

@comptest
def check_take_optim5():
    pass

@comptest
def check_take_optim6():
    pass

@comptest
def check_take_optim7():
    pass

