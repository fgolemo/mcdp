# -*- coding: utf-8 -*-
from .utils import assert_parsable_to_unconnected_ndp
from comptests.registrar import comptest
from mocdp.dp.dp_max import Max
from mocdp.lang.syntax import (
    binary_expr, code_spec, constraint_expr, funcname, idn, load_expr, ow,
    parse_wrap, res_shortcut3, rvalue, simple_dp_model, unit_expr,
    number_with_unit, unitst)
from mocdp.lang.tests.utils import (assert_parsable_to_connected_ndp,
    assert_semantic_error)
from nose.tools import assert_equal
from pyparsing import Literal, alphanums
import warnings

@comptest
def check_lang():
    parse_wrap(idn, 'battery')
    parse_wrap(idn + ow, 'battery ')
    parse_wrap(idn + ow + Literal('='), 'battery=')
    parse_wrap(load_expr, 'load battery')

    assert_parsable_to_connected_ndp("""
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
    """)


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
    assert_parsable_to_connected_ndp(data)

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
    assert_parsable_to_connected_ndp(data)

    
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

    assert_parsable_to_connected_ndp("""
cdp {
    provides c [J]
    requires w [g]
    
    battery = load battery
    battery.capacity >= c
    
    w >= battery.battery_weight
}
    """)

    # reused same function
    assert_parsable_to_connected_ndp("""
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
    parse_wrap(simple_dp_model, s)[0]



@comptest
def check_lang5_composition():
    parse_wrap(rvalue, 'mission_time')

    parse_wrap(funcname, 'mocdp.example_battery.Mobility')
    parse_wrap(code_spec, 'code mocdp.example_battery.Mobility')

    assert_parsable_to_connected_ndp("""
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
    """)


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
    assert_parsable_to_connected_ndp(s)


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
    assert_parsable_to_connected_ndp(s)


@comptest
def check_lang8_addition():
    # x of b  == x required by b
    p = assert_parsable_to_connected_ndp("""
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

    parse_wrap(binary_expr, 'max(f, g)')
    parse_wrap(rvalue, 'max(f, g)')
    parse_wrap(constraint_expr, 'hnlin.x >= max(f, g)')

    p = assert_parsable_to_connected_ndp("""
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
    p = assert_parsable_to_connected_ndp("""
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
    p = assert_parsable_to_connected_ndp("""
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
    assert_parsable_to_connected_ndp("""
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
    m1 = assert_parsable_to_connected_ndp("""
    cdp {
        provides x  [s]
        provides y  [s]
        requires z  [s]
                
        z >= max(x, y)
    }
""")
    dp1 = m1.get_dp()

    m2 = assert_parsable_to_connected_ndp("""
    cdp {
        provides x  [s]
        provides y  [s]
        requires z  [s]
                
        z >= max(x, y)
    }
""")
    dp2 = m2.get_dp()
    warnings.warn('readd')
    assert isinstance(dp1, Max)
    assert isinstance(dp2, Max)


@comptest
def check_lang13_diagram():
    assert_parsable_to_connected_ndp("""
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
#     p = assert_parsable_to_connected_ndp("""
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
    assert_parsable_to_connected_ndp("""
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
    assert_parsable_to_connected_ndp("""
cdp {
    requires g [s]
    provides f [s]
    
    g >= f + f + f

}""")

@comptest
def check_lang17():
    warnings.warn('fix this bug')
    assert_parsable_to_connected_ndp("""
cdp {
    requires g [R]
    provides f [R]
    
    g >= f * f * f 
}
    """)

@comptest
def check_lang18():
    warnings.warn('fix this bug')
    assert_parsable_to_connected_ndp("""
cdp {
    requires g [R]
    provides f [R]
    
    g >= f * f * f * f
}
    """)

@comptest
def check_lang19():
    assert_parsable_to_connected_ndp("""
cdp {
    requires g [R]
    provides f [R]
    
    g >= f * f * f + f * f * f + f
}
    """)

@comptest
def check_lang20():
    """ One loop """
    assert_parsable_to_connected_ndp("""
cdp {
    times = dp {
        provides a [R]
        provides b [R]
        requires c [R]
 
        implemented-by load times_R
    }

    times.a >= times.c
    times.b >= times.c 
}
""")

@comptest
def check_lang21():    
    assert_parsable_to_connected_ndp("""
    cdp {
        times = cdp {
            provides a [R]
            provides b [R]
            requires c [R]
     
            c >= a * b
        }
    
        times.a >= times.c
        times.b >= times.c 
    }
""")
    

@comptest
def check_lang22():    
    # Need connections: don't know the value of a
    assert_semantic_error("""    
    cdp  {
        requires a [R]
    }
    """)

@comptest
def check_lang23():
    # This is not fine
    assert_semantic_error("""    
    cdp  {
        provides a [R]
    }
    """)

@comptest
def check_lang24():
    # This is fine: it's just a sink
    assert_parsable_to_connected_ndp("""    
    cdp  {
        provides a [R]
        a <= 5.0 [R]
    }
    """)


@comptest
def check_lang25():
    # This should fail because -2 is not in Rcomp
    assert_semantic_error("""    
    cdp  {
        provides f [g]
        requires r [g]
        
        r >= f * -2 [R]
    }
    """)

@comptest
def check_lang26():

    assert_semantic_error("""    
    cdp  {
        provides a [R]
        a <= 5.0 [g] # invalid unit
    }
    """)


@comptest
def check_lang27():
    assert_parsable_to_unconnected_ndp("""
cdp {
    requires g [R]
    provides f [R] 
}
    """)

@comptest
def check_lang28():
    assert_semantic_error("""
cdp {
  
  child1 = cdp {
      provides a [R]
      provides b [R]
      requires c [R]
      c >= a + b
  }
  
  child1.F1 >= 0.0 [R] # no F1
}
""")
    
@comptest
def check_lang29():
    """ Fails because of double constraint on DP.a """
    assert_semantic_error("""
     cdp {
      
        DP = cdp {
            provides a [R]
            provides b [R]
            requires c [R]
            c >= a * b
        }
       
       DP.a >= DP.c
       DP.a >= DP.c
  }""")

@comptest
def check_lang30():
    assert_parsable_to_unconnected_ndp("""
cdp {
  motor = abstract dp {
    provides energy [J]
    requires mass [g]

    implemented-by load BatteryDP
  }
}
""")

@comptest
def check_lang31():
    # Should be joule
    assert_semantic_error("""
cdp {
  motor = abstract dp {
    provides energy [W]
    requires mass [g]

    implemented-by load BatteryDP
  }
}
""")

@comptest
def check_lang32():
    assert_semantic_error("""
cdp {
  motor = abstract cdp {
    provides capacity [W]
    requires mass [g]

  battery = dp {
    provides capacity [J]
    requires mass [g]

    implemented-by load BatteryDP
  }
    capacity <= battery.torque 
    battery.mass <= mass
}}""")

@comptest
def check_lang33():
    # This should work
    assert_parsable_to_unconnected_ndp("""
cdp {
  motor = abstract cdp {
    provides capacity [J]
    requires weight [g]

  battery = dp {
    provides capacity [J]
    requires weight [g]

    implemented-by load BatteryDP
  }
    capacity + 1.0 [J] <= battery.capacity 
    battery.weight <= weight
}}""")


@comptest
def check_lang34():
    # This should work
    assert_parsable_to_connected_ndp("""    
    abstract cdp {
  provides capacity [J]
  requires weight [g]

  motor = abstract cdp {
    provides capacity [J]
    requires weight [g]

  battery = dp {
    provides capacity [J]
    requires weight [g]

    implemented-by load BatteryDP
  }
    capacity + 1.0 [J] <= battery.capacity 
    battery.weight <= weight
  }

  motor.capacity >= capacity
  weight >= motor.weight

}
""")



@comptest
def check_lang36():
    assert_parsable_to_unconnected_ndp("""
 cdp {  

 motor = template cdp {
  requires cost [$]
  provides velocity [R]
  provides endurance [s]
}

}""")

# TODO:
#     assert_parsable_to_unconnected_ndp("""
# cdp {
#   motor = abstract cdp {
#     provides torque [R]
#     requires weight [R]
#
#     weight >= 1.0 [R]
#     torque <= 1.0 [R]
#   }
# }
# """)


@comptest
def check_lang37():
    assert_parsable_to_connected_ndp("""
      template cdp {
            provides voltage [V]
            provides current [A]
            #    
            requires cost [$]
            requires weight [g]
            requires voltage [V] # repeated, but should be ok!
            requires current [A]
          }
    """)


@comptest
def check_lang38():
    assert_parsable_to_connected_ndp("""
    cdp {  
    f =  cdp {
        provides a [R]
            
        requires c [R]
            
        c >= a
    }

    f.a >= f.c
  
  }
""")


@comptest
def check_lang39():
    assert_parsable_to_connected_ndp("""
    cdp {  
    f =  cdp {
        provides x [R]
        requires y [R]
        y >= x
    }

    f.x  >= f.y
  }""")


@comptest
def check_lang40():
    assert_parsable_to_connected_ndp("""
cdp {  
    f =  template cdp {
        provides x [R]
        requires y [R]

    }
    g = template cdp {
        provides a [R]
        requires x [R]
    }
    # conversion from int
    f.x  >= f.y + g.x + 4 [R]
    g.a >= f.y 
  }
""")

@comptest
def check_lang41():
    """ Allow empty models. """
    assert_parsable_to_unconnected_ndp(
"""
    cdp {
  
    DP1 = template cdp {
  
  
  
    }
  
  }""")

@comptest
def check_lang42():
    assert_parsable_to_connected_ndp(
"""    
 cdp {
          motor = template cdp {
            provides speed [R]
            provides torque [R]
            #    
            requires cost [$]
            requires weight [g]
            requires voltage [V]
            requires current [A]
          }
           #
          chassis = template cdp {
            provides payload [g]
            provides velocity [R]
            #
            requires cost [$]
            requires total_weight [g]
            requires motor_speed [R]
            requires motor_torque [R]

            requires controller [R]
          }
 

          requires cost [$]
          requires total_weight [g]
          
          requires voltage [V]
          requires current [A]

          total_weight >= chassis.total_weight 
          
          provides payload [g]
          chassis.payload >= payload + motor.weight
          
          cost >= chassis.cost + motor.cost

          torque provided by motor >= chassis.motor_torque
          speed provided by motor >= chassis.motor_speed

          provides velocity [R]
          chassis.velocity >= velocity
 
          voltage >= motor.voltage
          current >= motor.current

          requires controller [R]
          controller >= chassis.controller
      }
""")

@comptest
def check_lang43():
    """ Shortcuts """
    assert_parsable_to_connected_ndp(
"""    
 cdp {
          motor = template cdp {
            provides speed [R]
            provides torque [R]
            #    
            requires cost [$]
            requires weight [g]
            requires voltage [V]
            requires current [A]
          }
           #
          chassis = template cdp {
            provides payload [g]
            provides velocity [R]
            #
            requires cost [$]
            requires total_weight [g]
            requires motor_speed [R]
            requires motor_torque [R]

            requires controller [R]
          }

          requires total_weight for chassis
          
          requires voltage for motor
          requires current for motor
          
          provides payload [g]
          chassis.payload >= payload + motor.weight
          
          requires cost [$]
          cost >= chassis.cost + motor.cost

          torque provided by motor >= chassis.motor_torque
          speed provided by motor >= chassis.motor_speed

          provides velocity using chassis
          requires controller for chassis
      }
""")


@comptest
def check_lang44():
    """ Shortcuts "using" """
    assert_parsable_to_connected_ndp(
"""    
cdp {
    motor = template cdp {
        provides speed [R]
    }
            
    provides speed using motor
}
""")

@comptest
def check_lang45():
    """ Shortcuts "using" """
    assert_parsable_to_connected_ndp(
"""    
cdp {
    motor = template cdp {
        provides speed [R]
    }
            
    provides speed <= motor.speed
}
""")


@comptest
def check_lang46():
    """ Shortcuts "for" """
    assert_parsable_to_connected_ndp(
"""    
cdp {
    motor = template cdp {
        requires cost [$]
    }
            
    requires cost for motor
}
""")

@comptest
def check_lang47():
    """ Shortcuts "for" """
    assert_parsable_to_connected_ndp(
"""    
cdp {
    motor = template cdp {
        requires cost [$]
    }
            
    requires cost >= motor.cost
}
""")


@comptest
def check_lang48():
    """ Shortcuts "for" """
    assert_parsable_to_connected_ndp(
"""    
cdp {
    provides endurance [s]
    provides power [W]
    
    energy = endurance * power
    
    requires e2 >= energy + 2.0 [J]
}
""")

@comptest
def check_lang49():
    """ Shortcuts "for" """
    parse_wrap(res_shortcut3, "requires cost, weight for motor")
    assert_parsable_to_connected_ndp(
"""    
cdp {
    motor = template cdp {
        requires cost [$]
        requires weight [g]
    }
            
    requires cost, weight for motor
}
""")

@comptest
def check_lang50():
    """ Shortcuts "using" """
    assert_parsable_to_connected_ndp(
"""    
cdp {
    motor = template cdp {
        provides speed [R]
        provides torque [R]
        provides x [R]
    }
            
    provides speed, torque, x using motor
}
""")

@comptest
def check_lang52():
    assert_parsable_to_connected_ndp(
"""    
# test connected
cdp {


    requires weight >= 1.0 g
    provides capacity <= 2.0 J

}
""")

@comptest
def check_lang51():
    """ Shortcuts "using" """
    print unit_expr
    print alphanums
    print parse_wrap(unit_expr, 'R')
    print parse_wrap(unitst, '[R]')

    parse_wrap(number_with_unit, '4.0 [R]')

    parse_wrap(unit_expr, "N")
    parse_wrap(unit_expr, "m")
    parse_wrap(unit_expr, "N m")
    parse_wrap(unit_expr, "m / s^2")
    parse_wrap(unit_expr, "m/s^2")
    
    parse_wrap(number_with_unit, '1 m')
    parse_wrap(number_with_unit, '1 m/s')
    parse_wrap(number_with_unit, '1 m/s^2')



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





