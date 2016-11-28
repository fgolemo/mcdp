# -*- coding: utf-8 -*-
from comptests.registrar import comptest
from mcdp_lang.parse_interface import parse_constant


@comptest
def check_minimals1():  # TODO: rename
    p = parse_constant('Minimals V')
    print p
    p = parse_constant('Minimals finite_poset{ a b}')
    print p

@comptest
def check_maximals1():  # TODO: rename
    p = parse_constant('Maximals V')
    print p