# -*- coding: utf-8 -*-
from contracts.utils import check_isinstance

from .parts import CDPLanguage
from .pyparsing_bundled import Keyword, Literal, Optional, Suppress


CDP = CDPLanguage

def sp(a, b):
    from .parse_actions import spa
    spa(a, b)
    return a

def spk(a, part):
    """ Simple keyword literal """
    from .parse_actions import spa
    spa(a, lambda t: part(t[0]))
    return a

def keyword(a, part):
    """ 
        a must be a string
        
        we create Keyword(a)
    """
    check_isinstance(a, str)

    a = Keyword(a)
    from .parse_actions import spa
    spa(a, lambda t: part(t[0]))
    return a


# shortcuts
S = Suppress
L = Literal
O = Optional
LPAR = L('(')
RPAR = L(')')
SLPAR = S(LPAR)
SRPAR = S(RPAR)
COMMA = sp(L(','), lambda t: CDP.comma(t[0]))
SCOMMA = S(COMMA)
SCOLON = S(L(':'))

