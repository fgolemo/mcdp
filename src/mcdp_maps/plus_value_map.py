from contracts import contract
from mcdp_posets import (Map, MapNotDefinedHere, RcompUnits,
    express_value_in_isomorphic_space)

__all__ = [
    'PlusValueMap',
    'MinusValueMap',
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

class MinusValueMap(Map):
    """ 
        Implements _ -> _ - c
        
        with c a negative constant.
        
        It is not defined for x <= c. 
    """

#     @contract(F=RcompUnits, c_value='>=0')
    def __init__(self, F, c_value, c_space):
        assert c_value >= 0
        Map.__init__(self, dom=F, cod=F)
        self.c_value = c_value
        self.c_space = c_space

        self.c = express_value_in_isomorphic_space(c_space, c_value, F)
        self.F = F
        self.top = F.get_top()

    def __repr__(self):
        return "- %s" % self.c_space.format(self.c_value)

    def _call(self, x):
        if self.F.equal(x, self.c):
            return 0.0
        else:
            if self.F.leq(x, self.c):
            # undefined
                raise MapNotDefinedHere('%s < %s' % (self.F.format(x), self.F.format(self.c)))
            else:
                if self.F.equal(self.top, x):
                    return self.top
                else:
                    res = x - self.c
                    assert res >= 0
                    # todo: check underflow
                    return res
