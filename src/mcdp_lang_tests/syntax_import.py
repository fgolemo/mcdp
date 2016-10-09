from comptests.registrar import comptest
from mcdp_lang.parts import CDPLanguage
from mcdp_lang.syntax import Syntax
from .utils import parse_wrap_check


CDP = CDPLanguage

@comptest
def syntax_import1():
    """ syntax for posets """
    m = parse_wrap_check("`poset", Syntax.load_poset)
    assert isinstance(m, CDP.LoadPoset)
    assert isinstance(m.load_arg, CDP.PosetName)
    assert m.load_arg.value == 'poset'

    m = parse_wrap_check("`library.poset", Syntax.load_poset)
    assert isinstance(m.load_arg, CDP.PosetNameWithLibrary)
    assert m.load_arg.library.value == 'library'
    assert m.load_arg.name.value == 'poset'

@comptest
def syntax_import2():
    """ syntax for ndps """
    m = parse_wrap_check("`model", Syntax.ndpt_load)
    assert isinstance(m, CDP.LoadNDP)
    assert isinstance(m.load_arg, CDP.NDPName)
    assert m.load_arg.value == 'model'

    m = parse_wrap_check("`library.model", Syntax.ndpt_load)
    assert isinstance(m.load_arg, CDP.NDPNameWithLibrary)
    assert m.load_arg.library.value == 'library'
    assert m.load_arg.name.value == 'model'

@comptest
def syntax_import3():
    pass

@comptest
def syntax_import4():
    pass

@comptest
def syntax_import5():
    pass

@comptest
def syntax_import6():
    pass

@comptest
def syntax_import7():
    pass

@comptest
def syntax_import8():
    pass

@comptest
def syntax_import9():
    pass
