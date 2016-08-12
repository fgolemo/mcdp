from contracts import contract
from contracts.utils import raise_desc
from mcdp_cli.query_interpretation import interpret_params_1string
from mcdp_lang.eval_space_imp import eval_space
from mcdp_lang.parse_actions import parse_wrap
from mcdp_lang.syntax import Syntax
from mcdp_posets import UpperSets
from mcdp_posets.rcomp import RcompTop
from mcdp_posets.space import Space
from mcdp_posets.types_universe import express_value_in_isomorphic_space
from mocdp.comp.context import Context
from mocdp.comp.interfaces import NamedDP
import itertools
import numpy as np

def solve_combinations(ndp, combinations, result_like):
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
    return solve_queries(ndp, queries, result_like)

def solve_queries(ndp, queries, result_like):
    results = []
    queries2 = []
    for query in queries:
        res = friendly_solve(ndp, query=query, result_like=result_like)
        q2 = dict([(k, v) for k, (v, _) in query.items()])
        queries2.append(q2)
        results.append(res)
    return dict(queries=queries2, results=results)


@contract(ndp=NamedDP, query='dict(str:tuple(float|int,str))')
def friendly_solve(ndp, query, result_like='dict(str:str)'):
    """
        Returns a set of dict(rname:)
        
        
        query = dict(power=(100,"W"))
        result_like = dict(power="W")
        
        s = solve
    
    """

    # TODO: replace with convert_string_query(ndp, query, context):
    fnames = ndp.get_fnames()
    rnames = ndp.get_rnames()

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

    if len(fnames) == 1:
        value = value[0]
    else:
        value = tuple(value)

    if hasattr(ndp, '_cache_dp'):
        dp = ndp._cache_dp
    else:
        dp = ndp._cache_dp = ndp.get_dp()

    F = dp.get_fun_space()
    F.belongs(value)

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
    
#     print('res: %s' % str(res))
#     print('dtype: %s' % dtype)
#     print('n: %s' % n)
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

