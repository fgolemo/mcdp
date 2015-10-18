from mocdp.dp import make_series
from mocdp.dp.dp_flatten import Mux
from mocdp.dp.dp_identity import Identity
from mocdp.dp.dp_parallel import Parallel
from mocdp.dp.dp_sum import Product, Sum
from mocdp.dp.primitive import PrimitiveDP
from mocdp.posets.poset_product import PosetProduct
from mocdp.posets.rcomp import (R_Energy, R_Power, R_Time, R_Weight, Rcomp,
    RcompUnits)
from mocdp.posets.single import Single
import numpy as np
from mocdp.posets.space_product import SpaceProduct
from contracts import contract



class SimpleNonlinearity1(PrimitiveDP):
    # h(x) = 1+log(x+1) 
    # h(0) = 1
    # h(x) = x => x = 2.14

    def __init__(self):
        F = Rcomp()
        R = Rcomp()
        M = SpaceProduct(())
        PrimitiveDP.__init__(self, F=F, R=R, M=M)

    def solve(self, f):
        F = self.get_fun_space()
        R = self.get_res_space()
        if f == F.get_top():
            top = R.get_top()
            return R.U(top)
        y = 1.0 + np.log(1.0 + f)
        return R.U(y)

@contract(Ps='float')
def T_from_Ps(Ps):
    return float(10.0 + 1 / np.sqrt(Ps))

class TimeEnergyTradeoff(PrimitiveDP):

    def __init__(self):
        F = Single("navigate")
        R = PosetProduct((R_Power, R_Time))

        M = R_Power
        PrimitiveDP.__init__(self, F=F, R=R, M=M)

    def evaluate_f_m(self, func, m):
        assert func == 'navigate'
        Ps = m
        return (Ps, T_from_Ps(Ps))

    def solve(self, min_func):
        assert min_func == 'navigate'
        ressp = self.get_res_space()

        PS = np.linspace(0.01, 5.0, 10)

        choices = [ (Ps, T_from_Ps(Ps)) for Ps in PS ]

        for c in choices:
            ressp.belongs(c)

        from mocdp.posets.utils import poset_minima
        min_choices = poset_minima(choices, ressp.leq)

        return ressp.Us(min_choices)


class PowerTimeTradeoff(PrimitiveDP):

    def __init__(self):
        F = PosetProduct(())
        R = PosetProduct((R_Power, R_Time))

        M = R_Power
        PrimitiveDP.__init__(self, F=F, R=R, M=M)

    def evaluate_f_m(self, func, m):
        assert func == ()
        Ps = m
        print('M = %s m= %s' % (self.M, m))
        self.M.belongs(m)
        return (Ps, T_from_Ps(Ps))

    def solve(self, min_func):
        assert min_func == ()
        ressp = self.get_res_space()

        PS = np.linspace(0.01, 5.0, 10)

        choices = [ (Ps, T_from_Ps(Ps)) for Ps in PS ]

        for c in choices:
            ressp.belongs(c)

        from mocdp.posets.utils import poset_minima
        min_choices = poset_minima(choices, ressp.leq)

        return ressp.Us(min_choices)

def Pa_from_weight(W):
    return 1.0 + W

class Mobility(PrimitiveDP):

    def __init__(self):
        F = RcompUnits('g')
        R = RcompUnits('W')

        M = SpaceProduct(())
        PrimitiveDP.__init__(self, F=F, R=R, M=M)

    def solve(self, func):
        if func == self.F.get_top():
            r = self.R.get_top()
        else:
            r = Pa_from_weight(func)

        return self.R.U(r)


def series(l):
    if len(l) == 1:
        return l[0]
    else:
        return make_series(l[0], series(l[1:]))

def battery_complete():

    assert R_Time != R_Energy
    assert R_Time != R_Power
    assert R_Energy != R_Power
    assert PosetProduct((R_Time, R_Time)) != PosetProduct((R_Time, R_Energy))

    N = Single('navigate')
    
    F = PosetProduct((PosetProduct((R_Weight, N)), R_Weight))

    dpB = Mux(F, [[(0, 0), 1], (0, 1)])

    assert dpB.get_fun_space() == F

    dpA = Parallel(Sum(R_Weight), Identity(N))

    series([dpB, dpA])

    dp1 = Parallel(Mobility(), TimeEnergyTradeoff())

    series([dpA, dp1])

    dp2 = Mux(F=dp1.get_res_space(), coords=[[0, (1, 0)], (1, 1)])

    series([dp1, dp2])

    dp4 = Parallel(Sum(R_Power), Identity(R_Time))

    series([dp2, dp4])

    dp4b = Mux(dp4.get_res_space(), [1, [1, 0]])

    series([dp4, dp4b])

    e_from_tp = Product(R_Time, R_Power, R_Energy)

    from .dp_bat import BatteryDP
    battery = BatteryDP(energy_density=100.0)

    dp7 = Parallel(Identity(R_Time), make_series(e_from_tp, battery))

    series([dp4b, dp7])

    dps = series([dpB, dpA, dp1, dp2, dp4, dp4b, dp7])
#     dp = DPLoop(dps)

    return dps

def energy_product():
    return Product(R_Time, R_Power, R_Energy)

