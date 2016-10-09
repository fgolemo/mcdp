from comptests.registrar import comptest
from mcdp_lang.parts import CDPLanguage
from mcdp_lang.syntax import Syntax

from .utils import TestFailed, parse_wrap_check
from .utils2 import eval_rvalue_as_constant


CDP = CDPLanguage

@comptest
def check_syntax_load1():

    # "load <name>"
    # name_poset = sp(get_idn(), lambda t: CDP.PosetName(t[0]))
    # load_poset = sp(LOAD - name_poset, lambda t: CDP.LoadPoset(t[0], t[1]))

    parse_wrap_check('load foo', Syntax.load_poset,
                     CDP.LoadPoset(CDP.LoadKeyword('load'), CDP.PosetName('foo')))


@comptest
def check_syntax_load2():
    parse_wrap_check('`foo', Syntax.load_poset,
                     CDP.LoadPoset(CDP.LoadKeyword('`'), CDP.PosetName('foo')))


@comptest
def check_syntax_load3():
    parse_wrap_check('`foo : bar', Syntax.constant_value)

    parse_wrap_check('`foo : bar', Syntax.rvalue)
    parse_wrap_check('`foo : bar', Syntax.fvalue)


@comptest
def check_syntax_load4():
    parse_wrap_check('solve( 0 g, `model )', Syntax.constant_value)

    eval_rvalue_as_constant('solve ( 0 g, mcdp { provides f <= 10g} ) ')

@comptest
def check_syntax_load5():

    parse_wrap_check("code mcdp_posets.Int()", Syntax.code_spec)
    parse_wrap_check("code mcdp_posets.Int()", Syntax.space)

@comptest
def check_syntax_load6():
    parse_wrap_check("$", Syntax.space)
    parse_wrap_check("Top $", Syntax.constant_value)
    try:
        parse_wrap_check("Top$", Syntax.constant_value)
    except TestFailed:
        pass

    parse_wrap_check("approx(cost,0%,1$,Top $) mcdp {} ", Syntax.ndpt_approx)
    try:
        parse_wrap_check("approx(cost,0%,1$,Top$) mcdp {} ", Syntax.ndpt_approx)
    except TestFailed:
        pass
    pass
