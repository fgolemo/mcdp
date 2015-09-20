from mocdp.defs import Interval, UpperSet, PrimitiveDP, Rcomp


class BatteryDP(PrimitiveDP):
    
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
        weight = joules * 3
        us = UpperSet(set([weight]), ressp)
        return us
