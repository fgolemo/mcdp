from mocdp.defs import UpperSet, PrimitiveDP, Rcomp
from contracts import contract


class BatteryDP(PrimitiveDP):
    
    @contract(energy_density='float, >0')
    def __init__(self, energy_density):
        '''
        :param energy_density: Joule/gram
        '''
        self.energy_density = energy_density

    def get_fun_space(self):
        # return Interval(L=0.0, U=1.0)
        return Rcomp()
    
    def get_res_space(self):
        # return Interval(L=0.0, U=3.0)
        return Rcomp()
    
    def solve(self, min_func):
        funsp = self.get_fun_space()
        ressp = self.get_res_space()

        funsp.belongs(min_func)
        
        if min_func == funsp.get_top():
            return ressp.get_top()
        
        joules = min_func
        weight = joules / self.energy_density
        us = UpperSet(set([weight]), ressp)
        return us
