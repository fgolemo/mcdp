# -*- coding: utf-8 -*-
from .namedtuple_tricks import get_copy_with_where
from .parts import CDPLanguage
from .utils import isnamedtupleinstance, parse_action
from .utils_lists import make_list
from contextlib import contextmanager
from contracts import contract
from contracts.interface import Where
from contracts.utils import indent, raise_desc, raise_wrapped
from mocdp.exceptions import (DPInternalError, DPSemanticError, DPSyntaxError,
    MCDPExceptionWithWhere, mcdp_dev_warning)
from pyparsing import ParseException, ParseFatalException

CDP = CDPLanguage

@contextmanager
def add_where_information(where):
    """ Adds where field to DPSyntaxError or DPSemanticError thrown by code. """
    active = True
    if not active:
        yield
    else:
        try:
            yield
        except DPInternalError as e:
            raise
        except MCDPExceptionWithWhere as e:
            mcdp_dev_warning('add magic traceback handling here')
            existing = getattr(e, 'where', None)
            use_where = existing if existing is not None else where
            e = type(e)(e.error, where=use_where)
            raise e

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

        if isnamedtupleinstance(res) and res.where is None:  # or isinstance(res, ValueWithUnits):
            res = get_copy_with_where(res, where=where)

        return res
    return bb

def spa(x, b):
    @parse_action
    def p(tokens, loc, s):
        bb = wheredecorator(b)
        res = bb(tokens, loc, s)
        # if we are here, then it means the parse was succesful
        # we try again

        # not this, it would be recursive
        # x.parseString(s[loc:])

        x2 = x.copy()
        x2.setParseAction()
        # a = x2.parseString(s[loc:])
        loc_end, tokens = x2._parse(s[loc:], 0)
        character_end = loc + loc_end

        if isnamedtupleinstance(res) and (res.where is None or res.where.character_end is None):
            w2 = Where(s, character_end=character_end, character=loc)
            res = get_copy_with_where(res, where=w2)

        if not isinstance(res, (float, int, str)):
            if res.where is None:
                msg = 'Found element with no where'
                raise_desc(ValueError, msg, res=res)

        if hasattr(res, 'where'):
            assert res.where.character_end is not None, (res, isnamedtupleinstance(res))

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
def coprod_parse_action(tokens):
    tokens = list(tokens[0])
    l = make_list(tokens)
    assert l.where.character_end is not None
    res = CDP.Coproduct(l, where=l.where)
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
    # Nice trick: the removE_comments doesn't change the number of lines
    # it only truncates them...
    string0 = remove_comments(string)

#     print('parsing string0 %s %r %s' % (string0, string0, type(string0)))
    # m = boxit
    m = lambda x: x
    try:
        return expr.parseString(string0, parseAll=True)  # [0]
    except (ParseException, ParseFatalException) as e:
        # ... so we can use "string" here.
        where = Where(string, line=e.lineno, column=e.col)
        raise DPSyntaxError(str(e), where=where)
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
    return CDP.ResShortcut1m(requires=requires, rnames=rnames, prep_for=prep_for, name=name)

def parse_pint_unit(tokens):
    tokens = list(tokens)
    pint_string = " ".join(tokens)
    # print 'parse_pint_unit, tokens = %s, pint_string = %s' % (tokens, pint_string)

    # return CDP.Unit(make_rcompunit(pint_string))
    return CDP.RcompUnit(pint_string)

