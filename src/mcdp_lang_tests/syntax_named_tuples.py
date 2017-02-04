# -*- coding: utf-8 -*-
from comptests.registrar import comptest, run_module_tests
from mcdp_lang import parse_ndp, parse_poset
from mcdp_lang.parse_actions import parse_wrap
from mcdp_lang.syntax import Syntax
from mcdp_lang_tests.utils import assert_parse_ndp_semantic_error


@comptest
def check_lang_namedtuple1():
    parse_wrap(Syntax.PRODUCTWITHLABELS, 'product')
    parse_wrap(Syntax.space_product_with_labels, 'product(weight: g, energy: J)')
    P = parse_poset('product(weight: g, energy: J)')
    print P
    print P.format((2.0, 1.0))

@comptest
def check_lang_namedtuple2():
    parse_ndp("""
    
mcdp {

    provides capability [ product(weight: g, energy: J) ]
    
    capability <= < 1g, 1J>

}
    
    """)

@comptest
def check_lang_namedtuple3():
    parse_wrap(Syntax.rvalue_label_indexing, "capability..weight ")[0]

    parse_ndp("""
    
mcdp {

    provides capability [ product(weight: g, energy: J) ]
    
    capability..weight <= 1g
    capability..energy <= 2J
    
    
}
    
    """)



@comptest
def check_lang_namedtuple4():

    s = """
    
mcdp {

    provides capability [ product(weight: g, energy: J) ]
    
    (capability).weight <= 1g
    # (capability).energy <= 1J
    
}
    
    """
    e = assert_parse_ndp_semantic_error(s, contains="Missing value 'energy'")
    

@comptest
def check_lang_namedtuple5():
    parse_wrap(Syntax.fvalue_label_indexing, "capability..weight ")[0]

    parse_ndp("""
    
mcdp {

    requires capability [ product(weight: g, energy: J) ]
    
    capability..weight >= 1g
    capability..energy >= 1J
    
}
    
    """)


@comptest
def check_lang_namedtuple6():
    s = """namedproduct(
    tag: s
)"""
    print('1')
    parse_wrap(Syntax.space_product_with_labels, s)


    print('2')
    parse_wrap(Syntax.space_operand, s)

    print('2b')
    parse_poset(s)

    s = """namedproduct(
    tag: S(DuckiebotIntersectionSignal)
)"""
    print('3')
    parse_poset(s)
    print('4')

@comptest
def check_lang_namedtuple7():
    pass


if __name__ == '__main__': 
    
    run_module_tests()
    
    