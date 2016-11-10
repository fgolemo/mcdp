# -*- coding: utf-8 -*-
from contextlib import contextmanager
import sys
import traceback

from decorator import decorator

from contracts import contract
from contracts.interface import Where
from contracts.utils import indent, raise_desc, raise_wrapped, check_isinstance
from mocdp import logger
from mocdp.exceptions import (DPInternalError, DPSemanticError, DPSyntaxError,
    MCDPExceptionWithWhere, do_extra_checks, mcdp_dev_warning)

from .namedtuple_tricks import get_copy_with_where
from .parts import CDPLanguage
from .pyparsing_bundled import ParseException, ParseFatalException
from .utils import isnamedtupleinstance, parse_action
from .utils_lists import make_list


CDP = CDPLanguage
 

@decorator
def decorate_add_where(f, *args, **kwargs):
    where = args[0].where
    try:
        return f(*args, **kwargs)
    except MCDPExceptionWithWhere as e:
        _, _, tb = sys.exc_info()
        raise_with_info(e, where, tb)


@contextmanager
def add_where_information(where):
    """ Adds where field to DPSyntaxError or DPSemanticError thrown by code. """
    active = True
    if not active:
        logger.debug('Note: Error tracing disabled in add_where_information().')
        
    if not active:
        mcdp_dev_warning('add_where_information is disabled')
        yield
    else:
        try:
            yield
        except MCDPExceptionWithWhere as e:
            mcdp_dev_warning('add magic traceback handling here')
            _, _, tb = sys.exc_info()
            raise_with_info(e, where, tb)


def nice_stack(tb):
    lines = traceback.format_tb(tb)
    # remove contracts stuff
    lines = [_ for _ in lines if not '/src/contracts' in _]
    s = "".join(lines)
    import os
    curpath = os.path.realpath(os.getcwd())
    s = s.replace(curpath, '.')
    return s
    

def raise_with_info(e, where, tb):
    check_isinstance(e, MCDPExceptionWithWhere)
    existing = getattr(e, 'where', None)
    if existing: 
        raise
    use_where = existing if existing is not None else where
    error = e.error
    
    stack = nice_stack(tb)
    
    args = (error, use_where, stack)
    raise type(e), args, tb

def wheredecorator(b):
    def bb(tokens, loc, s):
        where = Where(s, loc)
        try:
            res = b(tokens)
        except DPSyntaxError as e:
            e.where = where
            raise DPSyntaxError(str(e), where=where)
        except DPSemanticError as e:
            if e.where is None:
                e.where = where
            raise DPSemanticError(str(e), where=where)
        except BaseException as e:
            raise_wrapped(DPInternalError, e, "Error while parsing.",
                          where=where.__str__(), tokens=tokens)

        if isnamedtupleinstance(res) and res.where is None:
            res = get_copy_with_where(res, where=where)

        return res
    return bb

def spa(x, b): 
    bb = wheredecorator(b)
    @parse_action
    def p(tokens, loc, s):
        # print('parsing %r %r %r ' % (tokens, loc, s))
        res = bb(tokens, loc, s)
        # if we are here, then it means the parse was succesful
        # we try again to get loc_end
        character_end = x.tryParse(s, loc)
        
        if isnamedtupleinstance(res) and \
            (res.where is None or res.where.character_end is None):
            w2 = Where(s, character=loc, character_end=character_end)
            res = get_copy_with_where(res, where=w2)

        if do_extra_checks():
            if not isinstance(res, (float, int, str)):
                if res.where is None:
                    msg = 'Found element with no where'
                    raise_desc(ValueError, msg, res=res)

            if hasattr(res, 'where'):
                assert res.where.character_end is not None, \
                    (res, isnamedtupleinstance(res))

        return res
    x.setParseAction(p)

@parse_action
@wheredecorator
def mult_parse_action(tokens):
    tokens = list(tokens[0])
    l = make_list(tokens)
    assert l.where.character_end is not None
    res = CDP.MultN(l, where=l.where)
    return res

@parse_action
@wheredecorator
def divide_parse_action(tokens):
    tokens = list(tokens[0])
    l = make_list(tokens)
    assert l.where.character_end is not None
    res = CDP.Divide(l, where=l.where)
    return res

@parse_action
@wheredecorator
def plus_parse_action(tokens):
    tokens = list(tokens[0])
    l = make_list(tokens)
    assert l.where.character_end is not None
    res = CDP.PlusN(l, where=l.where)
    return res

@parse_action
@wheredecorator
def rvalue_minus_parse_action(tokens):
    tokens = list(tokens[0])
    l = make_list(tokens)
    assert l.where.character_end is not None
    res = CDP.RValueMinusN(l, where=l.where)
    return res

@parse_action
@wheredecorator
def fvalue_minus_parse_action(tokens):
    tokens = list(tokens[0])
    l = make_list(tokens)
    assert l.where.character_end is not None
    res = CDP.FValueMinusN(l, where=l.where)
    return res

    
@parse_action
def space_product_parse_action(tokens):
    tokens = list(tokens[0])
    ops = make_list(tokens)
    return CDP.SpaceProduct(ops, where=ops.where)

@parse_action
def mult_inv_parse_action(tokens):
    tokens = list(tokens[0])
    ops = make_list(tokens)
    return CDP.InvMult(ops, where=ops.where)

@parse_action
def plus_inv_parse_action(tokens):
    tokens = list(tokens[0])
    ops = make_list(tokens)
    return CDP.InvPlus(ops, where=ops.where)

def parse_wrap_filename(expr, filename):
    with open(filename) as f:
        contents = f.read()
    try:
        return parse_wrap(expr, contents)
    except MCDPExceptionWithWhere  as e:
        raise e.with_filename(filename)

def parse_wrap(expr, string):
    if isinstance(string, unicode):
        msg = 'The string is unicode. It should be a str with utf-8 encoding.'
        msg += '\n' + string.encode('utf-8').__repr__()
        raise ValueError(msg)
    
    check_isinstance(string, str)

    # Nice trick: the removE_comments doesn't change the number of lines
    # it only truncates them...
    string0 = remove_comments(string)

    m = lambda x: x
    try:
        from mcdp_lang_tests.utils import find_parsing_element
        from mcdp_library_tests.tests import timeit
        try:
            w = str(find_parsing_element(expr))
        except ValueError:
            w = '(unknown)'
        with timeit(w, 0.5):
            return expr.parseString(string0, parseAll=True)  # [0]
    except RuntimeError as e:
        msg = 'We have a recursive grammar.'
        msg += "\n\n" + indent(m(string), '  ') + '\n'
        raise_desc(DPInternalError, msg)
    except (ParseException, ParseFatalException) as e:
        where = Where(string0, character=e.loc) # note: string0
        e2 = DPSyntaxError(str(e), where=where)
        raise DPSyntaxError, e2, sys.exc_info()[2]
    except DPSemanticError as e:
        msg = "User error while interpreting the model:"
        msg += "\n\n" + indent(m(string), '  ') + '\n'
        raise_wrapped(DPSemanticError, e, msg, compact=True)
    except DPInternalError as e:
        msg = "Internal error while evaluating the spec:"
        msg += "\n\n" + indent(m(string), '  ') + '\n'
        raise_wrapped(DPInternalError, e, msg, compact=False)

def remove_comments(s):
    lines = s.split("\n")
    def remove_comment(line):
        if '#' in line:
            return line[:line.index('#')]
        else:
            return line
    return "\n".join(map(remove_comment, lines))

def parse_line(line):
    from mcdp_lang.syntax import Syntax
    return parse_wrap(Syntax.line_expr, line)[0]

@contract(name= CDP.DPName)
def funshortcut1m(provides, fnames, prep_using, name):
    return CDP.FunShortcut1m(provides=provides,
                             fnames=fnames,
                             prep_using=prep_using,
                             name=name)
@contract(name=CDP.DPName)
def resshortcut1m(requires, rnames, prep_for, name):
    return CDP.ResShortcut1m(requires=requires, rnames=rnames, 
                             prep_for=prep_for, name=name)

def parse_pint_unit(tokens):
    tokens = list(tokens)
    pint_string = " ".join(tokens)
    return CDP.RcompUnit(pint_string)

