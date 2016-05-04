# -*- coding: utf-8 -*-
from contracts import contract
from contracts.utils import raise_desc
from mocdp.comp.context import Context
from mocdp.lang.eval_constant_imp import eval_constant
from mocdp.lang.parse_actions import parse_wrap
from mocdp.lang.syntax import Syntax
from mocdp.posets import PosetProduct, get_types_universe


@contract(params="seq(str)")
def interpret_params(params, fnames, F):
    fds = []
    Fds = []
    context = Context()
    for p in params:
        res = parse_wrap(Syntax.constant_value, p)[0]
        vu = eval_constant(res, context)
        fds.append(vu.value)
        Fds.append(vu.unit)
    Fd = PosetProduct(tuple(Fds))
    fd = tuple(fds)

    if len(fnames) != len(fd):
        msg = 'Length does not match.'
        raise_desc(ValueError, msg, fnames=fnames, params=params)

    if len(fnames) == 1:
        Fd = Fd[0]
        fd = fd[0]
    else:
        Fd = Fd
        fd = fd

    # TODO: check units compatible

    tu = get_types_universe()

    tu.check_leq(Fd, F)
    A_to_B, _ = tu.get_embedding(Fd, F)
    fg = A_to_B(fd)
    return fg

@contract(p="str")
def interpret_params_1string(p, F):
    context = Context()

    res = parse_wrap(Syntax.constant_value, p)[0]
    vu = eval_constant(res, context)

    Fd = vu.unit
    fd = vu.value

    tu = get_types_universe()

    tu.check_leq(Fd, F)
    A_to_B, _ = tu.get_embedding(Fd, F)
    fg = A_to_B(fd)
    return fg

@contract(p="str")
def interpret_string(p):
    context = Context()
    res = parse_wrap(Syntax.constant_value, p)[0]
    vu = eval_constant(res, context)
    return vu
