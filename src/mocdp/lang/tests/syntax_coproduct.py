from mocdp.lang.tests.utils import parse_wrap_check
from mocdp.lang.syntax import Syntax
from comptests.registrar import comptest

@comptest
def check_coproducts1():
    parse_wrap_check('a ^ b', Syntax.dp_rvalue)
