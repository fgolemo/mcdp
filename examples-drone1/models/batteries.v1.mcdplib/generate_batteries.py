#!/usr/bin/env python2

template = """
    approx(mass,0%,10g,10kg) 
    approx(cost,0%,1$$,Top$$) 

    mcdp {
        provides capacity [J]
        provides missions [R]

        requires mass     [g]
        requires cost     [$$]
        
        requires maintenance [s]

        specific_energy = $specific_energy
        specific_cost = $specific_cost
        replace_time = 120 s
        cycles = $cycles

        maintenance >= replace_time * (missions / cycles)

        mass >= capacity / specific_energy
        cost >= capacity / specific_cost
    }
"""


types = {
    'NCA':   dict(desc="Lithium nickel cobalt aluminum oxide", 
                    specific_energy="220 Wh/kg", specific_cost='', cycles="1500"),
    
    'NMC':   dict(desc="Lithium nickel manganese cobalt oxide", 
                        specific_energy="205 Wh/kg", specific_cost='', cycles="5000"),
    
    'LCO':   dict(desc="Lithium cobalt oxide", 
                  specific_energy="195 Wh/kg", specific_cost='2.84 Wh/$', cycles="750"),

    'LiPo':  dict(desc="Lithium polimer",
                  specific_energy="150 Wh/kg", specific_cost='2.50 Wh/$', cycles="600"),

    'LMO':   dict(desc="Lithium manganese oxide ",
                  specific_energy="150 Wh/kg", specific_cost='2.84 Wh/$', cycles="500"),

    'NiMH':  dict(desc="Nickel-metal hydride",
                  specific_energy="100 Wh/kg", specific_cost='3.41 Wh/$', cycles="500"),

    'LFP':   dict(desc="Lithium iron phosphate",
                  specific_energy=" 90 Wh/kg", specific_cost='', cycles="1500"),

    'NiH2':  dict(desc="Nickel-hydrogen", 
                  specific_energy=" 45 Wh/kg", specific_cost='', cycles="20000"),    

    'NiCad': dict(desc="Nickel-cadmium",
                  specific_energy=" 30 Wh/kg", specific_cost='', cycles="500"),

    'SLA':   dict(desc="Lead-acid", 
                    specific_energy=" 30 Wh/kg", specific_cost='7 Wh/$', cycles="500"),
}

def go():
    import string

    good = []
    discarded = []
    for name, v in types.items():
        if not v['specific_cost']:
            print('skipping %s because no specific cost' % name)
            discarded.append(name)
            continue

        v['cycles'] = '%s []'% v['cycles']
        s2 = string.Template(template).substitute(v) 

        print s2
        # ndp = parse_ndp(s2)
        model_name = 'bat_%s' % name
        fname = model_name + '.mcdp'
        with open(fname, 'w') as f:
            f.write(s2)

        good.append(model_name)

    ss = """
        choose(\n%s\n)
    """ % ",\n".join("%s:(load %s)" % (g,g) for g in good)
    with open('batteries.mcdp', 'w') as f:
        f.write(ss)

if __name__ == '__main__':
    go()

# class BatteryRandom(PrimitiveDP):

#     def __init__(self, seed):

#         F = R_Energy_J
#         R = R_Weight_g

#         M = SpaceProduct(())
#         PrimitiveDP.__init__(self, F=F, R=R, M=M)

#     def solve(self, func):
#         if func == self.F.get_top():
#             r = self.R.get_top()
#         else:
#             r = Pa_from_weight(func)

#         return self.R.U(r)
