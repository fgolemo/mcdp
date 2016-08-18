from contracts import contract
from mcdp_posets.rcomp_units import RcompUnits
from mcdp_posets.space import Map

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

    def __repr__(self):
        return "+ %s" % self.c_space.format(self.c_value)

    def _call(self, x):
        values = [self.c_value, x]
        Fs = [self.c_space, self.F]
        from mcdp_dp.dp_sum import sum_units
        return sum_units(Fs, values, self.R)
