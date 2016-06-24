from comptests.registrar import comptest
from mcdp_posets.types_universe import get_types_universe
from mcdp_lang.parse_interface import parse_poset

@comptest
def check_lang_interval1():
    tu = get_types_universe()
    P = parse_poset('interval(0g, 1g)')


@comptest
def check_lang_interval2():
    one = 'interval(0.0 [], 1.0 [])'
    rgb = "x".join([one] * 3)
    P = parse_poset(rgb)

@comptest
def check_lang_interval3():
    pass


@comptest
def check_lang_interval4():
    pass

@comptest
def check_lang_interval5():
    pass


@comptest
def check_lang_interval6():
    pass


@comptest
def check_lang_interval7():
    pass

