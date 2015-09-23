from mocdp.posets.single import Single
from mocdp.posets.poset_product import PosetProduct
from mocdp.posets.rcomp import RcompUnits
import numpy as np
from mocdp.dp.primitive import PrimitiveDP

def T_from_Ps(Ps):
    return 10.0 + 1 / np.sqrt(Ps)

class TimeEnergyTradeoff(PrimitiveDP):

    def __init__(self):
        self.F = Single("navigate")
        self.R = PosetProduct((RcompUnits("s"), RcompUnits("J")))

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
