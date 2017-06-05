# -*- coding: utf-8 -*-
""" Contains the main parsing interface """
import sys
import traceback

from contracts import contract
from contracts.utils import check_isinstance, indent

from mcdp import logger
from mcdp.exceptions import MCDPExceptionWithWhere, DPInternalError,\
    DPSemanticError
from mcdp_dp import PrimitiveDP
from mcdp_posets import Poset

from .parse_actions import parse_wrap
from .refinement import apply_refinement
from mcdp_lang.namedtuple_tricks import recursive_print


__all__ = [
    'parse_ndp',
    'parse_ndp_filename',
    'parse_poset',
    'parse_primitivedp',
    'parse_constant',
    'parse_template',
]

def decorator_check_exception_where_is_string(f):
    ''' Checks that if a DPSemanticError is thrown, it
        has a reference to the current string being parsed.
        
        f(string, context)
    '''
    def parse(string, context=None):
        try:
            return f(string, context)
        except DPSemanticError as e:
            if e.where is not None:
                if e.where.string != string:
                    msg = 'I expected this error to refer to somewhere in this string.'
                    msg += '\n string: %r' % string
                    msg += '\n e.where.string: %r' % e.where.string
                    msg += '\n' + indent(traceback.format_exc(e), 'e > ')
                    raise DPInternalError(msg)
            raise
    return parse

@decorator_check_exception_where_is_string
def parse_ndp(string, context=None):
    from mocdp.comp.context import Context
    from .syntax import Syntax
    from mocdp.comp.interfaces import NamedDP

    if context is None:
        context = Context()
    
    expr = parse_wrap(Syntax.ndpt_dp_rvalue, string)[0]
    #logger.debug('TMP:\n'+ recursive_print(expr))
    expr2 = parse_ndp_refine(expr, context)
    #logger.debug('TMP:\n'+ recursive_print(expr2))
    res = parse_ndp_eval(expr2, context)
    assert isinstance(res, NamedDP), res
    
    return res

def standard_refine(v, context):
    v2 = apply_refinement(v, context)
    return v2

parse_ndp_refine = standard_refine
parse_poset_refine = standard_refine
parse_constant_refine = standard_refine
parse_dp_refine = standard_refine
parse_template_refine = standard_refine
parse_primitivedp_refine = standard_refine

def parse_ndp_eval(v, context):
    from .eval_ndp_imp import eval_ndp
    from mocdp.comp.interfaces import NamedDP
    
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
        else: # pragma: no cover
            logger.debug('Deactivated trace in parse_ndp_filename().')
            raise

@contract(returns=Poset)
@decorator_check_exception_where_is_string
def parse_poset(string, context=None):
    from mocdp.comp.context import Context
    from .syntax import Syntax

    v = parse_wrap(Syntax.space, string)[0]
    
    if context is None:
        context = Context()
    
    v2 = parse_poset_refine(v, context)
    res = parse_poset_eval(v2, context)
    
    return res 

def parse_poset_eval(x, context):
    from .eval_space_imp import eval_space
    res = eval_space(x, context)
    check_isinstance(res, Poset)
    return res

@contract(returns=PrimitiveDP)
@decorator_check_exception_where_is_string
def parse_primitivedp(string, context=None):
    from mocdp.comp.context import Context
    from mcdp_lang.syntax import Syntax

    v = parse_wrap(Syntax.primitivedp_expr, string)[0]

    if context is None:
        context = Context()

    v2 = parse_primitivedp_refine(v, context)
    res = parse_primitivedp_eval(v2, context)
    return res 

def parse_primitivedp_eval(x, context):
    from mcdp_lang.eval_primitivedp_imp import eval_primitivedp
    res = eval_primitivedp(x, context)
    check_isinstance(res, PrimitiveDP)
    return res

@contract(returns='isinstance(ValueWithUnits)')
@decorator_check_exception_where_is_string
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

def parse_constant_eval(x, context):
    from mocdp.comp.context import ValueWithUnits
    from mcdp_lang.eval_constant_imp import eval_constant
    result = eval_constant(x, context)
    assert isinstance(result, ValueWithUnits)
    value = result.value
    space = result.unit
    space.belongs(value)
    return result
    
@contract(returns='isinstance(TemplateForNamedDP)')
@decorator_check_exception_where_is_string
def parse_template(string, context=None):
    from mcdp_lang.syntax import Syntax
    from mocdp.comp.context import Context

    if context is None:
        context = Context()

    expr = Syntax.template
    x = parse_wrap(expr, string)[0]
    x = parse_template_refine(x, context)
    res = parse_template_eval(x, context)
    return res

def parse_template_eval(x, context):
    from mcdp_lang.eval_template_imp import eval_template
    from mocdp.comp.template_for_nameddp import TemplateForNamedDP
    result = eval_template(x, context)
    assert isinstance(result, TemplateForNamedDP)
    return result
 
