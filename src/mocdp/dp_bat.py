# -*- coding: utf-8 -*-

from mocdp.defs import UpperSet, PrimitiveDP, Rcomp
from contracts import contract


class BatteryDP(PrimitiveDP):
    """ 
    
        F: need F Joule for energy
        R: need battery of weight W
        
    """
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
            return ressp.U(ressp.get_top())
        
        joules = min_func
        weight = joules / self.energy_density
        return ressp.U(weight)


class Weight2totalpayload(PrimitiveDP):

    def __init__(self, baseline=100):
        self.baseline = baseline

    def get_fun_space(self):
        return Rcomp()

    def get_res_space(self):
        return Rcomp()
    
    def solve(self, min_func):
        funsp = self.get_fun_space()
        ressp = self.get_res_space()
        funsp.belongs(min_func)

        if min_func == funsp.get_top():
            return ressp.U(ressp.get_top())

        battery_weight = min_func
        payload = self.baseline + battery_weight

        return ressp.U(payload)


class Payload2energy(PrimitiveDP):

    def __init__(self, T, alpha):
        self.T = T
        self.alpha = alpha

    def get_fun_space(self):
        return Rcomp()

    def get_res_space(self):
        return Rcomp()

    def solve(self, min_func):
        funsp = self.get_fun_space()
        ressp = self.get_res_space()
        funsp.belongs(min_func)

        if min_func == funsp.get_top():
            return ressp.U(ressp.get_top())

        payload = min_func
        energy = payload * self.alpha * self.T
        return ressp.U(energy)


"""
dp BatteryDP:
    energy_density = 12 
    icon battery
    
    F stored_energy (J)
    R battery_weight (g)
    
    battery_weight ≥ stored_energy * $energy_density
    
weight2payload = 
dp:
    "This is a simple"
    
    desc:
        This is a simple relation between payload and 
        weight:
        
        $ P ≥ X * x $
    
    C:
        baseline (g) = 100  "Baseline payload" 
        
    F:
        battery_weight (g) 
          
    R:
        total_payload  (g)  "Payload" / $P$ 
    
    total_payload ≥ battery_weight + baseline
    
dp payload2energy:
    
    F payload (g) "Carry this payload." tex P
    R energy  (J) "Required stored energy." tex E

dp rafc_example:

    dp energy2bweight = BatteryDP()
    dp weight2payload = weight2payload() 
    dp payload2energy = payload2energy / {battery: 0.1, battery.pok: 0.1}   

    energy2bweight |-- energy ≤ required --| weight2payload   

    dp 0 = MCB_plus_PSU
    dp 1 = chassis_plus_motor

    F velocity = velocity─┤1
    F extra_payload (g)   "Extra payload"
    F extra_power   (P)   "Extra power"
    F mission_time = mission_time─┤0

    please hurry !!!!111 
    
""" 
