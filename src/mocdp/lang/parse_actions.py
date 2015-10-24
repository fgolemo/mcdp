# -*- coding: utf-8 -*-
from .parts import CDPLanguage
from .utils import parse_action
from compmake.jobs.dependencies import isnamedtupleinstance
from contracts import contract
from contracts.interface import Where
from contracts.utils import indent, raise_desc, raise_wrapped
from mocdp.exceptions import DPInternalError, DPSemanticError, DPSyntaxError
from mocdp.posets import NotBelongs, Space, mult_table
from pyparsing import ParseException, ParseFatalException
import functools


CDP = CDPLanguage


def spa(x, b):
    @parse_action
    def p(tokens, loc, s):
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

        if isnamedtupleinstance(res):
            from mocdp.lang.parts import get_copy_with_where
            res = get_copy_with_where(res, where=where)
        return res
    x.setParseAction(p)

def number_with_unit_parse(t):
    value = t[0]
    units = t[1]
    from mocdp.posets.rcomp import Rcomp
    if isinstance(value, int) and isinstance(units, Rcomp):
        value = float(value)
    try:
        units.belongs(value)
    except NotBelongs:
        msg = 'Value %r does not belong to %s.' % (value, units)
        raise_desc(DPSemanticError, msg)
    res = CDP.ValueWithUnits(value, units)
    return res

def res_shortcut3_parse(tokens):
    name = tokens['name']
    res = []
    for rname in tokens['rnames']:
        res.append(CDP.ResShortcut1(rname, name))
    return CDP.MultipleStatements(res)

def fun_shortcut3_parse(tokens):
    name = tokens['name']
    res = []
    for fname in tokens['fnames']:
        res.append(CDP.FunShortcut1(fname, name))
    return CDP.MultipleStatements(res)

@parse_action
def mult_parse_action(tokens):
    tokens = list(tokens[0])

    ops = []
    for i, t in enumerate(tokens):
        if i % 2 == 0:
            ops.append(t)
        else:
            assert t == '*'

    assert len(ops) > 1

    constants = [op for op in ops if isinstance(op, CDP.ValueWithUnits)]
    nonconstants = [op for op in ops if not isinstance(op, CDP.ValueWithUnits)]

    if constants:
        # compile time optimization
        def mult(a, b):
            R = mult_table(a.unit, b.unit)
            value = a.value * b.value
            return CDP.ValueWithUnits(value=value, unit=R)
        res = functools.reduce(mult, constants)

        if len(nonconstants) == 0:
            return res

        if len(nonconstants) == 1:
            op1 = nonconstants[0]
        else:
            assert len(nonconstants) > 1
            op1 = CDP.MultN(nonconstants)
        function = MultValue(res.value)

        from mocdp.dp_report.gg_ndp import format_unit
        setattr(function, '__name__', '× %s %s' % (res.unit.format(res.value),
                                                   format_unit(res.unit)))
        R_from_F = MultType(res.unit)
        return CDP.GenericNonlinearity(function=function, op1=op1, R_from_F=R_from_F)

    return CDP.MultN(ops)

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

@parse_action
def plus_parse_action(tokens):
    tokens = list(tokens[0])

    ops = []
    for i, t in enumerate(tokens):
        if i % 2 == 0:
            ops.append(t)
        else:
            assert t == '+'

    def simplify(op):
        if isinstance(op, CDP.GenericNonlinearity) and isinstance(op.function, PlusValue):
            value = op.function.value
            unit = op.factor
            vu = CDP.ValueWithUnits(value=value, unit=unit)
            return [op.op1, vu]
        else:
            return [op]
    newops = []
    for op in ops:
        newops.extend(simplify(op))

    ops = newops

    constants = [op for op in ops if isinstance(op, CDP.ValueWithUnits)]
    nonconstants = [op for op in ops if not isinstance(op, CDP.ValueWithUnits)]

    if constants:
        # compile time optimization
        def add(a, b):
            R = add_table(a.unit, b.unit)
            value = a.value + b.value
            return CDP.ValueWithUnits(value=value, unit=R)
        res = functools.reduce(add, constants)
        if len(nonconstants) == 0:
            return res

        if len(nonconstants) == 1:
            op1 = nonconstants[0]
        else:
            assert len(nonconstants) > 1
            op1 = CDP.PlusN(nonconstants)
        function = PlusValue(res.value)
        from mocdp.dp_report.gg_ndp import format_unit
        setattr(function, '__name__', '+ %s %s' % (res.unit.format(res.value),
                                                   format_unit(res.unit)))
        R_from_F = PlusType(res.unit)
        return CDP.GenericNonlinearity(function=function, op1=op1, R_from_F=R_from_F)

    return CDP.PlusN(ops)

def add_table(F1, F2):
    if not F1 == F2:
        msg = 'Incompatible units for addition.'
        raise_desc(DPSemanticError, msg, F1=F1, F2=F2)
    return F1

class PlusType():
    @contract(factor=Space)
    def __init__(self, factor):
        self.factor = factor
    def __call__(self, F):
        return add_table(F, self.factor)

class PlusValue():
    def __init__(self, value):
        self.value = value
    def __call__(self, x):
        return x + self.value

@parse_action
def mult_inv_parse_action(tokens):
    tokens = list(tokens[0])

    ops = []
    for i, t in enumerate(tokens):
        if i % 2 == 0:
            ops.append(t)
        else:
            assert t == '*'

    assert len(ops) > 1
    assert len(ops) == 2
    return CDP.InvMult(ops)



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

# @contract(returns=NamedDP)
def parse_ndp(string):
    from mocdp.lang.syntax import Syntax
    v = parse_wrap(Syntax.dp_rvalue, string)[0]
    from mocdp.lang.blocks import Context, eval_dp_rvalue
    context = Context()
    res = eval_dp_rvalue(v, context)
    # I'm not sure what happens to the context
    # if context.names # error ??

    from mocdp.comp.interfaces import NamedDP
    assert isinstance(res, NamedDP), res
    return res

def parse_line(line):
    from mocdp.lang.syntax import Syntax
    return parse_wrap(Syntax.line_expr, line)[0]

@parse_action
def dp_model_parse_action(tokens):
    res = list(tokens)
    # if not res:
    #    raise DPSemanticError('Empty model')
    from mocdp.lang.blocks import interpret_commands
    return interpret_commands(res)

def power_expr_parse(t):
    op1 = t[0]
    exp = t[1]
    assert isinstance(exp, CDPLanguage.IntegerFraction)
    return CDP.Power(op1=op1, exponent=exp)

