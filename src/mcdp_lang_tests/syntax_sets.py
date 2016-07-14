# -*- coding: utf-8 -*-
from comptests.registrar import comptest
from mcdp_lang.syntax import Syntax
from mcdp_lang import parse_ndp

from .utils import ok

ok(Syntax.collection_of_constants, "{ 1.5 V, 5 V }")
ok(Syntax.constant_value, "{ 1.5 V, 5 V }")

# @comptest
# def check_sets1():
#     r = parse_wrap_check("{ 1.5 V, 5 V }",
#                      Syntax.collection_of_constants)
#     print r
#
#     r = parse_wrap_check("{ 1.5 V, 5 V }",
#                      Syntax.constant_value)
#     print r


ok(Syntax.unitst, "[set-of(V)]")

ok(Syntax.unitst, "[℘(V)]")

# @comptest
# def check_sets2():
#     r = parse_wrap_check("[set-of(V)]",
#                      Syntax.unitst)
#     print r
#     r = parse_wrap_check("[℘(V)]",
#                      Syntax.unitst)

@comptest
def check_sets3():
    parse_ndp("""
    mcdp {
    
    mcdp simple_cell = catalogue {

        provides voltage [set-of(V)]
        provides capacity [J]

        requires cost [$]
        requires mass [kg]

        model1 | {1.5 V} | 1 J | 5 $ | 0.20 kg 
        model2 | {1.5 V} | 1 J | 5 $ | 0.20 kg 
        model3 | {5.0 V} | 1 J | 5 $ | 0.30 kg

    }

    mcdp cell_plus_converter =  mcdp {
        provides voltage [set-of(V)]
        provides capacity [J]
        requires cost [$]
        requires mass [kg]

        converter = instance catalogue {
            provides voltage_out [set-of(V)]
            requires voltage_in  [set-of(V)]
            requires cost [$]
            requires mass [g]
    
            step_up1 |{5  V}      | {1.5 V} | 5 $  | 20 g  
            step_up2 |{12 V}      | {1.5 V} | 10 $ | 20 g  
            step_up2 |{12 V, 5 V} | {1.5 V} | 10 $ | 20 g  
        }

        cell = instance simple_cell

        voltage <= converter.voltage_out
        converter.voltage_in <= cell.voltage
        mass >= cell.mass + converter.mass
        cost >= cell.cost + converter.cost
        capacity <= cell.capacity
    }

    battery = instance choose(simple: simple_cell, conv: cell_plus_converter)

}
    """)
    pass

@comptest
def check_sets4():
    pass
