from mocdp.defs import Interval, UpperSet, PrimitiveDP


class BatteryDP(PrimitiveDP):
    
    def get_func_space(self):
        return Interval(L=0.0, U=1.0)
    
    def get_res_space(self):
        return Interval(L=0.0, U=3.0)
    
    def solve(self, min_func):
        joules = min_func
        weight = joules * 3
        us = UpperSet(minimal=set([weight]), poset=self.get_res_space())
        return us
