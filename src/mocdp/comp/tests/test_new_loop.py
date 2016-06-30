from comptests.registrar import comptest
from mcdp_lang.parse_interface import parse_ndp
from mocdp.comp.composite_abstraction import cndp_abstract_loop2

@comptest
def check_new_loop1():

    ndp = parse_ndp("""

mcdp {
    provides m [Nat]
        f = instance mcdp  {
            provides a [Nat]
            
            requires x [Nat]
            requires y [Nat]
            
            x + y >= a
        }


        f.a >= square(f.x) + square(f.y) + m

        requires x, y for f
}

    """)

    r = cndp_abstract_loop2(ndp)
    print r


@comptest
def check_new_loop2():
    pass


@comptest
def check_new_loop3():
    pass


@comptest
def check_new_loop4():
    pass


@comptest
def check_new_loop5():
    pass

@comptest
def check_new_loop6():
    pass


@comptest
def check_new_loop7():
    pass
