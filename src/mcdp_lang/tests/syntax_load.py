from comptests.registrar import comptest
from mcdp_lang.parts import CDPLanguage
from mcdp_lang.tests.utils import parse_wrap_check
from mcdp_lang.syntax import Syntax

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
    pass


@comptest
def check_syntax_load4():
    pass


@comptest
def check_syntax_load5():
    pass

@comptest
def check_syntax_load6():
    pass
