# -*- coding: utf-8 -*-
from comptests.registrar import comptest
from mocdp.lang.tests.utils import parse_wrap_check
from mocdp.lang.syntax import Syntax
from mocdp.comp.context import Context
from mocdp.lang.blocks import eval_space
from mocdp.lang.parse_actions import parse_ndp


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
         
        mcdp-type a = catalogue {

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
def check_spaces3():
    pass

@comptest
def check_spaces4():
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
