from comptests.registrar import comptest
from mocdp.lang.syntax import (idn, load_expr, ow, parse_model, parse_wrap,
    rvalue)
from pyparsing import Literal

@comptest
def check_lang():
    parse_wrap(idn, 'battery')
    parse_wrap(idn + ow, 'battery ')
    parse_wrap(idn + ow + Literal('='), 'battery=')
    parse_wrap(load_expr, 'load battery')

    data = """
dp {
    battery = load battery
    times = load energy_times
    actuation = load mobility
    
    times.power >= actuation.actuation_power
    battery.capacity >= times.energy
    actuation.weight >= battery.battery_weight
}
    """
    return parse_model(data)


@comptest
def check_lang2():
    data = """
dp {
    battery = load battery
    times = load energy_times
    actuation = load mobility
# comment
    times.power >= actuation.actuation_power
    # comment
    battery.capacity >= times.energy
# comment
    actuation.weight >= battery.battery_weight
    # comment
}
    """
    parse_model(data)

@comptest
def check_lang3_times():
    parse_wrap(rvalue, 'mission_time')

    data = """
dp {
    battery = load battery
    actuation = load mobility
     
    battery.capacity >= actuation.actuation_power * mission_time    
    actuation.weight >= battery.battery_weight
    }
    """
    parse_model(data)



# @comptest
def check_lang4_composition():
    parse_wrap(rvalue, 'mission_time')

    data = """
dp {
    battery = load battery
    actuation = load mobility
     
    battery.capacity >= actuation.actuation_power * mission_time    
    actuation.weight >= battery.battery_weight
    }
    """
    parse_model(data)


examples1 = [
    """
dp electric-battery {
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





