
from comptests.registrar import comptest
from contracts.utils import raise_desc
from mocdp.comp.connection import TheresALoop, dpconnect, dpgraph, dploop0
from mocdp.comp.wrap import dpwrap
from mocdp.dp import Product, Series, Terminator, make_series
from mocdp.example_battery import R_Energy, R_Power, R_Time, R_Weight
from mocdp.example_battery.dp_bat import BatteryDP
from mocdp.example_battery.dp_bat2 import Mobility
from mocdp.posets.poset_product import PosetProduct
from mocdp.posets.rcomp import Rcomp
from numpy.testing.utils import assert_equal


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

    _y = dpconnect(dict(battery=battery, x=x),
               ["battery.capacity >= x.energy"])



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

    dp = res.get_dp()
    funsp = dp.get_fun_space()
    ressp = dp.get_res_space()
    assert funsp == PosetProduct((R_Weight, R_Time)), funsp
    assert ressp == R_Weight, ressp


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
#
#
# @comptest
# def check_compose2_loop():
#     actuation = dpwrap(Mobility(),
#                        'weight', 'actuation_power')
#
#     battery = dpwrap((BatteryDP(energy_density=100.0)),
#                      'capacity', 'battery_weight')
#
#     times = dpwrap((Product(R_Time, R_Power, R_Energy)),
#                    ['mission_time', 'power'], 'energy')
#
#     x = dpconnect(dict(actuation=actuation, times=times, battery=battery),
#               ['times.power >= actuation.actuation_power',
#                'battery.capacity >= times.energy'])
#
#     y = dploop(x, 'battery_weight', 'weight')
#
#     print y.desc()
#
#     print y.get_fnames()
#     print y.get_rnames()
#
#     assert y.get_fnames() == ['mission_time'],y.get_fnames()
#     assert y.get_rnames() == [], y.get_rnames()
#
#     check_ftype(x, 'mission_time', R_Time)
#     check_ftype(x, 'weight', R_Weight)
#     check_ftype(x, 'weig2ht', R_Weight)



@comptest
def check_compose2_loop2():
    actuation = dpwrap(Mobility(),
                       'weight', 'actuation_power')

    battery = dpwrap((BatteryDP(energy_density=100.0)),
                     'capacity', 'battery_weight')

    times = dpwrap((Product(R_Time, R_Power, R_Energy)),
                   ['mission_time', 'power'], 'energy')

    x = dpconnect(dict(actuation=actuation, times=times, battery=battery),
              ['times.power >= actuation.actuation_power',
               'battery.capacity >= times.energy'])

    y = dploop0(x, 'battery_weight', 'weight')

    print y.desc()

    assert y.get_fnames() == ['mission_time'], y.get_fnames()
    assert y.get_rnames() == ['battery_weight'], y.get_rnames()

    check_ftype(x, 'mission_time', R_Time)
#     check_ftype(x, 'weight', R_Weight)
    check_rtype(x, 'battery_weight', R_Weight)


    dp = y.get_dp()

    funsp = dp.get_fun_space()
    ressp = dp.get_res_space()
    print('funsp: %s' % funsp)
    print('ressp: %s' % ressp)
    assert funsp == R_Time, funsp
    assert ressp == R_Weight, ressp



@comptest
def check_compose2_generic():
    actuation = dpwrap(Mobility(),
                       'weight', 'actuation_power')

    battery = dpwrap((BatteryDP(energy_density=100.0)),
                     'capacity', 'battery_weight')

    times = dpwrap((Product(R_Time, R_Power, R_Energy)),
                   ['mission_time', 'power'], 'energy')

    y = dpgraph(dict(actuation=actuation, times=times, battery=battery),
              ['times.power >= actuation.actuation_power',
               'battery.capacity >= times.energy',
               'actuation.weight >= battery.battery_weight'], split=[])

    print y.desc()

    assert y.get_fnames() == ['mission_time'], y.get_fnames()
    assert y.get_rnames() == [], y.get_rnames()

    check_ftype(y, 'mission_time', R_Time)
#     check_rtype(y, 'battery_weight', R_Weight)

    dp = y.get_dp()
    funsp = dp.get_fun_space()
    ressp = dp.get_res_space()
    assert funsp == R_Time, funsp
    assert ressp == PosetProduct(()), ressp


def check_same_spaces(dp1, dp2):
#     print('dp1: %s' % dp1)
#     print('dp2: %s' % dp2)
    F1 = dp1.get_fun_space()
    R1 = dp1.get_res_space()
    F2 = dp2.get_fun_space()
    R2 = dp2.get_res_space()
    if not (R1 == R2):
        msg = 'R not preserved'
        raise_desc(AssertionError, msg, R1=R1, R2=R2)
    if not (F1 == F2):
        msg = 'F not preserved'
        raise_desc(AssertionError, msg, F1=F1, F2=F2)

@comptest
def rule_terminator_series():
    # Series(X(F,R), Terminator(R)) => Terminator(F)
    F0 = Rcomp()
    from mocdp.dp.dp_flatten import Mux
    dp1 = Mux(F0, ())
    dp2 = Terminator(F0)
    # make sure we can obtain it
    s0 = Series(dp1, dp2)
    s1 = make_series(dp1, dp2)
    check_same_spaces(s0, s1)
    assert isinstance(s1, Terminator), s1

@comptest
def rule_terminator_parallel():
    pass
#     # Parallel(X(F,R), Terminator(R)) => Terminator(F)
#     F0 = Rcomp()
#     F = PosetProduct((F0, F0))
#     dp1 = Sum()












