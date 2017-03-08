# -*- coding: utf-8 -*-
from contextlib import contextmanager
import sys
import traceback

from decorator import decorator
from nose.tools import assert_equal

from contracts import contract
from contracts.utils import raise_desc, raise_wrapped, check_isinstance
from mcdp_utils_misc.timing import timeit
from mcdp_lang_utils import Where, line_and_col, location
from mcdp import logger, MCDPConstants
from mcdp.exceptions import (DPInternalError, DPSemanticError, DPSyntaxError,
                              MCDPExceptionWithWhere)

from .fix_whitespace_imp import fix_whitespace
from .namedtuple_tricks import get_copy_with_where, recursive_print
from .parts import CDPLanguage
from .pyparsing_bundled import ParseException, ParseFatalException
from .utils import isnamedtupleinstance, parse_action
from .utils_lists import make_list, unwrap_list
from .find_parsing_el import find_parsing_element
from mcdp.development import mcdp_dev_warning, do_extra_checks


CDP = CDPLanguage

def copy_expr_remove_action(expr):
    """ Use this instead of copy() """
    e2 = expr.copy()
    e2.parseAction = []
    return e2

@decorator
def decorate_add_where(f, *args, **kwargs):
    where = args[0].where
    try:
        return f(*args, **kwargs)
    except MCDPExceptionWithWhere as e:
        _, _, tb = sys.exc_info()
        raise_with_info(e, where, tb)
    except Exception as e:
        msg = 'Unexpected exception while executing %s.' % f.__name__
        if args and isnamedtupleinstance(args[0]):
            r = recursive_print(args[0])
        else:
            r = 'unavailable'
        raise_wrapped(DPInternalError, e, msg, exc=sys.exc_info(), r=r)


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
            if e.where is None:
                e.where = where
                raise DPSyntaxError(str(e), where=where)
            else:
                raise
        except DPSemanticError as e:
            if e.where is None:
                raise DPSemanticError(str(e), where=where)
            else:
                raise
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
        #print('spa(): parsing %s %r %r %r ' % (x, tokens, loc, s))
        res = bb(tokens, loc, s)
        # if we are here, then it means the parse was successful
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
    
    a = x.parseAction
    if a != []:
        msg = 'This parsing expression already had a parsing element'
        raise_desc(DPInternalError, msg, x=x, new_action=b)
    
    x.setParseAction(p)

@parse_action
def dp_model_statements_parse_action(tokens):
    line_exprs = list(tokens)
    return CDP.ModelStatements(make_list(line_exprs))


def add_where_to_empty_list(result_of_function_above):
    r = result_of_function_above
    check_isinstance(r, CDP.ModelStatements)
    ops = unwrap_list(r.statements)
    if len(ops) == 0:
        l = make_list(ops, where=r.where)
        res = CDP.ModelStatements(l, where=r.where)
        return res
    else:
        return r


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
# 
# 
# def get_token_of_class(tokens, klass):
#     """ Returns the lpar instance if it exists, or None.
#         It also removes it from the list. """
#     for i, _ in enumerate(tokens):
#         if isinstance(_, klass):
#             return tokens.pop(i)
#     return None

@parse_action
def space_product_parse_action(tokens):
    tokens = list(tokens[0])
#     if '(' in tokens: tokens.remove('(')
#     if ')' in tokens: tokens.remove(')')
#     lpar = get_token_of_class(tokens, CDP.LPAR)
#     rpar = get_token_of_class(tokens, CDP.RPAR)
    lpar = None
    rpar = None
    ops = make_list(tokens)
    return CDP.SpaceProduct(lpar=lpar, ops=ops, rpar=rpar, where=ops.where)


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

def translate_where(where0, string):
    """ 
        Take the first where; compute line, col according to where0.string,
        and find out the corresponding chars in the second string.
        
        This assumes that string and where0.string have the same number of lines.
    """
    
    nlines = len(string.split('\n'))
    nlines0 = len(where0.string.split('\n'))
    if nlines != nlines0:
        msg = 'I expected they have the same lines.'
        msg += '\n         string (%d lines): %r' % (nlines, string)
        msg += '\n  where0.string (%d lines): %r' % (nlines0, where0.string)
        raise_desc(DPInternalError, msg)
    
    string0 = where0.string
    line, col = line_and_col(where0.character, string0)
    character2 = location(line, col, string)
    
    if where0.character_end is None:
        character_end2 = None
    else:
        line, col = line_and_col(where0.character_end, string0)
        character_end2 = location(line, col, string) 
    
    where = Where(string=string, character=character2, character_end=character_end2)
    return where

def parse_wrap(expr, string):
    from .refinement import namedtuple_visitor_ext
    
    if isinstance(string, unicode):
        msg = 'The string is unicode. It should be a str with utf-8 encoding.'
        msg += '\n' + string.encode('utf-8').__repr__()
        raise ValueError(msg)
    
    check_isinstance(string, bytes)

    # Nice trick: the remove_comments doesn't change the number of lines
    # it only truncates them...
    
    string0 = remove_comments(string)
    
    if not string0.strip():
        msg = 'Nothing to parse.'
        where = Where(string, character=len(string))
        raise DPSyntaxError(msg, where=where)

    try:
        try:
            w = str(find_parsing_element(expr))
        except ValueError:
            w = '(unknown)'
            
        with timeit(w, MCDPConstants.parsing_too_slow_threshold):
            expr.parseWithTabs()
            
            parsed = expr.parseString(string0, parseAll=True)  # [0]
            def transform(x, parents):  # @UnusedVariable
                if x.where is None: # pragma: no cover
                    msg = 'Where is None for this element'
                    raise_desc(DPInternalError, msg, x=recursive_print(x),
                               all=recursive_print(parsed[0]))
                    
                where = translate_where(x.where, string)
                return get_copy_with_where(x, where)
            
            parsed_transformed = namedtuple_visitor_ext(parsed[0], transform)

            if hasattr(parsed_transformed, 'where'):            
                # could be an int, str
                assert_equal(parsed_transformed.where.string, string)
            
            res = fix_whitespace(parsed_transformed)
            return [res]
          
    except (ParseException, ParseFatalException) as e:
        where1 = Where(string0, e.loc)
        where2 = translate_where(where1, string)
        s0 = e.__str__()
        check_isinstance(s0, bytes)
        s = s0
        e2 = DPSyntaxError(s, where=where2)
        raise DPSyntaxError, e2.args, sys.exc_info()[2]
         
    except DPSemanticError as e:
        msg = 'This should not throw a DPSemanticError'
        raise_wrapped(DPInternalError, e, msg, exc=sys.exc_info()) 


def remove_comments(s):
    lines = s.split("\n")
    def remove_comment(line):
        if '#' in line:
            return line[:line.index('#')]
        else:
            return line
    return "\n".join(map(remove_comment, lines))


def parse_line(line):
    from .syntax import Syntax
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
    pint_string = " ".join(tokens) #_.encode('utf-8') for _ in tokens)
    return CDP.RcompUnit(pint_string)


def integer_fraction_from_superscript(x):
    w = None
    replacements = {
    '¹': CDP.IntegerFraction(num=1, den=1, where=w),
    '²': CDP.IntegerFraction(num=2, den=1, where=w),
    '³': CDP.IntegerFraction(num=3, den=1, where=w),
    '⁴': CDP.IntegerFraction(num=4, den=1, where=w),
    '⁵': CDP.IntegerFraction(num=5, den=1, where=w),
    '⁶': CDP.IntegerFraction(num=6, den=1, where=w),
    '⁷': CDP.IntegerFraction(num=7, den=1, where=w),
    '⁸': CDP.IntegerFraction(num=8, den=1, where=w),
    '⁹': CDP.IntegerFraction(num=9, den=1, where=w),
    }   
    return replacements[x]
