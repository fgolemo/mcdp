# -*- coding: utf-8 -*-
from mcdp_lang.parse_actions import parse_wrap
from mocdp.comp.context import Context
from mcdp_lang.eval_constant_imp import eval_constant
from mcdp_lang.syntax import Syntax
from mcdp_posets.types_universe import express_value_in_isomorphic_space


def eval_rvalue_as_constant(s):
    """ Parses as an rvalue (resource) and evaluates as a constant value.
        Returns ValueWithUnit. """
    parsed = parse_wrap(Syntax.rvalue, s)[0]
    context = Context()
    return eval_constant(parsed, context)


def eval_rvalue_as_constant_same(s1, s2):
    """ 
        Checks that the two strings evaluate to the same constant.
        
        
        Example:
            
            
            eval_rvalue_as_constant_same("1 g + 1 kg", "1001 g")
            
    """

    p1 = eval_rvalue_as_constant(s1)
    p2 = eval_rvalue_as_constant(s2)


    v2 = express_value_in_isomorphic_space(p2.unit, p2.value, p1.unit)

    print('Converted: %s' % p1.unit.format(v2))

    p1.unit.check_equal(p1.value, v2)
