# -*- coding: utf-8 -*-
from comptests.registrar import comptest
from mcdp_lang.parse_actions import parse_wrap
from mcdp_lang.syntax import Syntax
from mcdp_report.html import print_html_inner


@comptest
def test_escaping1():
    p = parse_wrap(Syntax.constant_value, '<0g>')[0]

    s = list(print_html_inner(p))[0].transformed
    
    se = """<span class='MakeTuple' where_character='0' where_character_end='4'><span class='OpenBraceKeyword' where_character='0' where_character_end='1'>&lt;</span><span class='SimpleValue' where_character='1' where_character_end='3'><span class='ValueExpr' where_character='1' where_character_end='2'>0</span><span class='RcompUnit' where_character='2' where_character_end='3'>g</span></span><span class='CloseBraceKeyword' where_character='3' where_character_end='4'>&gt;</span></span>"""
    assert se == s
#     print s



@comptest
def test_escaping2(): pass

@comptest
def test_escaping3(): pass

@comptest
def test_escaping4(): pass

@comptest
def test_escaping5(): pass
