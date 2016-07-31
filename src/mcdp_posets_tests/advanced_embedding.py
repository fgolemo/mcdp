from comptests.registrar import comptest
from mcdp_lang.parse_interface import parse_poset
from mcdp_posets.types_universe import get_types_universe


@comptest
def adv_embed_1():
    """ PosetProduct takes into account permutations. """
    P1 = parse_poset('m x J')
    P2 = parse_poset('J x m')
    tu = get_types_universe()
    tu.check_leq(P1, P2)
    tu.check_leq(P2, P1)

@comptest
def adv_embed_2():


    pass


@comptest
def adv_embed_3():
    pass



@comptest
def adv_embed_4():
    pass


@comptest
def adv_embed_5():
    pass


@comptest
def adv_embed_6():
    pass

@comptest
def adv_embed_7():
    pass


@comptest
def adv_embed_8():
    pass


@comptest
def adv_embed_9():
    pass

@comptest
def adv_embed_10():
    pass

@comptest
def adv_embed_11():
    pass

@comptest
def adv_embed_12():
    pass


@comptest
def adv_embed_13():
    pass

@comptest
def adv_embed_14():
    pass

@comptest
def adv_embed_15():
    pass

@comptest
def adv_embed_16():
    pass
