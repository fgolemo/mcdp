from .parts import CDPLanguage
from .syntax import SyntaxBasics, SyntaxIdentifiers
from .syntax_utils import L, O, S, SCOMMA, SLPAR, SRPAR, sp
from .utils_lists import make_list
from pyparsing import (
    CaselessLiteral, Combine, Forward, Group, Keyword, Literal, MatchFirst,
    NotAny, OneOrMore, Optional, Or, ParserElement, Suppress, Word, ZeroOrMore,
    alphanums, alphas, dblQuotedString, nums, oneOf, opAssoc, operatorPrecedence,
    sglQuotedString)

CDP = CDPLanguage



def get_code_spec_expr():
    """
        Examples:
            code my.python.function
            code my.python.function(a=1,b=2,...)
        
        For now, the value of the arguments are only integers or float.
    
        Evaluates to either CDP.CodeSpecNoArgs or CDP.CodeSpec.
    """

    return SyntaxCodeSpec.code_spec


class SyntaxCodeSpec():
    CODE = sp(L('code'), lambda t: CDP.CodeKeyword(t[0]))

    # Code specs
    # code my.module(a=1, b=2)
    # "idn" does not match keywords, but keywords might appear in functions names
    idn_ext = Combine(oneOf(list(alphas)) + Optional(Word('_' + alphanums)))
    funcname = sp(Combine(idn_ext + ZeroOrMore(L('.') - idn_ext)),
                   lambda t: CDP.FuncName(t[0]))

    code_spec_simple = sp(CODE + funcname,
                          lambda t: CDP.CodeSpecNoArgs(keyword=t[0], function=t[1]))

    arg_value = SyntaxBasics.integer_or_float
    arg_name = sp(SyntaxIdentifiers.get_idn(), lambda t: CDP.ArgName(t[0]))
    arg_pair = arg_name + S(L('=')) + arg_value
    arguments_spec = sp(O(arg_pair) + ZeroOrMore(SCOMMA + arg_pair),
                        lambda t: make_list(list(t)))
    code_spec_with_args = sp(CODE + funcname + SLPAR + arguments_spec + SRPAR,
                   lambda t: CDP.CodeSpec(keyword=t[0], function=t[1], arguments=t[2]))
    code_spec = code_spec_with_args ^ code_spec_simple

