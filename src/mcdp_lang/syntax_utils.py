from contracts import contract
from mcdp_lang.parts import CDPLanguage
from pyparsing import Literal, Optional, Suppress

CDP = CDPLanguage

def sp(a, b):
    from mcdp_lang.parse_actions import spa
    spa(a, b)
    return a


# shortcuts
S = Suppress
L = Literal
O = Optional
SLPAR = S(L('('))
SRPAR = S(L(')'))
COMMA = sp(L(','), lambda t: CDP.comma(t[0]))
SCOMMA = S(COMMA)
SCOLON = S(L(':'))


@contract(literal=str)
def simple_keyword_literal(literal, klass):
    return sp(L(literal), lambda t: klass(t[0]))

def VariableRef_make(t):
    name = t[0]
    if not isinstance(name, (str, unicode)):
        raise ValueError(t)

    res = CDPLanguage.VariableRef(name)
    return res
