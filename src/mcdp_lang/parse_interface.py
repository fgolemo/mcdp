# -*- coding: utf-8 -*-
""" Contains the main parsing interface """
import sys

from contracts import contract
from mcdp_dp import PrimitiveDP
from mcdp_posets import Poset
from mocdp import logger
from mocdp.exceptions import MCDPExceptionWithWhere

from .parse_actions import parse_wrap
from mcdp_lang.refinement import apply_refinement


__all__ = [
    'parse_ndp',
    'parse_ndp_filename',
    'parse_poset',
    'parse_primitivedp',
    'parse_constant',
    'parse_template',
]

def parse_ndp(string, context=None):
    from mocdp.comp.context import Context
    from mcdp_lang.syntax import Syntax
    from mocdp.comp.interfaces import NamedDP

    if context is None:
        context = Context()
    
    expr = parse_wrap(Syntax.ndpt_dp_rvalue, string)[0]
    expr2 = parse_ndp_refine(expr, context)
    res = parse_ndp_eval(expr2)
    assert isinstance(res, NamedDP), res
    return res

def parse_ndp_refine(v, context):
    v2 = apply_refinement(v, context)
    return v2

def parse_ndp_eval(v, context=None):
    from mcdp_lang.eval_ndp_imp import eval_ndp
    from mocdp.comp.context import Context
    from mocdp.comp.interfaces import NamedDP

    if context is None:
        context = Context()
    res = eval_ndp(v, context)
    assert isinstance(res, NamedDP), res
    return res
    

def parse_ndp_filename(filename, context=None):
    """ Reads the file and returns as NamedDP.
        The exception are annotated with filename. """
    with open(filename) as f:
        contents = f.read()
    try:
        return parse_ndp(contents, context)
    except MCDPExceptionWithWhere as e:
        active = True
        if active:
# http://stackoverflow.com/questions/1350671/inner-exception-with-traceback-in-python
            e = e.with_filename(filename)
            raise type(e), e.args, sys.exc_info()[2]
        else:
            logger.debug('Deactivated trace in parse_ndp_filename().')
            raise

@contract(returns=Poset)
def parse_poset(string, context=None):
    from mocdp.comp.context import Context
    from .syntax import Syntax

    if context is None:
        context = Context()

    v = parse_wrap(Syntax.space, string)[0]

    v2 = parse_poset_refine(v, context)
    res = parse_poset_eval(v2, context)
    return res 

def parse_poset_refine(x, context):  # @UnusedVariable
    return x

def parse_poset_eval(x, context):
    from .eval_space_imp import eval_space
    res = eval_space(x, context)
    assert isinstance(res, Poset), res
    return res

@contract(returns=PrimitiveDP)
def parse_primitivedp(string, context=None):
    from mocdp.comp.context import Context
    from mcdp_lang.syntax import Syntax
    from mcdp_lang.eval_primitivedp_imp import eval_primitivedp

    v = parse_wrap(Syntax.primitivedp_expr, string)[0]

    if context is None:
        context = Context()

    res = eval_primitivedp(v, context)

    assert isinstance(res, PrimitiveDP), res
    return res

@contract(returns='isinstance(ValueWithUnits)')
def parse_constant(string, context=None):
    from mcdp_lang.syntax import Syntax
    from mocdp.comp.context import Context

    expr = Syntax.rvalue
    x = parse_wrap(expr, string)[0]

    if context is None:
        context = Context()
    x = parse_constant_refine(x, context)
    res = parse_constant_eval(x, context)

    return res

def parse_constant_refine(x, context):  # @UnusedVariable
    return x

def parse_constant_eval(x, context):
    from mocdp.comp.context import ValueWithUnits
    from mcdp_lang.eval_constant_imp import eval_constant
    result = eval_constant(x, context)
    assert isinstance(result, ValueWithUnits)
    value = result.value
    space = result.unit
    space.belongs(value)
    
@contract(returns='isinstance(TemplateForNamedDP)')
def parse_template(string, context=None):
    from mcdp_lang.syntax import Syntax
    from mocdp.comp.context import Context

    if context is None:
        context = Context()

    expr = Syntax.template
    x = parse_wrap(expr, string)[0]
    x = parse_template_refine(x, context)
    res = parse_template_eval(x)
    return res

def parse_template_refine(x, context):  # @UnusedVariable
    return x
    
def parse_template_eval(x, context):
    from mcdp_lang.eval_template_imp import eval_template
    from mocdp.comp.template_for_nameddp import TemplateForNamedDP
    result = eval_template(x, context)
    assert isinstance(result, TemplateForNamedDP)
    return result
 
