from comptests.registrar import comptest
from mcdp_lang.parse_actions import parse_wrap
from mcdp_lang.syntax import Syntax
from mcdp_report.html import print_html_inner


@comptest
def test_escaping1():
    p = parse_wrap(Syntax.constant_value, '<0g>')[0]

    s = list(print_html_inner(p))[0].transformed
    
    se = ("<span class='MakeTuple'><span class='OpenBraceKeyword'>&lt;</span>"
        "<span class='SimpleValue'><span class='ValueExpr'>0</span><span class='RcompUnit'>g</span></span>"
        "<span class='CloseBraceKeyword'>&gt;</span></span>")
    print s
    assert se == s



@comptest
def test_escaping2(): pass

@comptest
def test_escaping3(): pass

@comptest
def test_escaping4(): pass

@comptest
def test_escaping5(): pass
