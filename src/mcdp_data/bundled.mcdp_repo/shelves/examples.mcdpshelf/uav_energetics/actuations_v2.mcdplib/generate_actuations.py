#!/usr/bin/env python2
# -*- coding: utf-8 -*-

template = """
approx(power,0%,0.1W,$max_watt) 

mcdp {
    provides lift  [N]
    requires power [W]
    requires actuator_mass [g]
    requires cost [$$]
    
    p0 = $p0
    p1 = $p1

    power >= p0 + (lift^2) * p1

    actuator_mass >= $mass
    cost >= $cost
}
"""


types = {
    'a1':   dict(desc="", p0='1 W', p1='2.0 W/N^2', mass='50 g', cost='50 $', max_watt='50 W'),
    'a2':   dict(desc="", p0='2 W', p1='1.5 W/N^2', mass='100 g', cost='100 $', max_watt='100 W'),
    'a3':   dict(desc="", p0='3 W', p1='1.0 W/N^2', mass='150 g', cost='150 $', max_watt='200 W'),
}

def go():
    import string
    good = []
    discarded = []
    for name, v in types.items():
        s2 = string.Template(template).substitute(v) 

        print s2
        # ndp = parse_ndp(s2)
        model_name = 'actuation_%s' % name
        fname = model_name + '.mcdp'
        with open(fname, 'w') as f:
            f.write(s2)

        good.append(model_name)

    ss = """
        choose(\n%s\n)
    """ % ",\n".join("%s:(load %s)" % (g,g) for g in good)
    with open('actuation.mcdp', 'w') as f:
        f.write(ss)

if __name__ == '__main__':
    go()
 