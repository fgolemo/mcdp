# -*- coding: utf-8 -*-

from contracts import contract
from mcdp_dp import make_series
from mcdp_dp.dp_flatten import Mux
from mcdp_dp.dp_identity import Identity
from mcdp_dp.dp_parallel import Parallel
from mcdp_dp.dp_sum import Product, Sum
from mcdp_dp.primitive import PrimitiveDP
from mcdp_posets import (PosetProduct, R_Energy, R_Power, R_Time, R_Weight_g,
    R_dimensionless, Single, SpaceProduct)
import numpy as np



class SimpleNonlinearity1(PrimitiveDP):
    # h(x) = 1+log(x+1) 
    # h(0) = 1
    # h(x) = x => x = 2.14

    def __init__(self):
        F = R_dimensionless
        R = R_dimensionless
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