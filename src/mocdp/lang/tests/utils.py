from contracts import contract
from contracts.utils import raise_desc, raise_wrapped
from mocdp.comp.interfaces import NamedDP
from mocdp.comp.wrap import SimpleWrap
from mocdp.exceptions import DPSyntaxError
from mocdp.lang.blocks import DPSemanticError
from mocdp.lang.syntax import parse_ndp, parse_wrap


def assert_syntax_error(s, expr, desc=None):
    try:
        res = parse_wrap(expr, s)
    except DPSyntaxError:
        pass
    except BaseException as e:
        msg = "Expected syntax error, got %s." % type(e)
        raise_wrapped(Exception, e, msg, s=s)
    else:
        msg = "Expected an exception, instead succesfull instantiation."
        if desc:
            msg += '\n' + desc
        raise_desc(Exception, msg, s=s, res=res.repr_long())


def assert_semantic_error(s , desc=None):
    """ This asserts that s can be parsed, but cannot  be compiled to a *connected* ndp. """
    try:
        res = parse_ndp(s)
        res.abstract()
    except DPSemanticError:
        pass
    except BaseException as e:
        msg = "Expected semantic error, got %s." % type(e)
        raise_wrapped(Exception, e, msg, s=s)
    else:
        msg = "Expected an exception, instead succesfull instantiation."
        if desc:
            msg += '\n' + desc
        raise_desc(Exception, msg, s=s, res=res.repr_long())

@contract(returns=NamedDP)
def assert_parsable_to_unconnected_ndp(s, desc=None):
    print(desc)
    res = parse_ndp(s)
    return res

@contract(returns=NamedDP)
def assert_parsable_to_connected_ndp(s , desc=None):
    """ This asserts that s can be compiled to a *connected* ndp. """
    print(desc)
    res = parse_ndp(s)
    if isinstance(res, SimpleWrap):
        return res
    ndp = res.abstract()
    return ndp
#         try:
#
#     except DPSemanticError:
#         pass
#     except BaseException as e:
#         msg = "Expected semantic error, got %s." % type(e)
#         raise_wrapped(Exception, e, msg, s=s)
#     else:
#         msg = "Expected an exception, instead succesfull instantiation."
#         if desc:
#             msg += '\n' + desc
#         raise_desc(Exception, msg, s=s, res=res.repr_long())
