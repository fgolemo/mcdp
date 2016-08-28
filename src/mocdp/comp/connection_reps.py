from collections import Counter
from contracts.utils import raise_desc
from mocdp.comp.context import Connection
from mocdp.comp.interfaces import NamedDP
from mocdp.comp.wrap import SimpleWrap


class ThereAreReps(ValueError):
    pass


def check_no_reps(name2dp):
    """ raises ThereAreReps if some are repeated """
    all_functions = []
    all_resources = []
    for _, ndp in name2dp.items():
        assert isinstance(ndp, NamedDP), ndp
        all_functions.extend(ndp.get_fnames())
        all_resources.extend(ndp.get_rnames())

    if there_are_repetitions(all_functions) or there_are_repetitions(all_resources):

        find_reps = lambda d: [k for (k, v) in Counter(d).iteritems() if v > 1]
        repeated_resources = find_reps(all_resources)
        repeated_functions = find_reps(all_functions)


        raise_desc(ThereAreReps, 'Repetitions',
                   all_functions=all_functions,
                   all_resources=all_resources,
                   repeated_resources=repeated_resources,
                   repeated_functions=repeated_functions)


def relabel(name2dp, connections):
    """ 
        Relabels signals so that there are no repetitions. 
    
        Works only on completely flattened model. (SimpleWrap) 
    """

    for ndp in name2dp.values():
        if not isinstance(ndp, SimpleWrap):
            raise_desc(ValueError, "I can only relabel if they are all SimpleWrap.")
            
    # id_ndp, name -> id_ndp, name2
    fun_map = {}
    fun_names = set()
    res_map = {}
    res_names = set()

    def get_new_name(f, names):
        for i in range(10):
            p = f + '%d' % i
            if not p in names:
                return p
        assert False

    for id_ndp, ndp in name2dp.items():
        for f in ndp.get_fnames():
            if not f in fun_names:
                fun_names.add(f)
            else:
                f2 = get_new_name(f, fun_names)
                fun_names.add(f2)
                fun_map[(id_ndp, f)] = (id_ndp, f2)

        for r in ndp.get_rnames():
            if not r in res_names:
                res_names.add(r)
            else:
                r2 = get_new_name(r, res_names)
                res_names.add(r2)
                res_map[(id_ndp, r)] = (id_ndp, r2)

    need1 = set([id_ndp for (id_ndp, _) in res_map])
    need2 = set([id_ndp for (id_ndp, _) in fun_map])
    need = need1
    need.update(need2)
    
    name2dp_ = dict(**name2dp)

    for id_ndp in need:
        fun = dict([(f, f2) for (_, f), (_, f2) in fun_map.items() if _ == id_ndp])
        res = dict([(r, r2) for (_, r), (_, r2) in res_map.items() if _ == id_ndp])

        print(id_ndp)

        name2dp_[id_ndp] = simplewrap_relabel(name2dp[id_ndp], fun_map=fun, res_map=res)

    connections_ = connections_relabel(connections, fun_map, res_map)

    relabeling = dict(fun_map=fun_map, res_map=res_map)

    return name2dp_, connections_, relabeling


def connections_relabel(connections, fun_map, res_map):
    def f(c):
        key = (c.dp1, c.s1)
        dp1, s1 = res_map.get(key, key)
        key = (c.dp2, c.s2)
        dp2, s2 = fun_map.get(key, key)
        return Connection(dp1=dp1, s1=s1, dp2=dp2, s2=s2)
    return map(f, connections)

    
def simplewrap_relabel(sw, fun_map, res_map):
    fnames2 = [ fun_map.get(_, _) for _ in sw.get_fnames()]
    rnames2 = [ res_map.get(_, _) for _ in sw.get_rnames()]
    if len(fnames2) == 1:
        fnames2 = fnames2[0]
    if len(rnames2) == 1:
        rnames2 = rnames2[0]
    return SimpleWrap(sw.dp, fnames2, rnames2, icon=sw.icon)
        

def there_are_reps(name2dp):
    try:
        check_no_reps(name2dp)
    except ThereAreReps:
        return True
    else:
        return False


def there_are_repetitions(x):
    return len(x) != len(set(x))
