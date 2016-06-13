from comptests.registrar import comptest
from mcdp_lang.parts import CDPLanguage
from mcdp_lang.tests.utils import parse_wrap_check
from mcdp_lang.syntax import Syntax
from mcdp_lang.tests.utils2 import eval_rvalue_as_constant

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

    eval_rvalue_as_constant('solve ( <0 g>, mcdp { provides f <= 10g} ) ')

@comptest
def check_syntax_load5():
    pass

@comptest
def check_syntax_load6():
    pass
