# -*- coding: utf-8 -*-
from .parts import CDPLanguage
from .utils import parse_action
from compmake.jobs.dependencies import isnamedtupleinstance
from contracts import contract
from contracts.interface import Where
from contracts.utils import indent, raise_desc, raise_wrapped, check_isinstance
from mocdp.comp.context import ValueWithUnits
from mocdp.dp.dp_sum import sum_units
from mocdp.exceptions import DPInternalError, DPSemanticError, DPSyntaxError
from mocdp.lang.namedtuple_tricks import get_copy_with_where
from mocdp.lang.utils_lists import make_list
from mocdp.posets import RcompUnits, Space, mult_table
from pyparsing import ParseException, ParseFatalException
import functools
import os
from mocdp.posets.nat import Nat
import warnings

CDP = CDPLanguage

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


class MultType():
    def __init__(self, factor):
        self.factor = factor
    def __call__(self, F):
        return mult_table(F, self.factor)

class MultValue():

    def __init__(self, res):
        self.res = res

    def __call__(self, x):
        return x * self.res

@contract(S=RcompUnits)
def inv_unit(S):
    # S.units is a pint quantity
    res = RcompUnits(1 / S.units)
    return res

def inv_constant(a):
    from mocdp.posets.rcomp import Rcomp
    if a.unit == Nat():
        raise NotImplementedError('division by natural number')
        warnings.warn('Please think more about this. Now 1/N -> 1.0/N')
        unit = Rcomp()
    else:
        unit = inv_unit(a.unit)

    if a.value == 0:
        raise DPSemanticError('Division by zero')
    # TODO: what about integers?
    value = 1.0 / a.value
    return ValueWithUnits(value=value, unit=unit)


def mult_constants2(a, b):
    R = mult_table(a.unit, b.unit)
    value = a.value * b.value
    return ValueWithUnits(value=value, unit=R)

def mult_constantsN(seq):
    res = functools.reduce(mult_constants2, seq)
    # print('seq: %s res: %s' % (seq, res))
    return res


def add_table(F1, F2):
    if not F1 == F2:
        msg = 'Incompatible units for addition.'
        raise_desc(DPSemanticError, msg, F1=F1, F2=F2)
    return F1

def plus_constants2(a, b):
    R = a.unit 
    Fs = [a.unit, b.unit]
    values = [a.value, b.value]
    res = sum_units(Fs, values, R)
    return ValueWithUnits(value=res, unit=R)

def plus_constantsN(constants):
    return functools.reduce(plus_constants2, constants)


@parse_action
@wheredecorator
def plus_parse_action(tokens):
    tokens = list(tokens[0])
#
#     ops = []
#     glyphs = []
#     for i, t in enumerate(tokens):
#         if i % 2 == 0:
#             ops.append(t)
#         else:
# #             assert t == '+'
#             assert isinstance(t, CDP.plus)
#             glyphs.append(t)


    l = make_list(tokens)
    assert l.where.character_end is not None
    res = CDP.PlusN(l, where=l.where)
    return res


class PlusType():
    @contract(factor=Space)
    def __init__(self, factor):
        self.factor = factor
    def __call__(self, F):
        return add_table(F, self.factor)

class PlusValue():

    def __init__(self, F, R, c):
        check_isinstance(F, RcompUnits)
        check_isinstance(c.unit, RcompUnits)
        self.F = F
        self.c = c
        c.unit
        c.value
        self.R = R
    def __call__(self, x):
        values = [self.c.value, x]
        Fs = [self.c.unit, self.F]
        return sum_units(Fs, values, self.R)


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
    except (DPSyntaxError, DPSemanticError) as e:
        raise e.with_filename(filename)

def parse_wrap(expr, string):
    # Nice trick: the removE_comments doesn't change the number of lines
    # it only truncates them...
    string0 = remove_comments(string)

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

def parse_ndp_filename(filename):
    """ Reads the file and returns as NamedDP.
        The exception are annotated with filename. """
    with open(filename) as f:
        contents = f.read()
    try:
        return parse_ndp(contents)
    except (DPSyntaxError, DPSemanticError) as e:
        raise e.with_filename(filename)

# @contract(returns=NamedDP)
def parse_ndp(string, context=None):
    from mocdp.comp.context import Context
    from mocdp.lang.syntax import Syntax
    from mocdp.lang.eval_mcdp_type_imp import eval_dp_rvalue
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

def parse_line(line):
    from mocdp.lang.syntax import Syntax
    return parse_wrap(Syntax.line_expr, line)[0]


def power_expr_parse(t):
    op1 = t[0]
    exp = t[1]
    assert isinstance(exp, (CDPLanguage.IntegerFraction, int))
    return CDP.Power(op1=op1, exponent=exp)

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

