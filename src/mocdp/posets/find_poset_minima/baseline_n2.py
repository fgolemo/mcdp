from .utils import time_poset_minima_func
from contracts import contract
from mocdp.posets.poset import Poset

__all__ = [
    'poset_minima',
]

@time_poset_minima_func
@contract(elements='seq|set')
def poset_minima(elements, leq):
    """ Find the minima of a poset according to given comparison 
        function. For small sets only - O(n^2). """
    n = len(elements)
    if n == 1:
        return set(elements)

    res = []
    for e in elements:
        # nobody is less than it
        # should_add = all([not leq(r, e) for r in res])
        for r in res:
            if leq(r, e):
                should_add = False
                break
        else:
            should_add = True

        if should_add:
            # remove the ones that are less than this
            res = [r for r in res if not leq(e, r)] + [e]
    return set(res)

@contract(poset=Poset, elements='set|seq')
def poset_minima_n2(poset, elements):
    """ Baseline implementation of "poset_minima" with 
        complexity n^2. """
    return poset_minima(elements, poset.leq)
