# -*- coding: utf-8 -*-
from comptests.registrar import comptest
from mocdp.lang.tests.utils import parse_wrap_check
from mocdp.lang.syntax import Syntax
from mocdp.lang.parse_actions import parse_ndp

@comptest
def check_sets1():
    r = parse_wrap_check("{ 1.5 V, 5 V }",
                     Syntax.collection_of_constants)
    print r

    r = parse_wrap_check("{ 1.5 V, 5 V }",
                     Syntax.constant_value)
    print r

@comptest
def check_sets2():
    r = parse_wrap_check("[set-of(V)]",
                     Syntax.unitst)
    print r
    r = parse_wrap_check("[℘(V)]",
                     Syntax.unitst)

@comptest
def check_sets3():
    ndp = parse_ndp("""
    mcdp {
    
    simple_cell = catalogue {

        provides voltage [set-of(V)]
        provides capacity [J]

        requires cost [$]
        requires mass [kg]

        model1 | {1.5 V} | 1 J | 5 $ | 0.20 kg 
        model2 | {1.5 V} | 1 J | 5 $ | 0.20 kg 
        model3 | {5.0 V} | 1 J | 5 $ | 0.30 kg

    }

    cell_plus_converter = mcdp {
        provides voltage [set-of(V)]
        provides capacity [J]
        requires cost [$]
        requires mass [kg]

        sub converter = catalogue {
            provides voltage_out [set-of(V)]
            requires voltage_in  [set-of(V)]
            requires cost [$]
            requires mass [g]
    
            step_up1 |{5  V}      | {1.5 V} | 5 $  | 20 g  
            step_up2 |{12 V}      | {1.5 V} | 10 $ | 20 g  
            step_up2 |{12 V, 5 V} | {1.5 V} | 10 $ | 20 g  
        }

        sub cell = simple_cell

        voltage <= converter.voltage_out
        converter.voltage_in <= cell.voltage
        mass >= cell.mass + converter.mass
        cost >= cell.cost + converter.cost
        capacity <= cell.capacity
    }

    sub battery = simple_cell ^ cell_plus_converter

}
    """)
    pass

@comptest
def check_sets4():
    pass
