from comptests.registrar import comptest
from mocdp.comp.connection import TheresALoop, dpconnect, dploop
from mocdp.comp.wrap import dpwrap
from mocdp.dp.dp_sum import Product
from mocdp.example_battery import R_Energy, R_Power, R_Time, R_Weight
from mocdp.example_battery.dp_bat import BatteryDP
from mocdp.example_battery.dp_bat2 import Mobility
from contracts.utils import raise_desc


@comptest
def check_compose():

    actuation = dpwrap(Mobility(), 'weight', 'actuation_power')

    check_ftype(actuation, 'weight', R_Weight)
    check_rtype(actuation, 'actuation_power', R_Power)
    
    battery = dpwrap(BatteryDP(energy_density=100.0),
                     'capacity', 'weight')

    check_ftype(battery, 'capacity', R_Energy)
    check_rtype(battery, 'weight', R_Weight)

    times = dpwrap(Product(R_Time, R_Power, R_Energy),
                   ['mission_time', 'power'], 'energy')
    
    check_ftype(times, 'mission_time', R_Time)
    check_ftype(times, 'power', R_Power)
    check_rtype(times, 'energy', R_Energy)

    x = dpconnect(dict(actuation=actuation, times=times), 
              ['times.power >= actuation.actuation_power'])
    
    print('WE have obtained x')
    print('x = %s' % x)
    print('x fun: %s' % x.get_dp().get_fun_space())
    print('x res: %s' % x.get_dp().get_res_space())

    y = dpconnect(dict(battery=battery, x=x),
               ["battery.capacity >= x.energy"])
#
#     z = dploop(y, 'weight', 'weight')
    


def check_rtype(ndp, r, expected):
    got = ndp.get_rtype(r)
    if not got == expected:
        raise_desc(ValueError, 'mismatch', r=r, expected=expected, got=got)


def check_ftype(ndp, f, expected):
    got = ndp.get_ftype(f)
    if not got == expected:
        raise_desc(ValueError, 'mismatch', f=f, expected=expected, got=got)

@comptest
def check_compose2():

    actuation = dpwrap((Mobility()),
                       'weight', 'actuation_power')

    battery = dpwrap((BatteryDP(energy_density=100.0)),
                     'capacity', 'weight')

    check_rtype(battery, 'weight', R_Weight)
    check_ftype(battery, 'capacity', R_Energy)

    times = dpwrap((Product(R_Time, R_Power, R_Energy)),
                   ['mission_time', 'power'], 'energy')

    check_ftype(times, 'mission_time', R_Time)
    check_ftype(times, 'power', R_Power)
    check_rtype(times, 'energy', R_Energy)

    res = dpconnect(dict(actuation=actuation, times=times, battery=battery),
              ['times.power >= actuation.actuation_power',
               'battery.capacity >= times.energy'])

    print res.desc()
    check_rtype(res, 'weight', R_Weight)
    check_ftype(res, 'mission_time', R_Time)
    check_ftype(res, 'weight', R_Weight)


@comptest
def check_compose2_fail():
    """ Fails because there is a recursive constraint """

    actuation = dpwrap((Mobility()),
                       'weight', 'actuation_power')

    battery = dpwrap((BatteryDP(energy_density=100.0)),
                     'capacity', 'weight')

    times = dpwrap((Product(R_Time, R_Power, R_Energy)),
                   ['mission_time', 'power'], 'energy')

    try:
        dpconnect(dict(actuation=actuation, times=times, battery=battery),
              ['times.power >= actuation.actuation_power',
               'battery.capacity >= times.energy',
               'actuation.weight >= battery.weight'])
    except TheresALoop:
        pass




@comptest
def check_compose2_loop():
    actuation = dpwrap(Mobility(),
                       'weight', 'actuation_power')

    battery = dpwrap((BatteryDP(energy_density=100.0)),
                     'capacity', 'battery_weight')

    times = dpwrap((Product(R_Time, R_Power, R_Energy)),
                   ['mission_time', 'power'], 'energy')

    x = dpconnect(dict(actuation=actuation, times=times, battery=battery),
              ['times.power >= actuation.actuation_power',
               'battery.capacity >= times.energy'])

    y = dploop(x, 'battery_weight', 'weight')

    print y.desc()

    check_ftype(x, 'weight', R_Weight)

    assert y.get_rnames() == []



