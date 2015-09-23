from mocdp.posets.single import Single
from mocdp.posets.poset_product import PosetProduct
from mocdp.posets.rcomp import RcompUnits, Rcomp
import numpy as np
from mocdp.dp.primitive import PrimitiveDP
from mocdp.dp.dp_parallel import Parallel
from mocdp.dp.dp_flatten import  Mux
from mocdp.dp.dp_series import Series
from mocdp.dp.dp_sum import Sum, Product
from mocdp.dp.dp_identity import Identity

from . import R_Energy, R_Time, R_Power, R_Weight
from mocdp.dp.dp_loop import DPLoop


def T_from_Ps(Ps):
    return 10.0 + 1 / np.sqrt(Ps)

class TimeEnergyTradeoff(PrimitiveDP):

    def __init__(self):
        self.F = Single("navigate")
        self.R = PosetProduct((R_Time, R_Energy))

    def get_fun_space(self):
        return self.F

    def get_res_space(self):
        return self.R

    def solve(self, min_func):
        funsp = self.get_fun_space()
        ressp = self.get_res_space()
        funsp.belongs(min_func)

        PS = np.linspace(0.01, 5.0, 10)

        choices = [ (Ps, T_from_Ps(Ps)) for Ps in PS ]

        for c in choices:
            ressp.belongs(c)

        from mocdp.posets.utils import poset_minima
        min_choices = poset_minima(choices, ressp.leq)

        return ressp.Us(min_choices)

    def __repr__(self):
        return 'TimeEnergyTradeoff()'


def Pa_from_weight(W):
    return 1.0 + W

class Mobility(PrimitiveDP):

    def __init__(self):
        self.F = RcompUnits('g')
        self.R = RcompUnits('W')

    def get_fun_space(self):
        return self.F

    def get_res_space(self):
        return self.R

    def solve(self, func):
        self.F.belongs(func)

        if func == self.F.get_top():
            r = self.R.get_top()
        else:
            r = Pa_from_weight(func)

        return self.R.U(r)

    def __repr__(self):
        return 'Mobility(%s->%s)' % (self.F, self.R)

def series(l):
    if len(l) == 1:
        return l[0]
    else:
        return Series(l[0], series(l[1:]))

def battery_complete():

    assert R_Time != R_Energy
    assert R_Time != R_Power
    assert R_Energy != R_Power
    assert PosetProduct((R_Time, R_Time)) != PosetProduct((R_Time, R_Energy))

    N = Single('navigate')
    
    F = PosetProduct((PosetProduct((R_Weight, N)), R_Weight))

    dpB = Mux(F, [[(0, 0), 1], (0, 1)])
    dpA = Parallel(Sum(R_Weight), Identity(N))

    dp1 = Parallel(Mobility(), TimeEnergyTradeoff())

    dp2 = Mux(F=dp1.get_res_space(), coords=[[0, (1, 0)], (1, 1)])

    dp4 = Parallel(Sum(Rcomp()), Identity(R_Time))
    dp4b = Mux(dp4.get_res_space(), [1, [0, 1]])
    e_from_tp = Product(R_Time, R_Power, R_Energy)

    from .dp_bat import BatteryDP
    battery = BatteryDP(energy_density=100.0)

    dp7 = Parallel(Identity(R_Time), Series(e_from_tp, battery))

    dps = series([dpB, dpA, dp1, dp2, dp4, dp4b, dp7])
    dp = DPLoop(dps)

    return dp

