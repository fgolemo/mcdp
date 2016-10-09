# -*- coding: utf-8 -*-
import itertools

from contracts import contract
from contracts.utils import raise_desc, raise_wrapped
from mcdp_cli.query_interpretation import interpret_params_1string
from mcdp_dp.dp_transformations import get_dp_bounds
from mcdp_dp.tracer import Tracer
from mcdp_lang.eval_space_imp import eval_space
from mcdp_lang.parse_actions import parse_wrap
from mcdp_lang.syntax import Syntax
from mcdp_posets import NotLeq, Space, UpperSets, express_value_in_isomorphic_space
from mcdp_posets.rcomp import RcompTop
from mocdp.comp.context import Context
from mocdp.comp.interfaces import NamedDP
import numpy as np


def solve_combinations(ndp, combinations, result_like, lower=None, upper=None):
    """
    combinations = {
        "capacity": (np.linspace(50, 3000, 10), "Wh"),
        "missions": ( 1000, "[]"),
    }
    result_like = dict(maintenance="s", cost="CHF", mass='kg')
    what_to_plot_res = result_like
    what_to_plot_fun = dict(capacity="Wh", missions="[]")
    
    """
    queries = list(get_combinations(combinations))
    return solve_queries(ndp, queries, result_like, lower=lower, upper=upper)

def solve_queries(ndp, queries, result_like, lower=None, upper=None):
    results = []
    queries2 = []
    implementations = []
    dp0 = ndp.get_dp()
    I = dp0.get_imp_space()
    for query in queries:
        res, imps = friendly_solve(ndp, query=query, result_like=result_like,
                                              upper=upper, lower=lower)
        
        q2 = dict([(k, v) for k, (v, _) in query.items()])
        queries2.append(q2)
        results.append(res)
        implementations.append(imps)
    return dict(queries=queries2, results=results, implementations=implementations,
                I = I)


@contract(ndp=NamedDP, query='dict(str:tuple(float|int,str))')
def friendly_solve(ndp, query, result_like='dict(str:str)', upper=None, lower=None):
    """
        query = dict(power=(100,"W"))
        result_like = dict(power="W")
        
        s = solve
    
    """
    print('friendly_solve(upper=%s, lower=%s)' % (upper, lower))
    # TODO: replace with convert_string_query(ndp, query, context):
    fnames = ndp.get_fnames()
    rnames = ndp.get_rnames()

    if not len(rnames) >= 1:
        raise NotImplementedError()
    
    value = []

    for fname in fnames:
        if not fname in query:
            msg = 'Missing function'
            raise_desc(ValueError, msg, fname=fname, query=query, fnames=fnames)

        F = ndp.get_ftype(fname)
        q, qs = query[fname]
        s = '%s %s' % (q, qs)

        try:
            val = interpret_params_1string(s, F=F)
        except NotLeq as e:
            raise_wrapped(ValueError, e, 'wrong type', fname=fname)
            
        value.append(val)

    if len(fnames) == 1:
        value = value[0]
    else:
        value = tuple(value)

    if hasattr(ndp, '_cache_dp0'):
        dp0 = ndp._cache_dp0
    else:
        
        dp0 = ndp.get_dp()
        ndp._cache_dp0 = dp0
        
    if upper is not None:
        _, dp = get_dp_bounds(dp0, nl=1, nu=upper)

    elif lower is not None:
        dp, _ = get_dp_bounds(dp0, nl=lower, nu=1)
    else:
        dp = dp0
        
    F = dp.get_fun_space()
    F.belongs(value)

    from mocdp import logger
    trace = Tracer(logger=logger)
    res = dp.solve_trace(value, trace)
    R = dp.get_res_space()
    UR = UpperSets(R)
    print('value: %s' % F.format(value))
    print('results: %s' % UR.format(res))

    ares = []
    implementations = []

    for r in res.minimals:
        rnames = ndp.get_rnames()
        fr = dict()
        for rname, sunit in result_like.items():
            if not rname in rnames:
                msg = 'Could not find resource %r.' % rname
                raise_desc(ValueError, msg, rnames=rnames)
            i = rnames.index(rname)
            unit = interpret_string_as_space(sunit)
            Ri = ndp.get_rtype(rname)
            if len(rnames) > 1:
                ri = r[i]
            else:
                assert i == 0
                ri = r
            v = express_value_in_isomorphic_space(S1=Ri, s1=ri, S2=unit)
            fr[rname] = v
        
        ares.append(fr)
        
        ms = dp.get_implementations_f_r(value, r)
        implementations.append(ms)
        
    return ares, implementations

@contract(res='list(dict(str:*))')
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
    res = parse_wrap(Syntax.space, p)[0]
    unit = eval_space(res, context)
    assert isinstance(unit, Space)
    return unit

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

