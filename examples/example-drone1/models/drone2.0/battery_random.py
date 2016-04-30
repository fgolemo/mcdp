from mocdp.dp.primitive import PrimitiveDP
from mocdp.posets.rcomp_units import R_Weight_g, R_Power, R_Energy_J
from mocdp.posets.space_product import SpaceProduct
from mocdp.example_battery.dp_bat import Pa_from_weight

class BatteryRandom(PrimitiveDP):

    def __init__(self, seed):

        F = R_Energy_J
        R = R_Weight_g

        M = SpaceProduct(())
        PrimitiveDP.__init__(self, F=F, R=R, M=M)

    def solve(self, func):
        if func == self.F.get_top():
            r = self.R.get_top()
        else:
            r = Pa_from_weight(func)

        return self.R.U(r)
