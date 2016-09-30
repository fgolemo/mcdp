# -*- coding: utf-8 -*-
""" Contains the main parsing interface """
from contracts import contract
from mcdp_dp import PrimitiveDP
from mcdp_posets import Poset
from mocdp.exceptions import MCDPExceptionWithWhere

from .parse_actions import parse_wrap


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
    from mcdp_lang.eval_ndp_imp import eval_ndp
    from mocdp.comp.interfaces import NamedDP

    v = parse_wrap(Syntax.ndpt_dp_rvalue, string)[0]

    if context is None:
        context = Context()

    res = eval_ndp(v, context)
    # I'm not sure what happens to the context
    # if context.names # error ??

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
        raise e.with_filename(filename)

@contract(returns=Poset)
def parse_poset(string, context=None):
    from mocdp.comp.context import Context
    from mcdp_lang.syntax import Syntax
    from mcdp_lang.eval_space_imp import eval_space

    v = parse_wrap(Syntax.space, string)[0]

    if context is None:
        context = Context()

    res = eval_space(v, context)

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
    from mocdp.comp.context import ValueWithUnits
    from mcdp_lang.eval_constant_imp import eval_constant
    from mocdp.comp.context import Context

    expr = Syntax.rvalue
    x = parse_wrap(expr, string)[0]

    if context is None:
        context = Context()

    result = eval_constant(x, context)

    assert isinstance(result, ValueWithUnits)
    value = result.value
    space = result.unit
    space.belongs(value)

    return result

@contract(returns='isinstance(TemplateForNamedDP)')
def parse_template(string, context=None):
    from mcdp_lang.syntax import Syntax
    from mocdp.comp.context import Context
    from mcdp_lang.eval_template_imp import eval_template
    from mocdp.comp.template_for_nameddp import TemplateForNamedDP

    expr = Syntax.template
    x = parse_wrap(expr, string)[0]

    if context is None:
        context = Context()

    result = eval_template(x, context)

    assert isinstance(result, TemplateForNamedDP)
    return result
