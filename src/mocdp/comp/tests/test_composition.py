from comptests.registrar import comptest
from mocdp.comp.connection import dpconnect
from mocdp.comp.wrap import LiftRToProduct, LiftToProduct, dploop, dpwrap
from mocdp.dp.dp_sum import Product
from mocdp.example_battery import R_Energy, R_Power, R_Time
from mocdp.example_battery.dp_bat import BatteryDP
from mocdp.example_battery.dp_bat2 import Mobility


@comptest
def check_compose():

    actuation = dpwrap(LiftToProduct(Mobility()),
                       ['weight'], ['actuation_power'])
    
    battery = dpwrap(LiftToProduct(BatteryDP(energy_density=100.0)),
                     ['capacity'], ['weight'])

    times = dpwrap(LiftRToProduct(Product(R_Time, R_Power, R_Energy)),
                   ['mission_time', 'power'], ['energy'])
    
    x = dpconnect(dict(actuation=actuation, times=times), 
              ['times.power >= actuation.actuation_power'])
    
    print('WE have obtained x')
    print('x = %s' % x)
    print('x fun: %s' % x.get_dp().get_fun_space())
    print('x res: %s' % x.get_dp().get_res_space())

    y = dpconnect(dict(battery=battery, x=x),
               ["battery.capacity >= x.energy"])
    
    z = dploop(y, 'weight', 'weight')
    



@comptest
def check_compose2():

    actuation = dpwrap(LiftToProduct(Mobility()),
                       ['weight'], ['actuation_power'])

    battery = dpwrap(LiftToProduct(BatteryDP(energy_density=100.0)),
                     ['capacity'], ['weight'])

    times = dpwrap(LiftRToProduct(Product(R_Time, R_Power, R_Energy)),
                   ['mission_time', 'power'], ['energy'])

    dpconnect(dict(actuation=actuation, times=times, battery=battery),
              ['times.power >= actuation.actuation_power',
               'battery.capacity >= times.energy'])






