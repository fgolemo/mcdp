# -*- coding: utf-8 -*-
from comptests.registrar import comptest
from .utils import parse_wrap_check
from mcdp_lang.syntax import Syntax
from mocdp.comp.context import Context

from mcdp_lang import parse_ndp
from mcdp_lang.eval_space_imp import eval_space


@comptest
def check_spaces1():
    def p(s):
        c = Context()
        r = parse_wrap_check(s, Syntax.space_expr)
        print r
        x = eval_space(r, c)
        print x
    p('V')
    p("V x m")
    p("V × m")
    p("V × m × J")
    p("m × m × m")
    p("m × (m × m)")

@comptest
def check_spaces2():
    ndp = parse_ndp("""
    mcdp {
         
        a = catalogue {

        provides voltage [set-of(V)]
        provides capacity [J]

        requires cost [$]
        requires mass [kg]

        model1 | {1.5 V} | 1 J | 5 $ | 0.20 kg 
        model2 | {1.5 V} | 1 J | 5 $ | 0.20 kg 
        model3 | {5.0 V} | 1 J | 5 $ | 0.30 kg

    }
    }
    """)
    print ndp

@comptest
def check_spaces3():  # changename
    parse_wrap_check('instance simple_cell', Syntax.dpinstance_from_type)
    parse_wrap_check('sub cell = instance simple_cell', Syntax.setsub_expr)

@comptest
def check_spaces4():
    print parse_wrap_check('<5mm, 5mm, 5mm>', Syntax.tuple_of_constants)
    print parse_wrap_check('step_up1 | {5 V}        | {1.5 V} |  5 $ | 20 g | <5mm, 5mm, 5mm>', Syntax.catalogue_row)
    parse_ndp("""
catalogue {
    provides voltage    [℘(V)]
    requires v_in       [℘(V)]
    requires cost       [$]
    requires mass       [g]
    requires shape      [m x m x m]
    
    step_up1 | {5 V}        | {1.5 V} |  5 $ | 20 g | <5mm, 5mm, 5mm>
    step_up2 |       {12 V} | {1.5 V} | 10 $ | 20 g | <5mm, 5mm, 5mm>
    step_up2 | {5 V,  12 V} | {1.5 V} | 10 $ | 20 g | <5mm, 5mm, 5mm>
}
""")
        
    pass

@comptest
def check_spaces5():
    pass

@comptest
def check_spaces6():
    pass

@comptest
def check_spaces7():
    pass

@comptest
def check_spaces8():
    pass
