

examples1 = [
    """
dp electric-battery:
    provides voltage (intervals of V)
    provides current (A)
    provides capacity (J)
    
    requires carry-weight (g)
    requires volume (L)
    requires shape (Shape-type)
    
dp nuclear-battery:
    requires cooling (Q/s)
    requires radiation-shelding
    

dp my-battery is-a power-source:
   
   param specific_energy = 100
   
   implementation ncells (int, >=0)
   implementation type (Lithium | Li-Po)
   
   volume = ncells * voltage-of(type)
   weight = ncells * 
   current = current-of(type)
   shape = 
   
   voltage-of = {Lithium: 0.2, Li-Po: 0.1}
   cur
    
    
dp solar-panels:

    requires 
    requires vibrations (

dp 

    
subsystem power-source:
    any of nuclear-battery, electric-battery, (nuclear+battery)
    


dp robot:
    dp power-source  
    dp chassis

    (required torque of chassis) >= (provided torque of motor)
    
    (provided payload of chassis) >= (required weight of power-source) + (required weight of motors) 
    
     
    
dp my-robot = (robot with power-source = (battery with rho=2), alpha = 2) 

my-robot 

    
    
    """


]


def f():
    pass





