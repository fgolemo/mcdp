
""" Contains the main parsing interface """
import os
from mcdp_lang.parse_actions import parse_wrap
from mcdp_posets.poset import Poset
from mocdp.exceptions import DPSemanticError, DPSyntaxError

__all__ = [
    'parse_ndp',
    'parse_ndp_filename',
    'parse_poset',

]

def parse_ndp(string, context=None):
    from mocdp.comp.context import Context
    from mcdp_lang.syntax import Syntax
    from mcdp_lang.eval_mcdp_type_imp import eval_dp_rvalue
    from mocdp.comp.interfaces import NamedDP

    if os.path.exists(string):
        raise ValueError('expected string, not filename :%s' % string)

    v = parse_wrap(Syntax.ndpt_dp_rvalue, string)[0]

    if context is None:
        context = Context()

    res = eval_dp_rvalue(v, context)
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
    except (DPSyntaxError, DPSemanticError) as e:
        raise e.with_filename(filename)

def parse_poset(string, context=None):
    from mocdp.comp.context import Context
    from mcdp_lang.syntax import Syntax
    from mcdp_lang.eval_space_imp import eval_space

    if os.path.exists(string):
        raise ValueError('expected string, not filename :%s' % string)

    v = parse_wrap(Syntax.space_expr, string)[0]

    if context is None:
        context = Context()

    res = eval_space(v, context)

    assert isinstance(res, Poset), res
    return res
