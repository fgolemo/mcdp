# -*- coding: utf-8 -*-
from comptests.registrar import comptest
from mcdp_lang.parse_interface import parse_poset
from mcdp_lang.parse_actions import parse_wrap
from mcdp_lang.syntax import Syntax

@comptest
def check_lang_interval1():
    parse_poset('Interval(0g, 1g)')


@comptest
def check_lang_interval2():
    one = 'Interval(0.0 [], 1.0 [])'
    rgb = " x ".join([one] * 3)
    print parse_poset(rgb)

@comptest
def check_lang_interval3():
    pass

@comptest
def check_lang_interval4():  # TODO: coporduct
    parse_wrap(Syntax.space_coproduct, 'coproduct(g, V)')

    P = parse_poset('coproduct(g, V)')
    print P

@comptest
def check_lang_interval5():
    pass


@comptest
def check_lang_interval6():
    pass


@comptest
def check_lang_interval7():
    pass

