# -*- coding: utf-8 -*-
from mcdp_lang.parse_actions import parse_wrap
from mocdp.comp.context import Context
from mcdp_lang.eval_constant_imp import eval_constant
from mcdp_lang.syntax import Syntax


def eval_rvalue_as_constant(s):
    """ Parses as an rvalue (resource) and evaluates as a constant value.
        Returns ValueWithUnit. """
    parsed = parse_wrap(Syntax.rvalue, s)[0]
    context = Context()
    return eval_constant(parsed, context)
