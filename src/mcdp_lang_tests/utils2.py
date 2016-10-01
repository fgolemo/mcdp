# -*- coding: utf-8 -*-
from mcdp_lang.eval_resources_imp import eval_rvalue
from mcdp_lang.parse_actions import parse_wrap
from mcdp_lang.syntax import Syntax
from mcdp_posets import express_value_in_isomorphic_space
from mocdp.comp.context import Context
from mocdp.comp.context_eval_as_constant import (can_resource_be_constant,
    eval_constant_resource)


def parse_as_rvalue(s):
    """ returns rvalue, context """
    parsed = parse_wrap(Syntax.rvalue, s)[0]
    context = Context()
    r = eval_rvalue(parsed, context)
    return r, context


def eval_rvalue_as_constant(s):
    """ Parses as an rvalue (resource) and evaluates as a constant value.
        Returns ValueWithUnit. """
    parsed = parse_wrap(Syntax.rvalue, s)[0]
    context = Context()
    from mcdp_lang.eval_constant_imp import eval_constant
    value = eval_constant(parsed, context)
    return value

def eval_rvalue_as_constant2(s):
    """ Parses as an rvalue (resource) and evaluates as a constant value.
        Returns ValueWithUnit. """
    r, context = parse_as_rvalue(s)
    assert can_resource_be_constant(context, r)
    value = eval_constant_resource(context, r)
    return value

def eval_rvalue_as_constant_same_exactly(s1, s2):
    """ 
        Checks that the two strings evaluate to the same constant
        considering equivalent types to be different.
    """

    p1 = eval_rvalue_as_constant2(s1)
    p2 = eval_rvalue_as_constant2(s2)
    print('Checking that %s === %s' % (p1, p2))

    assert p1.unit == p2.unit, (p1, p2)
    p1.unit.check_equal(p1.value, p2.value)

def eval_rvalue_as_constant_same(s1, s2):
    """ 
        Checks that the two strings evaluate to the same constant.
        (up to conversions)
        
        Example:
            
            eval_rvalue_as_constant_same("1 g + 1 kg", "1001 g")
            
    """

    p1 = eval_rvalue_as_constant2(s1)
    p2 = eval_rvalue_as_constant2(s2)

    v2 = express_value_in_isomorphic_space(p2.unit, p2.value, p1.unit)

    # print('Converted: %s' % p1.unit.format(v2))

    p1.unit.check_equal(p1.value, v2)
    print('Found that %s == %s' % (p1, p2))
# 
# 
# @contextmanager
# def check_properties(s):
#     """ Prints s if there is an exception """
#     try:
#         yield
#     except Exception as e:
#         msg = ''
#         from mcdp_lang.namedtuple_tricks import recursive_print
#         s = recursive_print(s)
#         raise_wrapped(Exception, e, msg, object=s)
