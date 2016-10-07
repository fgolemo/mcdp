# -*- coding: utf-8 -*-
from contracts import contract
from contracts.utils import raise_desc
from mcdp_lang.eval_constant_imp import eval_constant
from mcdp_lang.parse_actions import parse_wrap
from mcdp_lang.parse_interface import parse_constant
from mcdp_lang.syntax import Syntax
from mcdp_posets import PosetProduct, get_types_universe
from mocdp.comp.context import Context


@contract(query='dict(str:str)')
def convert_string_query(ndp, query, context):
    """
        Converts a string query to a value that can be passed to the DP.
        
        Example:
            f = bind(ndp, dict(power='100mW'))
            f == 0.1
            dp.solve(f)
    
    """
    # first: make sure the names are the same

    fnames = ndp.get_fnames()
    fnames2 = set(query)
    if set(fnames) != fnames2:
        msg = 'Missing values in query or too many values.'
        raise_desc(ValueError, msg, fnames=fnames, query=query)

    fds = []
    Fds = []

    tu = get_types_universe()

    for fname in fnames:
        q = query[fname]
        vu = parse_constant(q, context)

        fds.append(vu.value)
        Fds.append(vu.unit)

        F0 = ndp.get_ftype(fname)
        if not tu.leq(vu.unit, F0):
            msg = 'Invalid value for %r: %s does not cast to %s.' % (fname, vu, F0)
            raise_desc(ValueError, msg)

    Fd = PosetProduct(tuple(Fds))
    fd = tuple(fds)

    if len(fnames) == 1:
        Fd = Fd[0]
        fd = fd[0]
    else:
        Fd = Fd
        fd = fd

    F = ndp.get_ftypes(fnames)
    if len(fnames) == 1:
        F = F[0]

    tu.check_leq(Fd, F)
    A_to_B, _ = tu.get_embedding(Fd, F)
    fg = A_to_B(fd)

    print('Fd: %s' % Fd.format(fd))
    print('F: %s' % F.format(fg))
    return fg


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

    tu = get_types_universe()

    tu.check_leq(Fd, F)
    A_to_B, _ = tu.get_embedding(Fd, F)
    fg = A_to_B(fd)
    print('Fd: %s' % Fd.format(fd))
    print('F: %s' % F.format(fg))
    return fg

@contract(p="str")
def interpret_params_1string(p, F, context=None):
    if context is None:
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
