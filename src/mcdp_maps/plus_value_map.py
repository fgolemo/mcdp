from contracts import contract
from mcdp_posets.rcomp_units import RcompUnits
from mcdp_posets.space import Map
import numpy as np

__all__ = [
    'PlusValueMap',
]


class PlusValueMap(Map):
    """ 
        Implements _ -> _ + c 
    
    """

    @contract(F=RcompUnits)
    def __init__(self, F, c_value, c_space, R):
        Map.__init__(self, dom=F, cod=R)
        self.c_value = c_value
        self.c_space = c_space
        self.F = F
        self.R = R

        Fs = [self.c_space, self.F]
        from mcdp_dp.dp_sum import sum_units_factors
        self.factors = sum_units_factors(Fs, self.R)

    def _call(self, x):
        res = 0.0
        res += self.c_value * self.factors[0]
        res += x * self.factors[1]

        if np.isinf(res):
            return self.R.get_top()

        return res
