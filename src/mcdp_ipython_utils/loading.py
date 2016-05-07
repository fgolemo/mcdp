from contracts import contract
from mocdp.comp.interfaces import NamedDP
from mocdp.posets import UpperSets
from contracts.utils import raise_desc
from cdpview.query_interpretation import interpret_params_1string
from apptools.naming.context import Context
from mocdp.lang.parse_actions import parse_wrap
from mocdp.lang.syntax import Syntax
from mocdp.lang.eval_space_imp import eval_unit
from mocdp.posets.space import Space
from mocdp.posets.types_universe import express_value_in_isomorphic_space
from mocdp.posets.rcomp import RcompTop


@contract(ndp=NamedDP, query='dict(str:tuple(float|int,str))')
def friendly_solve(ndp, query, result_like='dict(str:str)'):
    """
        Returns a set of dict(rname:)
        
        
        query = dict(power=(100,"W"))
        result_like = dict(power="W")
        
        s = solve
        
    
    """

    fnames = ndp.get_fnames()
    rnames = ndp.get_rnames()
    if not len(fnames) > 1:
        raise NotImplementedError()
    if not len(rnames) > 1:
        raise NotImplementedError()
    
    value = []
    for fname in fnames:
        if not fname in query:
            msg = 'Missing function'
            raise_desc(ValueError, msg, fname=fname, query=query, fnames=fnames)

        F = ndp.get_ftype(fname)
        q, qs = query[fname]
        s = '%s %s' % (q, qs)

        val = interpret_params_1string(s, F=F)
        value.append(val)

    value = tuple(value)

    dp = ndp.get_dp()
    F = dp.get_fun_space()
    F.belongs(value)
#     print('query: %s' % F.format(value))

    res = dp.solve(value)
    R = dp.get_res_space()
    UR = UpperSets(R)
    print('results: %s' % UR.format(res))

    ares = []

    for r in res.minimals:
        fr = dict()
        for rname, sunit in result_like.items():
            i = ndp.get_rnames().index(rname)
            unit = interpret_string_as_space(sunit)
            Ri = ndp.get_rtype(rname)
            ri = r[i]
            v = express_value_in_isomorphic_space(S1=Ri, s1=ri, S2=unit)
            fr[rname] = v
        ares.append(fr)
    return ares

import numpy as np
def to_numpy_array(result_like, res):
    """
        a = 
           
    """
    dtype = []
    for field in result_like:
        dtype.append((field, 'float'))
    n = len(res)
    a = np.zeros(n, dtype=dtype)
    
    for i, r in enumerate(res):
        for field in result_like:
            value = r[field]
            if isinstance(value, RcompTop):
                value = np.inf
            a[field][i] = value
    return a

@contract(p="str", returns=Space)
def interpret_string_as_space(p):
    context = Context()
    res = parse_wrap(Syntax.space_expr, p)[0]
    unit = eval_unit(res, context)
    assert isinstance(unit, Space)
    return unit



import itertools
def get_combinations(c):
    """
        
        c1 = {
            "capacity": (np.linspace(100, 3000, 10), "Wh"),
            "missions": ( 1000, "[]"),
        }
    
    
    """
    iterations = []
    ordered = list(c.items())
    for name, (values, unit) in ordered:
        if isinstance(values, (float, int)):
            values = [values]
        iterations.append(values)
    for x in itertools.product(*tuple(iterations)):
        d = {}
        for i, (name, (_, unit)) in enumerate(ordered):
            d[name] = (x[i], unit)
        yield d

