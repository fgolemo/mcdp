# -*- coding: utf-8 -*-
from comptests.registrar import comptest
from mocdp.lang.syntax import (idn, load_expr, ow, parse_model, parse_wrap,
    rvalue, simple_dp_model, funcname, code_spec, max_expr, constraint_expr)
from pyparsing import Literal
from nose.tools import assert_equal
from mocdp.lang.blocks import DPSemanticError
from contracts.utils import raise_wrapped
import warnings

@comptest
def check_lang():
    parse_wrap(idn, 'battery')
    parse_wrap(idn + ow, 'battery ')
    parse_wrap(idn + ow + Literal('='), 'battery=')
    parse_wrap(load_expr, 'load battery')

    data = """
cdp {
    provides mission_time [s] 
    
    battery = load battery
    times = load energy_times
    actuation = load mobility
    
    times.mission_time >= mission_time
    
    times.power >= actuation.actuation_power
    battery.capacity >= times.energy
    actuation.weight >= battery.battery_weight
}
    """
    return parse_model(data)


@comptest
def check_lang2():
    data = """
cdp {
    provides mission_time [s] 
    
    battery = load battery
    times = load energy_times
    actuation = load mobility
# comment
    times.power >= actuation.actuation_power
    # comment
    battery.capacity >= times.energy
    times.mission_time >= mission_time

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
cdp {
    provides mission_time [s]

    battery = load battery
    actuation = load mobility
     
    battery.capacity >= actuation.actuation_power * mission_time    
    actuation.weight >= battery.battery_weight
}
    """
    parse_model(data)

def assert_semantic_error(s , desc=None):
    try:
        res = parse_model(s)
    except DPSemanticError:
        pass
    except BaseException as e:
        msg = "Expected semantic error, got %s." % type(e)
        raise_wrapped(Exception, e, msg, s=s)
    else:
        msg = "Expected an exception, instead succesfull instantiation."
        raise_wrapped(Exception, e, msg, s=s, res=res.desc_long())
    
    
@comptest
def check_lang10_asllspecified():

    s = """
cdp {
    battery = load battery
}
    """
    assert_semantic_error(s)  # unconnected

    s = """
cdp {
    provides capacity [J]

    battery = load battery
    battery.capacity >= capacity
}
    """
    assert_semantic_error(s)  # unconnected

    ndp = parse_model("""
cdp {
    provides c [J]
    requires w [g]
    
    battery = load battery
    battery.capacity >= c
    
    w >= battery.battery_weight
}
    """)

    # reused same function
    ndp = parse_model("""
cdp {
    provides c [J]
    requires w1 [g]
    requires w2 [g]
    
    battery = load battery
    battery.capacity >= c
    
    w1 >= battery.battery_weight
    w2 >= battery.battery_weight
}
    """)


@comptest
def check_lang4_composition():
    parse_wrap(rvalue, 'mission_time')

    s = """
dp {
    provides current [A]
    provides capacity [J]
    requires weight [g]
    
    implemented-by load times
}
    """
    res = parse_wrap(simple_dp_model, s)[0]



@comptest
def check_lang5_composition():
    parse_wrap(rvalue, 'mission_time')

    parse_wrap(funcname, 'mocdp.example_battery.Mobility')
    parse_wrap(code_spec, 'code mocdp.example_battery.Mobility')

    s = """
    cdp {
        provides mission_time [s]
    
        battery = dp {
            provides capacity [J]
            requires battery_weight [g]
            
            implemented-by load BatteryDP
        }
        
        actuation = dp {
            provides weight [g]
            requires actuation_power [W]
            
            implemented-by code mocdp.example_battery.Mobility
        }
        
        battery.capacity >= actuation.actuation_power * mission_time    
        actuation.weight >= battery.battery_weight
    }
    """
    res = parse_model(s)


@comptest
def check_lang6_composition():
    parse_wrap(rvalue, 'mission_time')

    parse_wrap(funcname, 'mocdp.example_battery.Mobility')
    parse_wrap(code_spec, 'code mocdp.example_battery.Mobility')


        # provides energy (T)
    s = """
    cdp {
        provides mission_time [s]
        
        battery = dp {
            provides capacity [J]
            requires battery_weight [g]
            
            implemented-by load BatteryDP
        }
        
        actuation = dp {
            provides payload [g]
            requires actuation_power [W]
            
            implemented-by code mocdp.example_battery.Mobility
        }
                
        capacity provided by battery >= mission_time * (actuation_power required by actuation)    
        payload provided by actuation >= battery_weight required by battery
    }
    """
    res = parse_model(s)


@comptest
def check_lang7_addition():
    s = """
    cdp {
        provides mission_time [s]
        provides extra_payload [g]
        
        battery = dp {
            provides capacity [J]
            requires battery_weight [g]
            
            implemented-by load BatteryDP
        }
        
        actuation = dp {
            provides payload [g]
            requires actuation_power [W]
            
            implemented-by code mocdp.example_battery.Mobility
        }
                
        capacity provided by battery >= mission_time * (actuation_power required by actuation)    
        payload provided by actuation >= (battery_weight required by battery) + extra_payload
    }
    """
    parse_model(s)


@comptest
def check_lang8_addition():
    # x of b  == x required by b
    p = parse_model("""
    cdp {
        provides mission_time  [s]
        provides extra_payload [g]
        requires total_weight [g]
        
        battery = dp {
            provides capacity [J]
            requires weight   [g]
            
            implemented-by load BatteryDP
        }
        
        actuation = dp {
            provides payload [g]
            requires power   [W]
            
            implemented-by code mocdp.example_battery.Mobility
        }
                
        capacity provided by battery >= mission_time * (power required by actuation)    
        payload provided by actuation >= (weight of battery) + extra_payload
        
        total_weight >= weight of battery
    }
    """)
    assert_equal(p.get_rnames(), ['total_weight'])
    assert_equal(p.get_fnames(), ['mission_time', 'extra_payload'])




@comptest
def check_lang9_max():

    parse_wrap(max_expr, 'max(f, g)')
    parse_wrap(rvalue, 'max(f, g)')
    parse_wrap(constraint_expr, 'hnlin.x >= max(f, g)')

    p = parse_model("""
    cdp {
        provides f [R]
        
        hnlin = dp {
            provides x [R]
            requires r [R]
            
            implemented-by load SimpleNonlinearity1
        }
        
        hnlin.x >= max(f, hnlin.r)        
    }
    """)

    assert_equal(p.get_rnames(), [])
    assert_equal(p.get_fnames(), ['f'])


@comptest
def check_lang10_comments():
    p = parse_model("""
    cdp {
        provides f [R]
        
        hnlin = dp {
            provides x [R]
            requires r [R]
            
            implemented-by load SimpleNonlinearity1
        }
        
        hnlin.x >= max(f, hnlin.r)        
    }
    """)
    assert_equal(p.get_rnames(), [])
    assert_equal(p.get_fnames(), ['f'])




@comptest
def check_lang11_resources():
    p = parse_model("""
    cdp {
        provides f [R]
        requires z [R]
        
        hnlin = dp {
            provides x [R]
            requires r [R]
            
            implemented-by load SimpleNonlinearity1
        }
        
        hnlin.x >= max(f, hnlin.r)
        z >= hnlin.r        
    }
    """)

    assert_equal(p.get_rnames(), ['z'])
    assert_equal(p.get_fnames(), ['f'])




@comptest
def check_lang11_leq():
    parse_model("""
    cdp {
        provides f [R]
        
        hnlin = dp {
            provides x [R]
            requires r [R]
            
            implemented-by load SimpleNonlinearity1
        }
        
        max(f, hnlin.r) <= hnlin.x        
    }
    """)

@comptest
def check_simplification():
    """
        Simplification for commutative stuff
        
        SimpleWrap
         provides          y (R[s]) 
         provides          x (R[s]) 
         requires          z (R[s]) 
        | Series:   R[s]×R[s] -> R[s]
        | S1 Mux(R[s]×R[s] → R[s]×R[s], [1, 0])
        | S2 Max(R[s])
    
    """
    m1 = parse_model("""
    cdp {
        provides x  [s]
        provides y  [s]
        requires z  [s]
                
        z >= max(x, y)
    }
""")
    dp1 = m1.get_dp()

    m2 = parse_model("""
    cdp {
        provides x  [s]
        provides y  [s]
        requires z  [s]
                
        z >= max(x, y)
    }
""")
    dp2 = m2.get_dp()
    warnings.warn('readd')
    # assert isinstance(dp1, Max)
#     assert isinstance(dp2, Max)


@comptest
def check_lang13_diagram():
    m1 = parse_model("""
    cdp {
        provides cargo [g]
        requires total_weight [g]
        
        battery = dp {
            provides capacity [J]
            requires battery_weight [g]
            
            implemented-by load BatteryDP
        }
        
        actuation = dp {
            provides weight [g]
            requires actuation_power [W]
            
            implemented-by code mocdp.example_battery.Mobility
        }

        sensing = dp {

            requires sensing_power [W]
            requires mission_time [s]
             
            implemented-by code mocdp.example_battery.PowerTimeTradeoff
        }
        
        (capacity provided by battery) >= sensing.mission_time  * (actuation.actuation_power + sensing.sensing_power)
        cargo + (battery_weight required by battery) <= weight provided by actuation
        
        total_weight >= cargo + (battery_weight required by battery)
    }
""")
# (capacity of battery) >= sensing_tradeoff.mission_time  * (actuation.actuation_power + sensing.sensing_power)
#        cargo + (weight required by battery) <= weight provided by actuation




@comptest
def check_lang12_addition_as_resources():
    # x of b  == x required by b
#     p = parse_model("""
#     cdp {
#         provides a [R]
#         provides b [R]
#         requires c [R]
#         requires d [R]
#         
#         c + d >= a + b
#         }
#     """)
    pass

@comptest
def check_lang14():
    p = parse_model("""
    cdp {
        provides g [s]
        requires f2 [s]

        f2 >= g + g
    }
    """)

@comptest
def check_lang15():
    assert_semantic_error("""
cdp {
    provides g [s]
    provides f [s]

    f >= g
}""", "the name 'f' can't be used as a function")

@comptest
def check_lang16():
    warnings.warn('fix this bug')
    p = parse_model("""
cdp {
    requires g [s]
    provides f [s]
    
    g >= f + f + f

}""")

@comptest
def check_lang17():
    warnings.warn('fix this bug')
    p = parse_model("""
cdp {
    requires g [R]
    provides f [R]
    
    g >= f * f * f 
}
    """)

@comptest
def check_lang18():
    warnings.warn('fix this bug')
    p = parse_model("""
cdp {
    requires g [R]
    provides f [R]
    
    g >= f * f * f * f
}
    """)

@comptest
def check_lang19():
    warnings.warn('fix this bug')
    p = parse_model("""
cdp {
    requires g [R]
    provides f [R]
    
    g >= f * f * f + f * f * f + f
}
    """)


examples1 = [
    """
dp electric-battery {
    provides voltage (intervals of V)
    provides current [A]
    provides capacity [J]
    
    requires carry-weight [g]
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





